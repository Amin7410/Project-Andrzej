//! Registry of test scenarios for the EML-SR engine.

pub struct TestCase {
    pub name: &'static str,
    pub description: &'static str,
    pub inputs: Vec<Vec<f64>>,
    pub targets: Vec<f64>,
}

/// Generates a suite of diverse mathematical challenges.
pub fn get_test_suite() -> Vec<TestCase> {
    vec![
        // Scenario 1: Basic Trigonometry
        TestCase {
            name: "Basic Trig",
            description: "Target: f(x) = sin(x) + 1",
            inputs: (0..10).map(|i| vec![i as f64 * 0.5]).collect(),
            targets: (0..10).map(|i| (i as f64 * 0.5).sin() + 1.0).collect(),
        },
        // Scenario 2: Gaussian Bell Curve
        TestCase {
            name: "Gaussian",
            description: "Target: f(x) = exp(-x^2)",
            inputs: (-5..5).map(|i| vec![i as f64 * 0.2]).collect(),
            targets: (-5..5).map(|i| (-(i as f64 * 0.2).powi(2)).exp()).collect(),
        },
        // Scenario 3: Bivariate Addition
        TestCase {
            name: "Bivariate Add",
            description: "Target: f(x, y) = x + y",
            inputs: vec![
                vec![1.0, 2.0],
                vec![3.0, 4.0],
                vec![5.0, 6.0],
                vec![7.0, 8.0],
            ],
            targets: vec![3.0, 7.0, 11.0, 15.0],
        },
        // Scenario 4: Constant Recognition
        TestCase {
            name: "Constant PI",
            description: "Target: f(x) = 3.141592",
            inputs: (0..5).map(|_| vec![0.0]).collect(),
            targets: (0..5).map(|_| 3.1415926535).collect(),
        },
    ]
}
