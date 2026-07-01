# Project Status & Technical Insights

This document provides a clear overview of what `eml_sr` can do today, its core benefits, and critical limitations you should be aware of to ensure a smooth experience.

## Current Status (v0.2.2)

`eml_sr` is in a highly optimized, production-ready phase. Recent updates (v0.2.1 and v0.2.2) introduce major new features:
- **Python Smart Search Wrapper (`SmartSearcher`)**: Introduces an Output Transformation layer at the Python level that dynamically searches on transformed targets ($y$, $y^2$, $\ln(y)$, $1/y$) to resolve non-linear dependencies (such as square roots or reciprocal structures).
- **Consolidated Pareto Frontier & Back-Transformation**: Automatically maps candidate formulas back to the original scale, recalculates actual MSE, adjusts complexity to reflect the outer operator, and produces a unified Pareto front.
- **Early Stop Strategy**: Stops the search process across strategies immediately if a mathematically perfect fit (original scale MSE $< 10^{-15}$) is discovered, reducing search time by up to 75%.
- **Quality-Diversity (QD) Beam Selection Heuristics**: Retains 80% of candidates based on score and fills the remaining 20% by prioritizing candidates with unique operator signatures to prevent search beam monoculture.
- **Levenberg-Marquardt Convergence Safeguards**: Optimizations abort early if consecutive steps fail to improve errors (3 iterations) or if the damping parameter $\lambda > 10^4$ to avoid wasting CPU cycles.
- **New Built-in Operators**: Added built-in support for `Square` ($x^2$) and `Cube` ($x^3$) to save complexity tree depth.
- **Model-First Parameter Fitting**: Constants are represented as dynamic parameter nodes (`Node::Param`) rather than static frozen numbers, enabling joint global optimization of nested constants.
- **Corrected Levenberg-Marquardt Optimizer**: Replaced basic SGD steps with Marquardt Diagonal Scaling to ensure robust convergence.
- **Univariate & Multivariate Regression**: Discovery of formulas for functions with one or more variables.
- **Pareto-Front Discovery**: Returns a list of candidate formulas optimized for the balance between accuracy and complexity.
- **Cross-Platform Support**: Official support for Windows (x64), Linux (x86_64), and macOS (Intel/Apple Silicon).

## Default Configuration Reference

Knowing the defaults helps you decide how to tune the engine for your hardware:
- `max_complexity` : 6 - Maximum depth of the expression tree.
- `beam_width` : 200 - Candidates kept per level (Critical for RAM; default lowered from 1000 to 200 for safe multi-core scaling).
- `precision_goal` : 1e-10 - Error threshold to stop the search early.
- `complexity_penalty` : 0.1 - Penalty to favor simpler formulas over complex ones.
- `optimize_constants` : true - Enables high-precision constant refinement.
- `alpha` : 0.0 - Elastic Net regularization multiplier (L1 + L2 penalty strength).
- `l1_ratio` : 0.5 - Ratio of L1 (Lasso) penalty to L2 (Ridge) penalty.

## Key Benefits

1. **Massive Speed**: Built on a multi-threaded Rust engine (parallelized via Rayon), it can process millions of expressions per second.
2. **Explainable AI**: Outputs sharp, human-readable mathematical formulas (with actual optimized constants formatted) instead of black-box weights.
3. **Architectural Purity**: Uses the EML operator to ensure all results are structurally uniform, making them ideal for hardware compilation or formal verification.

---

## 🛠 Test Suite & Developer Guide

### 1. Rebuilding Python Bindings
If you edit the Rust codebase, compile the Python extension using Maturin. On Windows PowerShell:
```powershell
$env:PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1; .venv\Scripts\maturin.exe develop
```

### 2. Generating the Feynman Equations Test Suite
Use the root generator script to dynamically create the hierarchical test suite folders:
```bash
python generate_suite.py
```
This automatically reads the dataset, cleans up legacy scripts, and creates a structured `Test/Feynman/` directory containing all 100 benchmark equations.

### 3. Running Individual Feynman Equations (e.g. Doppler Effect `I_34_1`)
Each equation is housed in its own folder under `Test/Feynman/<ID>/` and uses adaptive search configurations:
```bash
# Run a specific Feynman equation test using the local virtual env
.venv/Scripts/python -u Test/Feynman/I_34_1/test.py
```
The results (the Pareto front log `fit.txt` and regression plot `fit.png`) will be saved in `Test/Feynman/<ID>/Results/`.

---

## ⚠️ Critical Limitations & Safety Warnings

### 1. Memory Management (The `beam_width` Warning)
The most common cause of system crashes or "Out of Memory" (OOM) errors is improper configuration of the **Beam Width**.
- **How it works**: For every level of complexity, the searcher keeps the top `N` best candidates.
- **The Risk**: If you set `beam_width` to a very high value (e.g., 5,000, 10,000, or more) on a machine with limited RAM, the memory usage will explode exponentially as the search progresses.
- **Recommendation**: Start with a `beam_width` of **200 - 500**. Only increase it if your machine has significant RAM and your problem requires a very deep search.

### 2. Search Space Explosion
Increasing `max_complexity` adds nodes to the EML tree. The number of possible tree structures grows exponentially.
- **Tip**: Most physical laws can be discovered within a complexity of **8 - 12**. Avoid setting it higher unless absolutely necessary, as it will significantly increase search time.

### 3. Numerical Stability
Because EML trees can become very deep (nested exponents and logarithms), floating-point precision becomes a factor.
- **Behavior**: Extremely deep trees may suffer from "catastrophic cancellation" or overflow/underflow.
- **Fix**: Use `allow_approximate: true` in your config to allow the searcher to skip numerically unstable branches.

### 4. Convergence in Constant Optimization
While we use the Levenberg-Marquardt algorithm, it is a local optimizer.
- **Warning**: If the initial structure is far from the truth, constant optimization might get stuck in a local minimum. The searcher relies on finding a "good enough" structure first before fine-tuning the constants.
