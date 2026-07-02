"""
Path B - Prototype 8: HONEST blind test.

No hand-crafted, EML-native targets this time. We generate data from several REAL
formula shapes (the kinds that appear in the Feynman set) and ask a depth-2/3 EML
tree to fit them, WITHOUT telling it the answer. Leaves are the raw vocabulary
{1, x0, x1, ...} only (soft-selected). We report relative RMSE = RMSE / std(y),
so 0 = perfect, ~1 = no better than predicting the mean.

Purpose: find out where a shallow pure-EML tree genuinely wins and where it loses.
An honest negative on some shapes is a real result, not a failure of the experiment.
"""
import numpy as np
from autograd import grad
import autograd.numpy as anp
from eml_stable import eml_pair

def softmax(logits, tau):
    z = (logits - anp.max(logits)) / tau
    e = anp.exp(z); return e / anp.sum(e)

def leaf(logits, X, tau):
    w = softmax(logits, tau)
    re = w[1] * 1.0 + anp.zeros(X.shape[0])
    for i in range(X.shape[1]):
        re = re + w[2 + i] * X[:, i]
    return (re, 0.0 * re)

def tree(params, X, tau, cap, depth):
    n = 2 ** depth
    lvl = [leaf(params[i], X, tau) for i in range(n)]
    while len(lvl) > 1:
        lvl = [eml_pair(lvl[i], lvl[i + 1], cap=cap) for i in range(0, len(lvl), 2)]
    return lvl[0]

def loss(params, X, y, tau, cap, depth, yscale):
    re, _ = tree(params, X, tau, cap, depth)
    return anp.mean(((re - y) / yscale) ** 2)

def rel_rmse(params, X, y, cap, depth):
    re, _ = tree(params, X, 0.1, cap, depth)
    return float(np.sqrt(np.mean((np.array(re) - y) ** 2)) / (np.std(y) + 1e-12))

def fit(X, y, depth, dict_size, seeds=4, epochs=220, cap=6.0):
    yscale = np.std(y) + 1e-9
    g = grad(loss); best = 1e9
    for s in range(seeds):
        rng = np.random.RandomState(s)
        params = rng.randn(2 ** depth, dict_size) * 0.5
        m = np.zeros_like(params); v = np.zeros_like(params)
        b1, b2, e, lr = 0.9, 0.999, 1e-8, 0.03
        for t in range(1, epochs + 1):
            tau = max(0.15, 2.0 * (0.99 ** t))
            G = g(params, X, y, tau, cap, depth, yscale)
            G = np.clip(G, -1e6, 1e6)
            m = b1 * m + (1 - b1) * G; v = b2 * v + (1 - b2) * G ** 2
            params = params - lr * (m / (1 - b1 ** t)) / (np.sqrt(v / (1 - b2 ** t)) + e)
        best = min(best, rel_rmse(params, X, y, cap, depth))
    return best

def best_over_depth(X, y, dsz, depths=(1, 2), seeds=2, epochs=140):
    return min(fit(X, y, d, dsz, seeds=seeds, epochs=epochs) for d in depths)

if __name__ == "__main__":
    rng = np.random.RandomState(0)
    N = 50
    x0 = rng.uniform(0.3, 1.5, N); x1 = rng.uniform(0.5, 2.0, N)
    X = np.stack([x0, x1], axis=1)
    dsz = 2 + 2  # {0,1,x0,x1}

    targets = {
        "eml-native exp(x0)-ln(x1)  (control)": np.exp(x0) - np.log(x1),
        "product    x0 * x1":                    x0 * x1,
        "ratio      x0 / x1":                    x0 / x1,
        "power      x0**2":                      x0 ** 2,
        "sum        x0 + x1":                    x0 + x1,
        "exp-ratio  exp(x0/x1)":                 np.exp(x0 / x1),
    }
    print("Blind fit, pure-EML tree, leaves = {0,1,x0,x1}, best over depth in {1,2}")
    print("rel_RMSE: 0 = perfect, ~1 = no better than predicting the mean\n")
    print(f"{'target shape':>38} | {'best rel_RMSE':>13} | verdict")
    for name, y in targets.items():
        r = best_over_depth(X, y, dsz)
        verdict = "recovered" if r < 0.1 else ("partial" if r < 0.5 else "FAILS (>= mean)")
        print(f"{name:>38} | {r:>13.3f} | {verdict}")
