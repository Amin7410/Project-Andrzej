# Release v0.2.1 - Scientific Analysis: Issues & Solutions

This document analyzes the core bottlenecks addressed in version `v0.2.1` and details their mathematical solutions.

---

## 1. Issue: Structural Monoculture in Beam Search

### The Problem:
At higher search levels, the BFS search queue was frequently dominated by minor parameter variations of the same mathematical structure. For instance, the top 500 candidates would consist entirely of slightly different parameter variations of `C * v0 * v1`, completely crowding out other potential candidates.

### The Consequences:
* **Premature Search Convergence**: The algorithm lost the ability to explore alternative algebraic branches, causing searches on 3+ variable equations to fail.
* **Wasted Capacity**: The search beam width was effectively reduced from 500 unique formulas to a handful of unique structures.

### The Solution: Quality-Diversity (QD) Selection Heuristics
We modified the beam selection phase to enforce structural diversity. The searcher now fills the first **80%** of the beam with the best scored expressions, and the remaining **20%** with expressions displaying rare operator signatures (`get_sig`).

### Rationale:
* Ensures a continuous pool of diverse algebraic templates (e.g. fractions, trigonometry, power terms) are propagated to subsequent levels, even if their initial MSE is slightly worse than the dominant formula family.

---

## 2. Issue: Stagnant Parameter Optimization Overhead

### The Problem:
The Levenberg-Marquardt optimizer executed its full budget of 10 or 30 iterations on every single evaluated expression. However, many candidate structures are mathematically incompatible with the dataset, leading to divergent parameter updates.

### The Consequences:
* **Severe CPU Stagnation**: Extremely slow search times on Level 7 and Level 8 candidate pools due to executing useless linear algebra steps on divergent expressions.

### The Solution: Optimization Early Aborts
We introduced a divergence guard ($\lambda > 10^4$) and a consecutive failure limit (3 iterations without error reduction) to stop fitting immediately when convergence stalls.

### Rationale:
* If the dampening factor $\lambda$ blows up, the step size is effectively zero and no further improvement is mathematically possible. Terminating early saves CPU cycles.

### What was Improved:
* Evaluation speed dramatically improved, bringing single-candidate evaluation times down to **1.3ms - 1.5ms**, allowing the searcher to evaluate millions of Level 8 expressions.

---

## 3. Issue: Complexity Wastage on Powers

### The Problem:
Representing squared or cubed variables previously required nesting multiplication nodes (e.g., `Times(x, x)` or `Times(x, Times(x, x))`).

### The Consequences:
* **Node Exhaustion**: Consumed 3 to 5 nodes of complexity just to represent simple powers, leaving insufficient budget to model the rest of the equation within a `max_complexity=8` limit.

### The Solution: Built-in Unary Power Operators
We implemented `Square` and `Cube` as built-in unary operators under the `full-math` feature.

### Rationale:
* Reduces the node footprint of variables raised to the 2nd and 3rd powers to a single unary wrapper, preserving complexity budget.
