# Release v0.2.2 - Code Improvements

This document lists all code-level optimizations, architecture upgrades, and new features introduced in version `v0.2.2` compared to `v0.2.1`.

---

## 1. Python Smart Search Wrapper (`SmartSearcher`)
* **File added**: [smart_search.py](file:///c:/Users/minhd/Documents/GitHub/Project-Andrzej/smart_search.py)
* **Upgrade**: Implemented a dynamic Python wrapper wrapper layer to orchestrate multiple search strategies over transformed dataset targets.
* **Key Components**:
  * `SmartSearchResult`: Mimics the PyO3 `SearchResult` interface, adapting formula string rendering, Python/NumPy code compilation, and LaTeX formulas to reflect inverse transformations.
  * `SmartSearcher`: Wraps the native Rust `Searcher`, handling pre-checks, data transformations, and strategy aggregation.

## 2. Multi-Strategy Target Transformations
* **File affected**: [smart_search.py](file:///c:/Users/minhd/Documents/GitHub/Project-Andrzej/smart_search.py)
* **Upgrade**: Added 4 target transformation search strategies:
  1. **Identity** ($y$): Default search.
  2. **Square** ($y^2$): Automatically targeted if $y \ge 0$ everywhere.
  3. **Log** ($\ln(y)$): Automatically targeted if $y > 0$ everywhere.
  4. **Inverse** ($1/y$): Automatically targeted if $|y| > 10^{-5}$ everywhere.

## 3. Back-Transformation & Unified Pareto Front
* **File affected**: [smart_search.py](file:///c:/Users/minhd/Documents/GitHub/Project-Andrzej/smart_search.py)
* **Upgrade**: Integrates candidate results across all active transformation searches.
* **Mechanism**:
  * Evaluates predictions of all candidates by applying inverse transformations.
  * Computes the final Mean Squared Error (MSE) in the original $y$-space.
  * Adjusts the complexity of wrapped candidate formulas (adds $+1$ node to account for the outer operator, e.g. `Sqrt`, `Exp`, or `Inv`).
  * Generates a consolidated Pareto front based on the original scale MSE and adjusted complexity.

## 4. Search Loop Early Stop
* **File affected**: [smart_search.py](file:///c:/Users/minhd/Documents/GitHub/Project-Andrzej/smart_search.py)
* **Upgrade**: Integrated an early-stop condition inside the strategy search loop.
* **Mechanism**: If any search strategy resolves a mathematically perfect candidate ($\text{MSE} < 10^{-15}$ in the original space), the search loop breaks immediately, skipping remaining strategies.
* **Benefit**: Saves up to **75%** of search execution time for fast-converging formulas.

## 5. Hierarchical Benchmark Suite Restructuring
* **Files affected**: [generate_suite.py](file:///c:/Users/minhd/Documents/GitHub/Project-Andrzej/generate_suite.py), [.gitignore](file:///c:/Users/minhd/Documents/GitHub/Project-Andrzej/.gitignore)
* **Upgrade**: Reorganized the Feynman benchmark suite.
* **Key Features**:
  * Hierarchical directory layout: `Test/Feynman/<ID>/`.
  * Localized results directory: `Results/` per test folder to store `fit.txt` and `fit.png` separately.
  * Adaptive search configuration: Automatically assigns `beam_width=1000` for equations with 3 or more variables to prevent beam pruning failures on complex structures.
  * Auto-generated catalog: Created [Test/Feynman/README.md](file:///c:/Users/minhd/Documents/GitHub/Project-Andrzej/Test/Feynman/README.md) listing the formula, variables, complexity, and description of all 100 Feynman equations.
