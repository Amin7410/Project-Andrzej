# Project Status — Paused (open for review)

> **State:** actively paused by the author. The code works and is published; the EML
> research questions were explored thoroughly and honestly. This file is the single
> place to understand where things stand — for a future reader, a potential
> collaborator, or the author returning later. Nothing here is a dead end that can't be
> reopened if new tools, knowledge, or hardware change the picture.

---

## 1. What this project is

`eml_sr` is a **working symbolic-regression engine written in Rust** (published on
[crates.io](https://crates.io/crates/eml_sr) and [PyPI](https://pypi.org/project/eml-sr/)).
It searches for a closed-form formula that fits numerical data. Its search space includes
the **EML operator** `eml(x, y) = eˣ − ln(y)` — a genuine mathematical discovery by
Andrzej Odrzywołek (Jagiellonian University), who proved this single binary operator
plus the constant `1` can generate every elementary function.

Two things live in this repository:
- **The engine** (`src/`, `smart_search.py`) — a conventional, functioning SR tool.
- **A research sprint** (`prototype_pathB/`, `docs/PATH_B_*.md`) that asked whether EML's
  special mathematical property could be turned into a *better* SR method.

## 2. What works (the shipping engine)

- Parallel (Rayon) beam / breadth-first search over expression trees.
- Levenberg–Marquardt refinement of numeric constants (`src/engine/optimizer.rs`).
- A Pareto front trading accuracy vs. complexity; Rust + Python (PyO3) APIs.
- A Python `SmartSearcher` that retries on transformed targets (`y²`, `ln y`, `1/y`).
- Verified against a subset of the Feynman physics benchmark (exact/near-exact on
  several equations).

**Known gaps (honest):** no automated `cargo test` suite; CI only builds/publishes
wheels; `include_builtins` / `extra_operators` config fields are declared but unused; no
algebraic simplification pass. See `docs/STATUS.md`.

## 3. The EML research question — and the honest answer

The whole sprint is documented, reproducible, in `prototype_pathB/` (15 prototypes,
`pip install autograd` then run any `python3 *.py`) and summarized in
`docs/PATH_B_SUMMARY.md`. The arc:

1. **Engineering walls are removable.** EML's overflow at depth 4, exploding/vanishing
   gradients, and `log(negative)` all fall to a complex-domain + soft-clamp formulation.
   Deep EML trees become finite and trainable. *(real)*
2. **A pure-EML gradient tree is not a general SR method.** Blind, it fails on sums,
   products, ratios, powers — the backbone of physics. *(tested, not assumed)*
3. **EML as an activation function** (a small `affine → eml → affine → eml` net) *does*
   fit those shapes and real physics laws blind, and a distiller reads exact formulas
   back out for power laws and Gaussians. *(real, and interesting)*
4. **But the decisive test says EML has no performance edge over separate exp+log**, and
   scales *worse* with dimension. Its forced coupling is a constraint, not an advantage,
   for curve-fitting. *(the hard, honest verdict)*
5. **EML's true home is representation, not fitting.** A running, verified pure-EML
   *compiler* (`eml_compiler.py`) shows "one operator generates functions" as fact — but
   the trees are large and non-canonical, so the practical payoff (compression, hashing,
   hardware) is currently marginal.

**Bottom line:** EML is beautiful, verified mathematics. It is *not* (on the evidence
gathered here) a lever for a better formula-finder. Knowing this — with data, after
trying every angle — is itself the sprint's most valuable result: it prevents months
chasing a mirage.

## 4. What is genuinely valuable here

- A **functioning Rust SR engine** — valuable independent of whether EML is special.
- A **thorough, honest research record** that future work can build on without repeating
  the dead ends.
- A first **verified EML compiler** — a small but real artifact of "one operator,
  running."

## 5. If someone returns to this (doors left open)

None of the following is closed; each just needs something we didn't have (time,
compute, a collaborator, or new methods):

- **Harden the engine** (highest value, lowest risk): add `cargo test`, wire it into CI,
  fix the inert config fields, publish a full Feynman benchmark. This helps *any* user.
- **EML-as-activation for power-law science** (`eml_net.py` + `distill*.py`): scale to
  the full Feynman set in log space with more restarts; frame honestly as a specialist
  for multiplicative/physical laws. The one recurring bright spot was **extrapolation on
  coupled multi-variable monomials** (gravity) — worth confirming with a proper study.
- **Finish the EML compiler**: add `+`, `×`, negation via the paper's complex-number
  constructions; investigate a *canonical normal form* (the missing piece that would make
  hashing/equivalence actually work).
- **New tech that could change the verdict:** better second-order/global optimizers,
  learned symbolic priors (transformer-based SR), or hardware where a uniform single
  operator genuinely pays off.

## 6. Map of the repository

- `src/`, `Cargo.toml`, `smart_search.py` — the engine.
- `docs/STATUS.md` — engine status & limitations.
- `docs/PATH_B_RESEARCH.md` — the original research plan.
- `docs/PATH_B_SUMMARY.md` — the research arc, condensed.
- `prototype_pathB/` — 15 runnable prototypes + their own `README.md` with all measured
  results and honest verdicts.
- `paper/` — study notes, translations, and biology use-cases (epigenetic clocks, MEb).

## 7. A note from the author

Paused, not abandoned. Done solo, on limited hardware, without a mentor, against a
one-note market — and taken as far as one person reasonably could in the time available.
The library is shared so anyone can review, use, or extend whatever is useful. If new
knowledge or technology makes any of the open directions viable, this is a clean, honest
base to come back to.

*Credits: EML operator — Andrzej Odrzywołek (arXiv:2603.21852). Engine & research —
Minh Dinh Khoi. MIT licensed.*
