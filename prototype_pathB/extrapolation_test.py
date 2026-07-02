"""
Path B - Prototype 14: the last stone — EXTRAPOLATION, not interpolation.

Every earlier test measured fit quality ON the training domain (interpolation), where
separate exp+log (more flexible) ties or beats eml. But eml's forced exp-minus-log
COUPLING is a strong structural prior. A stronger prior usually hurts interpolation and
HELPS extrapolation. Physics laws are exactly the regime where the true structure IS
exp/log/power-law — so eml's constraint might make it generalize OUT of the training
range where a free exp+log net overfits locally and diverges.

Test: train both models on a NARROW variable range, evaluate on a WIDER, disjoint range.
Report extrapolation rel_RMSE. If eml wins here, that is its real, specific niche:
a physical inductive bias for scientific extrapolation.
"""
import numpy as np
from eml_vs_explog import eml_net, explog_net, unpack, nparams
from autograd import grad
import autograd.numpy as anp

def fit_eval(model, Xtr, ytr, Xte, yte, H, seeds=3, epochs=250):
    n = Xtr.shape[1]; P = nparams(n, H); ys = np.std(ytr) + 1e-9
    def loss(th):
        return anp.mean(((model(th, Xtr, n, H) - ytr) / ys) ** 2)
    g = grad(loss)
    best_te = 1e9
    for s in range(seeds):
        rng = np.random.RandomState(s); th = rng.randn(P) * 0.4
        m = np.zeros(P); v = np.zeros(P); b1, b2, e, lr = 0.9, 0.999, 1e-8, 0.02
        for t in range(1, epochs + 1):
            G = np.clip(g(th), -1e6, 1e6)
            m = b1*m+(1-b1)*G; v = b2*v+(1-b2)*G**2
            th = th - lr*(m/(1-b1**t))/(np.sqrt(v/(1-b2**t))+e)
        # pick by TRAIN fit, then report its TEST error (honest model selection)
        tr = float(np.sqrt(np.mean((np.array(model(th,Xtr,n,H))-ytr)**2))/ys)
        te = float(np.sqrt(np.mean((np.array(model(th,Xte,n,H))-yte)**2))/(np.std(yte)+1e-9))
        if tr < best_eval.tr:
            best_eval.tr = tr; best_te = te
    return best_te

class best_eval:  # tiny holder reset per call
    tr = 1e9

def run(name, gen, d, seed=5, H=6):
    rng = np.random.RandomState(seed)
    Xtr = rng.uniform(1.0, 1.8, (80, d))          # narrow training range
    Xte = rng.uniform(1.8, 3.2, (80, d))          # disjoint, wider  -> extrapolation
    ytr, yte = gen(Xtr), gen(Xte)
    best_eval.tr = 1e9
    e_eml = fit_eval(eml_net, Xtr, ytr, Xte, yte, H)
    best_eval.tr = 1e9
    e_xl  = fit_eval(explog_net, Xtr, ytr, Xte, yte, H)
    print(f"{name:>26} | eml={e_eml:7.3f} | explog={e_xl:7.3f} | "
          f"{'EML better' if e_eml<e_xl-0.03 else ('ExpLog better' if e_xl<e_eml-0.03 else 'tie')}")

if __name__ == "__main__":
    print("EXTRAPOLATION test: train on [1.0,1.8], test on [1.8,3.2] (disjoint)")
    print("rel_RMSE on the FAR test range (lower = generalizes better)\n")
    print(f"{'law':>26} | {'EML':>11} | {'ExpLog':>10} | winner")
    run("product a*b",         lambda X: X[:,0]*X[:,1], 2)
    run("ratio a/b",           lambda X: X[:,0]/X[:,1], 2)
    run("inverse-square m/r^2",lambda X: X[:,0]/X[:,1]**2, 2)
    run("gravity m1*m2/r^2",   lambda X: X[:,0]*X[:,1]/X[:,2]**2, 3)
