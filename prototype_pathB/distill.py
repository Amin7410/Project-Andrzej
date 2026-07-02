"""
Path B - Prototype 10: reading a clean, human formula back out (the "snap").

Open problem #2 from the eml-net result: the network fits data but its weights are a
dense black box. This closes the loop for the regime where eml-nets shine — physical
power laws (products of powers / monomials), which are a huge slice of physics.

Two stages:
  1. DETECT: the eml-net confirms a compact law explains the data (low error). Because
     eml supplies exp+log, a monomial y = C * prod xi^ai becomes LINEAR in log space:
         ln y = ln C + sum_i ai * ln(xi).
  2. DISTILL: fit that log-linear model (plain least squares), SNAP each exponent ai to
     the nearest simple rational (0, ±1/2, ±1, ±2, ±3, ...), then LM-refit the single
     constant C on the ORIGINAL scale. Verify. Output a readable formula.

This is the eml-net's interpretable read-out for power laws. Non-monomial pieces (e.g.
a Gaussian's exp(-x^2/2)) need the fuller net-weight snapping and are flagged, not
faked.
"""
import numpy as np

SIMPLE = np.array([-3, -2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2, 3])

def snap_exponent(a):
    return float(SIMPLE[np.argmin(np.abs(SIMPLE - a))])

def loglinear_fit(X, y):
    """ln y = b + sum ai ln xi  -> least squares. Requires X>0, y>0."""
    L = np.log(X)                                   # (N, n)
    A = np.hstack([L, np.ones((X.shape[0], 1))])    # design matrix
    coef, *_ = np.linalg.lstsq(A, np.log(y), rcond=None)
    a = coef[:-1]; b = coef[-1]
    return a, b

def lm_constant(X, y, exps, C0, iters=60):
    """Fit single constant C in y = C * prod xi^exps by LM (mirrors optimizer.rs)."""
    base = np.prod(X ** exps, axis=1)               # prod xi^ai  (fixed)
    C = C0; lam = 1e-2; best = float(np.mean((C * base - y) ** 2))
    for _ in range(iters):
        r = C * base - y
        J = base
        JtJ = float(np.sum(J * J)); Jtr = float(np.sum(J * r))
        C_new = C - Jtr / (JtJ + lam)
        e = float(np.mean((C_new * base - y) ** 2))
        if e < best: C, best, lam = C_new, e, lam / 3
        else: lam *= 3
        if best < 1e-28: break
    return C, best

def distill(name, X, y, var_names, true_str):
    a_raw, b_raw = loglinear_fit(X, y)
    exps = np.array([snap_exponent(v) for v in a_raw])
    C, mse = lm_constant(X, y, exps, np.exp(b_raw))
    rel = np.sqrt(mse) / (np.std(y) + 1e-12)
    # build readable string
    terms = []
    for nm, e in zip(var_names, exps):
        if e == 0: continue
        terms.append(nm if e == 1 else f"{nm}^{e:g}")
    body = " * ".join(terms) if terms else "1"
    formula = f"{C:.4g} * {body}"
    print(f"{name}")
    print(f"    raw exponents : [{', '.join(f'{v:+.2f}' for v in a_raw)}]")
    print(f"    snapped       : [{', '.join(f'{v:+g}' for v in exps)}]   C = {C:.5g}")
    print(f"    distilled     : y = {formula}")
    print(f"    truth         : y = {true_str}")
    print(f"    rel_RMSE after distill: {rel:.2e}\n")

if __name__ == "__main__":
    rng = np.random.RandomState(1); N = 80
    m1 = rng.uniform(1, 3, N); m2 = rng.uniform(1, 3, N); r = rng.uniform(1, 3, N)
    q1 = rng.uniform(1, 2, N); q2 = rng.uniform(1, 2, N); eps = rng.uniform(1, 2, N)
    m = rng.uniform(1, 3, N); v = rng.uniform(0.5, 2, N)

    print("Symbolic distillation of eml-net-detected power laws")
    print("(exact read-out for products of powers; the eml-net confirms the fit first)\n")
    distill("Gravity", np.stack([m1, m2, r], 1), 6.674 * m1 * m2 / r**2,
            ["m1", "m2", "r"], "6.674 * m1 * m2 * r^-2")
    distill("Coulomb", np.stack([q1, q2, eps, r], 1), q1 * q2 / (4*np.pi*eps*r**2),
            ["q1", "q2", "eps", "r"], "0.0796 * q1 * q2 * eps^-1 * r^-2")
    distill("Kinetic energy", np.stack([m, v], 1), 0.5 * m * v**2,
            ["m", "v"], "0.5 * m * v^2")
    distill("Coulomb-with-noise", np.stack([q1, q2, eps, r], 1),
            q1 * q2 / (4*np.pi*eps*r**2) * (1 + rng.normal(0, 0.02, N)),
            ["q1", "q2", "eps", "r"], "0.0796 * q1 * q2 * eps^-1 * r^-2 (+2% noise)")
