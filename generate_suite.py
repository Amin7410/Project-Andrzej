import os
import csv
import shutil
import ast


####################################################
####################################################

# DO NOT RUN IF YOU DONT KNOW WHAT IT DOES !!!

####################################################
####################################################

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

PHYSICS_NAMES = {
    "I.6.2": "Gaussian probability density (error distribution)",
    "I.6.2a": "Gaussian probability density (standard normal error distribution)",
    "I.9.18": "Gravitational force between two masses",
    "I.11.19": "Electric field of a charge distribution",
    "I.12.1": "Force of sliding friction",
    "I.12.5": "Viscous drag force on a sphere (Stokes' law)",
    "I.12.11": "Force on a charge in electromagnetic field (Lorentz force)",
    "I.13.4": "Potential energy of gravity near Earth's surface",
    "I.13.12": "Gravitational potential energy of two masses",
    "I.14.3": "Work done by a constant force",
    "I.14.4": "Kinetic energy of a moving mass",
    "I.15.3t": "Lorentz time dilation (relativity)",
    "I.15.3x": "Lorentz position transformation (relativity)",
    "I.15.10": "Relativistic momentum of a moving particle",
    "I.18.12": "Torque on a particle (angular momentum change)",
    "I.24.6": "Energy of a harmonic oscillator",
    "I.25.13": "Impedance of a capacitor",
    "I.26.2": "Refractive index of a medium (Snell's law coefficient)",
    "I.29.4": "Intensity of electromagnetic radiation",
    "I.30.5": "Intensity of double-slit interference pattern",
    "I.32.5": "Radiated power by an accelerating charge (Larmor formula)",
    "I.34.8": "Magnetic moment of a current loop",
    "I.34.10": "Gibbs free energy / partition function",
    "I.34.14": "Magnetic field of a dipole",
    "I.37.4": "Uncertainty principle relationship",
    "I.38.12": "De Broglie wavelength of a particle",
    "I.39.22": "Mean molecular kinetic energy of gas",
    "I.40.1": "Boltzmann distribution of gas density in atmosphere",
    "I.41.16": "Rotational energy of a molecule",
    "I.43.16": "Velocity distribution of gas molecules (Maxwell-Boltzmann)",
    "I.43.31": "Thermal conductivity of a gas",
    "I.43.43": "Viscosity of a gas",
    "I.47.8": "Speed of sound in a fluid",
    "I.48.2": "Phase velocity of wave in a dispersive medium",
    "I.50.26": "Electric field from an oscillating dipole",
    "II.2.42": "Electrostatic potential of a dipole",
    "II.3.24": "Flux of electric field (Gauss's law)",
    "II.4.23": "Energy density of electric field in vacuum",
    "II.6.15": "Electric field of a charged sphere",
    "II.8.7": "Energy stored in a capacitor",
    "II.11.3": "Polarization of a dielectric material",
    "II.11.20": "Refractive index of a gas (dispersion relation)",
    "II.11.27": "Transmission coefficient of electric field",
    "II.11.28": "Refractive index of a plasma",
    "II.13.17": "Magnetic field of a long straight wire",
    "II.13.23": "Force between two parallel current-carrying wires",
    "II.15.4": "Vector potential of a solenoid",
    "II.15.5": "Vector potential of a magnetic dipole",
    "II.21.32": "Electric field of an accelerating point charge",
    "II.24.17": "Transmission line impedance",
    "II.27.16": "Poynting vector (energy flux density of EM wave)",
    "II.27.18": "Energy density of electromagnetic field",
    "II.34.2a": "Magnetic susceptibility of a paramagnetic material",
    "II.34.11": "Magnetic moment of an electron spin",
    "II.34.29a": "Gyromagnetic ratio / g-factor",
    "II.35.18": "Work done on a magnetic dipole",
    "II.35.21": "Gibbs free energy of a magnetized material",
    "II.36.38": "Free energy density of a superconductor (London equation)",
    "II.38.3": "Velocity of a particle in a cyclotron",
    "II.38.14": "Force on a current-carrying wire in magnetic field",
    "III.4.16": "Energy states of a system in a magnetic field",
    "III.4.23": "Transition probability between two states",
    "III.8.19": "Hamiltonian matrix element for two-state system",
    "III.8.54": "Amplitudes for a particle in a periodic potential",
    "III.9.19": "Electric dipole transition matrix element",
    "III.10.19": "Energy eigenvalues of a two-state system with coupling",
    "III.12.43": "Probability distribution of scattering angle",
    "III.13.18": "Transition rate in a periodic lattice",
    "III.14.14": "Probability of a transition between energy levels",
    "III.15.12": "Dispersion relation for spin waves (magnons)",
    "III.15.14": "Energy of a spin wave in a ferromagnet",
    "III.17.37": "Scattering amplitude in Born approximation",
    "III.19.51": "Transmission coefficient of a potential barrier",
    "III.21.19": "Superfluid density in liquid helium"
}

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.abspath(os.path.join(
        script_dir, 'paper',
        'eml-sr_study', 'data', 'FeynmanEquations.csv'
    ))
    test_dir = os.path.join(script_dir, 'Test')
    feynman_dir = os.path.join(test_dir, 'Feynman')
    
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
            
    easy_targets = ["I.12.1", "I.12.5", "I.14.3", "I.18.12", "I.25.13", "I.26.2", "I.29.4"]
    
    # Check if old I.6.2a results exist in Test/Pict to migrate them
    old_pict_dir = os.path.join(test_dir, 'Pict')
    old_png = os.path.join(old_pict_dir, 'fit_I_6_2a.png')
    old_txt = os.path.join(old_pict_dir, 'fit_I_6_2a.txt')
    has_old_gauss = os.path.exists(old_png) and os.path.exists(old_txt)

    # Clean up old flat test files
    if os.path.exists(test_dir):
        for item in os.listdir(test_dir):
            item_path = os.path.join(test_dir, item)
            if item == 'Feynman':
                continue
            if item == 'Pict' and has_old_gauss:
                # Keep temporarily to migrate
                continue
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)
    else:
        os.makedirs(test_dir, exist_ok=True)
        
    os.makedirs(feynman_dir, exist_ok=True)

    # Generate each equation test folder
    for eq in equations:
        fn = eq["filename"]
        safe_fn = fn.replace(".", "_").replace("-", "_")
        eq_dir = os.path.join(feynman_dir, safe_fn)
        os.makedirs(eq_dir, exist_ok=True)

        # Decide max complexity and beam width
        if fn in easy_targets:
            mc = 6
            bw = 200
            samples = 100
        else:
            est = estimate_complexity(eq["formula"])
            samples = 300
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

        # Expand var ranges for symmetric variables
        expanded_ranges = []
        for name, (low, high) in zip(eq["var_names"], eq["var_ranges"]):
            if name in ["theta", "theta1", "theta2", "x", "y", "z", "x1", "x2", "y1", "y2", "z1", "z2"]:
                expanded_ranges.append((-high, high))
            else:
                expanded_ranges.append((low, high))

        # Write test.py inside eq_dir
        test_py_code = f"""import os
import sys
import time
import numpy as np
import eml_sr

# Add workspace root to sys.path to import smart_search
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from smart_search import SmartSearcher, pick_best

EQ_DATA = {{
    "filename": "{fn}",
    "formula": "{eq['formula']}",
    "n_vars": {eq['n_vars']},
    "var_names": {eq['var_names']},
    "var_ranges": {expanded_ranges}
}}

def generate_dataset(eq, n_samples={samples}, seed=42):
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
    eq = EQ_DATA
    script_dir = os.path.dirname(os.path.abspath(__file__))
    plot_dir = os.path.join(script_dir, 'Results')
    os.makedirs(plot_dir, exist_ok=True)
    plot_path = os.path.join(plot_dir, 'fit.png')
    txt_path = os.path.join(plot_dir, 'fit.txt')

    if os.path.exists(plot_path) and os.path.exists(txt_path):
        print(f"Results already exist in {{plot_dir}}. Skipping run.")
        return

    print("===========================================================")
    print(f"      EML-SR RUNNING FEYNMAN EQUATION: {fn}                ")
    print("===========================================================")
    print(f"Formula:      {{eq['formula']}}")
    print(f"Variables:    {{eq['var_names']}}")

    X, y = generate_dataset(eq)
    if len(X) == 0:
        print("Error: Generated dataset is empty. Cannot run EML-SR.")
        return

    print(f"\\n[EML-SR] Initializing Searcher (max_complexity={mc}, beam_width={bw})...")
    searcher = SmartSearcher(max_complexity={mc}, beam_width={bw})

    t0 = time.time()
    candidates = searcher.find_candidates(X, y)
    elapsed = time.time() - t0

    if not candidates:
        print("Error: No candidates found.")
        return

    best_candidate = pick_best(candidates)

    print("\\n====================== RESULTS ============================")
    print(f"Discovered:  {{best_candidate.formula}}")
    print(f"Python:      {{best_candidate.to_python()}}")
    print(f"LaTeX:       {{best_candidate.to_latex()}}")
    print(f"MSE Error:   {{best_candidate.error:.2e}}")
    print(f"Time taken:  {{elapsed:.2f}} seconds")
    print("===========================================================")

    with open(txt_path, "w", encoding="utf-8") as tf:
        tf.write("====================== SEARCH RESULTS ======================\\n")
        tf.write(f"Best Formula: {{best_candidate.formula}}\\n")
        tf.write(f"Python:       {{best_candidate.to_python()}}\\n")
        tf.write(f"LaTeX:        {{best_candidate.to_latex()}}\\n")
        tf.write(f"MSE Error:    {{best_candidate.error:.2e}}\\n")
        tf.write(f"Complexity:   {{best_candidate.complexity}} nodes\\n")
        tf.write(f"Time taken:   {{elapsed:.2f}} seconds\\n")
        tf.write("============================================================\\n\\n")

        tf.write("================== PATH OF FORMULA EVOLUTION ==================\\n")
        for cand in sorted(candidates, key=lambda c: c.complexity):
            tf.write(f"Complexity {{cand.complexity:2d}} nodes | MSE: {{cand.error:.2e}} | Formula: {{cand.to_python()}}\\n")
        tf.write("============================================================\\n")

    print(f"Saved results log to {{txt_path}}")

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
            plt.title(f"EML-SR Fit for {fn}: {eq['formula']}")
            plt.xlabel(eq['var_names'][0])
            plt.ylabel('y')
        else:
            y_pred = np.array(best_candidate.predict(X))
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
        with open(os.path.join(eq_dir, "test.py"), "w", encoding="utf-8") as f:
            f.write(test_py_code)

    # 5. Migrate old Gauss I.6.2a results if they exist
    if has_old_gauss:
        gauss_results_dir = os.path.join(feynman_dir, 'I_6_2a', 'Results')
        os.makedirs(gauss_results_dir, exist_ok=True)
        shutil.copy(old_png, os.path.join(gauss_results_dir, 'fit.png'))
        shutil.copy(old_txt, os.path.join(gauss_results_dir, 'fit.txt'))
        shutil.rmtree(old_pict_dir)
        print("Migrated old Gauss I.6.2a results successfully.")

    # 6. Generate Test/Feynman/README.md
    readme_path = os.path.join(feynman_dir, "README.md")
    with open(readme_path, "w", encoding="utf-8") as rf:
        rf.write("# Feynman Equations Test Suite\n\n")
        rf.write("A structured validation suite of 100 physics equations from the Feynman Lectures on Physics.\n\n")
        rf.write("| Equation ID | Formula | Variables | Complexity | Group | Physics Description |\n")
        rf.write("| :--- | :--- | :--- | :---: | :---: | :--- |\n")
        for eq in equations:
            fn = eq["filename"]
            safe_fn = fn.replace(".", "_").replace("-", "_")
            group = "Easy" if fn in easy_targets else "Difficult"
            desc = PHYSICS_NAMES.get(fn, f"Feynman Equation {fn}")
            est = estimate_complexity(eq["formula"])
            # Format folder link
            folder_link = f"[{fn}](file:///./{safe_fn}/test.py)"
            rf.write(f"| {folder_link} | `{eq['formula']}` | `{', '.join(eq['var_names'])}` | {est} | {group} | {desc} |\n")
            
    print("Generated Test/Feynman/README.md successfully.")

if __name__ == "__main__":
    main()
