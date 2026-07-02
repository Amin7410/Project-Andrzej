# Project Status & Technical Insights

This document gives an honest overview of what `eml_sr` can do today, its real (measured) performance characteristics, and the limitations you should know before relying on it. It was rewritten to remove marketing language that earlier versions of this document contained and was not fully backed by evidence.

## Current Status (v0.2.2)

`eml_sr` is a working, actively developed symbolic-regression engine. It is **not** claimed to be "production-ready" in the sense of having automated regression tests, a fully validated benchmark suite, or hardened error handling — see "Known Limitations" below. What it does have is a functioning search algorithm, verified against real formulas, with these features:

- **Python Smart Search Wrapper (`SmartSearcher`)**: an Output Transformation layer at the Python level that searches on transformed targets ($y$, $y^2$, $\ln(y)$, $1/y$) to resolve non-linear dependencies (such as square roots or reciprocal structures) that the base engine cannot see directly.
- **Consolidated Pareto Frontier & Back-Transformation**: maps candidate formulas back to the original scale, recalculates MSE, adjusts complexity to reflect the outer operator, and produces a unified Pareto front.
- **Early Stop Strategy**: stops the search across strategies immediately if a mathematically perfect fit (original-scale MSE $< 10^{-15}$) is found.
- **Quality-Diversity (QD) Beam Selection**: retains 80% of candidates by score and fills the remaining 20% with structurally diverse candidates, to avoid beam monoculture.
- **Levenberg-Marquardt Convergence Safeguards**: optimization aborts early if consecutive steps fail to improve error (3 iterations) or if the damping parameter $\lambda > 10^4$.
- **Built-in `Square` ($x^2$) and `Cube` ($x^3$) operators** to save tree depth.
- **Model-First Parameter Fitting**: constants are dynamic parameter nodes (`Node::Param`), enabling joint optimization of nested constants.
- **Univariate & Multivariate Regression**, **Pareto-Front Discovery**, **Cross-Platform Support** (Windows x64, Linux x86_64, macOS Intel/Apple Silicon).

## What EML Actually Contributes vs. the "Fast-Path" Operators

