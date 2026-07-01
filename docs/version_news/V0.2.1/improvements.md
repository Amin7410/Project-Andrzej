# Release v0.2.1 - Code Improvements

This document lists all code-level optimizations, architecture upgrades, and new features introduced in version `v0.2.1` compared to `v0.2.0`.

---

## 1. Quality-Diversity Beam Selection Heuristics
* **File affected**: [bfs.rs](file:///c:/Users/minhd/Documents/GitHub/Project-Andrzej/src/engine/bfs.rs)
* **Upgrade**: Replaced pure greedy beam selection with a Quality-Diversity (QD) heuristic.
* **Mechanism**:
  * When candidate expressions exceed the configured `beam_width`, the selector retains **80%** of the slots for the highest-performing expressions (Quality).
  * The remaining **20%** of the slots are filled by sorting the discarded candidates based on their structural operator signature frequency (Diversity). Expressions with rare operator signatures (`get_sig`) are promoted.
* **Benefit**: Prevents the search beam from collapsing into a monoculture of minor variations of the same formula, keeping alternative algebraic branches alive.

## 2. Levenberg-Marquardt Convergence Safeguards
* **File affected**: [optimizer.rs](file:///c:/Users/minhd/Documents/GitHub/Project-Andrzej/src/engine/optimizer.rs)
* **Upgrade**: Implemented early-abort criteria for divergent or stagnant parameter fittings.
* **Key Conditions**:
  * **Divergence Guard**: Optimization terminates immediately if the dampening parameter $\lambda$ exceeds $10^4$.
  * **Stagnation Guard**: Added a `consecutive_failures` counter; optimization halts if the error fails to improve for 3 consecutive iterations.
* **Benefit**: Cuts off millions of wasted CPU floating-point operations on degenerate candidate expressions at high levels of complexity.

## 3. Initial Parameter Value Tuning
* **File affected**: [expression.rs](file:///c:/Users/minhd/Documents/GitHub/Project-Andrzej/src/core/expression.rs)
* **Upgrade**: Changed the default initial value of parameter nodes (`Node::Param`) from `1.0` to `0.1`.
* **Benefit**: Prevents initial optimization singularities and numerical overflows on highly sensitive exponential or trigonometric terms.

## 4. Interactive Progress Bar & ETA Tracking
* **File affected**: [bfs.rs](file:///c:/Users/minhd/Documents/GitHub/Project-Andrzej/src/engine/bfs.rs)
* **Upgrade**: Replaced static multi-line text outputs with a thread-safe, inline progress bar.
* **Details**: Displays a visual indicator (`[██████░░░░]`) indicating completion percentage, candidates evaluated, elapsed time, and dynamic ETA estimation. Uses stdout flushing to update the line dynamically in the terminal.

## 5. Built-in Power Operators (`Square` and `Cube`)
* **File affected**: [builtin.rs](file:///c:/Users/minhd/Documents/GitHub/Project-Andrzej/src/ops/builtin.rs)
* **Upgrade**: Added native `Square` ($x^2$) and `Cube` ($x^3$) operators under the `full-math` build feature.
* **Benefit**: Reduces expression complexity by treating common powers as unary operations, saving valuable expression tree depth.
