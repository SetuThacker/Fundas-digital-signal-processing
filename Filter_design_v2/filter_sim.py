import argparse
import yaml
import os
import numpy as np
import matplotlib.pyplot as plt

def load_config(config_path):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def calculate_notch_roots(f_target, fs, r):
    """Calculates zeros and poles for a notch filter at a target frequency."""
    w0 = 2 * np.pi * (f_target / fs)
    
    # Zeros exactly on the unit circle
    zeros = [np.exp(1j * w0), np.exp(-1j * w0)]
    # Poles pulled inside by radius r
    poles = [r * np.exp(1j * w0), r * np.exp(-1j * w0)]
    
    return zeros, poles

def zpk_to_ba(zeros, poles):
    """Converts roots to polynomial coefficients and normalizes DC gain to 1.0."""
    b = np.poly(zeros)
    a = np.poly(poles) if len(poles) > 0 else [1.0]
    
    b = np.real_if_close(b)
    a = np.real_if_close(a)
    
    # Normalize DC gain (w=0, z=1)
    dc_gain = np.sum(b) / np.sum(a)
    b = b / dc_gain
    
    return b, a

def generate_composite_signal(fs, duration, frequencies):
    t = np.arange(0, duration, 1/fs)
    x = np.zeros(len(t))
    for f in frequencies:
        x += np.sin(2 * np.pi * f * t)
    return t, x

def generalized_filter(b, a, x):
    y = np.zeros(len(x))
    b = np.array(b) / a[0]
    a = np.array(a) / a[0]
    
    for n in range(len(x)):
        for k in range(len(b)):
            if n - k >= 0:
                y[n] += b[k] * x[n - k]
        for k in range(1, len(a)):
            if n - k >= 0:
                y[n] -= a[k] * y[n - k]
    return y

def plot_zplane(zeros, poles, ax, title):
    circle = plt.Circle((0, 0), 1, color='lightgray', fill=False, linestyle='--')
    ax.add_patch(circle)
    
    if len(zeros) > 0:
        ax.scatter(np.real(zeros), np.imag(zeros), s=100, facecolors='none', edgecolors='b', label='Zeros (O)')
    if len(poles) > 0:
        ax.scatter(np.real(poles), np.imag(poles), s=100, marker='x', color='r', label='Poles (X)')
    
    ax.axhline(0, color='black', lw=0.5)
    ax.axvline(0, color='black', lw=0.5)
    ax.set_aspect('equal')
    ax.set_xlim([-1.5, 1.5])
    ax.set_ylim([-1.5, 1.5])
    ax.set_title(title)
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

    sig_cfg = cfg['signal_generation']
    fs = sig_cfg['fs']
    notch_cfg = cfg['notch_experiment']

    # 1. Generate Input Signal
    t, input_signal = generate_composite_signal(fs, sig_cfg['duration'], sig_cfg['frequencies'])

    # 2. Design Filters
    zeros, poles = calculate_notch_roots(notch_cfg['target_freq'], fs, notch_cfg['pole_radius'])
    
    # Uncompensated (FIR) - No Poles
    b_uncomp, a_uncomp = zpk_to_ba(zeros, [])
    # Compensated (IIR) - Zeros and Poles
    b_comp, a_comp = zpk_to_ba(zeros, poles)

    # 3. Apply Filters
    filtered_uncomp = generalized_filter(b_uncomp, a_uncomp, input_signal)
    filtered_comp = generalized_filter(b_comp, a_comp, input_signal)

    # 4. Compute FFT
    N = len(input_signal)
    freqs = np.fft.rfftfreq(N, d=1/fs)
    fft_input = np.abs(np.fft.rfft(input_signal)) / (N / 2)
    fft_uncomp = np.abs(np.fft.rfft(filtered_uncomp)) / (N / 2)
    fft_comp = np.abs(np.fft.rfft(filtered_comp)) / (N / 2)

    # 5. Plotting (2x2 Grid)
    fig = plt.figure(figsize=(16, 12))
    
    # Top Left: Z-Plane (Uncompensated)
    ax1 = plt.subplot(2, 2, 1)
    plot_zplane(zeros, [], ax1, "Z-Plane: Uncompensated (Zeros Only)")
    
    # Top Right: Z-Plane (Compensated)
    ax2 = plt.subplot(2, 2, 2)
    plot_zplane(zeros, poles, ax2, f"Z-Plane: Compensated (r={notch_cfg['pole_radius']})")

    # Bottom Left: Time Domain
    ax3 = plt.subplot(2, 2, 3)
    ax3.plot(t, input_signal, color='lightgray', label='Raw Input')
    ax3.plot(t, filtered_uncomp, color='red', alpha=0.7, label='Uncompensated (FIR)')
    ax3.plot(t, filtered_comp, color='blue', linewidth=1.5, label='Compensated (IIR)')
    ax3.set_title("Time Domain Response")
    ax3.set_xlabel("Time (s)")
    ax3.set_ylabel("Amplitude")
    ax3.legend()
    ax3.grid(True, linestyle=':', alpha=0.6)

    # Bottom Right: Frequency Domain (FFT)
    ax4 = plt.subplot(2, 2, 4)
    ax4.plot(freqs, fft_input, color='lightgray', marker='o', label='Raw Spectrum')
    ax4.plot(freqs, fft_uncomp, color='red', marker='x', alpha=0.7, label='Uncompensated Spectrum')
    ax4.plot(freqs, fft_comp, color='blue', marker='+', linewidth=1.5, label='Compensated Spectrum')
    ax4.set_title("Frequency Domain (FFT Magnitude)")
    ax4.set_xlabel("Frequency (Hz)")
    ax4.set_ylabel("Magnitude")
    ax4.set_xlim(0, 150)
    ax4.legend()
    ax4.grid(True, linestyle=':', alpha=0.6)

    plt.tight_layout()
    save_path = os.path.join(out_dir, "notch_filter_comparison.png")
    plt.savefig(save_path)
    print(f"Saved visualization to {save_path}")

if __name__ == "__main__":
    main()