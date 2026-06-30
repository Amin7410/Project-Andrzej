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

    // Seed abstract parameter Param(C)
    let expr = Expression::parameter();
    if let Some(fp) = fingerprint(&expr, &registry) {
        if seen.insert(fp, ()).is_none() {
            score_and_update(&expr, &data_inputs, &targets, config, &front, &registry);
            levels[1].push(expr);
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
        return finalize_result(front, registry, config, &data_inputs, &targets);
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
                        child.param_count(),
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
                            let mut right_nodes = right.nodes.clone();
                            for node in &mut right_nodes {
                                if let Node::Param { id, .. } = node {
                                    *id += left.param_count();
                                }
                            }
                            nodes.extend_from_slice(&right_nodes);
                            nodes.push(Node::Op {
                                op_id: bid,
                                arity: 2,
                            });
                            let expr = Expression::new(
                                nodes,
                                left.var_count().max(right.var_count()),
                                left.param_count() + right.param_count(),
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

        let total_candidates = all_candidates.len();
        let counter = std::sync::atomic::AtomicUsize::new(0);
        let last_logged_percent = std::sync::atomic::AtomicUsize::new(0);
        let start_instant = std::time::Instant::now();

        let scored_candidates: Vec<(Expression, f64)> = all_candidates
            .into_par_iter()
            .filter_map(|mut expr| {
                if total_candidates > 0 {
                    let current_count = counter.fetch_add(1, std::sync::atomic::Ordering::Relaxed) + 1;
                    let current_percent = (current_count * 100) / total_candidates;
                    
                    let mut logged = last_logged_percent.load(std::sync::atomic::Ordering::Relaxed);
                    while current_percent > logged && logged < 100 {
                        if last_logged_percent.compare_exchange_weak(
                            logged,
                            current_percent,
                            std::sync::atomic::Ordering::Relaxed,
                            std::sync::atomic::Ordering::Relaxed,
                        ).is_ok() {
                            let elapsed = start_instant.elapsed().as_secs_f64();
                            let est_total = (elapsed * 100.0) / (current_percent as f64);
                            let est_remaining = est_total - elapsed;
                            
                            let filled = (current_percent / 10) as usize;
                            let mut bar = String::with_capacity(10);
                            for _ in 0..filled { bar.push('█'); }
                            for _ in filled..10 { bar.push('░'); }
                            
                            print!(
                                "\r  [EML] L{} Progress: [{}] {}% ({}/{}) | {:.1}s (Est: {:.1}s)   ",
                                k,
                                bar,
                                current_percent,
                                current_count,
                                total_candidates,
                                elapsed,
                                est_remaining
                            );
                            use std::io::Write;
                            let _ = std::io::stdout().flush();
                            break;
                        }
                        logged = last_logged_percent.load(std::sync::atomic::Ordering::Relaxed);
                    }
                }

                let mut error = compute_raw_error(&expr, &data_inputs, &targets, &reg, config.alpha, config.l1_ratio);

                // For search steps, run light parameter optimization (e.g. 10 iterations)
                if config.optimize_constants && expr.param_count() > 0 {
                    let (refined_expr, refined_error) =
                        optimizer::refine_constants(&expr, &data_inputs, &targets, &reg, config.alpha, config.l1_ratio, 10);
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

        if total_candidates > 0 {
            println!();
        }

        for (expr, error_with_penalty) in &scored_candidates {
            let raw_error =
                *error_with_penalty / (1.0 + expr.complexity() as f64 * config.complexity_penalty);
            update_pareto(&front, expr, raw_error);
        }

        let mut final_next = scored_candidates;
        final_next.sort_unstable_by(|a, b| a.1.partial_cmp(&b.1).unwrap());
        
        let beam_size = config.beam_width;
        if final_next.len() > beam_size {
            let q_count = (beam_size as f64 * 0.8) as usize;
            let d_count = beam_size - q_count;
            
            let mut selected = Vec::with_capacity(beam_size);
            for i in 0..q_count {
                selected.push(final_next[i].clone());
            }
            
            let get_sig = |expr: &Expression| -> String {
                let sig: Vec<String> = expr.nodes.iter()
                    .filter_map(|n| match n {
                        Node::Op { op_id, .. } => Some(format!("{}", op_id)),
                        _ => None
                    })
                    .collect();
                sig.join("-")
            };

            let mut root_freq = std::collections::HashMap::new();
            for (expr, _) in &selected {
                let sig = get_sig(expr);
                *root_freq.entry(sig).or_insert(0) += 1;
            }
            
            let mut remaining: Vec<_> = final_next.into_iter().skip(q_count).collect();
            remaining.sort_by(|a, b| {
                let sig_a = get_sig(&a.0);
                let sig_b = get_sig(&b.0);
                let freq_a = root_freq.get(&sig_a).cloned().unwrap_or(0);
                let freq_b = root_freq.get(&sig_b).cloned().unwrap_or(0);
                
                freq_a.cmp(&freq_b).then_with(|| a.1.partial_cmp(&b.1).unwrap())
            });
            
            for i in 0..d_count.min(remaining.len()) {
                selected.push(remaining[i].clone());
            }
            
            final_next = selected;
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

    finalize_result(front, registry, config, &data_inputs, &targets)
}

fn compute_raw_error(
    expr: &Expression,
    inputs: &[Vec<Value>],
    targets: &[f64],
    reg: &OperatorRegistry,
    alpha: f64,
    l1_ratio: f64,
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
    config: &SearchConfig,
    front: &Mutex<BTreeMap<usize, (f64, Expression)>>,
    reg: &OperatorRegistry,
) {
    let error = compute_raw_error(expr, inputs, targets, reg, config.alpha, config.l1_ratio);
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
    inputs: &[Vec<Value>],
    targets: &[f64],
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
        let mut final_expr = expr.clone();
        let mut final_error = *error;

        // Perform final deep parameter optimization (e.g. 30 iterations) for accuracy
        if config.optimize_constants && final_expr.param_count() > 0 {
            let (refined, err) = optimizer::refine_constants(&final_expr, inputs, targets, &reg, config.alpha, config.l1_ratio, 30);
            final_expr = refined;
            final_error = err;
        }

        // Strict Pareto dominance: only keep if strictly better than all simpler ones
        if final_error < current_best_error {
            results.push(SearchResult::new(final_expr, final_error, Arc::clone(&reg)));
            current_best_error = final_error;
        }
    }
    
    // Reverse to put the absolute best (lowest error, highest complexity) at index 0
    results.reverse();
    Ok(results)
}
