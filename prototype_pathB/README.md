# Path B Prototype — Gradient-based EML

Proof of concept (Python + `autograd`) for the "continuous optimization over an EML
tree, then snap to a closed-form formula" direction. Goal: numerically validate the
hypotheses in [`../docs/PATH_B_RESEARCH.md`](../docs/PATH_B_RESEARCH.md) before
investing in a Rust port.

## Honest verdict (read this first)

Two things are true at once, and prototype 8 (`blind_test.py`) forced the second:

1. **The engineering walls that pinned the paper at depth 4 are removable.** Overflow,
   exploding/vanishing gradients, `log(negative)` — all fixed (results A, B, C, 4).
   The hybrid front-end/back-end loop works (result 6). These are real.

2. **But a *pure*-EML gradient tree is NOT a general symbolic-regression method.**
   Given only raw-variable leaves `{0,1,x_i}`, a shallow EML tree can fit eml-shaped
   targets (control rel_RMSE 0.05) but **fails on the bread-and-butter of physics** —
   sums, products, ratios, powers all score no better than predicting the mean:

   | target | best rel_RMSE | verdict |
   |---|---|---|
   | exp(x0)−ln(x1) (eml-native) | 0.05 | recovered |
   | x0 + x1 | 0.86 | fails |
   | x0 * x1 | 1.00 | fails |
   | x0 / x1 | 0.65 | fails |
   | x0² | 1.00 | fails |

   The reason is structural: `eml = exp − log` only cheaply expresses exp/log-additive
   relationships; products and powers need *deep* eml composition, and (result 5's flip
   side) a fixed-depth full tree cannot even represent a formula shallower than itself,
   while deeper trees optimize worse. This is the same lesson the discrete engine
   already encoded by adding fast-path ×, ÷, Square operators — and it explains the
   project's own note that "discovered formulas almost never use EML."

**So the romantic pure-EML *tree* is the wrong frame.** But that failure pointed
straight at the right one (prototype 9, `eml_net.py`).

## Decisive verdict on performance (prototypes 12–13)

We then asked the hardest question directly: does eml (= exp − log) beat just having
exp and log as *separate* activations? At equal parameter budget, blind, on real laws:

| dimension d | EML rel_RMSE | ExpLog rel_RMSE | gap (explog − eml) |
|---|---|---|---|
| 2 | 0.46 | 0.49 | +0.03 (eml slightly ahead) |
| 3 | 0.11 | 0.08 | −0.03 |
| 4 | 0.19 | 0.13 | −0.06 |
| 5 | 2.83 | 0.18 | **−2.65 (eml collapses)** |

**Conclusion: eml has no performance advantage over separate exp+log, and it scales
*worse* — at higher dimension the forced exp-minus-log coupling becomes a liability and
optimization falls apart, while separate exp+log stays robust.** The earlier single eml
win (3-var gravity) was noise, not a trend.

So, as a tool for *finding better formulas*, gradient-EML is a dead end — tested
directly, not assumed. eml's remaining genuine value is purely the one it always had:
mathematical minimalism (one operator generates everything), which matters only for
theory / uniform-hardware ambitions, not for symbolic-regression accuracy.

## The reframe that actually fits eml: a compiler, not a fitter (prototype 15)

Every test above put eml in the *fitting* arena, where a single coupled operator can
only lose to separate exp+log. But eml's defining property is **minimalism**, and the
arena where minimalism wins by definition is **representation**, not fitting. So we
stopped asking eml to *find* formulas and built the thing where "one operator" is the
whole point: a compiler that turns an expression into a pure-eml tree
(`S -> 1 | x | eml(S,S)`) and **verifies numerically** that it computes the same value.

It runs. From nothing but `1`, `x`, and `eml`, all verified to machine precision:

| function | built from | nodes | max err |
|---|---|---|---|
| `e`, `0`, `exp(x)` | eml only | 3–7 | 0 |
| `ln(x)` | eml only | 19 | 1e-16 |
| `exp(x) − x`, `x − 1` | eml only | 23–25 | 4e-16 |
| `exp(x)/x`, `x/e` | eml only | 63 | 2e-15 |
| `ln(exp(x)) = x` (composition) | eml only | 21 | 0 |

