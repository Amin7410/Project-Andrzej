#![allow(dead_code, unused_imports)]

//! `eml-sr` — High-performance symbolic regression via the EML operator.

pub(crate) mod core;
pub(crate) mod engine;
pub(crate) mod ops;

pub mod config;
pub mod error;
pub mod result;

pub use config::{ErrorMetric, SearchConfig, SearchConfigBuilder};
pub use error::EmlError;
pub use ops::operator::Operator;
pub use result::SearchResult;

/// Core engine for symbolic regression search.
pub struct Searcher {
    config: SearchConfig,
}

impl Searcher {
    /// Initialises a new Searcher with the given configuration.
    pub fn new(config: SearchConfig) -> Self {
        Self { config }
    }

    /// Performs a symbolic regression search for univariate data f(x) ≈ y.
    pub fn find_function(&self, xs: &[f64], ys: &[f64]) -> Result<SearchResult, EmlError> {
        let inputs: Vec<Vec<f64>> = xs.iter().map(|&x| vec![x]).collect();
        engine::bfs::run_bfs(&inputs, ys, &self.config)
    }

    /// Performs a symbolic regression search for multivariate data f(x0, x1, ...) ≈ y.
    pub fn find_multivariate(
        &self,
        inputs: &[Vec<f64>],
        ys: &[f64],
    ) -> Result<SearchResult, EmlError> {
        engine::bfs::run_bfs(inputs, ys, &self.config)
    }

    /// Identifies a closed-form expression equivalent to a target scalar constant.
    pub fn recognize_constant(&self, target: f64) -> Result<SearchResult, EmlError> {
        let inputs: Vec<Vec<f64>> = vec![vec![0.0]];
        let ys: Vec<f64> = vec![target];
        engine::bfs::run_bfs(&inputs, &ys, &self.config)
    }

    /// Returns the best candidate formulas found during the search process.
    pub fn find_candidates(
        &self,
        inputs: &[Vec<f64>],
        ys: &[f64],
    ) -> Result<Vec<SearchResult>, EmlError> {
        let mut config = self.config.clone();
        config.allow_approximate = true;
        let result = engine::bfs::run_bfs(inputs, ys, &config)?;
        Ok(vec![result])
    }
}

impl Default for Searcher {
    fn default() -> Self {
        Self::new(SearchConfig::default())
    }
}