Read [README.md](../README.md#read-this-first-status--honesty-notes) first if you haven't. In short: this engine is a conventional discrete beam-search over an operator dictionary that happens to include EML. In practice, across the physics formulas this project has been tested against, discovered formulas almost never use the `EML` operator directly, because dedicated unary/binary shortcuts (Exp, Log, Sqrt, Square, Divide, ...) are cheaper in node count under the complexity-penalized scoring function. EML mainly pays off for expressions shaped like `eᴬ − ln(B)`.

Two `SearchConfig` fields, `include_builtins` and `extra_operators`, are currently **declared but not read anywhere in the search engine** (`run_bfs` always calls `OperatorRegistry::with_builtins()` regardless of config). If you need to customize the operator set (e.g. to force EML-heavy search), these fields will not currently do anything — this is a known gap, not a supported feature yet.

## Default Configuration Reference

- `max_complexity` : 6 - Maximum depth of the expression tree.
- `beam_width` : 200 - Candidates kept per level (Critical for RAM; default lowered from 1000 to 200 for safe multi-core scaling).
- `precision_goal` : 1e-10 - Error threshold to stop the search early.
- `complexity_penalty` : 0.1 - Penalty to favor simpler formulas over complex ones.
- `optimize_constants` : true - Enables high-precision constant refinement.
- `alpha` : 0.0 - Elastic Net regularization multiplier (L1 + L2 penalty strength).
- `l1_ratio` : 0.5 - Ratio of L1 (Lasso) penalty to L2 (Ridge) penalty.

## Measured Performance (Not Marketing Numbers)

- **Per-candidate evaluation** is genuinely fast (roughly 1–1.5ms per candidate on typical hardware), and the engine can screen hundreds of thousands of candidates at deeper search levels — this part of the "fast, parallel Rust engine" claim is real and measured.
- **End-to-end wall-clock time for a full search is not fast** for equations with several variables or higher complexity. In this project's own testing against real physics formulas, individual multi-variable equations (`max_complexity` 7–9, `beam_width` up to 1000) took on the order of **an hour or more** to complete on a single machine. Do not assume a search will finish in seconds just because individual candidate evaluation is fast — the total candidate count at higher levels can be very large.
- If you need a search to complete quickly, keep `max_complexity` low (5–7) and `beam_width` moderate (200–500), and expect to trade off completeness for speed.

## Known Limitations (Beyond Numerical Safety)

- **No automated test suite.** There are no `#[test]`-annotated unit tests anywhere in `src/`, and CI (`.github/workflows/`) only builds and publishes wheels — it does not run `cargo test`. Correctness is currently checked manually, via `cargo run --release` (demo verification cases in `src/tests/mod.rs`) and the Rust `examples/`. Treat any given release with appropriate caution until this is addressed.
- **No algebraic simplification pass.** The search can return redundant structures (e.g. an identity like `tan(arctan(x))` appearing inside a larger formula) if they happen to score well; results are not guaranteed to be in simplest form.
- **`include_builtins` / `extra_operators` config fields are inert** — see above.
- **`to_python()` output correctness**: earlier builds had an operator-precedence bug where `Neg`, `Inv`, and `Divide` did not individually parenthesize their operands before combining them, so nesting a `Plus`/`Subtract`/`Times` sub-expression inside them (e.g. as the denominator of a division) could silently produce Python code that computes the wrong value, even though the internal Rust evaluation and reported error were unaffected. This has been fixed in `src/ops/builtin.rs` (operands are now individually parenthesized), but if you're on an older build, verify exported Python code numerically before trusting it in a downstream pipeline.

---

## Developer Guide

### 1. Rebuilding Python Bindings
If you edit the Rust codebase, compile the Python extension using Maturin. On Windows PowerShell:
```powershell
$env:PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1; .venv\Scripts\maturin.exe develop
```

### 2. Running the Demo Verification Suite
```bash
cargo run --release
```
This runs a small set of hand-written test scenarios in `src/tests/mod.rs` and prints pass/fail-style output. It is a manual sanity check, not an automated regression test suite (see "Known Limitations" above).

### 3. Running the Rust Examples
```bash
cargo run --release --example 01_simple_discovery
cargo run --release --example 02_multivariate
cargo run --release --example 03_constant_recognition
```

---

## Critical Limitations & Safety Warnings

### 1. Memory Management (The `beam_width` Warning)
The most common cause of system crashes or "Out of Memory" (OOM) errors is improper configuration of the **Beam Width**.
- **How it works**: For every level of complexity, the searcher keeps the top `N` best candidates.
- **The Risk**: If you set `beam_width` to a very high value (e.g., 5,000, 10,000, or more) on a machine with limited RAM, the memory usage will explode exponentially as the search progresses.
- **Recommendation**: Start with a `beam_width` of **200 - 500**. Only increase it if your machine has significant RAM and your problem requires a very deep search.

### 2. Search Space Explosion
Increasing `max_complexity` adds nodes to the expression tree. The number of possible tree structures grows exponentially.
- **Tip**: Most physical laws can be discovered within a complexity of **8 - 12**. Avoid setting it higher unless absolutely necessary, as it will significantly increase search time — and, per the measured numbers above, "significantly" can mean going from minutes to over an hour.

### 3. Numerical Stability
Because expression trees (especially pure-EML ones) can become very deep (nested exponents and logarithms), floating-point precision becomes a factor.
- **Behavior**: Extremely deep trees may suffer from "catastrophic cancellation" or overflow/underflow.
- **Fix**: Use `allow_approximate: true` in your config to allow the searcher to skip numerically unstable branches.

### 4. Convergence in Constant Optimization
Levenberg-Marquardt is a local optimizer.
- **Warning**: If the initial structure is far from the truth, constant optimization might get stuck in a local minimum. The searcher relies on finding a "good enough" structure first before fine-tuning the constants.
