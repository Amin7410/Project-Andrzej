use crate::core::value::{self, Value};
use crate::ops::operator::Operator;

// MACROS
#[cfg(feature = "full-math")]
macro_rules! unary_op {
    ($Struct:ident, $name:expr, $fn:expr, $latex:expr, $python:expr, $mma:expr) => {
        #[derive(Debug)]
        pub struct $Struct;
        impl Operator for $Struct {
            fn name(&self) -> &str { $name }
            fn arity(&self) -> u8 { 1 }
            fn eval(&self, args: &[Value]) -> Option<Value> { ($fn)(args[0]) }
            fn to_latex(&self, args: &[&str]) -> String { format!($latex, args[0]) }
            fn to_python(&self, args: &[&str]) -> String { format!($python, args[0]) }
        }
    };
}

macro_rules! binary_op {
    ($Struct:ident, $name:expr, $commutative:expr, $fn:expr, $latex:expr, $python:expr) => {
        #[derive(Debug)]
        pub struct $Struct;
        impl Operator for $Struct {
            fn name(&self) -> &str { $name }
            fn arity(&self) -> u8 { 2 }
            fn is_commutative(&self) -> bool { $commutative }
            fn eval(&self, args: &[Value]) -> Option<Value> { ($fn)(args[0], args[1]) }
            fn to_latex(&self, args: &[&str]) -> String { format!($latex, args[0], args[1]) }
            fn to_python(&self, args: &[&str]) -> String { format!($python, args[0], args[1]) }
        }
    };
}

// CORE OPERATORS (Always Available)
#[derive(Debug)]
pub struct Eml;
impl Operator for Eml {
    fn name(&self) -> &str { "EML" }
    fn arity(&self) -> u8 { 2 }
    fn eval(&self, args: &[Value]) -> Option<Value> { value::c_eml(args[0], args[1]) }
    fn to_latex(&self, args: &[&str]) -> String { format!(r"e^{{{0}}} - \ln({1})", args[0], args[1]) }
    fn to_python(&self, args: &[&str]) -> String { format!("(np.exp({0}) - np.log({1}))", args[0], args[1]) }
}

#[derive(Debug)]
pub struct Neg;
impl Operator for Neg {
    fn name(&self) -> &str { "Neg" }
    fn arity(&self) -> u8 { 1 }
    fn eval(&self, args: &[Value]) -> Option<Value> { Some(-args[0]) }
    fn to_latex(&self, args: &[&str]) -> String { format!("(-{})", args[0]) }
    fn to_python(&self, args: &[&str]) -> String { format!("(-{})", args[0]) }
}

#[derive(Debug)]
pub struct Inv;
impl Operator for Inv {
    fn name(&self) -> &str { "Inv" }
    fn arity(&self) -> u8 { 1 }
    fn eval(&self, args: &[Value]) -> Option<Value> { value::c_div(value::real(1.0), args[0]) }
    fn to_latex(&self, args: &[&str]) -> String { format!(r"\frac{{1}}{{{}}}", args[0]) }
    fn to_python(&self, args: &[&str]) -> String { format!("(1/{})", args[0]) }
}

binary_op!(Plus,     "Plus",     true,  |a, b| Some(a + b),        "{0} + {1}", "({0})+({1})");
binary_op!(Times,    "Times",    true,  |a, b| Some(a * b),        "{0} \\cdot {1}", "({0})*({1})");
binary_op!(Subtract, "Subtract", false, |a, b| Some(a - b),        "{0} - {1}", "({0})-({1})");

#[derive(Debug)]
pub struct Divide;
impl Operator for Divide {
    fn name(&self) -> &str { "Divide" }
    fn arity(&self) -> u8 { 2 }
    fn eval(&self, args: &[Value]) -> Option<Value> { value::c_div(args[0], args[1]) }
    fn to_latex(&self, args: &[&str]) -> String { format!(r"\frac{{{}}}{{{}}}", args[0], args[1]) }
    fn to_python(&self, args: &[&str]) -> String { format!("({}/{})", args[0], args[1]) }
}

// EXTENDED MATHEMATICS (Toggleable via "full-math" feature)
#[cfg(feature = "full-math")]
unary_op!(Exp,    "Exp",    value::c_exp,   r"e^{{{0}}}",       "np.exp({0})",    "Exp[{0}]");
#[cfg(feature = "full-math")]
unary_op!(Log,    "Log",    value::c_ln,    r"\ln({0})",         "np.log({0})",    "Log[{0}]");
#[cfg(feature = "full-math")]
unary_op!(Sqrt,   "Sqrt",   value::c_sqrt,  r"\sqrt{{{0}}}",    "np.sqrt({0})",   "Sqrt[{0}]");
#[cfg(feature = "full-math")]
unary_op!(Sin,    "Sin",    value::c_sin,   r"\sin({0})",        "np.sin({0})",    "Sin[{0}]");
#[cfg(feature = "full-math")]
unary_op!(Cos,    "Cos",    value::c_cos,   r"\cos({0})",        "np.cos({0})",    "Cos[{0}]");
#[cfg(feature = "full-math")]
unary_op!(Tan,    "Tan",    value::c_tan,   r"\tan({0})",        "np.tan({0})",    "Tan[{0}]");
#[cfg(feature = "full-math")]
unary_op!(ArcSin, "ArcSin", value::c_asin,  r"\arcsin({0})",     "np.arcsin({0})",   "ArcSin[{0}]");
#[cfg(feature = "full-math")]
unary_op!(ArcCos, "ArcCos", value::c_acos,  r"\arccos({0})",     "np.arccos({0})",   "ArcCos[{0}]");
#[cfg(feature = "full-math")]
unary_op!(ArcTan, "ArcTan", value::c_atan,  r"\arctan({0})",     "np.arctan({0})",   "ArcTan[{0}]");


// CONSTANTS
#[derive(Debug)]
pub struct ConstOp {
    pub name: &'static str,
    pub value: Value,
    pub latex: &'static str,
    pub python: &'static str,
}

impl Operator for ConstOp {
    fn name(&self) -> &str { self.name }
    fn arity(&self) -> u8 { 0 }
    fn eval(&self, _args: &[Value]) -> Option<Value> { Some(self.value) }
    fn to_latex(&self, _args: &[&str]) -> String { self.latex.to_string() }
    fn to_python(&self, _args: &[&str]) -> String { self.python.to_string() }
}

pub fn seed_constants() -> Vec<Box<dyn Operator>> {
    use value::{real, unit_i};
    vec![
        Box::new(ConstOp { name: "0",  value: real(0.0),  latex: "0",       python: "0" }),
        Box::new(ConstOp { name: "1",  value: real(1.0),  latex: "1",       python: "1" }),
        Box::new(ConstOp { name: "I",  value: unit_i(),   latex: "i",       python: "1j" }),
    ]
}

pub fn all_builtins() -> Vec<Box<dyn Operator>> {
    #[allow(unused_mut)]
    let mut ops: Vec<Box<dyn Operator>> = vec![
        Box::new(Eml),
        Box::new(Neg),   Box::new(Inv),
        Box::new(Plus),  Box::new(Times), Box::new(Subtract), Box::new(Divide),
    ];

    #[cfg(feature = "full-math")]
    {
        ops.push(Box::new(Exp));    ops.push(Box::new(Log));    ops.push(Box::new(Sqrt));
        ops.push(Box::new(Sin));    ops.push(Box::new(Cos));    ops.push(Box::new(Tan));
        ops.push(Box::new(ArcSin)); ops.push(Box::new(ArcCos)); ops.push(Box::new(ArcTan));
    }

    ops
}
