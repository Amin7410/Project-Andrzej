# Path B: Realizing gradient-based EML — Research Plan

> **Historical document — the original plan.** Every improvement idea below was a
> **hypothesis to test**, not a confirmed result. Several were confirmed, several were
> refuted; for the honest conclusions and final verdict see
> [`PATH_B_SUMMARY.md`](PATH_B_SUMMARY.md) and
> [`../prototype_pathB/README.md`](../prototype_pathB/README.md). This file is kept as
> the reasoning that kicked off the sprint.
>
> Starting state at the time of writing: the gradient "master-tree" method was **not
> implemented anywhere** in the repo — the `eml-sr_model_first/second_AI` folders are the
> discrete engine plus `Node::Param`, not a gradient tree. This was greenfield.

## 0. The vision (stated precisely)

Minimal grammar: `S → 1 | eml(S, S)`, with `eml(x, y) = eˣ − ln(y)`.

Odrzywołek's "break the black box" idea: instead of a discrete combinatorial search
(choosing which operator sits at each node), build **one fixed homogeneous EML tree** of
depth D — every internal node is `eml`, every leaf is a **trainable weight**. Train the
weights by gradient descent (Adam), then **snap** the weights to discrete values
(`{0, 1, variable x}`) to reveal a closed-form formula. Combinatorial problem →
continuous optimization problem.

State validated in the paper: only at **depth ≤ 4**. Our central question: *why stop at
4, and how do we go deeper?*

## 1. Three core walls (confirmed numerically)

A quick experiment shows why depth 4 is the ceiling:

**Wall 1 — Numerical blow-up.** Real-domain `eˣ` overflows very quickly when nested:

```
depth 1: 3.95e+00   depth 2: 5.15e+01   depth 3: 2.23e+22   depth 4: inf
```

Depth 4 already overflows `f64`. This is almost certainly the physical reason the paper
stopped at ≤4.

**Wall 2 — Exploding gradients.** The derivative of the output w.r.t. one leaf weight
grows doubly-exponentially through the stacked `exp` layers:

```
depth 1: 1.6      depth 3: 2.9e+01     depth 4: 1.2e+04     depth 5: 1.3e+186
```

With gradients around 10¹⁸⁶, every standard gradient optimizer (Adam/SGD) is useless —
this is an *optimization* wall, not just a *representation* one.

**Wall 3 — `ln(y)` undefined for `y ≤ 0`.** The tree produces arbitrary negative
intermediates; `ln(negative)` = NaN in the real domain, breaking both forward and
backward passes.

## 2. Improvements the author may not have exploited

Odrzywołek is a theoretical physicist; many of the tools below come from modern ML
(differentiable architecture search, quantized nets, neural ODEs) and may not have been
connected to the EML problem. This is where the project could contribute something *new*.

### 2.1. Move the tree to the complex domain ℂ — not just to avoid NaN, but because it is the natural domain

Odrzywołek's own construction uses complex values to generate `i`, `π`. A gradient tree
forced into the real domain **fights the operator's nature**. Proposal: a **complex-valued
master-tree**, trained with **Wirtinger calculus / complex autodiff**, with
`ln(negative) = ln|y| + iπ` (measured: `ln(-2) = 0.693 + iπ`, clean).

Big plus: the codebase **already uses `num-complex`** with IEEE-754 branch cuts. The
complex-arithmetic foundation is ready — an advantage a from-scratch project would lack.

### 2.2. Log-domain reparameterization (against Walls 1 & 2)

Instead of carrying raw intermediate values, carry a **(sign, log-magnitude)** pair, like
`symlog`. Then `eˣ` and `ln(y)` become add/subtract in log coordinates — taming overflow
and flattening gradients. Requires redefining the propagation rules of `eml` in these
coordinates (a compact engineering task, worth doing first).

### 2.3. Snapping done right: relaxation + annealing instead of post-hoc rounding

The author's snapping is the naive version: train, then round — if a weight is not near
`{0,1}`, snapping destroys the fit. This is exactly the problem ML solved in
**DARTS / Gumbel-Softmax / binary neural nets**:

- **Gumbel-Softmax / Concrete relaxation**: each leaf is a *soft mixture* over the
  dictionary `{0, 1, x₁…xₙ, free parameter}` with temperature τ; anneal τ → 0 during
  training so the choice *becomes discrete on its own*, rather than being snapped at the
  end.
- **Straight-Through Estimator (STE)**: forward uses the snapped weight, backward uses the
  continuous gradient (standard in BinaryConnect).
- **Double-well penalty**: add `R(w) = min(w², (w−1)²)` to pull weights toward `{0,1}`
  during training → snapping becomes nearly lossless. (Shape verified: R(0)=R(1)=0, peak
  at 0.5.)
