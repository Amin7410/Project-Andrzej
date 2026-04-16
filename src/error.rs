use thiserror::Error;

/// Centralised error definitions for the `eml-sr` library.
#[derive(Debug, Error, PartialEq)]
pub enum EmlError {
    /// No solution found within the specified complexity limit.
    #[error("No formula found: searched all expressions up to complexity {max_complexity}.")]
    NotFound { max_complexity: usize },

    /// RAM allocation exceeded the defined threshold.
    #[error("Memory limit exceeded ({used_mb} MB used, limit is {limit_mb} MB).")]
    OutOfMemory { used_mb: usize, limit_mb: usize },

    /// Erroneous input data or configuration.
    #[error("Invalid input: {reason}")]
    InvalidInput { reason: String },

    /// Failure due to inconsistent operator argument counts.
    #[error("Internal arity error: operator '{name}' expects {expected} argument(s), got {got}.")]
    ArityMismatch {
        name: String,
        expected: u8,
        got: usize,
    },
}

impl EmlError {
    pub fn invalid(reason: impl Into<String>) -> Self {
        EmlError::InvalidInput {
            reason: reason.into(),
        }
    }
}
