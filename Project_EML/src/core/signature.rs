use crate::core::value::{quantise, real, Value};
use num_complex::Complex64;

const GLAISHER: f64 = 1.282_427_129_100_622_6;
const EULER_GAMMA: f64 = 0.577_215_664_901_532_9;

/// Quantised output vector used for expression deduplication.
pub type Fingerprint = Vec<(i64, i64)>;

static BASE_PROBES: &[f64] = &[
    EULER_GAMMA,
    GLAISHER,
    1.618_033_988_749_895,
    std::f64::consts::LN_2,
    1.202_056_903_159_594,
];

/// Generates a numerical fingerprint for an expression using complex probe points.
///
/// This mechanism allows the engine to identify mathematically equivalent
/// expressions (e.g., commutativity, identities) by comparing their outputs
/// at a set of algebraically independent coordinates.
pub fn fingerprint(
    expr: &crate::core::expression::Expression,
    registry: &crate::ops::registry::OperatorRegistry,
) -> Option<Fingerprint> {
    let var_count = expr.var_count() as usize;
    let num_probes = 5;
    let mut fp = Vec::with_capacity(num_probes);

    for p in 0..num_probes {
        let mut probe = Vec::with_capacity(var_count);
        for i in 0..var_count {
            let val = BASE_PROBES[(p + i) % BASE_PROBES.len()];
            if p % 2 == 1 {
                probe.push(Complex64::new(val, 0.1 * (i + 1) as f64));
            } else {
                probe.push(real(val));
            }
        }

        let v = expr.eval(&probe, registry)?;
        if !crate::core::value::is_usable(v) {
            return None;
        }
        fp.push(quantise(v));
    }

    Some(fp)
}
