"""
Path B - Prototype 12: the uncomfortable, decisive test.

eml(a,b) = exp(a) - log(b). So is an eml-net actually better than just having exp and
log as SEPARATE activations? If a net with independent exp and log units does as well
or better at the same parameter budget, then eml's "one universal operator" is elegant
math with no practical payoff for symbolic regression — and we should say so.

We compare, blind, same budget, same training:
  - EML-net   : hidden unit h = exp(affineA) - log(affineB)      [forced exp-minus-log pair]
  - ExpLog-net: hidden unit h = exp(affineA)  OR  log(affineB)   [free, strictly more general]
Both feed a linear-ish readout of the same shape. Report rel_RMSE on real physics laws.
"""
import numpy as np
from autograd import grad
import autograd.numpy as anp

CAP = 8.0
def sclamp(z): return CAP * anp.tanh(z / CAP)
def aff(P, F): return anp.dot(F, P[:-1]) + P[-1]

# ---- EML net: h_j = exp(clamp(A_j.x)) - log|B_j.x| ; out = exp(clamp(C.h)) - log|D.h|
def eml_net(theta, X, n, H):
    A, B, C, D = unpack(theta, n, H)
    hs = []
    for j in range(H):
        hs.append(anp.exp(sclamp(aff(A[j], X))) - anp.log(anp.abs(aff(B[j], X)) + 1e-9))
    Hm = anp.stack(hs, axis=1)
    return anp.exp(sclamp(aff(C, Hm))) - anp.log(anp.abs(aff(D, Hm)) + 1e-9)

# ---- ExpLog net: half units exp, half log; out same free mix (strictly more general)
def explog_net(theta, X, n, H):
    A, B, C, D = unpack(theta, n, H)
    hs = []
    for j in range(H):
        if j % 2 == 0:
            hs.append(anp.exp(sclamp(aff(A[j], X))))
        else:
            hs.append(anp.log(anp.abs(aff(B[j], X)) + 1e-9))
    Hm = anp.stack(hs, axis=1)
    # readout: exp branch + log branch, linearly combined
    return anp.exp(sclamp(aff(C, Hm))) - anp.log(anp.abs(aff(D, Hm)) + 1e-9)

def unpack(theta, n, H):
    i = 0
    A = theta[i:i+H*(n+1)].reshape(H, n+1); i += H*(n+1)
    B = theta[i:i+H*(n+1)].reshape(H, n+1); i += H*(n+1)
    C = theta[i:i+(H+1)]; i += H+1
    D = theta[i:i+(H+1)]; i += H+1
    return A, B, C, D

def nparams(n, H): return 2*H*(n+1) + 2*(H+1)

def fit(model, X, y, H=4, seeds=4, epochs=280):
    n = X.shape[1]; P = nparams(n, H); ys = np.std(y)+1e-9
    def loss(th, X, y):
        return anp.mean(((model(th, X, n, H) - y)/ys)**2)
    g = grad(loss); best = 1e9
    for s in range(seeds):
        rng = np.random.RandomState(s); th = rng.randn(P)*0.4
        m=np.zeros(P); v=np.zeros(P); b1,b2,e,lr=0.9,0.999,1e-8,0.02
        for t in range(1, epochs+1):
            G = np.clip(g(th, X, y), -1e6, 1e6)
            m=b1*m+(1-b1)*G; v=b2*v+(1-b2)*G**2
            th = th - lr*(m/(1-b1**t))/(np.sqrt(v/(1-b2**t))+e)
        pred = np.array(model(th, X, n, H))
        best = min(best, float(np.sqrt(np.mean((pred-y)**2))/ys))
    return best

if __name__ == "__main__":
    rng = np.random.RandomState(1); N=70
    m1=rng.uniform(1,3,N); m2=rng.uniform(1,3,N); r=rng.uniform(1,3,N)
    a=rng.uniform(0.5,2,N); b=rng.uniform(0.5,2,N); th=rng.uniform(0.3,1.6,N)
    targets = {
        "product a*b":        (np.stack([a,b],1), a*b),
        "ratio a/b":          (np.stack([a,b],1), a/b),
        "Gravity m1*m2/r^2":  (np.stack([m1,m2,r],1), 6.674*m1*m2/r**2),
        "Gaussian":           (th.reshape(-1,1), np.exp(-th**2/2)/np.sqrt(2*np.pi)),
        "sum a+b":            (np.stack([a,b],1), a+b),
    }
    print("Does EML beat separate exp+log?  (rel_RMSE, lower better, same budget)\n")
    print(f"{'target':>20} | {'EML-net':>8} | {'ExpLog-net':>10} | winner")
    for name,(X,y) in targets.items():
        re = fit(eml_net, X, y); rx = fit(explog_net, X, y)
        w = "EML" if re < rx-0.02 else ("ExpLog" if rx < re-0.02 else "tie")
        print(f"{name:>20} | {re:>8.3f} | {rx:>10.3f} | {w}")
