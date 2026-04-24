//! configuration primitives for Symbolic Regression search.

use crate::ops::operator::Operator;
use std::fmt;
use std::sync::Arc;

/// Type alias for user-supplied scoring functions to reduce complexity.
pub type CustomMetricFn = Arc<dyn Fn(&[f64], &[f64]) -> f64 + Send + Sync>;

/// Supported metrics for evaluating candidate fitness.
#[derive(Clone)]
pub enum ErrorMetric {
    RMSE,
    MAE,
    MaxAbsolute,
    RelativeMSE,
    /// User-defined scoring function.
    Custom(CustomMetricFn),
}

impl fmt::Debug for ErrorMetric {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            ErrorMetric::RMSE => write!(f, "RMSE"),
            ErrorMetric::MAE => write!(f, "MAE"),
            ErrorMetric::MaxAbsolute => write!(f, "MaxAbsolute"),
            ErrorMetric::RelativeMSE => write!(f, "RelativeMSE"),
            ErrorMetric::Custom(_) => write!(f, "Custom(<closure>)"),
        }
    }
}

impl ErrorMetric {
    /// Compute the discrepancy between predicted and actual values.
    pub fn compute(&self, predicted: &[f64], actual: &[f64]) -> f64 {
        assert_eq!(predicted.len(), actual.len());
        let n = predicted.len() as f64;
        match self {
            ErrorMetric::RMSE => {
                let mse: f64 = predicted
                    .iter()
                    .zip(actual)
                    .map(|(p, a)| (p - a).powi(2))
                    .sum::<f64>()
                    / n;
                mse.sqrt()
            }
            ErrorMetric::MAE => {
                predicted
                    .iter()
                    .zip(actual)
                    .map(|(p, a)| (p - a).abs())
                    .sum::<f64>()
                    / n
            }
            ErrorMetric::MaxAbsolute => predicted
                .iter()
                .zip(actual)
                .map(|(p, a)| (p - a).abs())
                .fold(0.0f64, f64::max),
            ErrorMetric::RelativeMSE => {
                predicted
                    .iter()
                    .zip(actual)
                    .map(|(p, a)| {
                        let denom = a.abs().max(1e-12);
                        ((p - a) / denom).powi(2)
                    })
                    .sum::<f64>()
                    / n
            }
            ErrorMetric::Custom(f) => (f)(predicted, actual),
        }
    }
}

/// Parameters controlling the symbolic regression search process.
#[derive(Clone, Debug)]
pub struct SearchConfig {
    pub max_complexity: usize,
    pub precision_goal: f64,
    pub allow_approximate: bool,
    pub error_metric: ErrorMetric,
    pub extra_operators: Vec<Arc<Box<dyn Operator>>>,
    pub include_builtins: bool,
    pub memory_limit_mb: usize,
    pub parallelism: usize,
    pub max_pool_size: usize,

    /// Beam Search width: maximum candidates retained per complexity level.
    pub beam_width: usize,
    /// Multiplicative penalty applied to the error based on expression complexity.
    pub complexity_penalty: f64,
    /// Enable iterative constant refinement via Levenberg-Marquardt.
    pub optimize_constants: bool,
}

impl Default for SearchConfig {
    fn default() -> Self {
        Self {
            max_complexity: 6,
            precision_goal: 1e-10,
            allow_approximate: false,
            error_metric: ErrorMetric::RMSE,
            extra_operators: Vec::new(),
            include_builtins: true,
            memory_limit_mb: 512,
            parallelism: rayon::current_num_threads(),
            max_pool_size: 300_000,

            beam_width: 1_000,
            complexity_penalty: 0.1,
            optimize_constants: true,
        }
    }
}

impl SearchConfig {
    pub fn builder() -> SearchConfigBuilder {
        SearchConfigBuilder::new()
    }
}

#[derive(Default)]
pub struct SearchConfigBuilder {
    inner: SearchConfig,
}

impl SearchConfigBuilder {
    pub fn new() -> Self {
        Self::default()
    }
}

impl SearchConfigBuilder {
    pub fn max_complexity(mut self, n: usize) -> Self {
        self.inner.max_complexity = n;
        self
    }
    pub fn precision_goal(mut self, goal: f64) -> Self {
        self.inner.precision_goal = goal;
        self
    }
    pub fn allow_approximate(mut self, allow: bool) -> Self {
        self.inner.allow_approximate = allow;
        self
    }
    pub fn error_metric(mut self, metric: ErrorMetric) -> Self {
        self.inner.error_metric = metric;
        self
    }
    pub fn beam_width(mut self, width: usize) -> Self {
        self.inner.beam_width = width;
        self
    }
    pub fn complexity_penalty(mut self, penalty: f64) -> Self {
        self.inner.complexity_penalty = penalty;
        self
    }
    pub fn optimize_constants(mut self, optimize: bool) -> Self {
        self.inner.optimize_constants = optimize;
        self
    }
    pub fn build(self) -> SearchConfig {
        self.inner
    }
}
