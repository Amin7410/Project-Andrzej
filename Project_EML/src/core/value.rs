use num_complex::Complex64;

/// The primary numeric type for the EML search engine.
///
/// We use complex numbers (ℂ) to facilitate the discovery of trigonometric and
/// inverse functional relations through Euler's formula and complex analytic
/// continuations of the EML operator.
pub type Value = Complex64;

/// Constructs a real-valued constant.
#[inline]
pub fn real(x: f64) -> Value {
    Value::new(x, 0.0)
}

/// Constructs a purely imaginary constant.
#[inline]
pub fn imag(y: f64) -> Value {
    Value::new(0.0, y)
}

/// Returns the imaginary unit `i`.
#[inline]
pub fn unit_i() -> Value {
    Value::new(0.0, 1.0)
}

/// Validates whether a result is numerically stable and usable.
#[inline]
pub fn is_usable(v: Value) -> bool {
    v.re.is_finite() && v.im.is_finite() && v.re.abs() < 1e15 && v.im.abs() < 1e15
}

const QUANTISE_SCALE: f64 = 1e10;

/// Maps a complex value to a discrete integer pair for fingerprinting.
#[inline]
pub fn quantise(v: Value) -> (i64, i64) {
    (
        (v.re * QUANTISE_SCALE).round() as i64,
        (v.im * QUANTISE_SCALE).round() as i64,
    )
}

#[inline]
pub fn c_exp(z: Value) -> Option<Value> {
    Some(z.exp())
}

#[inline]
pub fn c_ln(z: Value) -> Option<Value> {
    if z.norm() == 0.0 {
        return None;
    }
    Some(z.ln())
}

#[inline]
pub fn c_eml(x: Value, y: Value) -> Option<Value> {
    Some(x.exp() - c_ln(y)?)
}

#[inline]
pub fn c_div(z: Value, w: Value) -> Option<Value> {
    if w.norm() == 0.0 {
        return None;
    }
    Some(z / w)
}

#[inline]
pub fn c_pow(z: Value, w: Value) -> Option<Value> {
    if z.norm() == 0.0 {
        if w.re > 0.0 && w.im == 0.0 {
            return Some(real(0.0));
        }
        if w.re == 0.0 && w.im == 0.0 {
            return Some(real(1.0));
        }
        return None;
    }
    Some((w * z.ln()).exp())
}

#[inline]
pub fn c_sqrt(z: Value) -> Option<Value> {
    Some(z.sqrt())
}

#[inline]
pub fn c_sin(z: Value) -> Option<Value> {
    Some(z.sin())
}

#[inline]
pub fn c_cos(z: Value) -> Option<Value> {
    Some(z.cos())
}

#[inline]
pub fn c_tan(z: Value) -> Option<Value> {
    let cos = z.cos();
    if cos.norm() == 0.0 {
        return None;
    }
    Some(z.sin() / cos)
}

#[inline]
pub fn c_sinh(z: Value) -> Option<Value> {
    Some(z.sinh())
}

#[inline]
pub fn c_cosh(z: Value) -> Option<Value> {
    Some(z.cosh())
}

#[inline]
pub fn c_tanh(z: Value) -> Option<Value> {
    let cosh = z.cosh();
    if cosh.norm() == 0.0 {
        return None;
    }
    Some(z.sinh() / cosh)
}

#[inline]
pub fn c_asin(z: Value) -> Option<Value> {
    let i = unit_i();
    let one = real(1.0);
    let iz = i * z;
    let inside = (one - z * z).sqrt();
    c_ln(iz + inside).map(|ln| -i * ln)
}

#[inline]
pub fn c_acos(z: Value) -> Option<Value> {
    use std::f64::consts::FRAC_PI_2;
    Some(real(FRAC_PI_2) - c_asin(z)?)
}

#[inline]
pub fn c_atan(z: Value) -> Option<Value> {
    let i = unit_i();
    let one = real(1.0);
    let l1 = c_ln(one - i * z)?;
    let l2 = c_ln(one + i * z)?;
    Some(Value::new(0.0, 0.5) * (l1 - l2))
}

#[inline]
pub fn c_asinh(z: Value) -> Option<Value> {
    c_ln(z + (z * z + real(1.0)).sqrt())
}

#[inline]
pub fn c_acosh(z: Value) -> Option<Value> {
    c_ln(z + (z + real(1.0)).sqrt() * (z - real(1.0)).sqrt())
}

#[inline]
pub fn c_atanh(z: Value) -> Option<Value> {
    let one = real(1.0);
    let l1 = c_ln(one + z)?;
    let l2 = c_ln(one - z)?;
    Some(real(0.5) * (l1 - l2))
}
