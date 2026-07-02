"""
Path B - Prototype 6: Shaped / log-domain loss to fix weak-signal local minima.

Finding #2: on the ill-conditioned target y = exp(x) - ln(x) over x in [0.4, 2], the
ln(x) term is dwarfed by exp(x), so plain MSE has almost no gradient signal to prefer
the true eml(x, x) over the wrong eml(x, 1) = exp(x). Plain MSE weights high-magnitude
points most, exactly where ln(x) is least visible.

Fix tested: reweight the residual so every point counts comparably.
  - plain     : mean( (p - y)^2 )
  - relative  : mean( ((p - y) / (|y| + eps))^2 )        -> scale-free
  - arcsinh   : mean( (asinh(p) - asinh(y))^2 )          -> log-domain, sign-safe

We measure, over several random seeds, how often each loss recovers the TRUE structure
eml(x, x), plus the median snapped error. Ground truth leaves = (x, x).
"""
import autograd.numpy as np
from autograd import grad
from eml_stable import eml_pair

DICT = ["0", "1", "x"]

def softmax(logits, tau):
    z = (logits - np.max(logits)) / tau
    e = np.exp(z); return e / np.sum(e)

def leaf(logits, xb, tau):
    w = softmax(logits, tau)
    return (w[1] * 1.0 + w[2] * xb, 0.0 * xb)

def forward(params, xb, tau, cap):
    l = leaf(params[0], xb, tau); r = leaf(params[1], xb, tau)
    return eml_pair(l, r, cap=cap)

def entropy_pen(params, tau):
    e = 0.0
    for p in params:
        w = softmax(p, tau); e = e + (-np.sum(w * np.log(w + 1e-12)))
    return e

def residual_loss(pred, y, kind):
    if kind == "plain":
        return np.mean((pred - y) ** 2)
    if kind == "relative":
        return np.mean(((pred - y) / (np.abs(y) + 1e-3)) ** 2)
    if kind == "arcsinh":
        return np.mean((np.arcsinh(pred) - np.arcsinh(y)) ** 2)

def loss_fn(params, xb, y, tau, cap, beta, kind):
    re, _ = forward(params, xb, tau, cap)
    return residual_loss(re, y, kind) + beta * entropy_pen(params, tau)

def snap(params):
    return [int(np.argmax(p)) for p in params]

def snapped_error(params, xb, y, cap):
    idx = snap(params); basis = {0: 0.0, 1: 1.0}
    def lf(i):
        b = basis.get(idx[i], None)
        return (np.full_like(xb, b) if b is not None else xb, 0.0 * xb)
    re, _ = eml_pair(lf(0), lf(1), cap=cap)
    return float(np.mean((re - y) ** 2)), idx

def train_once(seed, xb, y, kind, cap=6.0, epochs=250):
    rng = np.random.RandomState(seed)
    params = rng.randn(2, 3) * 0.5
    g = grad(loss_fn)
    m = np.zeros_like(params); v = np.zeros_like(params)
    b1, b2, eps, lr = 0.9, 0.999, 1e-8, 0.04
    for t in range(1, epochs + 1):
        tau = max(0.1, 2.0 * (0.99 ** t))
        beta = 0.01 * min(1.0, t / 200.0)
        G = g(params, xb, y, tau, cap, beta, kind)
        G = np.clip(G, -1e6, 1e6)
        m = b1 * m + (1 - b1) * G; v = b2 * v + (1 - b2) * G ** 2
        mhat = m / (1 - b1 ** t); vhat = v / (1 - b2 ** t)
        params = params - lr * mhat / (np.sqrt(vhat) + eps)
    err, idx = snapped_error(params, xb, y, cap)
    return err, idx

def _loss_demo(xb, y, seeds):
    TRUE = [2, 2]
    for kind in ["plain", "relative", "arcsinh"]:
        errs = []; hits = 0
        for sd in seeds:
            err, idx = train_once(sd, xb, y, kind)
            errs.append(err)
            if idx == TRUE: hits += 1
        print(f"{kind:>10} | {hits}/{len(seeds)}{'':14} | {float(np.median(errs)):>16.3e}")


def _domain_demo(seeds):
    TRUE = [2, 2]
    print(f"{'x-range':>14} | {'loss':>9} | {'recovered':>9} | {'median snap_err':>16}")
    for lo, hi, tag in [(0.4, 2.0, "[0.4, 2.0]"), (0.05, 2.0, "[0.05, 2.0]"), (0.02, 1.0, "[0.02, 1.0]")]:
        xb = np.linspace(lo, hi, 24); y = np.exp(xb) - np.log(xb)
        for kind in ["plain", "relative"]:
            errs = []; hits = 0
            for sd in seeds:
                err, idx = train_once(sd, xb, y, kind)
                errs.append(err)
                if idx == TRUE: hits += 1
            print(f"{tag:>14} | {kind:>9} | {hits}/{len(seeds)}{'':6} | {float(np.median(errs)):>16.3e}")


if __name__ == "__main__":
    seeds = list(range(8))
    xb = np.linspace(0.4, 2.0, 24)
    y = np.exp(xb) - np.log(xb)      # = eml(x, x); ln(x) is tiny vs exp(x) here
    print("Ill-conditioned target: y = exp(x) - ln(x) = eml(x, x)")
    print("(TRUE structure = eml(x, x); the trap is eml(x, 1) = exp(x))\n")

    print("--- Experiment 1: loss shaping alone (fixed poor domain [0.4, 2]) ---")
    print(f"{'loss':>10} | {'recovered eml(x,x)':>18} | {'median snap_err':>16}")
    _loss_demo(xb, y, seeds)
    print("\n--- Experiment 2: DATA DOMAIN is the dominant lever ---")
    _domain_demo(seeds)
