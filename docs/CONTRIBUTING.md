# Contributing to eml_sr

This guide is for developers who want to compile `eml_sr` from source, run tests, or contribute to the project.

## Development Setup

### 1. Run the Verification Framework (Demo)
After downloading the source code, you can immediately run the verification suite to see the power of the EML operator:
```bash
cargo run --release
```

### 2. Browse Sample Examples
We provide a dedicated folder `examples/` for you to learn by doing. Run them with:
```bash
# Univariate discovery
cargo run --release --example 01_simple_discovery

# Multivariate (2+ variables)
cargo run --release --example 02_multivariate

# Identify mathematical constants
cargo run --release --example 03_constant_recognition
```

### 3. Add Your Own Test Scenarios
You can easily test any function by opening `src/tests/mod.rs` and adding a new `TestCase` to the `get_test_suite()` function. All changes will be automatically updated in the report when you run `cargo run`.

### 4. Advanced Modes (Feature Flags)
The library provides flexible compilation options:
- **Default**: Uses the full library of operators for best search performance.
- **Pure EML**: Uses only the single EML operator for theoretical research purposes.
  ```bash
  cargo run --release --no-default-features
  ```

---
*Note: The `eml_sr` library is optimized for high performance; always use `--release` mode for the best speed.*
