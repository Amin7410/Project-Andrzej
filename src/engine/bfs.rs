use crate::config::SearchConfig;
use crate::core::expression::{Expression, Node};
use crate::core::signature::{fingerprint, Fingerprint};
use crate::core::value::{is_usable, real, Value};
use crate::engine::optimizer;
use crate::error::EmlError;
use crate::ops::registry::OperatorRegistry;
use crate::result::SearchResult;
use dashmap::DashMap;
use rayon::prelude::*;
use std::collections::BTreeMap;
use std::sync::{Arc, Mutex};

/// Executes a parallel Breadth-First Search (BFS) for symbolic regression.
///
/// This engine explores the space of mathematical expressions by increasing
/// complexity. It utilizes:
/// - **Fingerprinting**: For algebraic deduplication.
/// - **Beam Search**: To prune the search space by retaining only high-fitness candidates.
/// - **Thread-Parallelism**: Scales across all available CPU cores via Rayon.
/// - **Constant Optimization**: Refines free parameters using numerical gradients.
pub fn run_bfs(
    inputs: &[Vec<f64>],
    ys: &[f64],
    config: &SearchConfig,
) -> Result<Vec<SearchResult>, EmlError> {
    if inputs.is_empty() || ys.is_empty() || inputs.len() != ys.len() {
        return Err(EmlError::invalid(
            "Inputs and target vector must be non-empty and equal length.",
        ));
    }

    let num_vars = inputs[0].len();
    let registry = Arc::new(OperatorRegistry::with_builtins());

    let data_inputs: Vec<Vec<Value>> = inputs
        .iter()
        .map(|row| row.iter().map(|&v| real(v)).collect())
        .collect();
    let targets: Vec<f64> = ys.to_vec();

    let seen: Arc<DashMap<Fingerprint, ()>> = Arc::new(DashMap::new());
    let front: Arc<Mutex<BTreeMap<usize, (f64, Expression)>>> = Arc::new(Mutex::new(BTreeMap::new()));

    let mut levels: Vec<Vec<Expression>> = vec![Vec::new(); config.max_complexity + 1];

    for id in registry.ids_by_arity(0) {
        let meta = registry.meta(id);
        let val = registry.eval(id, &[]).unwrap();
        let expr = Expression::new(
            vec![Node::Const {
                value: val,
                op_id: id,
            }],
            0,
            meta.name.clone(),
        );
        if let Some(fp) = fingerprint(&expr, &registry) {
            if seen.insert(fp, ()).is_none() {
                score_and_update(&expr, &data_inputs, &targets, config, &front, &registry);
                levels[1].push(expr);
            }
        }
    }

    for i in 0..num_vars {
        let expr = Expression::variable(i as u8, format!("v_{{{i}}}"));
        if let Some(fp) = fingerprint(&expr, &registry) {
            if seen.insert(fp, ()).is_none() {
                score_and_update(&expr, &data_inputs, &targets, config, &front, &registry);
                levels[1].push(expr);
            }
        }
    }

    if check_early_exit(&front, config) {
        return finalize_result(front, registry, config);
    }

    println!(
        "[EML-SR] Started search space exploration. Level 1 seeded with {} primary nodes.",
        levels[1].len()
    );

    for k in 2..=config.max_complexity {
        let t_level = std::time::Instant::now();
        let unary_ids = registry.ids_by_arity(1);
        let reg = Arc::clone(&registry);
        let seen_ref = Arc::clone(&seen);

        let new_unary: Vec<Expression> = levels[k - 1]
            .par_iter()
            .flat_map(|child| {
                let mut local = Vec::new();
                for &uid in &unary_ids {
                    let mut nodes = child.nodes.clone();
                    nodes.push(Node::Op {
                        op_id: uid,
                        arity: 1,
                    });
                    let expr = Expression::new(
                        nodes,
                        child.var_count(),
                        format!("{}({})", reg.meta(uid).name, child.display()),
                    );
                    if let Some(fp) = fingerprint(&expr, &reg) {
                        if seen_ref.insert(fp, ()).is_none() {
                            local.push(expr);
                        }
                    }
                }
                local
            })
            .collect();

        let binary_ids = registry.ids_by_arity(2);
        let mut binary_candidates = Vec::new();
        for lk in 1..k - 1 {
            let rk = k - 1 - lk;
            let reg_bin = Arc::clone(&registry);
            let seen_bin = Arc::clone(&seen);

            let new_binary: Vec<Expression> = levels[lk]
                .par_iter()
                .flat_map(|left| {
                    let mut local = Vec::new();
                    for right in &levels[rk] {
                        for &bid in &binary_ids {
                            let meta = reg_bin.meta(bid);
                            if meta.is_commutative && lk == rk && left.display() > right.display() {
                                continue;
                            }
                            let mut nodes = left.nodes.clone();
                            nodes.extend_from_slice(&right.nodes);
                            nodes.push(Node::Op {
                                op_id: bid,
                                arity: 2,
                            });
                            let expr = Expression::new(
                                nodes,
                                left.var_count().max(right.var_count()),
                                format!("{}({}, {})", meta.name, left.display(), right.display()),
                            );
                            if let Some(fp) = fingerprint(&expr, &reg_bin) {
                                if seen_bin.insert(fp, ()).is_none() {
                                    local.push(expr);
                                }
                            }
                        }
                    }
                    local
                })
                .collect();
            binary_candidates.extend(new_binary);
        }

        let mut all_candidates = new_unary;
        all_candidates.extend(binary_candidates);

        let scored_candidates: Vec<(Expression, f64)> = all_candidates
            .into_par_iter()
            .filter_map(|mut expr| {
                let mut error = compute_raw_error(&expr, &data_inputs, &targets, &reg);

                // Tighten optimization threshold to save CPU cycles (only optimize if very promising < 2.0)
                if config.optimize_constants && error.is_finite() && error < 2.0 {
                    let (refined_expr, refined_error) =
                        optimizer::refine_constants(&expr, &data_inputs, &targets, &reg);
                    if refined_error < error {
                        expr = refined_expr;
                        error = refined_error;
                    }
                }

                if error.is_finite() {
                    let score =
                        error * (1.0 + expr.complexity() as f64 * config.complexity_penalty);
                    Some((expr, score))
                } else {
                    None
                }
            })
            .collect();

        for (expr, error_with_penalty) in &scored_candidates {
            let raw_error =
                *error_with_penalty / (1.0 + expr.complexity() as f64 * config.complexity_penalty);
            update_pareto(&front, expr, raw_error);
        }

        let mut final_next = scored_candidates;
        final_next.sort_unstable_by(|a, b| a.1.partial_cmp(&b.1).unwrap());
        if final_next.len() > config.beam_width {
            final_next.truncate(config.beam_width);
        }

        levels[k] = final_next.into_iter().map(|(e, _)| e).collect();
        println!(
            "[EML-SR]   -> Level {} processed in {:?}. Retaining top {} candidates.",
            k,
            t_level.elapsed(),
            levels[k].len()
        );

        if check_early_exit(&front, config) {
            break;
        }
    }

    finalize_result(front, registry, config)
}

