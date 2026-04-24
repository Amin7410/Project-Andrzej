import eml_sr
import numpy as np

def main():
    print("===========================================================")
    print("      EML-SR PYTHON INTERFACE DEMO                         ")
    print("===========================================================")

    # 1. Initialize the searcher
    # max_complexity=10 is a good starting point for discovery
    # beam_width=200 ensures fast search with low memory usage
    searcher = eml_sr.Searcher(max_complexity=10, beam_width=500)

    # 2. Example: Identify a constant
    print("\n[Task] Identifying constant: 3.1415926535...")
    result = searcher.recognize_constant(3.141592653589793)
    print(f"      Formula:    {result.formula}")
    print(f"      LaTeX:      {result.to_latex()}")
    print(f"      Complexity: {result.complexity}")

    # 3. Example: Univariate function f(x) = sin(x) + 1
    print("\n[Task] Discovering f(x) = sin(x) + 1")
    xs = np.linspace(0, 2*np.pi, 20)
    ys = np.sin(xs) + 1.0

    result = searcher.find_function(xs, ys)
    print(f"      Found:      {result.formula}")
    print(f"      Python:     {result.to_python()}")
    print(f"      MSE Error:  {result.error:.2e}")

    # 4. Example: Scikit-Learn style API (fit & predict)
    print("\n[Task] Discovering f(x0, x1) = x0 * x1 + 0.5 using .fit() and .predict()")
    inputs = [
        [1.0, 2.0],
        [2.0, 3.0],
        [3.0, 4.0],
        [0.5, 0.5]
    ]
    targets = [v[0] * v[1] + 0.5 for v in inputs]

    result = searcher.fit(inputs, targets)
    print(f"      Found:      {result.formula}")
    
    predictions = result.predict(inputs)
    print(f"      Predictions: {predictions}")

    # 5. Example: Pareto-Front (Multiple candidates)
    print("\n[Task] Exploring the Pareto-Front for f(x) = sin(x) + 1")
    # find_candidates expects a 2D array, so we reshape xs to (N, 1)
    xs_2d = xs.reshape(-1, 1)
    candidates = searcher.find_candidates(xs_2d, ys)
    print(f"      Found {len(candidates)} candidates on the Pareto Front:")
    for i, c in enumerate(candidates):
        print(f"      [{i+1}] Error: {c.error:.2e} | Complexity: {c.complexity:2} | Formula: {c.formula}")

    # 6. The EML Challenge: Finding a complex law concisely
    # Target: f(x) = exp(x) - ln(x + 5)
    print("\n[Task] EML Challenge: Discovering f(x) = e^x - ln(x + 5)")
    xs_challenge = np.linspace(1, 10, 20)
    ys_challenge = np.exp(xs_challenge) - np.log(xs_challenge + 5.0)
    
    # EML should find this as EML(v0, v0 + 5) which is complexity 3
    # Traditional ops would need Exp(v0) - Log(v0 + 5) which is complexity 5
    result = searcher.find_function(xs_challenge, ys_challenge)
    print(f"      Formula:    {result.formula}")
    print(f"      Simplified: {result.to_python()}")
    print(f"      Complexity: {result.complexity} (Standard ops would need 5+)")

    print("\n===========================================================")

if __name__ == "__main__":
    main()
