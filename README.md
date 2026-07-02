[VietNamese click here!](READMEVN.md)

> [!IMPORTANT]
> **Release v0.2.2**
> This release introduces the `SmartSearcher` Output Transformation framework (Identity, Square, Log, Inverse) to resolve non-linear targets, adaptive beam width settings, and early-stop optimizations. Read our version updates for details:
> - **v0.2.2**: [Improvements](docs/version_news/V0.2.2/improvements.md) | [Issues & Solutions](docs/version_news/V0.2.2/issues_and_solutions.md)
> - **v0.2.1**: [Improvements](docs/version_news/V0.2.1/improvements.md) | [Issues & Solutions](docs/version_news/V0.2.1/issues_and_solutions.md)
> - **v0.2.0**: [Improvements](docs/version_news/v0.2.0/improvements.md) | [Issues & Solutions](docs/version_news/v0.2.0/issues_and_solutions.md)

# eml_sr: Symbolic Regression via the EML Operator

| System | Installation Command | Registry |
| :--- | :--- | :--- |
| **Rust / Cargo** | `cargo add eml_sr` | [crates.io](https://crates.io/crates/eml_sr) |
| **Python / Pip** | `pip install eml_sr` | [pypi.org](https://pypi.org/project/eml-sr/) |

## Introduction

**eml_sr** is a Rust library for symbolic regression — searching for a closed-form mathematical formula that fits a numerical dataset. Its search space is built around the **EML operator**, a genuine mathematical discovery by Andrzej Odrzywołek (Jagiellonian University):

```
eml(x, y) = e^x - ln(y)
```

Odrzywołek proved that this single binary operator, combined with only the constant `1`, is sufficient to reconstruct the standard repertoire of a scientific calculator — arithmetic, elementary transcendental functions, and constants like e, π, and i. The proof is published on arXiv: [*All elementary functions from a single binary operator*](https://arxiv.org/abs/2603.21852).

`eml_sr` uses EML as one operator inside a practical Rust symbolic-regression engine, alongside conventional "fast-path" operators (Sin, Cos, Exp, Log, Sqrt, Square, Cube, and standard arithmetic). See **[Read This First: Status & Honesty Notes](#read-this-first-status--honesty-notes)** below for exactly what is implemented today versus what is still a research direction.

## Read This First: Status & Honesty Notes

This section exists because earlier revisions of this README described capabilities more confidently than the current code supports. Please read it before deciding how to use this project.

**What is implemented and working today:**
- A parallel (Rayon) breadth-first / beam-search engine (`src/engine/bfs.rs`) that searches over increasingly complex expression trees, built from EML plus the standard operator set.
- Levenberg–Marquardt local optimization of numeric constants (`src/engine/optimizer.rs`) — a conventional technique, not something unique to EML.
- A Pareto front of formulas trading off accuracy vs. complexity, and a Python `SmartSearcher` wrapper (`smart_search.py`) that retries the search on transformed targets (`y`, `y²`, `ln(y)`, `1/y`) to catch functions nested inside `sqrt`/`log`/division.
- Rust and Python (PyO3) APIs, published on crates.io and PyPI. This part has been exercised against real physics formulas (a subset of the Feynman symbolic-regression benchmark) and found exact or near-exact matches for several of them.

**What is *not* implemented, despite being described in earlier versions of this document as the project's core idea:**
- **Continuous gradient optimization over a "master" EML tree** (training a large homogeneous EML tree with an optimizer like Adam, then snapping weights to 0/1 to reveal a formula) — this is the method described in Odrzywołek's own paper (validated there only at shallow tree depth, ≤4), and it is *not* what the current Rust engine does. The current engine is a conventional discrete combinatorial search, comparable in spirit to other symbolic-regression tools (e.g. PySR, gplearn), with EML available as one operator among several.
- **Compiling arbitrary formulas down to pure-EML instruction sequences**, and any **EML virtual machine / analog-circuit / VLSI compiler** — these are described as *potential applications* of the underlying math in the sections below, not as features this codebase provides.
- In practice, across the physics formulas this project has been tested against, the discovered formulas almost never use the `EML` operator directly — the cheaper "fast-path" operators (Exp, Log, Sqrt, Square, Divide, ...) are preferred by the search's complexity-penalized scoring, because they are unary and thus structurally cheaper than reconstructing the same function through EML. EML currently pays off mainly for expressions with the exact shape `eᴬ − ln(B)`, where `A` and `B` differ.

None of this means the underlying math is wrong — it's independently verified (see citation above). It means: what you get by installing `eml_sr` today is a working, conventional Rust symbolic-regression engine that happens to include EML as an operator, not yet a realization of the "continuous optimization over a universal operator" vision. If that gradient-based approach is what you're looking for, it does not exist here yet.

## Why EML *and* standard operators?

EML alone can represent any elementary function, but doing so can require deeply nested trees (e.g. reconstructing `sin(x)` purely from `eml` compositions), and search cost grows combinatorially with tree depth. So by default `eml_sr` also registers cheap, purpose-built unary/binary operators (Exp, Log, Sqrt, Sin, Cos, Tan, ArcSin/Cos/Tan, Square, Cube, and standard arithmetic) so the search can reach common functions in a single node instead of many. EML stays in the operator set as a general fallback — useful in particular for `exp(...) − ln(...)`-shaped relationships that don't have a dedicated shortcut.

If you want to force a search that can *only* use EML (no shortcuts), the library supports a compile-time "Pure EML" build — see [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md). Be aware this makes the search dramatically slower and deeper, as documented in [docs/STATUS.md](docs/STATUS.md).

## Scientific Foundation and Authors

**Andrzej Odrzywołek**, a theoretical physicist at the Institute of Theoretical Physics at the Jagiellonian University (Krakow, Poland), discovered the EML operator through a systematic exhaustive search and proved constructively that it — combined with the constant 1 — suffices to generate:
- Basic arithmetic operations (+, -, ×, /).
- All elementary functions (sin, cos, log, powers...).
- Fundamental constants of mathematics such as e, π, and the imaginary unit i.

Full reference: [All elementary functions from a single binary operator, arXiv:2603.21852](https://arxiv.org/abs/2603.21852). A follow-up paper by Tomasz Stachowiak, [*Algebraic structure behind Odrzywołek's EML operator*, arXiv:2604.23893](https://arxiv.org/abs/2604.23893), examines the group-theoretic structure behind it. This `eml_sr` project is an independent engineering effort that uses the EML operator; it is not authored by or officially affiliated with either paper's authors.

## Potential Applications of EML (Conceptual — Not Implemented Here)

The math itself opens interesting doors, discussed below for context. **`eml_sr` does not currently implement any of the following** — they are included so readers understand *why* EML is interesting, not as a feature list.

- **Breaking the AI "Black Box"**: training a neural network on an EML tree with a standard optimizer and snapping weights to exact values (0 or 1) could, in principle, produce closed-form formulas instead of opaque weights. This is the method demonstrated (at shallow depth) in Odrzywołek's paper — not something this Rust engine does.
- **EML Compiler / Single-Instruction Stack Machine**: because every elementary-function expression can in principle be rewritten as nested EML instructions, one could compile any formula into a "one-instruction" stack machine — useful for formal verification. No such compiler exists in this repository.
- **VLSI / Analog Computing**: a uniform binary-tree structure of identical EML units could, in principle, be mapped to repeated analog circuit elements instead of designing bespoke circuits per operation. Purely conceptual here.
- **Minimal grammar for parsing/storage**: the grammar `S -> 1 | eml(S, S)` is extremely simple, which could simplify storage/parsing of mathematical expressions. `eml_sr`'s own internal representation does not use this minimal form — it uses a mixed operator tree, for the performance reasons explained above.

## Quick Start

### 1. Installation

**Python Users:**
```bash
pip install eml_sr
```

**Rust Users:**
```bash
cargo add eml_sr
```

### 2. Basic Usage (Python)

```python
from eml_sr import Searcher

# Your data
X = [[1.0], [2.0], [3.0]]
y = [2.5, 4.5, 6.5]  # f(x) = 2x + 0.5

# Search for the formula
searcher = Searcher()
result = searcher.fit(X, y)

print(f"Formula: {result.formula}")
# Output: Formula: (v_{0} * 2.0) + 0.5
```

### 3. Basic Usage (Rust)

```rust
use eml_sr::{Searcher, SearchConfig};

fn main() {
    let searcher = Searcher::new(SearchConfig::default());
    let xs = vec![1.0, 2.0, 3.0];
    let ys = vec![2.5, 4.5, 6.5];

    if let Ok(result) = searcher.find_function(&xs, &ys) {
        println!("Found formula: {}", result.formula);
    }
}
```

## Project Status & Safety

For detailed information about current capabilities, supported platforms, measured (not aspirational) performance numbers, and safety warnings regarding memory usage (OOM), see [docs/STATUS.md](docs/STATUS.md).

## Development & Contributing

If you want to build from source, run benchmarks, or contribute to the core engine, see [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md).

---
*Note: `eml_sr` is an actively developed, working symbolic-regression engine. It is not yet a full realization of the continuous-optimization / gradient-training vision described above — see "Read This First" for the honest current state.*
