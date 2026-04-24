# Project Status & Technical Insights

This document provides a clear overview of what `eml_sr` can do today, its core benefits, and critical limitations you should be aware of to ensure a smooth experience.

## Current Status (v0.1.0)

`eml_sr` is currently in its stable early release phase. It is functional and production-ready for the following tasks:
- **Univariate & Multivariate Regression**: Discovery of formulas for functions with one or more variables.
- **Pareto-Front Discovery**: Returns a list of candidate formulas optimized for the balance between accuracy and complexity.
- **Constant Refinement**: Integrated Levenberg-Marquardt optimizer for high-precision constant identification.
- **Cross-Platform Support**: Official support for Windows (x64), Linux (x86_64), and macOS (Intel/Apple Silicon).

## Default Configuration Reference

Knowing the defaults helps you decide how to tune the engine for your hardware:

- max_complexity : 6 - Maximum depth of the expression tree. 
- beam_width : 1000 - Candidates kept per level (Critical for RAM). 
- precision_goal : 1e-10 - Error threshold to stop the search early.. 
- complexity_penalty : 0.1 - Penalty to favor simpler formulas over complex ones. 
- optimize_constants : true - Enables high-precision constant refinement.

## Key Benefits

1. **Massive Speed**: Built on a multi-threaded Rust engine, it can process millions of expressions per second.
2. **Explainable AI**: Outputs sharp, human-readable mathematical formulas instead of black-box weights.
3. **Architectural Purity**: Uses the EML operator to ensure all results are structurally uniform, making them ideal for hardware compilation or formal verification.

## ⚠️ Critical Limitations & Safety Warnings

### 1. Memory Management (The `beam_width` Warning)
The most common cause of system crashes or "Out of Memory" (OOM) errors is improper configuration of the **Beam Width**.
- **How it works**: For every level of complexity, the searcher keeps the top `N` best candidates.
- **The Risk**: If you set `beam_width` to a very high value (e.g., 5,000, 10,000, or more) on a machine with limited RAM (8GB or 16GB), the memory usage will explode exponentially as the search progresses.
- **Recommendation**: Start with a `beam_width` of **500 - 1,000**. Only increase it if your machine has significant RAM and your problem requires a very deep search.

### 2. Search Space Explosion
Increasing `max_complexity` adds nodes to the EML tree. The number of possible tree structures grows exponentially.
- **Tip**: Most physical laws can be discovered within a complexity of **10 - 15**. Avoid setting it higher unless absolutely necessary, as it will significantly increase search time.

### 3. Numerical Stability
Because EML trees can become very deep (nested exponents and logarithms), floating-point precision becomes a factor.
- **Behavior**: Extremely deep trees may suffer from "catastrophic cancellation" or overflow/underflow.
- **Fix**: Use `allow_approximate: true` in your config to allow the searcher to skip numerically unstable branches.

### 4. Convergence in Constant Optimization
While we use the Levenberg-Marquardt algorithm, it is a local optimizer.
- **Warning**: If the initial structure is far from the truth, constant optimization might get stuck in a local minimum. The searcher relies on finding a "good enough" structure first before fine-tuning the constants.

---
*By understanding these limits, you can harness the full power of EML-SR without crashing your environment.*