"One operator generates functions" is now a **running, verified fact** rather than a
paper claim — and the node counts make the cost of minimalism concrete. Honest scope:
the exp/log/subtraction/division fragment is derived and verified; full `+`/`*`/negation
need the paper's complex-number constructions and are the documented next step. This is
eml's real home: a canonical, single-instruction encoding of mathematics — useful for
expression hashing/equivalence, minimal serialization, and the author's own unbuilt
"single-instruction machine," not for beating exp+log at curve-fitting.

## The opening: EML as an activation function

Pure-eml-by-depth fights the operator. The reframe is to stop asking eml to *be* the
whole formula and instead use it as the **nonlinearity between linear layers**, exactly
like an activation in a neural net. The reason this is powerful and specific to eml:
`eml` yields **exp *and* log in a single op**, and log turns the multiplicative
structure of physics into addition — `x*y = exp(ln x + ln y)`, `x² = exp(2 ln x)`,
`x/y = exp(ln x − ln y)`. So an affine layer (sums) + eml (exp/log) expresses exactly
what pure-eml-by-depth could not. A tiny 2-eml-layer net, trained **blind**, recovers
what the pure tree and the discrete engine both failed:

| target (blind, raw-variable inputs) | pure-eml tree | **eml-net** |
|---|---|---|
| x0 + x1 | fails (0.86) | **0.02** |
| x0 * x1 | fails (1.00) | **0.09** |
| x0 / x1 | fails (0.65) | **0.10** |
| x0² | fails (1.00) | **0.06** |
| Gravity `G·m1·m2/r²` (3 var) | — | **0.08** |
| Kinetic `½·m·r²` (2 var) | — | **0.06** |
| Gaussian `e^(−θ²/2)/√(2π)` | — | **0.05** |

(rel_RMSE; 0 = perfect, ~1 = predicting the mean. Real laws here are ones the discrete
engine failed in its own Feynman tests.)

**Why this is genuinely promising and genuinely eml's:** a network whose activation is
`eml` natively speaks the language of power laws and products — the backbone of physics
— which ReLU/tanh nets and additive-operator SR both handle awkwardly. This is a real,
specific role for eml, not "one operator among many."

**Honest open problems** (measured, not hand-waved):
- *Optimization robustness.* The 4-var Coulomb monomial fit poorly in raw space
  (rel_RMSE 1.7) but well in **log space** (0.12) — the same lesson as finding #2:
  wide-dynamic-range targets need log-space fitting + more restarts. Representability is
  fine; conditioning is the work.
- *Reading a symbolic formula back out.* **Solved for the power-law regime**
  (prototype 10, `distill.py`). Because eml turns a monomial `y = C·∏xi^ai` into a line
  in log space, we fit `ln y = ln C + Σ ai ln xi`, snap each exponent to the nearest
  simple rational, and LM-refit `C`. It recovers exact, readable formulas — at machine
  precision, and robustly under noise:

  | law | distilled formula | rel_RMSE |
  |---|---|---|
  | Gravity | `6.674 · m1 · m2 · r⁻²` | 3e-16 |
  | Coulomb (4 var) | `0.0796 · q1 · q2 · ε⁻¹ · r⁻²` | 3e-16 |
  | Kinetic | `0.5 · m · v²` | 5e-17 |
  | Coulomb +2% noise | correct exponents, `C≈0.0798` | 3e-2 (= noise) |

  The general read-out (prototype 11, `distill_general.py`) extends this to
  **non-monomial** laws by sparse regression over an eml-informed feature library,
  auto-choosing the linear-`y` or log-`y` frame. It recovers, exactly:

  | law | best frame | distilled | rel_RMSE |
  |---|---|---|---|
  | Gaussian `e^(−x²/2)/√(2π)` | log | `exp(−0.5·x² − 0.919)` | 1e-11 |
  | Sum `a + b` | linear | `a + b` | 4e-15 |
  | Gravity | log | `exp(ln m1 + ln m2 − 2 ln r + 1.898)` | 2e-13 |
  | Quadratic `3x²+1` | linear | `3·x² + 1` | 2e-14 |

  Honest scope: the read-out is sparse regression + snapping (a SINDy-style move); the
  eml-net's own contribution is *detection* — the two frames (linear/log) are exactly
  the exp/log that eml supplies. Distilling a *deep, mixed* eml-net (many nested
  non-monomial layers) directly from its own weights is the remaining frontier.


