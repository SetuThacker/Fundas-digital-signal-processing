import numpy as np

x_input = np.float64(input("Enter a number to approximate its square root: "))
# initial_guess = 

x = x_input/5

threshold = 1e-12
for i in range(100):
    new_avg = 0.5 * (x + (x_input / x))
    x = new_avg
    print(f"Iteration {i+1}: Approximation = {x} | Error = {abs(x - np.sqrt(x_input))}")
    if abs(x - np.sqrt(x_input)) < threshold:
        print(f"Converged after {i+1} iterations.")
        break