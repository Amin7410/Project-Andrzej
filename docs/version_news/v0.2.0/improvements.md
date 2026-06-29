# Release v0.2.0 - Code Improvements

This document lists all code-level optimizations, architecture upgrades, and new features introduced in version `v0.2.0` compared to the legacy codebase.

---

## 1. Model-First Parameter Architecture (`Node::Param`)
* **Files affected**: [expression.rs](file:///c:/Users/minhd/Documents/GitHub/Project-Andrzej/src/core/expression.rs), [bfs.rs](file:///c:/Users/minhd/Documents/GitHub/Project-Andrzej/src/engine/bfs.rs)
* **Upgrade**: Replaced the legacy approach of freezing constants into static numbers (`Node::Num`) after search steps. Constants are now represented as persistent parameter placeholders (`Node::Param` or "C").
* **Key Mechanisms**:
  * Added parameter count tracking (`param_count`) to `Expression`.
  * Implemented parameter index offset logic during binary tree composition to prevent parameter ID collisions:
    $$\text{Right Parameter ID} \mathrel{+}= \text{Left Parameter Count}$$
  * **Benefit**: Parameters remain dynamic throughout the search, enabling joint global optimization of nested parameters at higher levels of complexity.

## 2. Mathematically Corrected Levenberg-Marquardt Optimizer
* **File affected**: [optimizer.rs](file:///c:/Users/minhd/Documents/GitHub/Project-Andrzej/src/engine/optimizer.rs)
* **Problem**: The legacy implementation used a simple gradient descent step scaled by the dataset size $n$. This caused severe overshoots and prevented non-linear parameter convergence.
* **Fix**: Replaced the update formula with a mathematically correct Marquardt Diagonal Scaling:
  $$\Delta \theta_i = \frac{g_i}{\sum J_{\text{row}, i}^2 + \lambda}$$
  This divides the gradient step by the curvature approximation (diagonal of Hessian $J^T J$) plus dampening, ensuring stable and robust convergence.

## 3. Elastic Net Regularization (L1 + L2 Penalty)
* **Files affected**: [config.rs](file:///c:/Users/minhd/Documents/GitHub/Project-Andrzej/src/config.rs), [optimizer.rs](file:///c:/Users/minhd/Documents/GitHub/Project-Andrzej/src/engine/optimizer.rs), [bfs.rs](file:///c:/Users/minhd/Documents/GitHub/Project-Andrzej/src/engine/bfs.rs)
* **Upgrade**: Introduced Elastic Net regularization directly into the search and optimization loss function.
* **Math**:
  $$\text{Loss} = \text{MSE} + \alpha \left( \rho \sum |\theta_i| + \frac{1-\rho}{2} \sum \theta_i^2 \right)$$
  (where $\alpha$ is `alpha` and $\rho$ is the L1 ratio `l1_ratio`).
* **Benefit**: Prevents parameters from growing excessively large and enforces structural sparsity (encouraging parameters to zero out if they add no value).

## 4. Two-Stage Parameter Optimization
* **File affected**: [bfs.rs](file:///c:/Users/minhd/Documents/GitHub/Project-Andrzej/src/engine/bfs.rs)
* **Upgrade**: Implemented a dual-phase optimization pipeline to save CPU cycles:
  * **Search phase**: Runs a fast, light **10-iteration** Levenberg-Marquardt optimization on candidate expressions to quickly filter out unpromising structures.
  * **Finalization phase**: Runs a deep **30-iteration** Levenberg-Marquardt optimization on the final Pareto front candidates to maximize numerical precision.

## 5. Scikit-Learn Python Binding Upgrades
* **File affected**: [python.rs](file:///c:/Users/minhd/Documents/GitHub/Project-Andrzej/src/python.rs)
* **Upgrade**: 
  * Exposed configuration getters/setters (`alpha`, `l1_ratio`, `max_complexity`, `beam_width`) on the `PySearcher` object.
  * Python users can now override Elastic Net constraints dynamically inside fit methods:
    `searcher.fit(X, y, alpha=0.1, l1_ratio=0.5)`

## 6. Improved Display & Mathematical Output Formatting
* **File affected**: [result.rs](file:///c:/Users/minhd/Documents/GitHub/Project-Andrzej/src/result.rs)
* **Upgrade**: Updated the LaTeX and Python code generation formats.
* **Fix**: Instead of displaying generic placeholders like `p_{0}`, generated expressions now output the actual optimized numeric constants (e.g. `1.2636`), making the discovered models immediately usable.

## 7. Multi-Threaded Atomic Progress & ETA Tracking
* **File affected**: [bfs.rs](file:///c:/Users/minhd/Documents/GitHub/Project-Andrzej/src/engine/bfs.rs)
* **Upgrade**: Added thread-safe progress logging for candidate evaluations.
* **Details**: Prints progress at each `10%` milestone per level, including elapsed time and estimated remaining time (ETA). Uses lock-free atomic variables (`AtomicUsize`) to prevent Rayon thread blocking.
