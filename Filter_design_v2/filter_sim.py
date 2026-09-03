import argparse
import yaml
import os
import numpy as np
import matplotlib.pyplot as plt

def load_config(config_path):
    """Loads YAML configuration from a relative path."""
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def simulate_iir_pole(pole_val, length):
    """y[n] = p * y[n-1] + x[n]"""
    x = np.zeros(length)
    x[0] = 1.0  # Unit impulse
    y = np.zeros(length)
    
    for n in range(length):
        if n == 0:
            y[n] = x[n]
        else:
            y[n] = pole_val * y[n-1] + x[n]
    return y

def simulate_fir_zero(zero_val, length):
    """y[n] = x[n] - z_0 * x[n-1]"""
    x = np.zeros(length)
    x[0] = 1.0  # Unit impulse
    y = np.zeros(length)
    
    for n in range(length):
        if n == 0:
            y[n] = x[n]
        else:
            y[n] = x[n] - zero_val * x[n-1]
    return y

def main():
    # CLI setup
    parser = argparse.ArgumentParser(description="Run filter stability simulation.")
    parser.add_argument("--config", type=str, default="./config.yaml", help="Relative path to YAML config")
    args = parser.parse_args()

    # Load parameters
    cfg = load_config(args.config)
    out_dir = cfg['system']['output_dir']
    
    # Ensure relative output directory exists
    os.makedirs(out_dir, exist_ok=True)

    # --- Experiment 1: IIR Pole Stability ---
    length_iir = cfg['iir_pole_experiment']['impulse_length']
    y_stable = simulate_iir_pole(cfg['iir_pole_experiment']['stable_pole'], length_iir)
    y_unstable = simulate_iir_pole(cfg['iir_pole_experiment']['unstable_pole'], length_iir)

    plt.figure(figsize=(10, 4))
    plt.subplot(1, 2, 1)
    plt.stem(range(length_iir), y_stable)
    plt.title(f"Stable Pole (p={cfg['iir_pole_experiment']['stable_pole']})")
    
    plt.subplot(1, 2, 2)
    plt.stem(range(length_iir), y_unstable, linefmt='r-', markerfmt='ro')
    plt.title(f"Unstable Pole (p={cfg['iir_pole_experiment']['unstable_pole']})")
    
    plt.tight_layout()
    iir_path = os.path.join(out_dir, "iir_pole_response.png")
    plt.savefig(iir_path)
    print(f"Saved IIR simulation to {iir_path}")

    # --- Experiment 2: FIR Zero Stability ---
    length_fir = cfg['fir_zero_experiment']['impulse_length']
    y_min_phase = simulate_fir_zero(cfg['fir_zero_experiment']['minimum_phase_zero'], length_fir)
    y_max_phase = simulate_fir_zero(cfg['fir_zero_experiment']['maximum_phase_zero'], length_fir)

    plt.figure(figsize=(10, 4))
    plt.subplot(1, 2, 1)
    plt.stem(range(length_fir), y_min_phase)
    plt.title(f"Zero Inside (z={cfg['fir_zero_experiment']['minimum_phase_zero']})")
    
    plt.subplot(1, 2, 2)
    plt.stem(range(length_fir), y_max_phase)
    plt.title(f"Zero Outside (z={cfg['fir_zero_experiment']['maximum_phase_zero']})")
    
    plt.tight_layout()
    fir_path = os.path.join(out_dir, "fir_zero_response.png")
    plt.savefig(fir_path)
    print(f"Saved FIR simulation to {fir_path}")

if __name__ == "__main__":
    main()