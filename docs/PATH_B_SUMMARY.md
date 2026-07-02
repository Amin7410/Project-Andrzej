# Path B — Research Summary & Go-Forward

Research sprint on the "gradient-based EML" direction. This file tells the whole
arc honestly: what we tried, what failed, what worked, and what to do next. All numbers
are reproducible from `prototype_pathB/` (Python + `autograd`, `pip install autograd`).

## The question

The author's original vision: instead of the current discrete beam-search engine, grow
one homogeneous EML tree, tune its weights by gradient descent, and snap them to reveal
a closed-form formula. The paper only validated this at depth ≤ 4. Can it go further —
and is it actually a better way to find formulas?

## The arc (what we learned, in order)

1. **The engineering walls that stopped the paper at depth 4 are removable.**
   Overflow (naive eml overflows at depth 4), exploding gradients (~1e186 at depth 5),
   and `log(negative)` all fall to: complex-domain evaluation + a smooth `tanh` clamp.
   Deep trees now stay finite and differentiable. *(prototypes 1–2)*

2. **The clamp then causes vanishing gradients; node normalization fixes it.**
   Deep trees saturate to a fixed point; a BatchNorm-style per-node normalization keeps
   gradients depth-invariant and deep trees trainable. *(prototype 4)*

3. **Reliable structure recovery needs informative sampling + a relative loss + multi-
   start**, not loss reshaping alone — measured: recovery of a weak-signal target went
   from 1/8 to 8/8 once we sampled where the weak term matters. *(prototype 6)*

4. **The hybrid loop works: gradient front-end finds structure, the existing discrete/LM
   back-end makes it exact** — approximate fit (1.8e-3) → exact re-eval (5e-32) → LM
   nails the constant (3e-16). *(prototype 7)*

5. **HONEST REALITY CHECK: a *pure*-EML tree is not a general SR method.** Blind, with
   raw-variable leaves, it fits eml-shaped targets but **fails on sums, products, ratios,
   powers** — the backbone of physics. Deeper trees optimize worse and can't represent
   shallower formulas. The romantic "universal EML tree" is the wrong frame. *(prototype 8)*

6. **THE OPENING: use EML as an activation function, not as the whole tree.** Because
   `eml` gives exp *and* log in one op, and log turns products/powers into sums, a tiny
   network `affine → eml → affine → eml` recovers — blind — exactly what the pure tree
   and the discrete engine both failed:

   | blind target | pure-eml tree | eml-net |
   |---|---|---|
   | x0+x1, x0*x1, x0/x1, x0² | all fail (0.65–1.0) | **0.02–0.10** |
   | Gravity `G·m1·m2/r²` (3 var) | — | **0.08** |
   | Gaussian `e^(−θ²/2)/√(2π)` | — | **0.05** |

   *(prototype 9)*

7. **The formula can be read back out — exactly.** For power laws, log-linear fit + snap
   exponents + LM constant recovers e.g. `6.674·m1·m2·r⁻²` at machine precision, robust
   to noise. The general distiller extends this to non-monomials (Gaussian, sums,
   polynomials) via sparse regression choosing the linear-or-log frame — all recovered
   exactly. *(prototypes 10–11)*

## Where this leaves us (honest)

- **Dead:** the pure-EML universal tree as a general SR method. It only natively speaks
  exp-minus-log; forcing it to build everything by depth does not work.
- **Alive and genuinely EML-specific:** **EML as an activation function.** A network
  whose nonlinearity is eml natively expresses the multiplicative / power-law structure
  that dominates physics — a real, specific niche that ReLU/tanh nets and additive-
  operator SR both handle poorly. Detection (eml-net) + read-out (distiller) is a working
  end-to-end pipeline on real laws the current discrete engine fails.
- **Open frontier:** distilling a *deep, mixed* eml-net directly from its own weights
  (beyond the linear/log-frame sparse-regression read-out).

## Recommended go-forward

Two tracks, in priority order:

1. **Harden the existing engine regardless** — it ships today and has no tests. Add a
   `cargo test` suite, fix the inert `include_builtins`/`extra_operators` config, and
   publish a real Feynman benchmark. This is low-risk, high-value, and independent of
   Path B. *(see the earlier project review)*

2. **Pursue "EML-net" as the research bet**, not the pure tree. Concretely:
   a. Reproduce prototypes 9–11 at larger scale on the full Feynman set, in log space,
      with more restarts (fixes the Coulomb-style conditioning gap).
   b. Frame the contribution honestly: *"EML as an activation for symbolic regression of
      physical/power-law relationships"* — a specialist that beats the discrete engine on
      multiplicative multi-variable laws.
   c. Only then port the eml-net + distiller to Rust, reusing `src/engine/optimizer.rs`
      (LM) as the constant-polish back-end.

The single most important honesty note: the flashy 1e-32 numbers earlier came from
targets hand-built to be eml-shaped. The results that matter are the **blind** ones
(prototypes 8–11) on real physics laws — those are what justify continuing.
