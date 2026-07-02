"""
Path B - Prototype 13: the decisive scaling test.

Question that decides whether eml has a real niche: does its edge over separate exp+log
GROW with the number of variables / interaction complexity? Our 2-var toys may have been
under-selling it; the one eml win earlier was the highest-dimensional case (3-var gravity).

Setup: monomial physical-law targets y = prod xi^ai with integer exponents, for growing
dimension d. Same budget, same training, blind. We report rel_RMSE for each model and the
GAP = explog - eml (positive => eml is winning by that much).
"""
import numpy as np
from eml_vs_explog import eml_net, explog_net, fit

def make_monomial(d, seed):
    rng = np.random.RandomState(seed)
    N = 60
    X = rng.uniform(1.0, 2.5, (N, d))
    exps = rng.choice([-2, -1, 1, 2], size=d)
    y = np.prod(X ** exps, axis=1)
    return X, y, exps

def run_d(d, seed=7):
    X, y, exps = make_monomial(d, seed)
    H = max(4, 2 * d)
    re = fit(eml_net, X, y, H=H, seeds=2, epochs=180)
    rx = fit(explog_net, X, y, H=H, seeds=2, epochs=180)
    return d, re, rx, exps

if __name__ == "__main__":
    print("Does EML's edge grow with dimension?  (monomial targets, blind)")
    print("GAP = explog - eml   (positive => EML winning)\n")
    print(f"{'d (vars)':>8} | {'EML':>7} | {'ExpLog':>7} | {'GAP':>7}")
    for d in [2, 3, 4, 5]:
        _, re, rx, exps = run_d(d)
        print(f"{d:>8} | {re:>7.3f} | {rx:>7.3f} | {rx-re:>+7.3f}")
