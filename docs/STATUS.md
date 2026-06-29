# Project Status & Technical Insights

This document provides a clear overview of what `eml_sr` can do today, its core benefits, and critical limitations you should be aware of to ensure a smooth experience.

## Current Status (v0.2.0)

`eml_sr` is in a highly optimized, production-ready phase. In version `v0.2.0`, major mathematical and architectural enhancements have been introduced:
- **Model-First Parameter Fitting**: Constants are represented as dynamic parameter nodes (`Node::Param`) rather than static frozen numbers, enabling joint global optimization of nested constants across complexity levels without wasting expression tree depth.
- **Corrected Levenberg-Marquardt Optimizer**: Replaced basic SGD steps with Marquardt Diagonal Scaling to ensure robust, stable convergence of non-linear parameters even deep within nested functions.
- **Elastic Net Regularization ($L_1 + L_2$)**: Integrated parameter magnitude constraints directly into the search loss function to enforce model sparsity and prevent numerical instability.
- **Two-Stage Optimization**: Uses a fast 10-iteration LM screening during the BFS search phase to save CPU cycles and a deep 30-iteration LM optimization on final Pareto-front candidates to maximize precision.
- **Multi-Threaded Progress & ETA Tracking**: Lock-free parallel counters display search progress at every 10% milestone, including elapsed time and estimated remaining time (ETA).
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
Use the root generator script to dynamically create the test suite folder:
```bash
python generate_suite.py
```
This automatically reads the dataset, cleans up legacy scripts, and creates a git-ignored `Test/` folder containing the easy suite and 92 individual challenge scripts.

### 3. Running the Easy Feynman Suite (7 Equations)
Verifies the core search capability under standard configuration (`max_complexity=6`, `beam_width=200`):
```bash
python Test/test_easy.py
```

### 4. Running Individual Challenge Equations (e.g. Relativistic Mass `I.10.7`)
Runs a high-complexity challenge script with `max_complexity=8` and `beam_width=500`:
```bash
python Test/test_diff_I_10_7.py
```

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
