"""
Path B - Prototype 9: EML AS AN ACTIVATION FUNCTION (the untried direction).

The blind test failed on +, *, /, x^2 because we forced discrete leaves and made a
PURE-eml tree build everything by brute depth. That fights eml's nature.

New idea: use eml as the *nonlinearity* between LINEAR layers, exactly like an
activation in a neural net. Why this should work: eml provides exp AND log in one op,
and log turns multiplication/powers into ADDITION:
    x*y = exp(ln x + ln y),   x^2 = exp(2 ln x),   x/y = exp(ln x - ln y).
So an affine layer (does sums) + eml (does exp/log) can express the multiplicative
structure that pure-eml-by-depth could not.

Architecture (small "eml-MLP", 2 eml layers):
    h_j = eml( A_j . [x,1] , B_j . [x,1] )        # H eml features (use real part)
    y   = Re( eml( C . [h,1] , D . [h,1] ) )       # one more eml layer -> scalar
Trained blind with Adam + relative loss + multi-start on the SAME shapes that failed.
"""
import numpy as np
from autograd import grad
import autograd.numpy as anp
from eml_stable import eml_pair

def affine(P, feats):
    # P: (k+1,), feats: (N,k) -> (N,)
    return anp.dot(feats, P[:-1]) + P[-1]

def net(params, X, cap):
    A, B, C, D = params
    H = A.shape[0]
    hs = []
    for j in range(H):
        z1 = (affine(A[j], X), anp.zeros(X.shape[0]))
        z2 = (affine(B[j], X), anp.zeros(X.shape[0]))
        hj = eml_pair(z1, z2, cap=cap)
        hs.append(hj[0])                 # real part of each eml feature
    Hmat = anp.stack(hs, axis=1)         # (N, H)
    o1 = (affine(C, Hmat), anp.zeros(X.shape[0]))
    o2 = (affine(D, Hmat), anp.zeros(X.shape[0]))
    out = eml_pair(o1, o2, cap=cap)
    return out[0]

def unpack(theta, n, H):
    i = 0
    A = theta[i:i + H * (n + 1)].reshape(H, n + 1); i += H * (n + 1)
    B = theta[i:i + H * (n + 1)].reshape(H, n + 1); i += H * (n + 1)
    C = theta[i:i + (H + 1)]; i += H + 1
    D = theta[i:i + (H + 1)]; i += H + 1
    return (A, B, C, D)

def loss(theta, X, y, cap, n, H, yscale):
    pred = net(unpack(theta, n, H), X, cap)
    return anp.mean(((pred - y) / yscale) ** 2)

def rel_rmse(theta, X, y, cap, n, H):
    pred = np.array(net(unpack(theta, n, H), X, cap))
    return float(np.sqrt(np.mean((pred - y) ** 2)) / (np.std(y) + 1e-12))

def fit(X, y, H=4, seeds=4, epochs=300, cap=8.0):
    n = X.shape[1]
    P = 2 * H * (n + 1) + 2 * (H + 1)
    yscale = np.std(y) + 1e-9
    g = grad(loss); best = 1e9
    for s in range(seeds):
        rng = np.random.RandomState(s)
        theta = rng.randn(P) * 0.4
        m = np.zeros(P); v = np.zeros(P); b1, b2, e, lr = 0.9, 0.999, 1e-8, 0.02
        for t in range(1, epochs + 1):
            G = np.clip(g(theta, X, y, cap, n, H, yscale), -1e6, 1e6)
            m = b1 * m + (1 - b1) * G; v = b2 * v + (1 - b2) * G ** 2
            theta = theta - lr * (m / (1 - b1 ** t)) / (np.sqrt(v / (1 - b2 ** t)) + e)
        best = min(best, rel_rmse(theta, X, y, cap, n, H))
    return best

if __name__ == "__main__":
    rng = np.random.RandomState(0); N = 60
    x0 = rng.uniform(0.4, 1.6, N); x1 = rng.uniform(0.5, 2.0, N)
    X = np.stack([x0, x1], axis=1)
    targets = {
        "sum      x0 + x1":   x0 + x1,
        "product  x0 * x1":   x0 * x1,
        "ratio    x0 / x1":   x0 / x1,
        "power    x0**2":     x0 ** 2,
        "exp-ratio exp(x0/x1)": np.exp(x0 / x1),
    }
    print("EML-as-activation net (affine -> eml -> affine -> eml), blind fit")
    print("rel_RMSE: 0 = perfect, ~1 = mean.  (pure-eml tree failed ALL of these)\n")
    print(f"{'target':>22} | {'eml-net rel_RMSE':>16} | verdict")
    for name, y in targets.items():
        r = fit(X, y)
        verdict = "recovered" if r < 0.1 else ("partial" if r < 0.4 else "fails")
        print(f"{name:>22} | {r:>16.3f} | {verdict}")
