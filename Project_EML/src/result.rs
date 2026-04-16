//! standardised output format for search results.

use crate::core::expression::Expression;
use crate::core::value::{real, Value};
use crate::ops::registry::OperatorRegistry;

/// Encapsulates a discovered formula and its associated metadata.
pub struct SearchResult {
    expression: Expression,
    pub error: f64,
    registry: std::sync::Arc<OperatorRegistry>,
}

impl SearchResult {
    pub(crate) fn new(
        expression: Expression,
        error: f64,
        registry: std::sync::Arc<OperatorRegistry>,
    ) -> Self {
        Self {
            expression,
            error,
            registry,
        }
    }

    /// Returns the Kolmogorov complexity of the expression.
    pub fn complexity(&self) -> usize {
        self.expression.complexity()
    }

    /// Returns the canonical prefix-notation representation.
    pub fn formula(&self) -> &str {
        self.expression.display()
    }

    /// Renders the formula in LaTeX format.
    pub fn to_latex(&self) -> String {
        self.render(|reg, id, args| reg.to_latex(id, args))
    }

    /// Renders the formula as a Python-compatible string.
    pub fn to_python(&self) -> String {
        self.render(|reg, id, args| reg.to_python(id, args))
    }

    /// Renders the formula in Wolfram Language (Mathematica) format.
    pub fn to_mathematica(&self) -> String {
        self.render(|reg, id, args| reg.to_mathematica(id, args))
    }

    /// Evaluates the formula for a single input (univariate convenience).
    pub fn eval(&self, x: f64) -> f64 {
        self.eval_multi(&[x])
    }

    /// Evaluates the formula for a multivariate input vector.
    pub fn eval_multi(&self, xs: &[f64]) -> f64 {
        let inputs: Vec<Value> = xs.iter().map(|&x| real(x)).collect();
        self.expression
            .eval(&inputs, &self.registry)
            .map(|v| v.re)
            .unwrap_or(f64::NAN)
    }

    /// Evaluates the formula for a batch of input vectors.
    pub fn eval_batch(&self, inputs_batch: &[Vec<f64>]) -> Vec<f64> {
        let values_batch: Vec<Vec<Value>> = inputs_batch
            .iter()
            .map(|row| row.iter().map(|&x| real(x)).collect())
            .collect();

        self.expression
            .eval_batch(&values_batch, &self.registry)
            .into_iter()
            .map(|v| v.map(|c| c.re).unwrap_or(f64::NAN))
            .collect()
    }

    /// Returns the residual error of the best formula found.
    pub fn error(&self) -> f64 {
        self.error
    }

    #[cfg(feature = "serde")]
    pub fn to_json(&self) -> String {
        serde_json::json!({
            "formula": self.formula(),
            "latex":   self.to_latex(),
            "python":  self.to_python(),
            "error":   self.error,
            "complexity": self.complexity(),
        })
        .to_string()
    }

    fn render<F>(&self, format_op: F) -> String
    where
        F: Fn(&OperatorRegistry, usize, &[&str]) -> String,
    {
        use crate::core::expression::Node;
        let mut stack: Vec<String> = Vec::with_capacity(self.expression.complexity());

        for node in &self.expression.nodes {
            match node {
                Node::Const { op_id, .. } => {
                    stack.push(format_op(&self.registry, *op_id, &[]));
                }
                Node::Num(val) => {
                    stack.push(format!("{:.4}", val));
                }
                Node::Var(i) => {
                    stack.push(format!("v_{{{i}}}"));
                }
                Node::Param { id, .. } => {
                    stack.push(format!("p_{{{id}}}"));
                }
                Node::Op { op_id, arity } => {
                    let arity = *arity as usize;
                    let start = stack.len().saturating_sub(arity);
                    let arg_strings: Vec<String> = stack.drain(start..).collect();
                    let arg_refs: Vec<&str> = arg_strings.iter().map(String::as_str).collect();
                    stack.push(format_op(&self.registry, *op_id, &arg_refs));
                }
            }
        }
        stack.pop().unwrap_or_default()
    }
}

impl std::fmt::Display for SearchResult {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{} (error={:.2e})", self.formula(), self.error)
    }
}

impl std::fmt::Debug for SearchResult {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("SearchResult")
            .field("formula", &self.formula())
            .field("error", &self.error)
            .field("complexity", &self.complexity())
            .finish()
    }
}
