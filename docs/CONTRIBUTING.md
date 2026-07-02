# Contributing to eml_sr

This guide is for developers who want to compile `eml_sr` from source, run the demo/example scenarios, or contribute to the project.

Note: this project currently has **no automated test suite** (no `#[test]` functions, no `cargo test` step in CI). The "verification" steps below are manual sanity checks, not regression tests. Contributions that add real `#[test]`-based coverage are especially welcome — see [STATUS.md](STATUS.md) for the full list of known gaps.

## Development Setup

### 1. Run the Demo Verification Scenarios
After downloading the source code, you can run a small hand-written set of demo scenarios (see `src/tests/mod.rs`) to see the engine in action:
```bash
cargo run --release
```
This prints formulas found and pass/fail-style output for a handful of scenarios — it is not an automated test suite.

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

### 3. Add Your Own Demo Scenarios
You can try any function by opening `src/tests/mod.rs` and adding a new `TestCase` to the `get_test_suite()` function. It will show up in the report when you run `cargo run`. This is a manual demo mechanism, not an automated test — if you want to contribute real regression tests, prefer adding `#[test]` functions instead.

### 4. Compiling Python Bindings
If you are developing the Python wrapper locally, you can rebuild the bindings using Maturin. In your Python virtual environment on Windows PowerShell, run:
```powershell
$env:PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1; .venv\Scripts\maturin.exe develop
```


### 5. Advanced Modes (Feature Flags)
The library provides flexible compilation options:
- **Default**: Uses the full library of operators for best search performance.
- **Pure EML**: Uses only the single EML operator for theoretical research purposes.
  ```bash
  cargo run --release --no-default-features
  ```

---
*Note: The `eml_sr` library is optimized for high performance; always use `--release` mode for the best speed.*