## Run

```bash
pip install autograd              # the only dependency
python3 eml_stable.py             # (A)(C) numerical stability
python3 master_tree.py            # (B) finite gradients vs depth
python3 train_toy_multistart.py   # multi-start: exact formula recovery
python3 deep_gradient_flow.py     # node-normalization keeps deep trees trainable
python3 multivar_tree.py          # multivariable target the discrete engine can't reach
python3 loss_shaping.py           # shaped loss + informative sampling fix weak-signal traps
python3 hybrid_pipeline.py        # full hybrid: gradient front-end -> LM back-end
python3 blind_test.py             # HONEST blind test: pure-eml tree fails real shapes
python3 eml_net.py                # THE OPENING: eml as an activation function
python3 distill.py                # read an EXACT human formula back out (power laws)
python3 distill_general.py        # GENERAL read-out: monomial AND non-monomial
python3 eml_vs_explog.py          # DECISIVE: eml vs separate exp+log
python3 scaling_test.py           # DECISIVE: does eml edge grow with dimension? (no)
python3 extrapolation_test.py     # extrapolation: eml vs exp+log (mixed, gravity outlier)
python3 eml_compiler.py           # THE REFRAME: a real, verified pure-EML compiler
```

## Key design choices

- **Complex numbers as (re, im) real-array pairs.** `autograd` has weak complex-dtype
  support, so every op stays real -> reverse-mode autodiff flows. `c_exp`, `c_log`
  (via `atan2`) are hand-rolled.
- **Soft, stable `eml`:** smoothly clamp the real part before `exp` with
  `cap*tanh(re/cap)` — caps overflow yet stays differentiable. `cap` acts as a
  temperature; `cap -> inf` recovers exact `eml` (used for homotopy/annealing).
- **Leaves as soft gates:** temperature-softmax over `{0, 1, x}` (DARTS/Gumbel
  relaxation). Annealing tau + entropy penalty push leaves to one-hot -> lossless snap.
- **Node normalization:** batch-normalize each node's real part to keep deep trees
  trainable (the EML analogue of BatchNorm; echoes the MEb "centered EML gate").

## Measured results (reproducible)

**(A) Numerical stability — removes the main wall that pinned the paper at depth 4.**

| depth | naive real eml | stable complex eml \|·\| |
|------:|---------------:|-------------------------:|
| 3 | 2.23e+22 | 19.48 |
| 4 | **inf (overflow)** | 19.55 |
| 12 | inf | 19.55 |

**(B) Finite gradients at every depth** (naive real tree: ~1e186 at depth 5):

| depth | #params | max\|grad\| | finite? |
|------:|--------:|------------:|:-------:|
| 4 | 48 | 4.5e+00 | yes |
| 8 | 768 | 8.8e-05 | yes |
| 10 | 3072 | 1.6e-07 | yes |

**(C)** `eml_pair(0,-2) = 0.307 − 3.1416i` — `log(negative)` handled cleanly in ℂ.

**(3) End-to-end pipeline (train -> anneal -> snap) works:**
well-conditioned target `y = e − ln(x) = eml(1, x)` -> **exact** structure recovery
`eml(1, x)`, snapped error **6e-4**.

**(4) Node normalization keeps DEEP trees trainable:**

