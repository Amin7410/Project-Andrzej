use pyo3::prelude::*;
use pyo3::create_exception;
use pyo3::exceptions::{PyValueError, PyException};
use numpy::{PyArray1, PyReadonlyArray1, PyReadonlyArray2, PyArrayMethods};
use crate::{Searcher as RustSearcher, SearchConfig, SearchResult as RustSearchResult};

create_exception!(eml_sr, EmlDimensionError, PyException);
create_exception!(eml_sr, EmlComplexityError, PyException);
create_exception!(eml_sr, EmlRuntimeError, PyException);

fn map_error(e: crate::EmlError) -> PyErr {
    match e {
        crate::EmlError::InvalidInput { reason } => EmlDimensionError::new_err(reason),
        crate::EmlError::NotFound { max_complexity } => {
            EmlComplexityError::new_err(format!("No formula found up to complexity {}", max_complexity))
        }
        crate::EmlError::OutOfMemory { used_mb, limit_mb } => {
            EmlComplexityError::new_err(format!("Memory limit exceeded: {}MB > {}MB", used_mb, limit_mb))
        }
        crate::EmlError::ArityMismatch { name, expected, got } => {
            EmlRuntimeError::new_err(format!("Operator {} expects {} args, got {}", name, expected, got))
        }
    }
}

/// A high-performance symbolic regression result.
#[pyclass(name = "SearchResult")]
pub struct PySearchResult {
    inner: RustSearchResult,
}

#[pymethods]
impl PySearchResult {
    /// The discovered mathematical formula as a string.
    #[getter]
    fn formula(&self) -> String {
        self.inner.formula().to_string()
    }

    /// The residual error (Mean Squared Error) of the formula.
    #[getter]
    fn error(&self) -> f64 {
        self.inner.error()
    }

    /// The structural complexity of the formula.
    #[getter]
    fn complexity(&self) -> usize {
        self.inner.complexity()
    }

    /// Returns the formula in LaTeX format for academic reporting.
    fn to_latex(&self) -> String {
        self.inner.to_latex()
    }

    /// Returns the formula in Python/NumPy format for immediate use.
    fn to_python(&self) -> String {
        self.inner.to_python()
    }

    /// Evaluates the discovered formula for a given input (float or list/array).
    fn eval(&self, x: Bound<'_, PyAny>) -> PyResult<PyObject> {
        let py = x.py();
        if let Ok(val) = x.extract::<f64>() {
            Ok(self.inner.eval(val).into_py(py))
        } else if let Ok(vec) = convert_to_vec(x) {
            Ok(self.inner.eval_multi(&vec).into_py(py))
        } else {
            Err(PyValueError::new_err("Input must be a float or a 1D list/array"))
        }
    }

    /// Evaluates the formula for a batch of inputs (list of lists or 2D array).
    fn eval_batch(&self, inputs: Bound<'_, PyAny>) -> PyResult<PyObject> {
        let py = inputs.py();
        let matrix = convert_to_matrix(inputs)?;
        let results = self.inner.eval_batch(&matrix);
        Ok(results.into_py(py))
    }

    /// Alias for eval_batch (Scikit-Learn style).
    fn predict(&self, inputs: Bound<'_, PyAny>) -> PyResult<PyObject> {
        self.eval_batch(inputs)
    }

    fn __repr__(&self) -> String {
        format!(
            "SearchResult(formula='{}', error={:.6e}, complexity={})",
            self.inner.formula(),
            self.inner.error(),
            self.inner.complexity()
        )
    }
}

/// The core EML-SR search engine exposed to Python.
#[pyclass(name = "Searcher")]
pub struct PySearcher {
    inner: RustSearcher,
}

#[pymethods]
impl PySearcher {
    #[new]
    #[pyo3(signature = (max_complexity=10, complexity_penalty=0.1))]
    fn new(max_complexity: usize, complexity_penalty: f64) -> Self {
        let mut config = SearchConfig::default();
        config.max_complexity = max_complexity;
        config.complexity_penalty = complexity_penalty;
        Self {
            inner: RustSearcher::new(config),
        }
    }

