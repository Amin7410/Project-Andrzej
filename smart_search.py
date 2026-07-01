import eml_sr
import numpy as np

class SmartSearchResult:
    def __init__(self, inner, strategy, X, y, complexity_offset=0):
        self._inner = inner
        self._strategy = strategy
        self._complexity_offset = complexity_offset
        self._complexity = inner.complexity + complexity_offset
        # Calculate actual predictions and error in original y-space
        self._error = self._calculate_error(X, y)

    def _calculate_error(self, X, y):
        if len(X) == 0 or len(y) == 0:
            return self._inner.error
        try:
            preds = self.eval_batch(X)
            if np.any(np.isnan(preds)) or np.any(np.isinf(preds)):
                return 1e10
            mse = np.mean((preds - y) ** 2)
            return mse
        except Exception:
            return 1e10

    @property
    def formula(self):
        form = self._inner.formula
        if self._strategy == "identity":
            return form
        elif self._strategy == "sqrt":
            return f"Sqrt({form})"
        elif self._strategy == "log":
            return f"Exp({form})"
        elif self._strategy == "inverse":
            return f"Inv({form})"
        return form

    @property
    def error(self):
        return self._error

    @property
    def complexity(self):
        return self._complexity

    def to_latex(self):
        latex = self._inner.to_latex()
        if self._strategy == "identity":
            return latex
        elif self._strategy == "sqrt":
            return f"\\sqrt{{{latex}}}"
        elif self._strategy == "log":
            return f"e^{{{latex}}}"
        elif self._strategy == "inverse":
            return f"\\frac{{1}}{{{latex}}}"
        return latex

    def to_python(self):
        py = self._inner.to_python()
        if self._strategy == "identity":
            return py
        elif self._strategy == "sqrt":
            return f"np.sqrt(np.maximum({py}, 0.0))"
        elif self._strategy == "log":
            return f"np.exp({py})"
        elif self._strategy == "inverse":
            return f"(1.0 / ({py}))"
        return py

    def eval(self, x):
        val = self._inner.eval(x)
        if self._strategy == "identity":
            return val
        elif self._strategy == "sqrt":
            return np.sqrt(max(val, 0.0))
        elif self._strategy == "log":
            return np.exp(val)
        elif self._strategy == "inverse":
            return 1.0 / val if val != 0 else 1e15
        return val

    def eval_batch(self, inputs):
        inner_preds = np.array(self._inner.eval_batch(inputs))
        if self._strategy == "identity":
            return inner_preds
        elif self._strategy == "sqrt":
            return np.sqrt(np.maximum(inner_preds, 0.0))
        elif self._strategy == "log":
            return np.exp(inner_preds)
        elif self._strategy == "inverse":
            return 1.0 / np.where(inner_preds == 0, 1e-15, inner_preds)
        return inner_preds

    def predict(self, inputs):
        return self.eval_batch(inputs)

    def __repr__(self):
        return f"SearchResult(formula='{self.formula}', error={self.error:.6e}, complexity={self.complexity})"


class SmartSearcher:
    def __init__(self, max_complexity=10, complexity_penalty=0.1, beam_width=1000, alpha=0.0, l1_ratio=0.5):
        self._rust_searcher = eml_sr.Searcher(
            max_complexity=max_complexity,
            complexity_penalty=complexity_penalty,
            beam_width=beam_width,
            alpha=alpha,
            l1_ratio=l1_ratio
        )

    @property
    def max_complexity(self):
        return self._rust_searcher.max_complexity

    @property
    def beam_width(self):
        return self._rust_searcher.beam_width

    @property
    def complexity_penalty(self):
        return self._rust_searcher.complexity_penalty

    @property
    def alpha(self):
        return self._rust_searcher.alpha

    @property
    def l1_ratio(self):
        return self._rust_searcher.l1_ratio

    def recognize_constant(self, value, alpha=None, l1_ratio=None):
        res = self._rust_searcher.recognize_constant(value, alpha=alpha, l1_ratio=l1_ratio)
        return SmartSearchResult(res, "identity", np.array([]), np.array([]))

    def find_candidates(self, X, y, alpha=None, l1_ratio=None):
        X_arr = np.array(X, dtype=float)
        y_arr = np.array(y, dtype=float)
        
        strategies = []
        # Strategy 1: Identity
        strategies.append(("identity", y_arr, 0))

        # Strategy 2: Square (Only if target y >= 0 everywhere)
        if np.all(y_arr >= 0):
            strategies.append(("sqrt", y_arr ** 2, 1))

        # Strategy 3: Log (Only if target y > 0 everywhere)
        if np.all(y_arr > 0):
            strategies.append(("log", np.log(y_arr), 1))

        # Strategy 4: Inverse (Only if target |y| > 1e-5 everywhere)
        if np.all(np.abs(y_arr) > 1e-5):
            strategies.append(("inverse", 1.0 / y_arr, 1))

        combined_candidates = []
        for strat_name, y_trans, comp_offset in strategies:
            try:
                rust_cands = self._rust_searcher.find_candidates(X_arr, y_trans, alpha=alpha, l1_ratio=l1_ratio)
                strat_candidates = []
                for cand in rust_cands:
                    smart_cand = SmartSearchResult(cand, strat_name, X_arr, y_arr, comp_offset)
                    strat_candidates.append(smart_cand)
                combined_candidates.extend(strat_candidates)
                
                # Early stop if we found a mathematically perfect formula (MSE < 1e-15)
                if any(c.error < 1e-15 for c in strat_candidates):
                    print(f"[SmartSearcher] Found perfect candidate (MSE < 1e-15) with strategy '{strat_name}'. Stopping search.")
                    break
            except Exception as e:
                print(f"[SmartSearcher] Strategy '{strat_name}' failed: {e}")
                continue

        if not combined_candidates:
            return []

        # Sort by complexity ascending, then error ascending
        sorted_candidates = sorted(combined_candidates, key=lambda c: (c.complexity, c.error))
        
        # Build Pareto-front
        pareto_front = []
        min_error = float('inf')
        for c in sorted_candidates:
            if c.error < min_error:
                pareto_front.append(c)
                min_error = c.error

        return pareto_front

    def find_multivariate(self, inputs, ys, alpha=None, l1_ratio=None):
        candidates = self.find_candidates(inputs, ys, alpha=alpha, l1_ratio=l1_ratio)
        return pick_best(candidates)

    def fit(self, inputs, ys, alpha=None, l1_ratio=None):
        return self.find_multivariate(inputs, ys, alpha=alpha, l1_ratio=l1_ratio)

    def find_function(self, xs, ys, alpha=None, l1_ratio=None):
        xs_arr = np.array(xs, dtype=float).reshape(-1, 1)
        candidates = self.find_candidates(xs_arr, ys, alpha=alpha, l1_ratio=l1_ratio)
        return pick_best(candidates)


def pick_best(candidates, mse_threshold=1e-15):
    # Select the simplest formula that is already within the acceptable double-precision numerical error floor
    for cand in sorted(candidates, key=lambda c: c.complexity):
        if cand.error < mse_threshold:
            return cand
    return min(candidates, key=lambda c: c.error) if candidates else None
