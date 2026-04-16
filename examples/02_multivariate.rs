//! Example: Multivariate formula discovery.
//! This script demonstrates how to find a function with multiple inputs, e.g., f(x0, x1) = x0 + x1.
//! Run this with: cargo run --example 02_multivariate

use eml_sr::{Searcher, SearchConfig};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("--- Example 02: Multivariate Discovery ---");

    // 1. Prepare multivariate data points
    // inputs: Vec<Vec<f64>> where each inner vec is [x0, x1, ...]
    // targets: Vec<f64>
    // Target: f(x0, x1) = x0 + x1
    let inputs = vec![
        vec![1.0, 2.0],
        vec![3.0, 4.0],
        vec![10.0, 20.0],
        vec![0.5, 0.5],
    ];
    let targets = vec![3.0, 7.0, 30.0, 1.0];

    println!("Attempting to discover the formula for x0 + x1...");

    // 2. Perform search
    let searcher = Searcher::default();
    let result = searcher.find_multivariate(&inputs, &targets)?;

    // 3. Print results
    println!("SUCCESS!");
    println!("Formula found:  {}", result.formula());
    println!("Variables:      (Note: v_{{0}} and v_{{1}} represent x0 and x1)");
    println!("Error (MSE):    {:.10}", result.error());

    Ok(())
}
