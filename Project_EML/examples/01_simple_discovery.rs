//! Example: Basic univariate formula discovery.
//! This script demonstrates how to find a simple function like f(x) = sin(x) + 1.
//! Run this with: cargo run --example 01_simple_discovery

use eml_sr::{Searcher, SearchConfig};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("--- Example 01: Simple Discovery ---");

    // 1. Prepare raw data points (x, y)
    // Target: y = sin(x) + 1
    let xs: Vec<f64> = (0..20).map(|i| i as f64 * 0.1).collect();
    let ys: Vec<f64> = xs.iter().map(|&x| x.sin() + 1.0).collect();

    println!("Attempting to discover the formula for sin(x) + 1...");

    // 2. Initialise the search engine with default configuration
    let config = SearchConfig::default();
    let searcher = Searcher::new(config);

    // 3. Find the function
    // find_function is a convenience method for single-variable data
    let result = searcher.find_function(&xs, &ys)?;

    // 4. Print results
    println!("SUCCESS!");
    println!("Formula found:  {}", result.formula());
    println!("Residual Error: {:.10}", result.error());
    println!("Complexity:     {}", result.complexity());

    Ok(())
}