    /// Finds a univariate function f(x) ≈ y.
    /// Supports both Python lists and NumPy arrays.
    #[pyo3(signature = (xs, ys))]
    fn find_function(&self, xs: Bound<'_, PyAny>, ys: Bound<'_, PyAny>) -> PyResult<PySearchResult> {
        let x_vec: Vec<f64> = convert_to_vec(xs)?;
        let y_vec: Vec<f64> = convert_to_vec(ys)?;

        self.inner
            .find_function(&x_vec, &y_vec)
            .map(|inner| PySearchResult { inner })
            .map_err(map_error)
    }

    /// Finds a multivariate function f(x0, x1, ...) ≈ y.
    /// Inputs should be a 2D array-like structure.
    #[pyo3(signature = (inputs, ys))]
    fn find_multivariate(&self, inputs: Bound<'_, PyAny>, ys: Bound<'_, PyAny>) -> PyResult<PySearchResult> {
        let input_matrix: Vec<Vec<f64>> = convert_to_matrix(inputs)?;
        let y_vec: Vec<f64> = convert_to_vec(ys)?;

        self.inner
            .find_multivariate(&input_matrix, &y_vec)
            .map(|inner| PySearchResult { inner })
            .map_err(map_error)
    }

    /// Alias for find_multivariate (Scikit-Learn style).
    #[pyo3(signature = (inputs, ys))]
    fn fit(&self, inputs: Bound<'_, PyAny>, ys: Bound<'_, PyAny>) -> PyResult<PySearchResult> {
        self.find_multivariate(inputs, ys)
    }

    /// Returns the Pareto-front of all candidate formulas found.
    #[pyo3(signature = (inputs, ys))]
    fn find_candidates(&self, inputs: Bound<'_, PyAny>, ys: Bound<'_, PyAny>) -> PyResult<Vec<PySearchResult>> {
        let input_matrix: Vec<Vec<f64>> = convert_to_matrix(inputs)?;
        let y_vec: Vec<f64> = convert_to_vec(ys)?;

        self.inner
            .find_candidates(&input_matrix, &y_vec)
            .map(|results| {
                results
                    .into_iter()
                    .map(|inner| PySearchResult { inner })
                    .collect()
            })
            .map_err(map_error)
    }

    /// Identifies a closed-form expression for a scalar constant.
    fn recognize_constant(&self, value: f64) -> PyResult<PySearchResult> {
        self.inner
            .recognize_constant(value)
            .map(|inner| PySearchResult { inner })
            .map_err(map_error)
    }
}

/// Helper to convert a Python object (List or NumPy array) to Vec<f64>.
fn convert_to_vec(obj: Bound<'_, PyAny>) -> PyResult<Vec<f64>> {
    if let Ok(array) = obj.extract::<PyReadonlyArray1<f64>>() {
        Ok(array.to_vec()?)
    } else if let Ok(list) = obj.extract::<Vec<f64>>() {
        Ok(list)
    } else {
        Err(PyValueError::new_err("Input must be a 1D list or NumPy array of floats"))
    }
}

/// Helper to convert a Python object (2D List or 2D NumPy array) to Vec<Vec<f64>>.
fn convert_to_matrix(obj: Bound<'_, PyAny>) -> PyResult<Vec<Vec<f64>>> {
    if let Ok(array) = obj.extract::<PyReadonlyArray2<f64>>() {
        let mut matrix = Vec::new();
        for row in array.as_array().rows() {
            matrix.push(row.to_vec());
        }
        Ok(matrix)
    } else if let Ok(list) = obj.extract::<Vec<Vec<f64>>>() {
        Ok(list)
    } else {
        Err(PyValueError::new_err("Input must be a 2D list or 2D NumPy array of floats"))
    }
}

/// The main Python module entry point.
#[pymodule]
fn eml_sr(py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PySearcher>()?;
    m.add_class::<PySearchResult>()?;
    
    // Register custom exceptions
    m.add("EmlDimensionError", py.get_type::<EmlDimensionError>())?;
    m.add("EmlComplexityError", py.get_type::<EmlComplexityError>())?;
    m.add("EmlRuntimeError", py.get_type::<EmlRuntimeError>())?;
    
    Ok(())
}
