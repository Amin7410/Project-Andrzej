import os
import csv
import shutil
import ast

class ComplexityEstimator(ast.NodeVisitor):
    def __init__(self):
        self.count = 0
    def visit_BinOp(self, node):
        self.count += 1
        self.generic_visit(node)
    def visit_UnaryOp(self, node):
        self.count += 1
        self.generic_visit(node)
    def visit_Call(self, node):
        self.count += 1
        self.generic_visit(node)
    def visit_Name(self, node):
        self.count += 1
    def visit_Constant(self, node):
        self.count += 1
    def visit_Num(self, node):
        self.count += 1

def estimate_complexity(formula_str):
    formula_str = formula_str.replace("theta", "v0")
    try:
        tree = ast.parse(formula_str, mode='eval')
        estimator = ComplexityEstimator()
        estimator.visit(tree)
        return estimator.count
    except Exception:
        return 8

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.abspath(os.path.join(
        script_dir, 'paper',
        'eml-sr_study', 'data', 'FeynmanEquations.csv'
    ))
    test_dir = os.path.join(script_dir, 'Test')
    
    # 1. Read equations
    if not os.path.exists(csv_path):
        print(f"Error: Could not find FeynmanEquations.csv at {csv_path}")
        return
        
    equations = []
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row.get("Filename") or not row.get("Formula"):
                continue
            filename = row["Filename"].strip()
            formula = row["Formula"].strip()
            if not filename or not formula:
                continue
            output_var = row["Output"].strip()
            
            # Read variables dynamically (ignore the potentially incorrect # variables column)
            var_names = []
            var_ranges = []
            i = 1
            while True:
                name_col = f"v{i}_name"
                low_col = f"v{i}_low"
                high_col = f"v{i}_high"
                if name_col in row and row[name_col] and row[name_col].strip():
                    var_names.append(row[name_col].strip())
                    var_ranges.append((float(row[low_col]), float(row[high_col])))
                    i += 1
                else:
                    break
            
            if len(var_names) == 0:
                continue
                
            equations.append({
                "filename": filename,
                "formula": formula,
                "output_var": output_var,
                "n_vars": len(var_names),
                "var_names": var_names,
                "var_ranges": var_ranges,
            })
            
    # 2. Define Easy vs Difficult equations
    easy_targets = ["I.12.1", "I.12.5", "I.14.3", "I.18.12", "I.25.13", "I.26.2", "I.29.4"]
    
    # Clean up and recreate the Test folder, preserving Test/Pict
    if os.path.exists(test_dir):
        for item in os.listdir(test_dir):
            item_path = os.path.join(test_dir, item)
            if item == 'Pict':
                continue
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)
    else:
        os.makedirs(test_dir, exist_ok=True)
                 
    # 3. Generate Test/test_easy.py
    easy_code = f"""import os
import csv
import time
import numpy as np
import eml_sr

CSV_PATH = r"{csv_path}"

def load_equations():
    equations = []
    with open(CSV_PATH, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row.get("Filename") or not row.get("Formula"):
                continue
            filename = row["Filename"].strip()
            if filename not in {easy_targets}:
                continue
            formula = row["Formula"].strip()
            
            # Read variables dynamically (ignore the potentially incorrect # variables column)
            var_names = []
            var_ranges = []
            i = 1
            while True:
                name_col = f"v{{i}}_name"
                low_col = f"v{{i}}_low"
                high_col = f"v{{i}}_high"
                if name_col in row and row[name_col] and row[name_col].strip():
                    var_names.append(row[name_col].strip())
                    var_ranges.append((float(row[low_col]), float(row[high_col])))
                    i += 1
                else:
                    break
            
            equations.append({{
                "filename": filename,
                "formula": formula,
                "n_vars": len(var_names),
                "var_names": var_names,
                "var_ranges": var_ranges,
            }})
    return equations

def generate_dataset(eq, n_samples=100, seed=42):
    rng = np.random.default_rng(seed)
    formula = eq["formula"]
    var_names = eq["var_names"]
    var_ranges = eq["var_ranges"]
    eval_env = {{
        "exp": np.exp, "sqrt": np.sqrt, "sin": np.sin, "cos": np.cos, "tan": np.tan,
        "arcsin": np.arcsin, "arccos": np.arccos, "arctan": np.arctan, "log": np.log,
        "ln": np.log, "pi": np.pi, "e": np.e
    }}
    X_list, y_list = [], []
    attempts = 0
    while len(y_list) < n_samples and attempts < n_samples * 15:
        attempts += 1
        point = []
        local_env = eval_env.copy()
        for name, (low, high) in zip(var_names, var_ranges):
            current_low, current_high = low, high
            if name in ["theta", "theta1", "theta2", "x", "y", "z", "x1", "x2", "y1", "y2", "z1", "z2"]:
                current_low = -high
            val = rng.uniform(current_low, current_high)
            point.append(val)
            local_env[name] = val
        try:
            y = float(eval(formula, {{"__builtins__": None}}, local_env))
            if np.isfinite(y):
                X_list.append(point)
                y_list.append(y)
        except Exception:
            continue
    return np.array(X_list), np.array(y_list)

def main():
    print("===========================================================")
    print("      EML-SR EASY FEYNMAN VERIFICATION SUITE               ")
    print("===========================================================")
    eqs = load_equations()
    searcher = eml_sr.Searcher(max_complexity=6, beam_width=200)
    success = 0
    
    plot_dir = os.path.join('Test', 'Pict')
    os.makedirs(plot_dir, exist_ok=True)
    
    for eq in eqs:
        fn = eq["filename"]
        safe_fn = fn.replace(".", "_").replace("-", "_")
        plot_path = os.path.join(plot_dir, f"fit_{{safe_fn}}.png")
        
        if os.path.exists(plot_path):
            print(f"\\n[Task] Skipping easy equation {{fn}} (plot already exists: {{plot_path}})")
            success += 1
            continue
            
        print(f"\\n[Task] Running easy equation {{fn}}: {{eq['formula']}}")
        X, y = generate_dataset(eq)
        if len(X) == 0:
            print(f"      Status:      Failed (No valid dataset generated due to evaluation errors)")
            continue
        t0 = time.time()
        result = searcher.fit(X, y)
        elapsed = time.time() - t0
        print(f"      Status:      {{'Success' if result.error < 1e-4 else 'Failure'}}")
        print(f"      Discovered:  {{result.formula}}")
        print(f"      Python:      {{result.to_python()}}")
        print(f"      MSE Error:   {{result.error:.2e}}")
        print(f"      Time taken:  {{elapsed:.3f}}s")
        if result.error < 1e-4:
            success += 1
            
        try:
            import matplotlib.pyplot as plt
            plt.figure(figsize=(9, 6))

            if eq['n_vars'] == 1:
                sort_idx = np.argsort(X[:, 0])
                X_sorted = X[sort_idx]
                y_sorted = y[sort_idx]
                y_pred = np.array(result.predict(X_sorted))

                plt.scatter(X[:, 0], y, color='blue', alpha=0.5, label='Actual Data')
                plt.plot(X_sorted[:, 0], y_pred, color='red', linewidth=2, label='EML-SR Discovered')
                plt.title(f"EML-SR Fit for {{fn}}: {{eq['formula']}}")
                plt.xlabel(eq['var_names'][0])
                plt.ylabel('y')
            else:
                y_pred = np.array(result.predict(X))
                plt.scatter(y, y_pred, color='purple', alpha=0.6, label='Discovered vs. Actual')
                ideal = np.linspace(min(y), max(y), 100)
                plt.plot(ideal, ideal, color='gray', linestyle='--', label='Perfect Fit')
                plt.title(f"Parity Plot for {{fn}}: {{eq['formula']}}")
                plt.xlabel('Actual y')
                plt.ylabel('Discovered y')

            plt.legend()
            plt.grid(True)
            plt.savefig(plot_path)
            plt.close()
            print(f"      Saved fit plot to {{plot_path}}")
        except ImportError:
            pass
        except Exception as e:
            print(f"      Warning: Could not generate plot: {{e}}")
            
    print(f"\\n================ SUMMARY: {{success}}/{{len(eqs)}} resolved. ================")

if __name__ == '__main__':
    main()
"""
    
    with open(os.path.join(test_dir, "test_easy.py"), "w", encoding="utf-8") as f:
        f.write(easy_code)
    print("Generated Test/test_easy.py successfully.")

    # 4. Generate individual Test/test_diff_<filename>.py files
    for eq in equations:
        fn = eq["filename"]
        if fn in easy_targets:
            continue
            
        safe_fn = fn.replace(".", "_").replace("-", "_")
        est = estimate_complexity(eq["formula"])
        if est <= 4:
            mc = 5
            bw = 500
        elif est <= 6:
            mc = 7
            bw = 500
        elif est <= 8:
            mc = 8
            bw = 500
        else:
            mc = 9
            bw = 400

        diff_code = f"""import os
import csv
import time
import numpy as np
import eml_sr

CSV_PATH = r"{csv_path}"
EQ_FILENAME = "{fn}"

def load_equation():
    with open(CSV_PATH, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row.get("Filename") or not row.get("Formula"):
                continue
            filename = row["Filename"].strip()
            if filename != EQ_FILENAME:
                continue
            formula = row["Formula"].strip()
            
            # Read variables dynamically (ignore the potentially incorrect # variables column)
            var_names = []
            var_ranges = []
            i = 1
            while True:
                name_col = f"v{{i}}_name"
                low_col = f"v{{i}}_low"
                high_col = f"v{{i}}_high"
                if name_col in row and row[name_col] and row[name_col].strip():
                    var_names.append(row[name_col].strip())
                    var_ranges.append((float(row[low_col]), float(row[high_col])))
                    i += 1
                else:
                    break
            return {{
                "filename": filename,
                "formula": formula,
                "n_vars": len(var_names),
                "var_names": var_names,
                "var_ranges": var_ranges,
            }}
    return None

def generate_dataset(eq, n_samples=300, seed=42):
    rng = np.random.default_rng(seed)
    formula = eq["formula"]
    var_names = eq["var_names"]
    var_ranges = eq["var_ranges"]
    eval_env = {{
        "exp": np.exp, "sqrt": np.sqrt, "sin": np.sin, "cos": np.cos, "tan": np.tan,
        "arcsin": np.arcsin, "arccos": np.arccos, "arctan": np.arctan, "log": np.log,
        "ln": np.log, "pi": np.pi, "e": np.e
    }}
    X_list, y_list = [], []
    attempts = 0
    while len(y_list) < n_samples and attempts < n_samples * 15:
        attempts += 1
        point = []
        local_env = eval_env.copy()
        for name, (low, high) in zip(var_names, var_ranges):
            current_low, current_high = low, high
            if name in ["theta", "theta1", "theta2", "x", "y", "z", "x1", "x2", "y1", "y2", "z1", "z2"]:
                current_low = -high
            val = rng.uniform(current_low, current_high)
            point.append(val)
            local_env[name] = val
        try:
            y = float(eval(formula, {{"__builtins__": None}}, local_env))
            if np.isfinite(y):
                X_list.append(point)
                y_list.append(y)
        except Exception:
            continue
    return np.array(X_list), np.array(y_list)

def main():
    eq = load_equation()
    if not eq:
        print("Error: Could not load equation {fn}")
        return
        
    plot_dir = os.path.join('Test', 'Pict')
    os.makedirs(plot_dir, exist_ok=True)
    plot_path = os.path.join(plot_dir, f"fit_{safe_fn}.png")
    
    txt_path = os.path.join(plot_dir, f"fit_{safe_fn}.txt")
    if os.path.exists(plot_path) and os.path.exists(txt_path):
        print(f"Plot and log already exist for {safe_fn}. Skipping run.")
        return

    print("===========================================================")
    print(f"      EML-SR INDIVIDUAL CHALLENGE: {fn}                  ")
    print("===========================================================")
    print(f"Formula:      {{eq['formula']}}")
    print(f"Variables:    {{eq['var_names']}}")
    
    X, y = generate_dataset(eq)
    if len(X) == 0:
        print("Error: Generated dataset is empty. Cannot run EML-SR.")
        return
        
    print(f"\\n[EML-SR] Initializing Searcher (max_complexity={mc}, beam_width={bw})...")
    searcher = eml_sr.Searcher(max_complexity={mc}, beam_width={bw})
    
    t0 = time.time()
    result = searcher.fit(X, y)
    elapsed = time.time() - t0
    
    print("\\n====================== RESULTS ============================")
    print(f"Discovered:  {{result.formula}}")
    print(f"Python:      {{result.to_python()}}")
    print(f"LaTeX:       {{result.to_latex()}}")
    print(f"MSE Error:   {{result.error:.2e}}")
    print(f"Time taken:  {{elapsed:.2f}} seconds")
    print("===========================================================")

    txt_path = os.path.join(plot_dir, f"fit_{safe_fn}.txt")
    with open(txt_path, "w", encoding="utf-8") as tf:
        tf.write("====================== RESULTS ============================\\n")
        tf.write(f"Discovered:  {{result.formula}}\\n")
        tf.write(f"Python:      {{result.to_python()}}\\n")
        tf.write(f"LaTeX:       {{result.to_latex()}}\\n")
        tf.write(f"MSE Error:   {{result.error:.2e}}\\n")
        tf.write(f"Time taken:  {{elapsed:.2f}} seconds\\n")
        tf.write("===========================================================\\n")
    print(f"Saved results log to {{txt_path}}")

    try:
        import matplotlib.pyplot as plt
        plt.figure(figsize=(9, 6))

        if eq['n_vars'] == 1:
            sort_idx = np.argsort(X[:, 0])
            X_sorted = X[sort_idx]
            y_sorted = y[sort_idx]
            y_pred = np.array(result.predict(X_sorted))

            plt.scatter(X[:, 0], y, color='blue', alpha=0.5, label='Actual Data')
            plt.plot(X_sorted[:, 0], y_pred, color='red', linewidth=2, label='EML-SR Discovered')
            plt.title(f"EML-SR Fit for {fn}: {eq['formula']}")
            plt.xlabel(eq['var_names'][0])
            plt.ylabel('y')
        else:
            y_pred = np.array(result.predict(X))
            plt.scatter(y, y_pred, color='purple', alpha=0.6, label='Discovered vs. Actual')
            ideal = np.linspace(min(y), max(y), 100)
            plt.plot(ideal, ideal, color='gray', linestyle='--', label='Perfect Fit')
            plt.title(f"Parity Plot for {fn}: {eq['formula']}")
            plt.xlabel('Actual y')
            plt.ylabel('Discovered y')

        plt.legend()
        plt.grid(True)
        plt.savefig(plot_path)
        plt.close()
        print(f"Saved fit plot to {{plot_path}}")
    except ImportError:
        pass
    except Exception as e:
        print(f"Warning: Could not generate plot: {{e}}")

if __name__ == '__main__':
    main()
"""
        with open(os.path.join(test_dir, f"test_diff_{safe_fn}.py"), "w", encoding="utf-8") as f:
            f.write(diff_code)
            
    print(f"Generated {len(equations) - len(easy_targets)} individual difficulty test files in Test/ successfully.")

if __name__ == "__main__":
    main()
