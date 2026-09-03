import argparse
import yaml
import os
import numpy as np
import matplotlib.pyplot as plt

def load_config(config_path):
    """Loads YAML configuration from a relative path."""
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def zpk_to_ba(zeros, poles, gain=1.0):
    """
    Converts zero-pole roots to feedforward (b) and feedback (a) coefficients.
    
    Formula: Polynomial Expansion of Transfer Function H(z)
    H(z) = Gain * [ (z - z_1)(z - z_2)...(z - z_M) ] / [ (z - p_1)(z - p_2)...(z - p_N) ]
    
    np.poly() multiplies these binomial factors to yield the coefficients of 
    the resulting polynomial in descending powers of z.
    """
    b = np.poly(zeros) * gain  # Numerator polynomial coefficients
    a = np.poly(poles)         # Denominator polynomial coefficients
    return np.real_if_close(b), np.real_if_close(a)

def generalized_filter(b, a, x):
    """
    Applies a generalized digital filter using difference equations.
    
    Formula: Linear Constant-Coefficient Difference Equation (LCCDE)
    y[n] = (1/a[0]) * ( sum_{k=0}^{M} b[k]*x[n-k] - sum_{k=1}^{N} a[k]*y[n-k] )
    """
    y = np.zeros(len(x))
    
    # Normalize by a[0] as required by the LCCDE formula
    b = np.array(b) / a[0]
    a = np.array(a) / a[0]
    
    for n in range(len(x)):
        # Feedforward calculation: sum_{k=0}^{M} b[k]*x[n-k]
        for k in range(len(b)):
            if n - k >= 0:
                y[n] += b[k] * x[n - k]
                
        # Feedback calculation: sum_{k=1}^{N} a[k]*y[n-k]
        for k in range(1, len(a)):
            if n - k >= 0:
                y[n] -= a[k] * y[n - k]
    return y

def plot_zplane(zeros, poles, ax):
    """Plots poles and zeros on the complex unit circle."""
    # Formula for unit circle boundary: |z| = 1
    circle = plt.Circle((0, 0), 1, color='lightgray', fill=False, linestyle='--')
    ax.add_patch(circle)
    
    ax.scatter(np.real(zeros), np.imag(zeros), s=80, facecolors='none', edgecolors='b', label='Zeros (O)')
    ax.scatter(np.real(poles), np.imag(poles), s=80, marker='x', color='r', label='Poles (X)')
    
    ax.axhline(0, color='black', lw=0.5)
    ax.axvline(0, color='black', lw=0.5)
    ax.set_aspect('equal')
    ax.set_xlim([-1.5, 1.5])
    ax.set_ylim([-1.5, 1.5])
    ax.set_title("Z-Plane (Pole-Zero Plot)")
    ax.set_xlabel("Real")
    ax.set_ylabel("Imaginary")
    ax.legend(loc='upper right')
    ax.grid(True, linestyle=':', alpha=0.6)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="./config.yaml", help="Relative path to YAML config")
    args = parser.parse_args()

    cfg = load_config(args.config)
    out_dir = cfg['system']['output_dir']
    os.makedirs(out_dir, exist_ok=True)

    cfg_exp = cfg['multi_root_experiment']
    length = cfg_exp['impulse_length']
    
    # Complex parsing logic: converting "0+0.9j" string to complex type
    zeros = np.array([complex(z) if isinstance(z, str) else z for z in cfg_exp['zeros']])
    poles = np.array([complex(p) if isinstance(p, str) else p for p in cfg_exp['poles']])

    b, a = zpk_to_ba(zeros, poles)
    
    # Formula: Impulse generation (discrete delta function)
    # delta[n] = 1 for n=0, 0 otherwise
    impulse = np.zeros(length)
    impulse[0] = 1.0
    
    response = generalized_filter(b, a, impulse)

    fig = plt.figure(figsize=(12, 5))
    
    ax1 = plt.subplot(1, 2, 1)
    plot_zplane(zeros, poles, ax1)
    
    ax2 = plt.subplot(1, 2, 2)
    ax2.stem(range(length), response)
    ax2.set_title("Time Domain: Impulse Response")
    ax2.set_xlabel("Samples (n)")
    ax2.set_ylabel("Amplitude")
    ax2.grid(True, linestyle=':', alpha=0.6)

    plt.tight_layout()
    save_path = os.path.join(out_dir, "multi_root_response.png")
    plt.savefig(save_path)
    print(f"Saved visualization to {save_path}")

if __name__ == "__main__":
    main()