"""
Path B - Prototype 11: GENERAL symbolic distillation (the remaining frontier).

Prototype 10 read out monomials (products of powers) only. Real laws also include
non-monomial structure: sums, and Gaussians y = exp(-x^2/2) whose log is a POLYNOMIAL,
not linear-in-log. This distiller handles both by sparse regression over an
eml-informed feature library, in whichever target space (linear y or log y) is sparser.

Key idea (why eml matters): eml natively produces exp and log, so the two natural
"reading frames" are:
  - LINEAR space:  y      ~ sum of features        (captures sums, polynomials, Gaussians)
  - LOG space:     ln(y)  ~ sum of features        (captures products of powers)
Feature library per variable xi: { xi, xi^2, 1/xi, ln(xi) }, plus a constant.
Forward-selection keeps only a few terms -> an interpretable formula. Coefficients are
snapped to simple rationals; the constant is kept as a fitted number.
"""
import numpy as np

SIMPLE = np.array([-3,-2,-1.5,-1,-0.5,0,0.5,1,1.5,2,3])
def snap(c):
    j = np.argmin(np.abs(SIMPLE - c))
    return float(SIMPLE[j]) if abs(SIMPLE[j] - c) < 0.08 else round(c, 4)

def build_features(X, names, kind="full"):
    feats = []; labels = []
    n = X.shape[1]
    for i in range(n):
        xi = X[:, i]
        if kind == "ln":                      # pure-monomial hypothesis
            feats += [np.log(np.abs(xi)+1e-12)]
            labels += [f"ln({names[i]})"]
        else:
            feats += [xi, xi**2, 1.0/xi, np.log(np.abs(xi)+1e-12)]
            labels += [names[i], f"{names[i]}^2", f"{names[i]}^-1", f"ln({names[i]})"]
    return np.array(feats).T, labels

def forward_select(F, t, k=3):
    """Greedy forward selection: pick up to k features minimizing residual of t."""
    N, P = F.shape
    chosen = []; resid = t - t.mean()
    Fz = (F - F.mean(0)) / (F.std(0) + 1e-12)
    for _ in range(k):
        best_j, best_err = None, np.mean(resid**2)
        for j in range(P):
            if j in chosen: continue
            cols = chosen + [j]
            A = np.hstack([Fz[:, cols], np.ones((N,1))])
            coef, *_ = np.linalg.lstsq(A, t, rcond=None)
            e = np.mean((A@coef - t)**2)
            if e < best_err - 1e-9:
                best_err, best_j = e, j
        if best_j is None: break
        chosen.append(best_j)
    A = np.hstack([Fz[:, chosen], np.ones((N,1))])
    coef, *_ = np.linalg.lstsq(A, t, rcond=None)
    # map standardized coeffs back to raw feature scale
    raw = coef[:-1] / (F[:, chosen].std(0) + 1e-12)
    intercept = coef[-1] - np.sum(coef[:-1] * F[:, chosen].mean(0) / (F[:, chosen].std(0)+1e-12))
    return chosen, raw, intercept

def try_space(X, y, names, space, kind="full", k=3):
    F, labels = build_features(X, names, kind)
    t = y if space == "linear" else np.log(np.abs(y)+1e-12)
    chosen, coef, b = forward_select(F, t, k=min(k, F.shape[1]))
    # reconstruct prediction on ORIGINAL scale
    pred_t = F[:, chosen] @ coef + b
    pred = pred_t if space == "linear" else np.exp(pred_t)
    rel = np.sqrt(np.mean((pred - y)**2)) / (np.std(y)+1e-12)
    terms = [(labels[j], snap(c)) for j, c in zip(chosen, coef)]
    return rel, terms, b, space

def distill(name, X, y, names, truth):
    cands = [
        try_space(X, y, names, "linear", "full"),
        try_space(X, y, names, "log", "full"),
        try_space(X, y, names, "log", "ln", k=X.shape[1]),   # pure-monomial hypothesis
    ]
    rel, terms, b, space = min(cands, key=lambda r: r[0])
    body = " + ".join(f"{c:g}*{lab}" for lab, c in terms if c != 0)
    if space == "linear":
        formula = f"{body} + {b:.4g}"
    else:
        formula = f"exp({body} + {b:.4g})"
    print(f"{name}   [best frame: {space}]")
    print(f"    distilled: y = {formula}")
    print(f"    truth    : y = {truth}")
    print(f"    rel_RMSE : {rel:.2e}\n")

if __name__ == "__main__":
    rng = np.random.RandomState(2); N = 120
    th = rng.uniform(0.2, 2.0, N)
    m1 = rng.uniform(1,3,N); m2 = rng.uniform(1,3,N); r = rng.uniform(1,3,N)
    a = rng.uniform(0.5,2,N); b = rng.uniform(0.5,2,N)

    print("GENERAL distillation: monomial AND non-monomial, auto-picking the frame\n")
    distill("Gaussian (non-monomial: log is a polynomial)",
            th.reshape(-1,1), np.exp(-th**2/2)/np.sqrt(2*np.pi), ["x"],
            "exp(-0.5*x^2 - 0.919)   [= e^(-x^2/2)/sqrt(2pi)]")
    distill("Sum (non-monomial: needs linear frame)",
            np.stack([a,b],1), a + b, ["a","b"], "a + b")
    distill("Gravity (monomial: needs log frame)",
            np.stack([m1,m2,r],1), 6.674*m1*m2/r**2, ["m1","m2","r"],
            "exp(ln m1 + ln m2 - 2 ln r + 1.898)")
    distill("Quadratic (polynomial)",
            th.reshape(-1,1), 3*th**2 + 1.0, ["x"], "3*x^2 + 1")
