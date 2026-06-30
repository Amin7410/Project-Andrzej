use crate::core::expression::{Expression, Node};
use crate::core::value::{real, Value};
use crate::ops::registry::OperatorRegistry;
use std::sync::Arc;

/// A structural template for numerical optimization of expression constants.
pub struct Template {
    pub expression: Expression,
    pub param_indices: Vec<usize>,
}

impl Template {
    /// Extracts parameter locations and initial values from an expression.
    pub fn from_expression(expr: &Expression) -> (Self, Vec<f64>) {
        let mut nodes = expr.nodes.clone();
        let mut param_indices = Vec::new();
        let mut initial_values = Vec::new();

        for (i, node) in nodes.iter_mut().enumerate() {
            if let Node::Param { initial_value, .. } = node {
                param_indices.push(i);
                initial_values.push(initial_value.re);
            }
        }

        (
            Self {
                expression: Expression::new(nodes, expr.var_count(), expr.param_count(), expr.display().to_string()),
                param_indices,
            },
            initial_values,
        )
    }
}

/// Refines numerical constants within an expression using a second-order optimization approach.
///
/// This function identifies fixed constants, treats them as floating-point parameters,
/// and applies a gradient-based refinement loop to minimize the residual error.
pub fn refine_constants(
    expr: &Expression,
    inputs: &[Vec<Value>],
    targets: &[f64],
    registry: &Arc<OperatorRegistry>,
    alpha: f64,
    l1_ratio: f64,
    max_iters: usize,
) -> (Expression, f64) {
    let (template, mut params) = Template::from_expression(expr);
    if params.is_empty() {
        return (expr.clone(), compute_error(expr, inputs, targets, registry, alpha, l1_ratio));
    }

    let mut lambda = 0.01;
    let mut best_error =
        compute_error_with_params(&template.expression, &params, inputs, targets, registry, alpha, l1_ratio);
    let mut consecutive_failures = 0;

    for _ in 0..max_iters {
        if lambda > 1e4 {
            break;
        }

        let (j, r) = compute_jacobian_and_residuals(
            &template.expression,
            &params,
            inputs,
            targets,
            registry,
        );

        let mut jtj_diag = vec![0.0; params.len()];
        let mut gradient = vec![0.0; params.len()];
        for i in 0..params.len() {
            for row in 0..targets.len() {
                jtj_diag[i] += j[row][i] * j[row][i];
                gradient[i] += j[row][i] * r[row];
            }
        }

        let mut next_params = params.clone();
        for i in 0..params.len() {
            next_params[i] -= gradient[i] / (jtj_diag[i] + lambda + 1e-6);
        }

        let next_error = compute_error_with_params(
            &template.expression,
            &next_params,
            inputs,
            targets,
            registry,
            alpha,
            l1_ratio,
        );
        if next_error < best_error {
            best_error = next_error;
            params = next_params;
            lambda /= 10.0;
            consecutive_failures = 0;
            if (best_error - next_error).abs() < 1e-9 {
                break;
            }
        } else {
            lambda *= 10.0;
            consecutive_failures += 1;
            if consecutive_failures >= 3 {
                break;
            }
        }
    }

    let mut final_nodes = template.expression.nodes.clone();
    for (i, &v) in params.iter().enumerate() {
        let node_idx = template.param_indices[i];
        if let Node::Param { id, .. } = final_nodes[node_idx] {
            // Keep it as a Param so it can be jointly optimized again at higher levels,
            // but update the initial_value to the best found so far.
            final_nodes[node_idx] = Node::Param { id, initial_value: real(v) };
        }
    }

    (
        Expression::new(final_nodes, expr.var_count(), expr.param_count(), expr.display().to_string()),
        best_error,
    )
}

fn compute_error(
    expr: &Expression,
    inputs: &[Vec<Value>],
    targets: &[f64],
    reg: &OperatorRegistry,
    alpha: f64,
    l1_ratio: f64,
) -> f64 {
    let mut total = 0.0;
    for (i, row) in inputs.iter().enumerate() {
        if let Some(val) = expr.eval(row, reg) {
            total += (val.re - targets[i]).powi(2);
        } else {
            return f64::INFINITY;
        }
    }
    let mse = total / inputs.len() as f64;

    let mut l1 = 0.0;
    let mut l2 = 0.0;
    for node in &expr.nodes {
        match node {
            Node::Num(val) => {
                l1 += val.abs();
                l2 += val * val;
            }
            Node::Param { initial_value, .. } => {
                l1 += initial_value.re.abs();
                l2 += initial_value.re * initial_value.re;
            }
            _ => {}
        }
    }
    let penalty = alpha * (l1_ratio * l1 + 0.5 * (1.0 - l1_ratio) * l2);
    mse + penalty
}

fn compute_error_with_params(
    expr: &Expression,
    params: &[f64],
    inputs: &[Vec<Value>],
    targets: &[f64],
    reg: &OperatorRegistry,
    alpha: f64,
    l1_ratio: f64,
) -> f64 {
    let param_values: Vec<Value> = params.iter().map(|&v| real(v)).collect();
    let mut total = 0.0;
    for (i, row) in inputs.iter().enumerate() {
        if let Some(val) = expr.eval_with_params(row, &param_values, reg) {
            total += (val.re - targets[i]).powi(2);
        } else {
            return f64::INFINITY;
        }
    }
    let mse = total / inputs.len() as f64;

    let mut l1 = 0.0;
    let mut l2 = 0.0;
    // When evaluating with params, the params array contains the current values
    for &p in params {
        l1 += p.abs();
        l2 += p * p;
    }
    // Also add any fixed Num nodes (if they exist)
    for node in &expr.nodes {
        if let Node::Num(val) = node {
            l1 += val.abs();
            l2 += val * val;
        }
    }
    let penalty = alpha * (l1_ratio * l1 + 0.5 * (1.0 - l1_ratio) * l2);
    mse + penalty
}

fn compute_jacobian_and_residuals(
    expr: &Expression,
    params: &[f64],
    inputs: &[Vec<Value>],
    targets: &[f64],
    reg: &OperatorRegistry,
) -> (Vec<Vec<f64>>, Vec<f64>) {
    let n = targets.len();
    let m = params.len();
    let epsilon = 1e-6;
    let mut jacobian = vec![vec![0.0; m]; n];
    let mut residuals = vec![0.0; n];

    let base_v: Vec<Value> = params.iter().map(|&v| real(v)).collect();

    for i in 0..n {
        let f0 = expr
            .eval_with_params(&inputs[i], &base_v, reg)
            .map(|v| v.re)
            .unwrap_or(0.0);
        residuals[i] = f0 - targets[i];

        for j in 0..m {
            let mut shifted_params = params.to_vec();
            shifted_params[j] += epsilon;
            let shifted_v: Vec<Value> = shifted_params.iter().map(|&v| real(v)).collect();
            let f1 = expr
                .eval_with_params(&inputs[i], &shifted_v, reg)
                .map(|v| v.re)
                .unwrap_or(0.0);
            jacobian[i][j] = (f1 - f0) / epsilon;
        }
    }

    (jacobian, residuals)
}
