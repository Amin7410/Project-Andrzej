use crate::core::value::Value;

/// Represents a single computational step in an RPN expression.
#[derive(Clone, Debug, PartialEq)]
pub enum Node {
    /// A fixed numerical constant.
    Const { value: Value, op_id: usize },
    /// A raw optimized numerical scalar.
    Num(f64),
    /// A reference to an input variable by index.
    Var(u8),
    /// A tunable parameter for numerical optimization.
    Param { id: u8, initial_value: Value },
    /// A functional operator with a specific arity.
    Op { op_id: usize, arity: u8 },
}

/// A linearised representation of a mathematical formula in Reverse Polish Notation.
#[derive(Clone, Debug)]
pub struct Expression {
    pub(crate) nodes: Vec<Node>,
    pub(crate) var_count: u8,
    pub(crate) complexity: usize,
    display: String,
}

impl Expression {
    /// Constructs a new expression from a sequence of nodes.
    pub fn new(nodes: Vec<Node>, var_count: u8, display: String) -> Self {
        let complexity = nodes.len();
        Self {
            nodes,
            var_count,
            complexity,
            display,
        }
    }

    /// Constructs a constant expression.
    pub fn constant(value: Value, op_id: usize, name: impl Into<String>) -> Self {
        Self::new(vec![Node::Const { value, op_id }], 0, name.into())
    }

    /// Constructs a variable reference expression.
    pub fn variable(index: u8, name: impl Into<String>) -> Self {
        Self::new(vec![Node::Var(index)], index + 1, name.into())
    }

    /// Evaluates the expression given a set of input values.
    pub fn eval(
        &self,
        inputs: &[Value],
        registry: &crate::ops::registry::OperatorRegistry,
    ) -> Option<Value> {
        let mut stack: Vec<Value> = Vec::with_capacity(self.complexity);
        self.eval_internal(inputs, &[], registry, &mut stack)
    }

    /// Evaluates the expression with explicit parameter overrides.
    pub fn eval_with_params(
        &self,
        inputs: &[Value],
        params: &[Value],
        registry: &crate::ops::registry::OperatorRegistry,
    ) -> Option<Value> {
        let mut stack: Vec<Value> = Vec::with_capacity(self.complexity);
        self.eval_internal(inputs, params, registry, &mut stack)
    }

    /// Evaluates the expression against a batch of input vectors.
    pub fn eval_batch(
        &self,
        inputs_batch: &[Vec<Value>],
        registry: &crate::ops::registry::OperatorRegistry,
    ) -> Vec<Option<Value>> {
        let mut stack: Vec<Value> = Vec::with_capacity(self.complexity);
        let mut results = Vec::with_capacity(inputs_batch.len());
        for inputs in inputs_batch {
            stack.clear();
            results.push(self.eval_internal(inputs, &[], registry, &mut stack));
        }
        results
    }

    pub(crate) fn eval_internal(
        &self,
        inputs: &[Value],
        params: &[Value],
        registry: &crate::ops::registry::OperatorRegistry,
        stack: &mut Vec<Value>,
    ) -> Option<Value> {
        for node in &self.nodes {
            match node {
                Node::Const { value, .. } => stack.push(*value),
                Node::Num(val) => stack.push(crate::core::value::real(*val)),
                Node::Var(i) => {
                    let v = inputs.get(*i as usize).copied()?;
                    stack.push(v);
                }
                Node::Param { id, initial_value } => {
                    let v = params.get(*id as usize).copied().unwrap_or(*initial_value);
                    stack.push(v);
                }
                Node::Op { op_id, arity } => {
                    let arity = *arity as usize;
                    if stack.len() < arity {
                        return None;
                    }
                    let start = stack.len() - arity;
                    let args: Vec<Value> = stack.drain(start..).collect();
                    let result = registry.eval(*op_id, &args)?;
                    if !crate::core::value::is_usable(result) {
                        return None;
                    }
                    stack.push(result);
                }
            }
        }
        if stack.len() == 1 {
            Some(stack[0])
        } else {
            None
        }
    }

    pub fn complexity(&self) -> usize {
        self.complexity
    }
    pub fn display(&self) -> &str {
        &self.display
    }
    pub fn var_count(&self) -> u8 {
        self.var_count
    }
}

impl std::fmt::Display for Expression {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.display)
    }
}
