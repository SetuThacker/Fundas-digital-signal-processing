import argparse
import yaml
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import filtfilt

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
    b = np.poly(zeros)
    a = np.poly(poles) if len(poles) > 0 else [1.0]
    b = np.real_if_close(b)
    a = np.real_if_close(a)
    dc_gain = np.sum(b) / np.sum(a)
    b = b / dc_gain
    return b, a

def generate_signals(fs, duration, all_freqs, target_freq):
    """Generates both the noisy input and the clean ground truth."""
    t = np.arange(0, duration, 1/fs)
    clean_signal = np.zeros(len(t))
    noisy_signal = np.zeros(len(t))
    
    for f in all_freqs:
        wave = np.sin(2 * np.pi * f * t)
        noisy_signal += wave
        # Add to clean signal ONLY if it is not the target frequency
        if f != target_freq:
            clean_signal += wave
            
    return t, clean_signal, noisy_signal

def evaluate_filter_performance(clean_signal, filtered_signal):
    error = clean_signal - filtered_signal
    rmse = np.sqrt(np.mean(error**2))
    correlation = np.corrcoef(clean_signal, filtered_signal)[0, 1]
    
    signal_power = np.sum(clean_signal**2)
    noise_power = np.sum(error**2)
    sdr = 10 * np.log10(signal_power / noise_power) if noise_power > 0 else np.inf
    
    return rmse, correlation, sdr

def extract_passband_attenuation(clean_signal, filtered_signal, fs, check_freq):
    N = len(clean_signal)
    freqs = np.fft.rfftfreq(N, d=1/fs)
    bin_idx = np.argmin(np.abs(freqs - check_freq))
    
    mag_clean = np.abs(np.fft.rfft(clean_signal))[bin_idx]
    mag_filtered = np.abs(np.fft.rfft(filtered_signal))[bin_idx]
    
    return 20 * np.log10((mag_filtered + 1e-12) / (mag_clean + 1e-12))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="./config.yaml", help="Relative path to YAML config")
    args = parser.parse_args()

    cfg = load_config(args.config)
    fs = cfg['signal_generation']['fs']
    target_freq = cfg['notch_experiment']['target_freq']
    
    # 1. Generate Clean (Ground Truth) and Noisy Signals
    t, clean_signal, noisy_signal = generate_signals(
        fs, 
        cfg['signal_generation']['duration'], 
        cfg['signal_generation']['frequencies'], 
        target_freq
    )

    # 2. Design Filters
    zeros, poles = calculate_notch_roots(target_freq, fs, cfg['notch_experiment']['pole_radius'])
    b_uncomp, a_uncomp = zpk_to_ba(zeros, [])
    b_comp, a_comp = zpk_to_ba(zeros, poles)

    # 3. Apply Zero-Phase Filtering (filtfilt) for Accurate Metric Comparison
    filtered_uncomp = filtfilt(b_uncomp, a_uncomp, noisy_signal)
    filtered_comp = filtfilt(b_comp, a_comp, noisy_signal)

    # 4. Evaluate and Print Metrics
    print("\n--- Uncompensated Filter (Zeros Only) ---")
    rmse_u, corr_u, sdr_u = evaluate_filter_performance(clean_signal, filtered_uncomp)
    print(f"RMSE: {rmse_u:.4f}")
    print(f"Correlation: {corr_u:.4f}")
    print(f"Signal-to-Distortion Ratio (SDR): {sdr_u:.2f} dB")
    for f in cfg['signal_generation']['frequencies']:
        if f != target_freq:
            att = extract_passband_attenuation(clean_signal, filtered_uncomp, fs, f)
            print(f"Attenuation at {f}Hz: {att:.2f} dB")

    print("\n--- Compensated Filter (Zeros + Poles) ---")
    rmse_c, corr_c, sdr_c = evaluate_filter_performance(clean_signal, filtered_comp)
    print(f"RMSE: {rmse_c:.4f}")
    print(f"Correlation: {corr_c:.4f}")
    print(f"Signal-to-Distortion Ratio (SDR): {sdr_c:.2f} dB")
    for f in cfg['signal_generation']['frequencies']:
        if f != target_freq:
            att = extract_passband_attenuation(clean_signal, filtered_comp, fs, f)
            print(f"Attenuation at {f}Hz: {att:.2f} dB")

if __name__ == "__main__":
    main()