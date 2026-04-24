[VietNamese click here!](READMEVN.md)

# eml_sr: Primitivizing Continuous Mathematics in Rust

[![Crates.io](https://img.shields.io/crates/v/eml_sr.svg)](https://crates.io/crates/eml_sr)
[![PyPI](https://img.shields.io/pypi/v/eml-sr.svg)](https://pypi.org/project/eml-sr/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

| System | Installation Command | Registry |
| :--- | :--- | :--- |
| **Rust / Cargo** | `cargo add eml_sr` | [crates.io](https://crates.io/crates/eml_sr) |
| **Python / Pip** | `pip install eml_sr` | [pypi.org](https://pypi.org/project/eml-sr/) |

## Introduction
**eml_sr** is a high-performance Rust library that implements one of the deepest structural discoveries in continuous mathematics: **All elementary functions can be represented using just a single binary operator.**

In the world of digital electronics, the NAND gate is the fundamental building block for every complex logic circuit. Similarly, **eml_sr** provides a "NAND gate for continuous mathematics." This library allows developers to compile any complex formula (from basic arithmetic to trigonometry, logarithms, and transcendental constants) into an absolutely uniform binary tree structure.

Instead of maintaining a cumbersome Abstract Syntax Tree (AST) with dozens of different node types (Add, Sub, Sin, Cos, Exp), **eml_sr** collapses your entire architecture down to exactly one single node type.

## Paradigm Shift with EML

**eml_sr** was not created to replace standard math libraries, but to provide a completely new approach to representing and discovering mathematical structures.

### 1. Data Structure Transformation: From Heterogeneous to Homogeneous
When building an Abstract Syntax Tree (AST) for a mathematical expression:

*   **Traditional Method (Heterogeneous AST)**: Uses many different node types (Add, Mul, Sin, Exp...).
    *   **Pros**: Direct description and extremely fast computation on current hardware.
    *   **Challenges**: When writing formula transformation algorithms (like auto-differentiation or expression simplification), developers must handle countless branch cases (switch-case) for each operator.

*   **The EML Approach (Homogeneous Binary Tree)**:
    Reduces the entire mathematical space to a single node type: `EmlNode`.
    *   **Value Proposition**: The diversity of mathematics is "compressed" into a uniform graph structure. Tree traversal, parsing, or structural transformation now only require a single recursive rule. Your core code becomes ultra-thin and extremely safe.

### 2. Artificial Intelligence (Symbolic Regression): From Discrete Search to Continuous Optimization
In tasks where AI is required to automatically discover formulas from raw data:

*   **Traditional Method (Combinatorial Search)**: AI must choose and combine from a "dictionary" containing dozens of different base operators (Base Set) through genetic algorithms.
    *   **Characteristics**: Effective for short expressions, but the search space explodes exponentially as complexity increases.

*   **The EML Approach (Continuous Optimization)**:
    Completely skips the function selection step. The AI is provided with a "Master Formula" – a massive EML tree containing all possibilities of elementary functions.
    *   **Value Proposition**: EML turns the difficult "combinatorial search" problem into a smooth "Gradient Optimization" problem. By using standard optimizers (like Adam) on the tree branches and rounding weights (snapping), Neural Networks can automatically prune and reveal sharp, precise physical and mathematical laws, fundamentally solving the "black box" problem of AI.

> [!NOTE]
> **💡 Note on Architecture & Trade-offs**: The absolute uniformity of EML comes with trade-offs regarding expression tree depth and strict requirements for floating-point precision. To understand these issues better, please see my personal analysis and discussion in [WHATITHINK.txt](WHATITHINK.txt).

## Scientific Foundation and Authors

**Andrzej Odrzywołek**, a theoretical physicist at the Institute of Theoretical Physics at the Jagiellonian University (Krakow, Poland), is the author behind the groundbreaking discovery of the minimalism of continuous mathematics. Through personal research effort and a systematic exhaustive search method, he solved a problem that had no precedent: finding a single "atom" for all functions.

The core discovery of Andrzej Odrzywołek is the EML (Exp-Minus-Log) operator:
                eml(x, y) = e^(x) - ln(y)
He has convincingly proven that this operator, when combined with only the constant 1, can reproduce the entire catalog of a standard scientific calculator. This includes:
- Basic arithmetic operations (+, -, x, /).
- All elementary functions (sin, cos, log, powers...).
- Fundamental constants of mathematics such as e, pi, and the imaginary unit i.

Andrzej Odrzywołek's vision does not stop at pure theory. He has established a rigorous verification process, using independent transcendental constants to prove that all mathematical expressions can be converted into a uniform binary tree structure of EML nodes. His work opens up massive potential applications in creating minimalist analog computing circuits and enhancing the explainability of artificial intelligence through symbolic regression.

Full reference documentation: [All elementary functions from a single operator](https://www.alphaxiv.org/abs/2603.21852v2)

## Practical Applications of EML

The power of the EML operator lies not only in its theoretical elegance. Below are the areas where the `eml_sr` library can become the core engine for next-generation software systems.

### 1. Artificial Intelligence (Machine Learning & Symbolic Regression)

This is the largest and most practical application of EML in software today:

- **Symbolic Regression**: Instead of AI models searching over messy grammars containing many different operators, EML allows for the creation of a multi-parameter "master formula" using a binary tree structure. The entire search space is collapsed into weight optimization on a single uniform structure, instead of fumbling through billions of different structural combinations.

- **Breaking the AI "Black Box"**: You can use standard optimization algorithms (like Adam) to train neural networks based on this EML tree. Upon successful training, the system can snap weights to exact values (0 or 1), helping the AI output a **clear mathematical formula** (closed-form expressions) instead of just predicted numbers. This is the key to turning AI from a "black box" into a tool that humans can read, understand, and trust.

### 2. Building Compilers and Virtual Machines

EML provides an ideal foundation for developers to build ultra-minimalist execution systems:

- **EML Compiler**: You can use the `eml_sr` library as a core engine to write compiler software capable of converting any mathematical formula (e.g., sin(x) + e^x) into pure EML form — a series of nested EML instructions containing only the constant 1.

- **Single Instruction Stack Machine**: This pure EML form can be executed on a simulated stack machine that has exactly one single instruction. Imagine an RPN (Reverse Polish Notation) calculator with exactly one button — that is the essence of an EML virtual machine. This extreme simplicity makes formal verification more feasible and easier than ever.

### 3. VLSI Design and Analog Computing

EML acts as a bridge between software engineers and hardware engineers:

- Because all elementary functions become uniform binary trees in EML notation, you can use the `eml_sr` library to write software that compiles formulas into **circuit schematics**.

- This is very useful in **analog computing**, where engineers can create multivariate function computing circuits by connecting a binary tree topology structure of identical EML elements. Instead of designing separate circuits for each operation (+, x, sin...), you can mass-produce a single type of EML component and connect them according to the tree diagram.

### 4. Data Structure Design and Parsing

EML brings radical simplicity to the processing of mathematical expressions in software:

- Instead of writing handling code for dozens of different operations (+, -, sin, cos...), your software only needs to handle one **extremely simple context-free grammar**:
S -> 1|eml(S, S)

- This makes systems for storage, parsing, or formal processing of mathematical expressions incredibly uniform. Every expression — no matter how complex — is represented by the same data structure, the same tree traversal algorithm, and the same evaluation logic. No more exceptions, no more special branching.

## Usage Guide

The project is designed to serve both theoretical research and practical application purposes.

### 1. Run the Verification Framework (Demo)
After downloading the source code, you can immediately run the verification suite to see the power of the EML operator:
```bash
cargo run
```

### 2. Browse Sample Examples
We provide a dedicated folder `examples/` for you to learn by doing. Run them with:
```bash
# Univariate discovery
cargo run --example 01_simple_discovery

# Multivariate (2+ variables)
cargo run --example 02_multivariate

# Identify mathematical constants
cargo run --example 03_constant_recognition
```

### 3. Add Your Own Test Scenarios
You can easily test any function by opening `src/tests/mod.rs` and adding a new `TestCase` to the `get_test_suite()` function. All changes will be automatically updated in the report when you run `cargo run`.

### 3. Integrate EML-SR into Your Project
If you are building another application and want to use the "brain" of `eml_sr`, add the following to your `Cargo.toml`:
```toml
[dependencies]
eml_sr = { git = "https://github.com/Amin7410/Project-Andrzej.git" }
```

And use it in your source code:
```rust
use eml_sr::{Searcher, SearchConfig};

fn main() {
    let config = SearchConfig::default();
    let searcher = Searcher::new(config);
    
    // Search for a formula from your x, y data
    // let result = searcher.find_function(&xs, &ys);
}
```

### 4. Advanced Modes (Feature Flags)
The library provides flexible compilation options:
- **Default**: Uses the full library of operators for best search performance.
- **Pure EML**: Uses only the single EML operator for theoretical research purposes.
  ```bash
  cargo run --no-default-features
  ```

---
*Note: The `eml_sr` library is optimized for high performance; running in `--release` mode is recommended for the best speed.*
