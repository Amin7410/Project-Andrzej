# Release v0.2.0 - Scientific Analysis: Issues & Solutions

This document analyzes the core bottlenecks of legacy symbolic regression search, explains why the updates in `v0.2.0` were introduced, and validates their mathematical outcomes.

---

## 1. Issue: Constant Complexity Waste & Limited Coefficient Sets

### The Problem:
In the previous version, the engine attempted to represent constants by combining basic operators or freezing them into hardcoded static numbers. For example, to represent a fractional coefficient like `0.5`, the searcher had to nest multiple operators, consuming significant tree depth. Furthermore, if a coefficient (like $1/2$ or $3/2$) was not present in the hardcoded constant set, the search failed completely.

### The Consequences:
* **Complexity Exhaustion**: Most of the complexity budget (expression tree depth) was wasted on constructing numbers rather than modeling the relationships between variables.
* **Failure on Rational Coefficients**: Even simple physical laws with fractions failed to resolve unless custom, arbitrary constant lists were predefined in the search configuration.

### The Solution: Model-First Parameter Architecture (`Node::Param`)
We introduced a persistent parameter node (`Node::Param` or "C") that stays dynamic throughout the entire BFS search instead of being frozen.

### Rationale:
* **Zero Depth Waste**: Any optimized real value (e.g., `0.5`, `1.5`, `3.1416`) now occupies exactly **1 node** of complexity. This preserves the remaining tree depth budget for complex algebraic relationships.
* **Domain Independence**: Bypasses the need for hardcoded constant lists by allowing the Levenberg-Marquardt optimizer to tune the parameter to any real number dynamically.

### What was Improved:
* All 7 equations in the easy verification suite (including equations with fractional coefficients and physical constants) now resolve successfully with MSEs near machine precision ($\approx 10^{-32}$).

---

## 2. Issue: Parameter Divergence & Chaotic Optimization Steps

### The Problem:
The legacy parameter optimizer divided the gradient descent update steps purely by the dataset size $n$. This simple scaling did not account for the curvature of the loss surface.

### The Consequences:
For non-linear parameters nested deep within mathematical functions (such as exponents or trigonometric terms), the optimization steps would overshoot violently. The parameters diverged, causing potentially correct mathematical structures to be discarded during the BFS phase due to artificially high MSE scores.

### The Solution: Corrected Levenberg-Marquardt Optimizer
We replaced the update step with a mathematically sound Marquardt Diagonal Scaling formula:
$$\Delta \theta_i = \frac{g_i}{\sum J_{\text{row}, i}^2 + \lambda}$$
This divides the gradient step by the diagonal of the approximated Hessian matrix (sum of squared Jacobian elements) plus a dampening factor $\lambda$.

### Rationale:
* Ensures that parameter updates are scaled inversely to the sensitivity of the loss function, stabilizing convergence even for highly sensitive, nested non-linear terms.

### What was Improved:
* Stable, rapid parameter convergence within few iterations.
* In high-complexity tests (like the 1-variable Gaussian test), the optimizer is robust enough to fit a complex-domain surrogate curve down to an MSE of **$1.72 \times 10^{-5}$** by precisely tuning the parameters of a highly non-linear 8-node expression.

---

## 3. Issue: Search Speed vs. Optimization Depth Trade-off

### The Problem:
Running full parameter optimizations on all candidate expressions during the BFS search is computationally expensive. As the search level increases, candidate counts scale exponentially (reaching hundreds of thousands of candidate expressions), leading to severe CPU bottlenecks or memory freezes.

### The Solution: Two-Stage Parameter Optimization
We split the optimization pipeline into two stages:
1. **Search phase**: A fast, light **10-iteration** optimization is run on all candidates to screen out unpromising structures.
2. **Finalization phase**: A deep **30-iteration** optimization is run only on the final Pareto-front candidate models.

### Rationale:
* Maximizes search throughput during BFS while still ensuring that the final returned mathematical formulas are refined to the highest numerical accuracy.

### What was Improved:
* Enabled the engine to evaluate **786,757 candidates** in parallel at Level 8 in a reasonable timeframe without memory overflow (OOM) or thread locking.

---

## 4. Issue: Overfitting & Numerical Instability

### The Problem:
Unconstrained parameter optimization can lead to extremely large parameter values (numerical instability) or overfitting, where the searcher constructs overly complex models with redundant parameters to fit noise.

### The Solution: Elastic Net Regularization
We added Elastic Net regularization ($L_1 + L_2$ penalties) to the error evaluation function:
$$\text{Loss} = \text{MSE} + \alpha \left( \rho \sum |\theta_i| + \frac{1-\rho}{2} \sum \theta_i^2 \right)$$

### Rationale:
* The $L_1$ penalty enforces sparsity, driving unnecessary parameters to zero and encouraging simpler mathematical models.
* The $L_2$ penalty prevents parameter values from exploding, maintaining numerical stability.

### What was Improved:
* Cleaner expression trees and improved generalization.
