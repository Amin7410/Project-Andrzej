# Hacker's Guide: Exploring the Eml-SR Source Code

So, you want to dive into the internals of **eml_sr**? Welcome! This guide is for those who cloned the repository and want to understand how it works, experiment with the EML operator, or even "break" things to see what happens.

## Project Philosophy
The core focus of this library is **Extreme Minimalism**. We believe that reducing all continuous math to a single operator isn't just a gimmick—it's a path to a new kind of computing.

## How to Explore & "Hack"

### 1. The Rust Core Structure
- **`src/ops/`**: The heart of the project. This is where the EML operator logic lives. Check here to see how `Plus`, `Sin`, or `Log` are derived from a single operator.
- **`src/engine/`**: The search logic (BFS) that explores the mathematical formula space.
- **`src/tests/`**: The "Playground". Add your own mathematical functions here and see if the engine can find them.
- **`examples/`**: Practical use cases that show the API in action.

### 2. Running Local Experiments
Since you have the source code, you can use `cargo` to run the internal tools and demos:

```bash
# Run the main verification orchestrator (the test suite)
cargo run

# Run specific examples (univariate, multivariate, etc.)
cargo run --example 01_simple_discovery
cargo run --example 02_multivariate
cargo run --example 03_constant_recognition
```

### 3. Testing Your Changes
If you modify the search logic or add new deriving rules, verify your changes using:
```bash
cargo test
```

## Important Note on Registry Usage
This guide is for those working **inside the cloned repository**. 
- If you just want to use the library in a separate project, follow the **README.md** instructions (`pip install` or `cargo add`).
- We have already published formal versions to PyPI and Crates.io. You do not need to publish your own versions to use the library.

---
*Happy Hacking! Let the EML operator show you the hidden simplicity of math.*
