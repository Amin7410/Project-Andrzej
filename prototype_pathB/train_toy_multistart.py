"""
Path B - Prototype 3: End-to-end gradient training + annealing + snapping,
with multi-start to escape local minima.

A single run easily gets stuck in a local minimum (see finding #2 in README).
The practical fix (matching the hybrid architecture in ../docs/PATH_B_RESEARCH.md,
sec. 2.6/2.7): run SEVERAL random restarts with slow annealing, keep the best snap.

Toy target (exactly representable by an EML tree):
    y = e - ln(x) = eml(1, x)     -> depth-1 tree: root eml(left_leaf, right_leaf)
Each leaf: soft softmax over {0, 1, x}; tau annealed 2.0 -> 0.1; entropy penalty
drives each leaf toward one-hot so the final hard snap is lossless.
"""
import autograd.numpy as np
from autograd import grad
from eml_stable import eml_pair

DICT = ["0", "1", "x"]

def softmax(logits, tau):
    z = (logits - np.max(logits)) / tau
    e = np.exp(z); return e / np.sum(e)

def leaf_pair(logits, x, tau):
    w = softmax(logits, tau)
    return (w[1] * 1.0 + w[2] * x, 0.0 * w[0])

def forward(params, x, tau, cap):
    l = leaf_pair(params[0], x, tau); r = leaf_pair(params[1], x, tau)
    return eml_pair(l, r, cap=cap)

def entropy_pen(params, tau):
    e = 0.0
    for p in params:
        w = softmax(p, tau); e = e + (-np.sum(w * np.log(w + 1e-12)))
    return e

def loss_fn(params, xs, ys, tau, cap, beta):
    tot = 0.0
    for x, y in zip(xs, ys):
        re, _ = forward(params, x, tau, cap); tot = tot + (re - y) ** 2
    return tot / len(xs) + beta * entropy_pen(params, tau)

def snapped_error(params, xs, ys, cap):
    """Error after hard-snapping each leaf to its argmax dictionary symbol."""
    idx = [int(np.argmax(p)) for p in params]; basis = {0: 0.0, 1: 1.0}
    tot = 0.0
    for x, y in zip(xs, ys):
        vals = [(basis.get(i, x), 0.0) for i in idx]
        re, _ = eml_pair(vals[0], vals[1], cap=cap); tot += (re - y) ** 2
    return tot / len(xs), f"eml({DICT[idx[0]]}, {DICT[idx[1]]})"

def train_once(seed, xs, ys, cap=6.0, epochs=300):
    rng = np.random.RandomState(seed)
    params = rng.randn(2, 3) * 0.5
    g = grad(loss_fn)
    m = [np.zeros(3), np.zeros(3)]; v = [np.zeros(3), np.zeros(3)]
    b1, b2, eps, lr = 0.9, 0.999, 1e-8, 0.04
    for t in range(1, epochs + 1):
        tau = max(0.1, 2.0 * (0.992 ** t))       # slow annealing
        beta = 0.01 * min(1.0, t / 300.0)
        G = g(params, xs, ys, tau, cap, beta)
        for i in range(2):
            m[i] = b1 * m[i] + (1 - b1) * G[i]; v[i] = b2 * v[i] + (1 - b2) * G[i] ** 2
            mhat = m[i] / (1 - b1 ** t); vhat = v[i] / (1 - b2 ** t)
            params[i] = params[i] - lr * mhat / (np.sqrt(vhat) + eps)
    return snapped_error(params, xs, ys, cap)

if __name__ == "__main__":
    # Well-conditioned target: each leaf is well-identified -> strong gradient signal
    xs = np.linspace(0.1, 1.5, 24)
    ys = np.exp(np.ones_like(xs)) - np.log(xs)   # = eml(1, x) = e - ln(x)
    print("Target: y = e - ln(x) = eml(1, x)\n")
    print(f"{'restart':>7} | {'snap_err':>10} | {'snap_formula':>16}")
    best = (1e9, None)
    for s in range(6):
        err, formula = train_once(s, xs, ys)
        star = "  <--" if err < best[0] else ""
        if err < best[0]: best = (err, formula)
        print(f"{s:>7} | {err:>10.3e} | {formula:>16}{star}")
    print("\n--- BEST ---")
    print(f"Formula: {best[1]}   snap_err = {best[0]:.3e}   (ground truth: eml(1, x))")
