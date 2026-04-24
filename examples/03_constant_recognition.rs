//! Example: Constant factor recognition.
//! This script demonstrates how to identify a numerical constant as a mathematical expression.
//! Run this with: cargo run --example 03_constant_recognition

use eml_sr::Searcher;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("--- Example 03: Constant Recognition ---");

    // Let's say we have a mystery number: 3.14159...
    let target_constant = std::f64::consts::PI;

    println!("Attempting to identify the number {:.6} as a formula...", target_constant);

    // 1. Perform search specifically for a scalar value
    let searcher = Searcher::default();
    let result = searcher.recognize_constant(target_constant)?;

    // 2. Print results
    println!("Identified as:  {}", result.formula());
    println!("LaTeX version:  {}", result.to_latex());
    println!("Python version: {}", result.to_python());
    println!("Error:          {:.10}", result.error());

    Ok(())
}
