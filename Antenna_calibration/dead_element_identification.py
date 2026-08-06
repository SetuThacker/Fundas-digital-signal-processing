import numpy as np
import matplotlib.pyplot as plt

# ==========================================
# 1. Hardware Initialization & Hadamard Code
# ==========================================
rows = 4
cols = 19
total_trms = rows * cols
pulses = 128  # Next power of 2 for a full module-level check

def generate_hadamard(n):
    """Recursively generates a Hadamard matrix of size n x n."""
    H = np.array([[1]])
    while H.shape[0] < n:
        H = np.vstack((np.hstack((H, H)), np.hstack((H, -H))))
    return H

H_full = generate_hadamard(pulses)
# We only need the first 76 columns to modulate our 76 TRMs
H_active = H_full[:, :total_trms]

# ==========================================
# 2. Define Independent TX & RX True States
# ==========================================
np.random.seed(42)

# Generate baseline Geometric Coding Phase (-180 to +180 in 5 deg steps)
geo_phase_deg_tx = np.random.choice(np.arange(-180, 180, 5), size=total_trms)
geo_phase_deg_rx = np.random.choice(np.arange(-180, 180, 5), size=total_trms)

# Baseline Gain with 5% manufacturing error (Gaussian distribution)
gain_tx = np.random.normal(1.0, 0.05, size=total_trms)
gain_rx = np.random.normal(1.0, 0.05, size=total_trms)

# Inject Independent Hardware Failures
# TX Failures (e.g., blown High-Power Amplifiers)
gain_tx[24] = 0.0  # TRM at Row 2, Col 6
gain_tx[43] = 0.0  # TRM at Row 3, Col 6

# RX Failures (e.g., damaged Low-Noise Amplifiers)
gain_rx[50] = 0.0  # TRM at Row 3, Col 13
gain_rx[59] = 0.0  # TRM at Row 4, Col 3

# Construct Complex Physical State
true_state_tx = gain_tx * np.exp(1j * np.radians(geo_phase_deg_tx))
true_state_rx = gain_rx * np.exp(1j * np.radians(geo_phase_deg_rx))

# ==========================================
# 3. Simulate 20 Measurement Iterations
# ==========================================
iterations = 20
noise_std = 0.4  # Thermal receiver noise standard deviation

# Storage arrays for the decoded results across all iterations
all_gain_tx = np.zeros((iterations, total_trms))
all_gain_rx = np.zeros((iterations, total_trms))
all_phase_tx = np.zeros((iterations, total_trms))
all_phase_rx = np.zeros((iterations, total_trms))

for i in range(iterations):
    # Step A: Forward Transmission (Multiplexing)
    # We add complex Gaussian noise to the composite received pulse to simulate real hardware conditions
    rx_pulses_tx = H_active.dot(true_state_tx) + (np.random.randn(pulses) + 1j * np.random.randn(pulses)) * noise_std
    rx_pulses_rx = H_active.dot(true_state_rx) + (np.random.randn(pulses) + 1j * np.random.randn(pulses)) * noise_std

    # Step B: Ground Processing Decoding (Inverse Hadamard)
    # H^T * s / N
    decoded_tx = (H_active.T.dot(rx_pulses_tx)) / pulses
    decoded_rx = (H_active.T.dot(rx_pulses_rx)) / pulses

    # Step C: Demodulate the geometric phase to extract pure error metrics
    demodulated_tx = decoded_tx * np.exp(-1j * np.radians(geo_phase_deg_tx))
    demodulated_rx = decoded_rx * np.exp(-1j * np.radians(geo_phase_deg_rx))

    # Convert Gain to dB (1.0 nominal gain equals 0 dB)
    all_gain_tx[i, :] = 20 * np.log10(np.abs(demodulated_tx) + 1e-12)
    all_gain_rx[i, :] = 20 * np.log10(np.abs(demodulated_rx) + 1e-12)

    # Extract Phase variation from 0 degrees
    all_phase_tx[i, :] = np.degrees(np.angle(demodulated_tx))
    all_phase_rx[i, :] = np.degrees(np.angle(demodulated_rx))

# ==========================================
# 4. Average the 20 Iterations
# ==========================================
avg_gain_tx = np.mean(all_gain_tx, axis=0)
avg_gain_rx = np.mean(all_gain_rx, axis=0)
avg_phase_tx = np.mean(all_phase_tx, axis=0)
avg_phase_rx = np.mean(all_phase_rx, axis=0)

# ==========================================
# 5. Diagnostic Plotting (Telemetry Format)
# ==========================================
trm_indices = np.arange(total_trms)
fig, axes = plt.subplots(2, 2, figsize=(18, 10))
fig.suptitle(f"Active Phased Array TRM Diagnostics\n(Averaged over {iterations} PN Gating Iterations)", 
             fontsize=16, fontweight='bold', y=0.96)

# Formatting Helper
def format_subplot(ax, x_data, y_data, title, y_label, y_lim, line_color):
    ax.plot(x_data, y_data, marker='.', linestyle='-', color=line_color, linewidth=1.5, alpha=0.8)
    ax.axhline(0, color='black', linestyle='--', linewidth=1)
    ax.set_title(title, fontweight='bold')
    ax.set_xlabel("TRM Index Number")
    ax.set_ylabel(y_label)
    ax.set_ylim(y_lim)
    ax.set_xlim(0, total_trms - 1)
    ax.grid(True, linestyle=':', alpha=0.6)

# Top Left: TX Gain
format_subplot(axes[0, 0], trm_indices, avg_gain_tx, 
               "Transmit (TX) Path Gain Variation", "Gain Deviation (dB)", 
               [-25, 2], '#C62828')

# Top Right: RX Gain
format_subplot(axes[0, 1], trm_indices, avg_gain_rx, 
               "Receive (RX) Path Gain Variation", "Gain Deviation (dB)", 
               [-25, 2], '#283593')

# Bottom Left: TX Phase Error
# Dead TRMs (gain~0) will have random phase noise, so we mask them to keep the plot clean
valid_tx_mask = avg_gain_tx > -10
masked_phase_tx = np.where(valid_tx_mask, avg_phase_tx, np.nan)
format_subplot(axes[1, 0], trm_indices, masked_phase_tx, 
               "Transmit (TX) Phase Deviation (Dead Modules Masked)", "Phase Error (Degrees)", 
               [-20, 20], '#C62828')

# Bottom Right: RX Phase Error
valid_rx_mask = avg_gain_rx > -10
masked_phase_rx = np.where(valid_rx_mask, avg_phase_rx, np.nan)
format_subplot(axes[1, 1], trm_indices, masked_phase_rx, 
               "Receive (RX) Phase Deviation (Dead Modules Masked)", "Phase Error (Degrees)", 
               [-20, 20], '#283593')

plt.tight_layout(rect=[0, 0.03, 1, 0.93])
plt.show()