"""
Path B - Prototype 5: Multivariable EML tree recovering a formula the discrete
beam-search engine cannot reach at its complexity-6 budget.

Target (exactly a full depth-2 EML tree, leaves = x0, x1, x2, 1):
    y = eml( eml(x0, x1), eml(x2, 1) )
      = exp( exp(x0) - ln(x1) ) - x2
As a discrete expression tree this is
    Subtract( Exp(Subtract(Exp(v0), Log(v1))), v2 )
whose node count is ~8 -> UNREACHABLE by the published engine at max_complexity=6.
The gradient tree, by contrast, has a FIXED depth-2 structure and just tunes the leaf
gates, so cost does not explode with variable count.

Model: full binary EML tree, depth 2 (4 leaves). Each leaf is a temperature-softmax
soft gate over the dictionary {0, 1, x0, x1, x2}. Complex numbers = (re, im) pairs.
Train with Adam + tau annealing + entropy penalty; multi-start; then hard-snap and
read off the closed-form formula. No node-norm here: at depth 2 it is unnecessary and
would perturb the exact symbolic semantics we want to recover.
"""
import autograd.numpy as np
from autograd import grad
from eml_stable import eml_pair

def make_dict(n_vars):
    return ["0", "1"] + [f"x{i}" for i in range(n_vars)]

def softmax(logits, tau):
    z = (logits - np.max(logits)) / tau
    e = np.exp(z); return e / np.sum(e)

def leaf_pair(logits, X, tau):
    """X: (N, n_vars) batch. Leaf = soft mix over {0,1,x0..}; returns (re[N], im[N])."""
    w = softmax(logits, tau)
    re = w[1] * 1.0 + np.zeros(X.shape[0])
    for i in range(X.shape[1]):
        re = re + w[2 + i] * X[:, i]
    return (re, 0.0 * re)

def tree_forward(params, X, tau, cap):
    """Full depth-2 tree over a batch: eml(eml(l0,l1), eml(l2,l3))."""
    leaves = [leaf_pair(params[i], X, tau) for i in range(4)]
    left = eml_pair(leaves[0], leaves[1], cap=cap)
    right = eml_pair(leaves[2], leaves[3], cap=cap)
    return eml_pair(left, right, cap=cap)

def entropy_pen(params, tau):
    e = 0.0
    for p in params:
        w = softmax(p, tau); e = e + (-np.sum(w * np.log(w + 1e-12)))
    return e

def loss_fn(params, X, y, tau, cap, beta, yscale):
    re, _ = tree_forward(params, X, tau, cap)      # (N,)
    mse = np.mean(((re - y) / yscale) ** 2)        # scale-normalized MSE (shaped loss)
    return mse + beta * entropy_pen(params, tau)

def snap_formula(params, dct):
    idx = [int(np.argmax(p)) for p in params]
    s = [dct[i] for i in idx]
    return idx, f"eml(eml({s[0]}, {s[1]}), eml({s[2]}, {s[3]}))"

def snapped_error(params, X, y, cap, n_vars):
    idx = [int(np.argmax(p)) for p in params]
    def leaf_hard(i):
        if idx[i] == 0: return (np.zeros(len(y)), np.zeros(len(y)))
        if idx[i] == 1: return (np.ones(len(y)), np.zeros(len(y)))
        return (X[:, idx[i] - 2], np.zeros(len(y)))
    l = [leaf_hard(i) for i in range(4)]
    left = eml_pair(l[0], l[1], cap=cap); right = eml_pair(l[2], l[3], cap=cap)
    re, _ = eml_pair(left, right, cap=cap)
    return float(np.mean((re - y) ** 2))

def train_once(seed, X, y, n_vars, dct, cap=6.0, epochs=300):
    rng = np.random.RandomState(seed)
    params = rng.randn(4, len(dct)) * 0.5
    yscale = np.std(y) + 1e-9
    g = grad(loss_fn)
    m = np.zeros_like(params); v = np.zeros_like(params)
    b1, b2, eps, lr = 0.9, 0.999, 1e-8, 0.03
    for t in range(1, epochs + 1):
        tau = max(0.1, 2.0 * (0.99 ** t))
        beta = 0.01 * min(1.0, t / 250.0)
        G = g(params, X, y, tau, cap, beta, yscale)
        G = np.clip(G, -1e6, 1e6)
        m = b1 * m + (1 - b1) * G; v = b2 * v + (1 - b2) * G ** 2
        mhat = m / (1 - b1 ** t); vhat = v / (1 - b2 ** t)
        params = params - lr * mhat / (np.sqrt(vhat) + eps)
    err = snapped_error(params, X, y, cap, n_vars)
    _, formula = snap_formula(params, dct)
    return err, formula

if __name__ == "__main__":
    rng = np.random.RandomState(3)
    n_vars = 3
    dct = make_dict(n_vars)
    N = 60
    x0 = rng.uniform(0.0, 0.6, N)
    x1 = rng.uniform(1.0, 2.0, N)
    x2 = rng.uniform(0.0, 1.0, N)
    X = np.stack([x0, x1, x2], axis=1)
    y = np.exp(np.exp(x0) - np.log(x1)) - x2      # = eml(eml(x0,x1), eml(x2,1))

    print("Target: y = exp(exp(x0) - ln(x1)) - x2   [3 vars, needs discrete complexity ~8]")
    print("Ground truth tree: eml(eml(x0, x1), eml(x2, 1))\n")
    print(f"{'restart':>7} | {'snap_err':>11} | {'snap_formula'}")
    best = (1e9, None)
    for s in range(5):
        err, formula = train_once(s, X, y, n_vars, dct)
        mark = "  <--" if err < best[0] else ""
        if err < best[0]: best = (err, formula)
        print(f"{s:>7} | {err:>11.3e} | {formula}{mark}")
    print("\n--- BEST ---")
    print(f"{best[1]}   snap_err = {best[0]:.3e}")
    print("Ground truth : eml(eml(x0, x1), eml(x2, 1))")
