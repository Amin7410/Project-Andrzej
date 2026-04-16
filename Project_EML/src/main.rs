mod tests;

use eml_sr::{Searcher, SearchConfig};
use std::time::Instant;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("===========================================================");
    println!("      EML_SR EXPERIMENTAL VERIFICATION SUITE              ");
    println!("===========================================================");
    println!("Environment: Production/Research");
    println!("Date: {}\n", chrono::Local::now().format("%Y-%m-%d %H:%M:%S"));

    let cases = tests::get_test_suite();
    let config = SearchConfig::default();
    let searcher = Searcher::new(config);

    let mut success_count = 0;
    let total_start = Instant::now();

    for (i, case) in cases.iter().enumerate() {
        println!("[{}/{}] Running: {}...", i + 1, cases.len(), case.name);
        println!("      Description: {}", case.description);
        
        let start = Instant::now();
        let result = searcher.find_multivariate(&case.inputs, &case.targets)?;
        let duration = start.elapsed();

        println!("      Found:       {}", result.formula());
        println!("      Error (MSE): {:.10}", result.error());
        println!("      Complexity:  {}", result.complexity());
        println!("      Execution:   {:?}\n", duration);

        if result.error() < 1e-6 {
            success_count += 1;
        }
    }

    let total_duration = total_start.elapsed();
    println!("===========================================================");
    println!("SUMMARY REPORT");
    println!("===========================================================");
    println!("Tests executed: {}", cases.len());
    println!("Successful:     {}", success_count);
    println!("Total time:     {:?}", total_duration);
    println!("Overall status: {}", if success_count == cases.len() { "PASS" } else { "FAIL" });
    println!("===========================================================");

    Ok(())
}
