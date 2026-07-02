"""
Path B - Prototype 2: Differentiable EML master-tree + finite-gradient check.

A full binary EML tree of depth D. Each LEAF is a "soft gate": a temperature-softmax
over the dictionary {0, 1, x} (DARTS/Gumbel-style relaxation). Complex numbers are
(re, im) pairs. Parameters are the gate logits -> differentiable -> Adam-trainable.

(B) Gradient of the loss w.r.t. parameters stays FINITE at depths 4/6/8/10
    (contrast: the naive real tree gives max|grad| ~ 1e186 at depth 5).
"""
import autograd.numpy as np
from autograd import grad
from eml_stable import eml_pair

LEAF_DICT_SIZE = 3  # {0, 1, x}

def softmax(logits):
    z = logits - np.max(logits)
    e = np.exp(z)
    return e / np.sum(e)

def leaf_value(leaf_logits, x, tau):
    """Leaf = soft mixture over {0, 1, x}, returned as (re, im). tau small -> discrete."""
    w = softmax(leaf_logits / tau)
    re = w[1] * 1.0 + w[2] * x
    im = 0.0 * w[0]
    return (re, im)

def full_tree_leaves(depth):
    return 2 ** depth

def tree_forward(params, x, depth, cap, tau):
    n = full_tree_leaves(depth)
    level = [leaf_value(params[i], x, tau) for i in range(n)]
    while len(level) > 1:
        nxt = []
        for i in range(0, len(level), 2):
            nxt.append(eml_pair(level[i], level[i + 1], cap=cap))
        level = nxt
    return level[0]  # (re, im) pair

def loss_fn(params, xs, ys, depth, cap, tau):
    total = 0.0
    for x, y in zip(xs, ys):
        re, _ = tree_forward(params, x, depth, cap, tau)
        total = total + (re - y) ** 2
    return total / len(xs)

if __name__ == "__main__":
    rng = np.random.RandomState(0)
    xs = np.linspace(0.5, 2.0, 12)
    ys = np.sin(xs)

    print("=" * 74)
    print("(B) Gradient magnitude of the loss vs tree depth (cap=3.0, tau=1.0)")
    print("    Contrast naive real tree: max|grad| ~ 1e186 at depth 5 (useless).")
    print("=" * 74)
    print(f"{'depth':>6} | {'#leaves':>8} | {'#params':>8} | {'loss':>10} | {'max|grad|':>12} | {'finite?':>8}")
    g = grad(loss_fn)
    for depth in [2, 4, 6, 8, 10]:
        nl = full_tree_leaves(depth)
        params = rng.randn(nl, LEAF_DICT_SIZE) * 0.5
        L = loss_fn(params, xs, ys, depth, 3.0, 1.0)
        G = g(params, xs, ys, depth, 3.0, 1.0)
        mx = float(np.max(np.abs(G)))
        finite = bool(np.all(np.isfinite(G)))
        print(f"{depth:>6} | {nl:>8} | {params.size:>8} | {L:>10.4f} | {mx:>12.4e} | {str(finite):>8}")
