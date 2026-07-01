import os
import sys
import time
import numpy as np
import eml_sr

# Add workspace root to sys.path to import smart_search
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from smart_search import SmartSearcher, pick_best

EQ_DATA = {
    "filename": "II.21.32",
    "formula": "q/(4*pi*epsilon*r*(1-v/c))",
    "n_vars": 5,
    "var_names": ['q', 'epsilon', 'r', 'v', 'c'],
    "var_ranges": [(1.0, 5.0), (1.0, 5.0), (1.0, 5.0), (1.0, 2.0), (3.0, 10.0)]
}

def generate_dataset(eq, n_samples=300, seed=42):
    rng = np.random.default_rng(seed)
    formula = eq["formula"]
    var_names = eq["var_names"]
    var_ranges = eq["var_ranges"]
    eval_env = {
        "exp": np.exp, "sqrt": np.sqrt, "sin": np.sin, "cos": np.cos, "tan": np.tan,
        "arcsin": np.arcsin, "arccos": np.arccos, "arctan": np.arctan, "log": np.log,
        "ln": np.log, "pi": np.pi, "e": np.e
    }
    X_list, y_list = [], []
    attempts = 0
    while len(y_list) < n_samples and attempts < n_samples * 15:
        attempts += 1
        point = []
        local_env = eval_env.copy()
        for name, (low, high) in zip(var_names, var_ranges):
            val = rng.uniform(low, high)
            point.append(val)
            local_env[name] = val
        try:
            y = float(eval(formula, {"__builtins__": None}, local_env))
            if np.isfinite(y):
                X_list.append(point)
                y_list.append(y)
        except Exception:
            continue
    return np.array(X_list), np.array(y_list)

def main():
    eq = EQ_DATA
    script_dir = os.path.dirname(os.path.abspath(__file__))
    plot_dir = os.path.join(script_dir, 'Results')
    os.makedirs(plot_dir, exist_ok=True)
    plot_path = os.path.join(plot_dir, 'fit.png')
    txt_path = os.path.join(plot_dir, 'fit.txt')

    if os.path.exists(plot_path) and os.path.exists(txt_path):
        print(f"Results already exist in {plot_dir}. Skipping run.")
        return

    print("===========================================================")
    print(f"      EML-SR RUNNING FEYNMAN EQUATION: II.21.32                ")
    print("===========================================================")
    print(f"Formula:      {eq['formula']}")
    print(f"Variables:    {eq['var_names']}")

    X, y = generate_dataset(eq)
    if len(X) == 0:
        print("Error: Generated dataset is empty. Cannot run EML-SR.")
        return

    print(f"\n[EML-SR] Initializing Searcher (max_complexity=9, beam_width=400)...")
    searcher = SmartSearcher(max_complexity=9, beam_width=400)

    t0 = time.time()
    candidates = searcher.find_candidates(X, y)
    elapsed = time.time() - t0

    if not candidates:
        print("Error: No candidates found.")
        return

    best_candidate = pick_best(candidates)

    print("\n====================== RESULTS ============================")
    print(f"Discovered:  {best_candidate.formula}")
    print(f"Python:      {best_candidate.to_python()}")
    print(f"LaTeX:       {best_candidate.to_latex()}")
    print(f"MSE Error:   {best_candidate.error:.2e}")
    print(f"Time taken:  {elapsed:.2f} seconds")
    print("===========================================================")

    with open(txt_path, "w", encoding="utf-8") as tf:
        tf.write("====================== SEARCH RESULTS ======================\n")
        tf.write(f"Best Formula: {best_candidate.formula}\n")
        tf.write(f"Python:       {best_candidate.to_python()}\n")
        tf.write(f"LaTeX:        {best_candidate.to_latex()}\n")
        tf.write(f"MSE Error:    {best_candidate.error:.2e}\n")
        tf.write(f"Complexity:   {best_candidate.complexity} nodes\n")
        tf.write(f"Time taken:   {elapsed:.2f} seconds\n")
        tf.write("============================================================\n\n")

        tf.write("================== PATH OF FORMULA EVOLUTION ==================\n")
        for cand in sorted(candidates, key=lambda c: c.complexity):
            tf.write(f"Complexity {cand.complexity:2d} nodes | MSE: {cand.error:.2e} | Formula: {cand.to_python()}\n")
        tf.write("============================================================\n")

    print(f"Saved results log to {txt_path}")

    try:
        import matplotlib.pyplot as plt
        plt.figure(figsize=(9, 6))

        if eq['n_vars'] == 1:
            sort_idx = np.argsort(X[:, 0])
            X_sorted = X[sort_idx]
            y_sorted = y[sort_idx]
            y_pred = np.array(best_candidate.predict(X_sorted))

            plt.scatter(X[:, 0], y, color='blue', alpha=0.5, label='Actual Data')
            plt.plot(X_sorted[:, 0], y_pred, color='red', linewidth=2, label='EML-SR Discovered')
            plt.title(f"EML-SR Fit for II.21.32: q/(4*pi*epsilon*r*(1-v/c))")
            plt.xlabel(eq['var_names'][0])
            plt.ylabel('y')
        else:
            y_pred = np.array(best_candidate.predict(X))
            plt.scatter(y, y_pred, color='purple', alpha=0.6, label='Discovered vs. Actual')
            ideal = np.linspace(min(y), max(y), 100)
            plt.plot(ideal, ideal, color='gray', linestyle='--', label='Perfect Fit')
            plt.title(f"Parity Plot for II.21.32: q/(4*pi*epsilon*r*(1-v/c))")
            plt.xlabel('Actual y')
            plt.ylabel('Discovered y')

        plt.legend()
        plt.grid(True)
        plt.savefig(plot_path)
        plt.close()
        print(f"Saved fit plot to {plot_path}")
    except ImportError:
        pass
    except Exception as e:
        print(f"Warning: Could not generate plot: {e}")

if __name__ == '__main__':
    main()
