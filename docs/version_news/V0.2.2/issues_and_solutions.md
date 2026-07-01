# Release v0.2.2 - Scientific Analysis: Issues & Solutions

This document analyzes the core bottlenecks addressed in version `v0.2.2` and details their mathematical solutions.

---

## 1. Issue: Sqrt Blindness & Intermediate Term Pruning

### The Problem:
BFS candidate evaluation compares expressions directly against the target variable $y$. When the true equation is nested inside a non-linear operator (such as $y = \sqrt{f(x)}$), the intermediate expression $f(x)$ evaluates to $y^2$. Because $f(x)$ is compared directly to $y$, its MSE is extremely high, causing the BFS engine to prune $f(x)$ at early levels before it can be wrapped in a square root at later levels.

### The Consequences:
* **Failure on Nested Non-linear Functions**: BFS search was completely "blind" to equations wrapped in square roots, logarithms, or division denominators (e.g., speed of sound $v = \sqrt{\gamma pr/\rho}$).

### The Solution: Multi-Strategy Target Transformations
We introduced `SmartSearcher`, which runs searches on transformed targets: $y_{trans} \in \{y, y^2, \ln(y), 1/y\}$.

### Rationale:
* Transforming $y \to y^2$ linearizes the nested term, allowing the BFS engine to easily find $f(x)$ at low complexity levels since its MSE against $y^2$ is zero. Once found, we wrap $f(x)$ back into $\sqrt{f(x)}$.

### What was Improved:
* **Speed of Sound (`I_47_23`)**: Resolved successfully with an MSE of **$2.15 \times 10^{-32}$** using the `sqrt` strategy.

---

## 2. Issue: Constant Overfitting and Numeric Bloat

### The Problem:
When fitting equations containing floating-point constants, the Levenberg-Marquardt optimizer attempts to minimize every bit of numerical noise. This causes the searcher to append redundant operators (such as adding `arccos(v0)` or scaling offsets) to squeeze out minuscule error reductions below the double-precision noise floor.

### The Consequences:
* **Expression Bloat**: Correct physical laws were returned as bloated 8-node equations containing useless terms, rather than clean 3-node equations.

### The Solution: Pareto Error-Floor Filtering (`pick_best`)
We introduced `pick_best` with an MSE threshold of $10^{-15}$. If any formula in the Pareto front achieves an MSE below this threshold, the selector picks the **simplest** formula meeting this accuracy criteria rather than the most complex one.

### Rationale:
* $10^{-15}$ represents the physical limit of double-precision (`float64`) arithmetic. Any error reduction below this is numerical noise, not physics. Prioritizing simplicity at this floor preserves physical interpretability.

### What was Improved:
* **Planck (`I_34_27`)** and **Molecular Kinetic (`I_39_1`)**: Now return clean, physically accurate 3-node formulas ($0.1592 \cdot h \cdot \omega$ and $1.5 \cdot pr \cdot V$) instead of bloated 8-node expressions.

---

## 3. Issue: Beam Pruning on Multi-Variable Denominators

### The Problem:
Equations with variables nested in the denominator (like Doppler: $\frac{\omega_0}{1-v/c}$) suffer from beam pruning. The intermediate sub-expression `1 - v/c` is discarded early because it has no correlation to $y$ before the division is applied.

### The Solution: Adaptive Beam Width Scaling
We configured `generate_suite.py` to automatically scale `beam_width` from `500` to `1000` for equations with 3 or more variables.

### Rationale:
* A wider beam (1000 candidates) preserves more diverse sub-expressions in the queue, giving complex algebraic structures (like denominators) the necessary "short-term memory" to survive until they are combined.

### What was Improved:
* **Doppler (`I_34_1`)**: Discovered successfully with an MSE of **$3.48 \times 10^{-31}$** by expanding the beam width to 1000.