| depth | mean\|grad\| no-norm | mean\|grad\| norm | train MSE no-norm | train MSE norm |
|------:|---------------------:|------------------:|------------------:|---------------:|
| 4 | 9.6e+04 | 3.5e+00 | 36.6 | **3.17** |
| 6 | 1.3e+08 | 4.8e+00 | 7.35 | **2.07** |
| 8 | 5.1e+13 | 1.3e+01 | — | — |

Without normalization, deep-tree gradients are wildly depth-dependent (either explode
or vanish depending on cap/leaf scale); with normalization they stay in a stable band
(~3–13) independent of depth, and training reaches markedly lower loss.

**(5) Multivariable recovery beyond the discrete engine's reach.**
Target `y = exp(exp(x0) − ln(x1)) − x2` (3 variables) is exactly the full depth-2 tree
`eml(eml(x0,x1), eml(x2,1))`. As a discrete expression it has ~8 nodes, so the
published beam engine — capped at `max_complexity = 6` — cannot reach it (and indeed
failed the analogous 3-variable Feynman cases in its own tests). The gradient tree has
a FIXED depth-2 structure, so cost does not explode with variable count; with
multi-start it recovers the **exact** ground-truth structure:

```
eml(eml(x0, x1), eml(x2, 1))    snap_err = 1.8e-3
```

This is the core value proposition of Path B: the discrete search explodes
combinatorially with variables/depth, while the gradient tree pays a fixed,
polynomial-per-step cost and reaches deeper structures.

**(6) The full HYBRID pipeline turns an approximate gradient result into an EXACT
formula.** The gradient front-end (soft-clamped eml + annealing) finds the structure
but leaves a small residual and does not nail constants. The back-end — exact eml
re-evaluation + Levenberg-Marquardt (this is what `src/engine/optimizer.rs` already
does) — closes the gap:

| stage | what it does | error |
|---|---|---|
| front-end | snap structure `eml(eml(x0,x1),eml(x2,1))` (soft eml) | 1.8e-3 |
| back-end verify | re-evaluate exact eml (no clamp) | **4.9e-32** |
| back-end polish | LM recovers hidden constant c=0.5 | \|err\| 3.3e-16 |

Front-end for *structure over many variables at fixed cost*; back-end for *exactness*.
This is the whole thesis of Path B validated end to end: not pure gradient, but a
gradient front-end feeding the existing discrete/LM engine.

## Findings that shape the roadmap

1. **The overflow clamp trades "exploding" for "vanishing" gradients** (deep trees
   saturate to a fixed point). The naive clamp alone is *not enough* at large depth.
   -> **Fixed here** with node normalization (prototype 4): gradients become
   depth-invariant and deep trees train. This is the EML analogue of BatchNorm.

2. **Weak-signal traps are fixed by informative sampling + a relative loss — not by
   loss reshaping alone.** Fitting `exp(x) − ln(x)` on `x∈[0.4,2]`, the `ln(x)` term is
   dwarfed by `exp(x)`, so the optimizer settles on the trap `eml(x,1)=exp(x)`. We
   measured recovery rate of the TRUE `eml(x,x)` over 8 seeds (prototype 6):

   | x-range | plain MSE | relative loss |
   |---|---|---|
   | [0.4, 2.0] | 1/8 | 2/8 |
   | [0.05, 2.0] | 6/8 | **8/8** |
   | [0.02, 1.0] | 8/8 | 8/8 (err 8e-5) |

   The dominant lever is **sampling where the weak term is informative** (small `x`,
   where `ln(x)` is large); a **relative/scale-free loss** then closes the gap
   (6/8 → 8/8). Reshaping the loss on a poorly-sampled domain barely helps. Combined
   with multi-start and a discrete verify back-end, this makes structure recovery
   reliable — reinforcing the **hybrid** (not pure-gradient) architecture.

## Next steps

1. Full leaf dictionary `{0, 1, x₁…xₙ}`; attack a multivariable Feynman equation that
   the discrete engine fails on.
2. (done — prototype 6) Relative loss + informative sampling.
3. (done — prototype 7) Hybrid loop validated in Python; maps onto `src/engine/optimizer.rs`.
4. Port to Rust only once the recipe is stable.
