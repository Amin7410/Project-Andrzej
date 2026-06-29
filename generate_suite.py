import os
import csv
import shutil

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.abspath(os.path.join(
        script_dir, 'Scientific research paper from an external source',
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
    
    # Clean up and recreate the Test folder
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
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
            val = rng.uniform(low, high)
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
    for eq in eqs:
        fn = eq["filename"]
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
            val = rng.uniform(low, high)
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
        
    print("===========================================================")
    print(f"      EML-SR INDIVIDUAL CHALLENGE: {fn}                  ")
    print("===========================================================")
    print(f"Formula:      {{eq['formula']}}")
    print(f"Variables:    {{eq['var_names']}}")
    
    X, y = generate_dataset(eq)
    if len(X) == 0:
        print("Error: Generated dataset is empty. Cannot run EML-SR.")
        return
        
    print("\\n[EML-SR] Initializing Searcher (max_complexity=8, beam_width=500)...")
    searcher = eml_sr.Searcher(max_complexity=8, beam_width=500)
    
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

if __name__ == '__main__':
    main()
"""
        with open(os.path.join(test_dir, f"test_diff_{safe_fn}.py"), "w", encoding="utf-8") as f:
            f.write(diff_code)
            
    print(f"Generated {len(equations) - len(easy_targets)} individual difficulty test files in Test/ successfully.")

if __name__ == "__main__":
    main()
