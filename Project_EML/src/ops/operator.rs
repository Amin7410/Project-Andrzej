use crate::core::value::Value;

/// Abstract interface for mathematical operators (functions and constants).
pub trait Operator: Send + Sync + std::fmt::Debug {
    /// Canonical identifier for the operator.
    fn name(&self) -> &str;

    /// Number of operational arguments (0, 1, 2, or 3).
    fn arity(&self) -> u8;

    /// Mathematical commutativity property: f(a, b) = f(b, a).
    fn is_commutative(&self) -> bool {
        false
    }

    /// Primary evaluation bridge between search engine and operator logic.
    fn eval(&self, args: &[Value]) -> Option<Value>;

    /// LaTeX representation logic.
    fn to_latex(&self, args: &[&str]) -> String;

    /// Python runtime representation (e.g. math.sin, numpy.exp).
    fn to_python(&self, args: &[&str]) -> String;

    /// Wolfram Language representation.
    fn to_mathematica(&self, args: &[&str]) -> String {
        if args.is_empty() {
            return self.name().to_string();
        }
        format!("{}[{}]", self.name(), args.join(", "))
    }
}

/// Lightweight descriptor of an operator's signature.
pub struct OperatorMeta {
    pub name: String,
    pub arity: u8,
    pub is_commutative: bool,
}

impl OperatorMeta {
    pub fn from(op: &dyn Operator) -> Self {
        Self {
            name: op.name().to_string(),
            arity: op.arity(),
            is_commutative: op.is_commutative(),
        }
    }
}
