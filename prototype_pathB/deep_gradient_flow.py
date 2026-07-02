"""
Path B - Prototype 4: Keeping gradients alive in DEEP EML trees.

Finding #1 from earlier: the tanh soft-clamp that fixes overflow ALSO makes deep
trees saturate to a fixed point, so gradients w.r.t. the leaves vanish (~1e-7 at
depth 10) and the tree stops learning. This is the classic exploding->vanishing
trade-off of very deep computation graphs.

Fix tested here: NODE NORMALIZATION. At every internal eml node we normalize the
node's output across the data batch (subtract mean, divide by std) on the real part.
This is the EML analogue of BatchNorm/LayerNorm in deep nets, and echoes the
"centered EML gate" used in the MEb biophysics paper. It rescales each node back to
an informative range so downstream gradients don't collapse.

We measure the gradient magnitude at the DEEPEST leaves as depth grows, with the
normalization ON vs OFF. Batched (vectorized over the data) so per-node batch stats
are well defined.
"""
import autograd.numpy as np
from autograd import grad
from eml_stable import c_exp, c_log, soft_clamp_re

def batch_norm_re(v, eps=1e-5):
    """Normalize the real part across the batch axis; leave imag untouched."""
    re, im = v
    mu = np.mean(re)
    sd = np.sqrt(np.mean((re - mu) ** 2) + eps)
    return ((re - mu) / sd, im)

def eml_node(x, y, cap, normalize):
    xs = soft_clamp_re(x, cap)
    out = (c_exp(xs)[0] - c_log(y)[0], c_exp(xs)[1] - c_log(y)[1])
    if normalize:
        out = batch_norm_re(out)
    return out

def tree_forward_batched(params, xb, depth, cap, normalize):
    """xb: array over the batch. Leaves are affine-in-x gates; returns (re, im) arrays."""
    n = 2 ** depth
    # leaf i = w_i * x + b_i  (real), imag 0 -> simple trainable affine leaves
    level = []
    for i in range(n):
        wi, bi = params[i, 0], params[i, 1]
        level.append((wi * xb + bi, 0.0 * xb))
    while len(level) > 1:
        nxt = []
        for i in range(0, len(level), 2):
            nxt.append(eml_node(level[i], level[i + 1], cap, normalize))
        level = nxt
    return level[0]

def loss_batched(params, xb, yb, depth, cap, normalize):
    re, _ = tree_forward_batched(params, xb, depth, cap, normalize)
    return np.mean((re - yb) ** 2)

def _gradient_flow_demo():
    rng = np.random.RandomState(0)
    xb = np.linspace(0.3, 1.8, 32)
    yb = np.sin(xb) + 0.5 * xb

    print("=" * 78)
    print("Gradient magnitude at the DEEPEST leaves vs depth: node-norm OFF vs ON")
    print("(un-normalized deep trees are unstable; normalization keeps grads well-scaled)")
    print("=" * 78)
    print(f"{'depth':>6} | {'#leaves':>8} | {'mean|grad| OFF':>16} | {'mean|grad| ON':>16} | {'verdict':>14}")
    g = grad(loss_batched)
    for depth in [2, 4, 6, 8]:
        n = 2 ** depth
        params = rng.randn(n, 2) * 0.5
        G_off = g(params, xb, yb, depth, 6.0, False)
        G_on  = g(params, xb, yb, depth, 6.0, True)
        off = float(np.mean(np.abs(G_off)))
        on  = float(np.mean(np.abs(G_on)))
        verdict = "OFF diverging" if off > 1e2 else ("OFF vanishing" if off < 1e-3 else "OFF ok")
        print(f"{depth:>6} | {n:>8} | {off:>16.3e} | {on:>16.3e} | {verdict:>14}")


def train_deep(depth, normalize, xb, yb, cap=6.0, steps=250, seed=0):
    """Train a batched EML tree; return final MSE. Shows norm enables deep training."""
    rng = np.random.RandomState(seed)
    params = rng.randn(2 ** depth, 2) * 0.5
    g = grad(loss_batched)
    m = np.zeros_like(params); v = np.zeros_like(params)
    b1, b2, eps, lr = 0.9, 0.999, 1e-8, 0.02
    for t in range(1, steps + 1):
        G = g(params, xb, yb, depth, cap, normalize)
        G = np.clip(G, -1e6, 1e6)  # guard the OFF case from inf
        m = b1 * m + (1 - b1) * G; v = b2 * v + (1 - b2) * G ** 2
        mhat = m / (1 - b1 ** t); vhat = v / (1 - b2 ** t)
        params = params - lr * mhat / (np.sqrt(vhat) + eps)
    re, _ = tree_forward_batched(params, xb, depth, cap, normalize)
    return float(np.mean((re - yb) ** 2))


def _extra_training_demo():
    xb = np.linspace(0.3, 1.8, 32)
    yb = np.sin(xb) + 0.5 * xb
    print()
    print("=" * 78)
    print("Can a DEEP tree actually train?  Final MSE after 250 Adam steps")
    print("=" * 78)
    print(f"{'depth':>6} | {'final MSE OFF':>14} | {'final MSE ON':>14}")
    for depth in [4, 6]:
        off = train_deep(depth, False, xb, yb)
        on = train_deep(depth, True, xb, yb)
        print(f"{depth:>6} | {off:>14.4e} | {on:>14.4e}")


if __name__ == "__main__":
    _gradient_flow_demo()
    _extra_training_demo()