- **L0 via hard-concrete gates** (Louizos): automatic branch pruning, making the tree
  sparse → most of it collapses to constants/identity.

### 2.4. Overparameterize then prune — instead of a fixed just-big-enough tree

A full depth-D EML tree has 2^D leaves; the landscape is full of symmetry and saddles.
ML paradox: **a wider-than-necessary tree is easier to optimize** (smoother landscape),
after which L0 / lottery-ticket pruning trims it to a small skeleton. Unlikely the author
tried this.

### 2.5. Neural-ODE framing: connect to the MEb paper

The MEb paper (Erez) uses an **EML cascade** with parameters shared across layers —
essentially an unrolled RNN/ODE, "depth = dynamical depth." But MEb fits with least
squares, **not** backprop-through-ODE. Joining the two:

> **EML-ODE as a Neural ODE with a non-monotone vector field**, trained with the
> **adjoint method**.

Sharing parameters across layers → far fewer parameters, turning "infinite depth" into a
fixed point (Deep Equilibrium Model). This is a genuinely new framing, with a ready
biology use-case (MEb, cheetah/cat epigenetic clocks).

### 2.6. Gauge-fixing via the algebraic structure (Stachowiak)

Stachowiak's follow-up paper describes the group structure behind EML. That structure
means **many distinct weight sets represent the same function** → the minimizer is a
*manifold*, not a point; gradient descent wanders. Proposal: use the known symmetries to
**gauge-fix** (optimize on the quotient manifold), or add a symmetry-breaking
regularizer. The group-theory author may not have connected this structure to the
*optimization landscape*.

### 2.7. Hybrid second-order optimizer — reuse the existing LM

`exp/log` make the Hessian extremely ill-conditioned; plain Adam is weak. Hybrid strategy:
**gradient for global structure, Levenberg–Marquardt for final constant polish** — and LM
**already exists** in `src/engine/optimizer.rs`. Add **homotopy/continuation**: start with
a "soft" `eml` (exp/log range limited by a temperature) then anneal toward the true
operator (a curriculum on operator sharpness).

## 3. Proposed hybrid architecture (maximize reuse of existing assets)

Do not throw away the discrete engine. The strongest architecture — and most likely the
new contribution — is a **continuous front-end + discrete back-end hybrid**:

```
[Complex, log-domain master-tree]  →  gradient training + annealing snap
        ↓ (read discrete skeleton)
[Existing discrete beam search]    →  verify & refine structure
        ↓
[Existing LM optimizer]            →  polish constants to exact values
```

The gradient front-end targets the discrete engine's fatal weakness: **multivariable
equations** (where combinatorial search explodes and the engine reaches only ~9–12% on
Feynman). A fixed-depth tree's cost is polynomial per step, not combinatorial in the
number of variables.

## 4. Prototype roadmap (proposed order)

1. **Numerically stable kernel first.** Implement complex + log-domain `eml` in Rust or a
   Python/JAX prototype. Goal: a depth 8–10 tree that does **not** overflow, with finite
   gradients. This is a prerequisite for everything else.
2. **Prototype in JAX/PyTorch first, Rust later.** Autodiff + Adam + annealing are needed
   to iterate quickly on the research. Port to Rust only once the recipe is stable. (Don't
   hand-write autodiff in Rust yet.)
3. **Toy problems with known answers.** Reproduce the paper's depth-≤4 results *via
   gradients*, then push to depth 6, 8. This is the "beat the numerical wall" milestone.
4. **Get relaxation snapping right.** Add double-well + Gumbel; measure the snap success
   rate (do the final weights land near the lattice?).
5. **Multivariable Feynman.** Target equations the discrete engine fails on. This is the
   real evidence of value.
6. **Wire the discrete back-end + LM** for verification and polish.
7. **Biology use-case** (MEb / cheetah clock) as a differentiated application.

## 5. Risks & honest failure criteria

- Snapping may still fail even with annealing → then the contribution recedes to "a good
  differentiable SR engine," still valuable but not "breaking the black box."
- Log-domain + complex may still not stabilize depth > 10 → determine the real depth
  ceiling and report it honestly (in the spirit of the current README).
- Minimum success criterion to call Path B "alive": reproduce, via gradients, at least one
  function at **depth ≥ 6** whose snapping yields an exact closed form — beating the
  paper's ≤4 ceiling.

---
*Note: the experimental numbers (overflow at depth 4, gradient 10¹⁸⁶ at depth 5,
ln(−2)=0.693+iπ) come from direct numerical checks and are reproducible.*