fn compute_raw_error(
    expr: &Expression,
    inputs: &[Vec<Value>],
    targets: &[f64],
    reg: &OperatorRegistry,
) -> f64 {
    let mut predicted = Vec::with_capacity(inputs.len());
    for row in inputs {
        if let Some(v) = expr.eval(row, reg) {
            if is_usable(v) {
                predicted.push(v.re);
                continue;
            }
        }
        return f64::INFINITY;
    }
    let mse: f64 = predicted
        .iter()
        .zip(targets)
        .map(|(p, a)| (p - a).powi(2))
        .sum::<f64>()
        / targets.len() as f64;
    mse.sqrt()
}

fn update_pareto(front: &Mutex<BTreeMap<usize, (f64, Expression)>>, expr: &Expression, error: f64) {
    let mut guard = front.lock().unwrap();
    let comp = expr.complexity();
    
    let should_insert = match guard.get(&comp) {
        None => true,
        Some((prev_error, _)) => error < *prev_error,
    };
    
    if should_insert {
        guard.insert(comp, (error, expr.clone()));
    }
}

fn score_and_update(
    expr: &Expression,
    inputs: &[Vec<Value>],
    targets: &[f64],
    _config: &SearchConfig,
    front: &Mutex<BTreeMap<usize, (f64, Expression)>>,
    reg: &OperatorRegistry,
) {
    let error = compute_raw_error(expr, inputs, targets, reg);
    if error.is_finite() {
        update_pareto(front, expr, error);
    }
}

fn check_early_exit(front: &Mutex<BTreeMap<usize, (f64, Expression)>>, config: &SearchConfig) -> bool {
    if config.allow_approximate {
        return false;
    }
    let guard = front.lock().unwrap();
    for (error, _) in guard.values() {
        if *error <= config.precision_goal {
            return true;
        }
    }
    false
}

fn finalize_result(
    front: Arc<Mutex<BTreeMap<usize, (f64, Expression)>>>,
    reg: Arc<OperatorRegistry>,
    config: &SearchConfig,
) -> Result<Vec<SearchResult>, EmlError> {
    let guard = front.lock().unwrap();
    if guard.is_empty() {
        return Err(EmlError::NotFound {
            max_complexity: config.max_complexity,
        });
    }

    let mut results = Vec::new();
    let mut current_best_error = f64::INFINITY;
    
    for (&_comp, (error, expr)) in guard.iter() {
        // Strict Pareto dominance: only keep if strictly better than all simpler ones
        if *error < current_best_error {
            results.push(SearchResult::new(expr.clone(), *error, Arc::clone(&reg)));
            current_best_error = *error;
        }
    }
    
    // Reverse to put the absolute best (lowest error, highest complexity) at index 0
    results.reverse();
    Ok(results)
}
