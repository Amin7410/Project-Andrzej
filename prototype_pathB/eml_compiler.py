"""
Path B - Prototype 15: a REAL, verified EML compiler.

This is the ONE arena where eml wins by definition: minimalism. Not "fit data better"
(a dead end, tested), but "express any function using a SINGLE operator." Everyone
(including the paper) left this at the level of a claim. Here it actually runs.

Grammar of the target language:   S -> ONE | X | eml(S, S),   eml(x,y) = e^x - ln(y).
Every macro below emits a tree in THIS grammar and is checked numerically against the
function it is supposed to equal. So "one operator generates ..." becomes a running,
verified fact, not a slogan.

Scope (honest): we derive and verify the exp/log/subtraction/division fragment — eml's
true home. Full +,*,negation need the paper's complex-number constructions and are the
documented next step. What runs here already reconstructs non-trivial functions from
nothing but `1`, `x`, and `eml`.
"""
import numpy as np

# ---- tree evaluator: a program is a nested tuple over ('1',),('x',),('eml',A,B) ----
def ev(t, x):
    k = t[0]
    if k == '1': return 1.0
    if k == 'x': return x
    if k == 'eml':
        a = ev(t[1], x); b = ev(t[2], x)
        return np.exp(a) - np.log(b)      # eml(a,b) = e^a - ln(b)
    raise ValueError(k)

def size(t):
    return 1 if t[0] in ('1','x') else 1 + size(t[1]) + size(t[2])

# ---- the ONLY constructor is eml; everything else is a macro that emits eml-trees ----
ONE = ('1',)
X   = ('x',)
def EML(a, b): return ('eml', a, b)

E    = EML(ONE, ONE)                    # e^1 - ln1 = e
def EXP(a): return EML(a, ONE)          # e^a - ln1 = e^a
ZERO = EML(ONE, EXP(E))                 # e - ln(e^e) = e - e = 0
def LN(b):                              # derived, subtraction-free:
    u = EML(ZERO, b)                    #   u = 1 - ln b
    return EML(ZERO, EXP(u))            #   1 - ln(e^u) = 1 - u = ln b
def SUB(a, b): return EML(LN(a), EXP(b))          # e^{ln a} - ln(e^b) = a - b   (a>0)
def DIV(a, b): return EXP(SUB(LN(a), LN(b)))      # e^{ln a - ln b} = a/b   (a>1, b>0)

# ---- verification harness ----
def check(name, tree, fn, xs):
    ok = True; worst = 0.0
    for x in xs:
        got = ev(tree, x); want = fn(x)
        d = abs(got - want)
        worst = max(worst, d)
        if not np.isfinite(got) or d > 1e-8: ok = False
    print(f"  {name:<26} nodes={size(tree):>3}  max|err|={worst:.1e}  {'OK' if ok else 'FAIL'}")
    return ok

if __name__ == "__main__":
    print("Pure-EML compiler: every function below is built from ONLY  1, x, eml.\n")

    print("Primitives (constants & unary):")
    check("e      (=eml(1,1))",   E,       lambda x: np.e, [0.5, 1, 2])
    check("0      (=eml(1,e^e))", ZERO,    lambda x: 0.0,  [0.5, 1, 2])
    check("exp(x)",               EXP(X),  np.exp,         [0.3, 1.0, 1.7])
    check("ln(x)",                LN(X),   np.log,         [0.4, 1.0, 2.5])

    print("\nBinary (subtraction & division), on their valid domains:")
    check("exp(x) - x", SUB(EXP(X), X), lambda x: np.exp(x) - x, [0.3, 1.0, 1.7])
    check("x - 1",      SUB(X, ONE),    lambda x: x - 1,        [1.5, 2.0, 3.0])
    check("exp(x) / x", DIV(EXP(X), X), lambda x: np.exp(x)/x,  [1.2, 2.0, 3.0])
    check("x / e",      DIV(X, E),      lambda x: x/np.e,       [1.5, 2.5, 3.5])

    print("\nCompositions (nesting macros — one operator all the way down):")
    check("ln(exp(x)) == x", LN(EXP(X)), lambda x: x,           [0.4, 1.0, 2.0])
    check("exp(ln(x)) == x", EXP(LN(X)), lambda x: x,           [0.4, 1.0, 2.0])
    check("exp(x-1)",        EXP(SUB(X, ONE)), lambda x: np.exp(x-1), [1.2, 2.0, 3.0])

    print("\n=> 'one operator generates functions' is now a running, verified fact,")
    print("   not a slogan. Node counts show the real cost of minimalism.")
