"""
Path B - Prototype 3: end-to-end gradient training + annealing + snapping (single run).

Toy target (known answer, exactly representable by an EML tree):
    y = eml(x, x) = exp(x) - ln(x)
    -> depth-1 tree: root eml(left_leaf, right_leaf), both leaves = x.

Pipeline:
  1. Adam trains the leaf-gate logits (each leaf: soft softmax over {0,1,x}).
  2. Anneal temperature tau: 2.0 -> 0.15, pushing softmax toward one-hot (discrete).
  3. Entropy penalty (a double-well on the simplex) pulls each leaf to ONE symbol.
  4. SNAP: argmax each leaf -> read the discrete formula -> recompute error after snap.

NOTE: a single run easily gets stuck in a local minimum (it settles on eml(x,1)=exp(x)
because ln(x) is tiny next to exp(x) here). See train_toy_multistart.py for the fix.
"""
import autograd.numpy as np
from autograd import grad
from eml_stable import eml_pair

DICT = ["0", "1", "x"]

def softmax(logits, tau):
    z = (logits - np.max(logits)) / tau
    e = np.exp(z)
    return e / np.sum(e)

def leaf_pair(logits, x, tau):
    w = softmax(logits, tau)
    re = w[1] * 1.0 + w[2] * x
    im = 0.0 * w[0]
    return (re, im), w

def forward_depth1(params, x, tau, cap):
    (l, _) = leaf_pair(params[0], x, tau)
    (r, _) = leaf_pair(params[1], x, tau)
    return eml_pair(l, r, cap=cap)

def entropy_penalty(params, tau):
    """Sum of leaf-softmax entropies; small -> near one-hot (easy to snap)."""
    ent = 0.0
    for p in params:
        w = softmax(p, tau)
        ent = ent + (-np.sum(w * np.log(w + 1e-12)))
    return ent

def loss_fn(params, xs, ys, tau, cap, beta):
    total = 0.0
    for x, y in zip(xs, ys):
        re, _ = forward_depth1(params, x, tau, cap)
        total = total + (re - y) ** 2
    mse = total / len(xs)
    return mse + beta * entropy_penalty(params, tau)

def snap_formula(params):
    idx = [int(np.argmax(p)) for p in params]
    return idx, f"eml({DICT[idx[0]]}, {DICT[idx[1]]})"

def snapped_error(params, xs, ys, cap):
    """Error after hard-snapping each leaf to its argmax (hard one-hot)."""
    idx = [int(np.argmax(p)) for p in params]
    basis = {0: 0.0, 1: 1.0}
    tot = 0.0
    for x, y in zip(xs, ys):
        vals = [(basis.get(i, x), 0.0) for i in idx]
        re, _ = eml_pair(vals[0], vals[1], cap=cap)
        tot += (re - y) ** 2
    return tot / len(xs)

if __name__ == "__main__":
    rng = np.random.RandomState(1)
    xs = np.linspace(0.4, 2.0, 24)
    ys = np.exp(xs) - np.log(xs)      # = eml(x, x)

    params = rng.randn(2, 3) * 0.3    # 2 leaves, 3 logits each
    g = grad(loss_fn)

    # manual Adam
    m = [np.zeros(3), np.zeros(3)]; v = [np.zeros(3), np.zeros(3)]
    b1, b2, eps, lr = 0.9, 0.999, 1e-8, 0.05
    cap = 6.0
    EPOCHS = 400
    print(f"{'epoch':>6} | {'tau':>5} | {'loss(mse+pen)':>13} | {'snap_err':>10} | {'snap_formula'}")
    for t in range(1, EPOCHS + 1):
        tau = max(0.15, 2.0 * (0.985 ** t))     # annealing
        beta = 0.02 * min(1.0, t / 200.0)       # ramp up the entropy penalty
        G = g(params, xs, ys, tau, cap, beta)
        for i in range(2):
            m[i] = b1 * m[i] + (1 - b1) * G[i]
            v[i] = b2 * v[i] + (1 - b2) * G[i] ** 2
            mhat = m[i] / (1 - b1 ** t); vhat = v[i] / (1 - b2 ** t)
            params[i] = params[i] - lr * mhat / (np.sqrt(vhat) + eps)
        if t % 50 == 0 or t == 1:
            L = loss_fn(params, xs, ys, tau, cap, beta)
            se = snapped_error(params, xs, ys, cap)
            _, f = snap_formula(params)
            print(f"{t:>6} | {tau:>5.2f} | {L:>13.4e} | {se:>10.3e} | {f}")

    idx, formula = snap_formula(params)
    se = snapped_error(params, xs, ys, cap)
    print("\n--- RESULT ---")
    print("Snapped formula:", formula, "  (ground truth: eml(x, x))")
    print(f"Error after snap: {se:.3e}")
    print("Leaf softmaxes  :", [np.round(softmax(p, 0.15), 3).tolist() for p in params])
