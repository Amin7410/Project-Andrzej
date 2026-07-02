"""
Path B - Prototype 1: Numerically stable EML kernel (complex domain via (re, im) pairs).

Because `autograd` has incomplete support for complex dtypes, we represent every
complex number z = (zr, zi) as TWO real arrays. All operations stay real-valued, so
reverse-mode autodiff flows cleanly.

eml(x, y) = exp(x) - log(y), stabilized:
  - SOFT-CLAMP the real part of x with tanh before exp -> caps overflow while staying
    differentiable everywhere. This is the "soft eml" eml_tau; cap == tau, and
    cap -> inf recovers the exact eml (used for homotopy / annealing).
  - complex log: log(z) = 0.5*ln(zr^2 + zi^2) + i*atan2(zi, zr) -> log(negative) is
    well defined, no NaN.
"""
import autograd.numpy as np

def c_add(a, b):   return (a[0] + b[0], a[1] + b[1])
def c_sub(a, b):   return (a[0] - b[0], a[1] - b[1])
def c_scale(s, a): return (s * a[0], s * a[1])

def c_exp(a):
    """exp(zr + i zi) = e^zr (cos zi + i sin zi)."""
    m = np.exp(a[0])
    return (m * np.cos(a[1]), m * np.sin(a[1]))

def c_log(a, eps=1e-12):
    """log(z) = 0.5 ln(|z|^2) + i atan2(zi, zr). Defined even when zr < 0."""
    mag2 = a[0] * a[0] + a[1] * a[1] + eps
    return (0.5 * np.log(mag2), np.arctan2(a[1], a[0]))

def soft_clamp_re(a, cap):
    """Smoothly clamp the real part into (-cap, cap) via tanh; keep the imag part."""
    return (cap * np.tanh(a[0] / cap), a[1])

def eml_pair(x, y, cap=3.0):
    """x, y are (re, im) pairs. Returns eml(x, y) = exp(clamp(x)) - log(y) as a pair."""
    xs = soft_clamp_re(x, cap)
    return c_sub(c_exp(xs), c_log(y))

# Naive real-domain version, kept for contrast (this one overflows).
def eml_real_naive(x, y):
    return np.exp(x) - np.log(y)

def nested_chain_pair(v0, w, depth, cap=3.0):
    val = v0
    for _ in range(depth):
        val = eml_pair(val, w, cap=cap)
    return val

if __name__ == "__main__":
    print("=" * 64)
    print("(A) Deep nested chain: naive real  vs  stable complex")
    print("=" * 64)
    print(f"{'depth':>6} | {'real-naive':>16} | {'complex-stable |.|':>20}")
    w = (1.7, 0.0)
    for d in range(1, 13):
        try:
            val = 1.5
            for _ in range(d):
                val = eml_real_naive(val, 1.7)
            r = val
        except Exception:
            r = float('nan')
        cr, ci = nested_chain_pair((1.5, 0.0), w, d)
        mag = np.sqrt(cr * cr + ci * ci)
        r_str = f"{r:.3e}" if np.isfinite(r) else "  inf/NaN (overflow)"
        print(f"{d:>6} | {r_str:>16} | {mag:>20.4f}")

    print()
    print("=" * 64)
    print("(C) log(negative) in the complex domain (pair form)")
    print("=" * 64)
    e = eml_pair((0.0, 0.0), (-2.0, 0.0))
    print(f"eml_pair(0, -2) = {e[0]:.4f} + {e[1]:.4f}i   (log(-2) = 0.693 + i*pi)")
