use crate::core::value::Value;
use crate::ops::builtin;
use crate::ops::operator::{Operator, OperatorMeta};

/// Runtime catalogue of all operators available to the search engine.
pub struct OperatorRegistry {
    operators: Vec<Box<dyn Operator>>,
    meta: Vec<OperatorMeta>,
}

impl OperatorRegistry {
    pub fn new() -> Self {
        Self {
            operators: Vec::new(),
            meta: Vec::new(),
        }
    }

    /// Initialises a registry with the core EML operator set and standard constants.
    pub fn with_builtins() -> Self {
        let mut reg = Self::new();
        for op in builtin::seed_constants() {
            reg.register(op);
        }
        for op in builtin::all_builtins() {
            reg.register(op);
        }
        reg
    }

    /// Registers a new operator and returns its stable operational ID.
    pub fn register(&mut self, op: Box<dyn Operator>) -> usize {
        let id = self.operators.len();
        self.meta.push(OperatorMeta::from(op.as_ref()));
        self.operators.push(op);
        id
    }

    #[inline]
    pub fn get(&self, id: usize) -> &dyn Operator {
        self.operators[id].as_ref()
    }

    #[inline]
    pub fn eval(&self, id: usize, args: &[Value]) -> Option<Value> {
        self.operators[id].eval(args)
    }

    #[inline]
    pub fn meta(&self, id: usize) -> &OperatorMeta {
        &self.meta[id]
    }

    pub fn iter_meta(&self) -> impl Iterator<Item = (usize, &OperatorMeta)> {
        self.meta.iter().enumerate()
    }

    pub fn len(&self) -> usize {
        self.operators.len()
    }

    /// Filters operator IDs by their required argument count.
    pub fn ids_by_arity(&self, n: u8) -> Vec<usize> {
        self.meta
            .iter()
            .enumerate()
            .filter(|(_, m)| m.arity == n)
            .map(|(id, _)| id)
            .collect()
    }

    pub fn to_latex(&self, id: usize, args: &[&str]) -> String {
        self.operators[id].to_latex(args)
    }

    pub fn to_python(&self, id: usize, args: &[&str]) -> String {
        self.operators[id].to_python(args)
    }

    pub fn to_mathematica(&self, id: usize, args: &[&str]) -> String {
        self.operators[id].to_mathematica(args)
    }
}

impl Default for OperatorRegistry {
    fn default() -> Self {
        Self::with_builtins()
    }
}
