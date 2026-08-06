import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from pathlib import Path

# Directory where this script is located
script_dir = Path(__file__).resolve().parent

# ==========================================
# 1. Helpers: Math & Matrix Generation
# ==========================================
def next_power_of_2(n):
    return 1 if n == 0 else 2**(n - 1).bit_length()

def generate_hadamard(n):
    H = np.array([[1]])
    while H.shape[0] < n:
        H = np.vstack((np.hstack((H, H)), np.hstack((H, -H))))
    return H

# ==========================================
# 2. Antenna Dimensions & Hardware Setup
# ==========================================
rows = 4
cols = 19
total_trms = rows * cols

pulses_row = next_power_of_2(rows)
pulses_col = next_power_of_2(cols)
pulses_full = next_power_of_2(total_trms)
pulses_fast_total = pulses_row + pulses_col

# ==========================================
# 3. Phase Maps & Dynamic Range (DR) Math
# ==========================================
# Boresight Condition (All 0 degrees)
phase_boresight_deg = np.zeros((rows, cols))
phase_boresight_rad = np.radians(phase_boresight_deg)

# Geometric Coding (Randomized discrete 5-degree steps for DR suppression)
discrete_phases = np.arange(-180, 180, 5)
np.random.seed(42)
geo_phase_deg = np.random.choice(discrete_phases, size=(rows, cols))
geo_phase_rad = np.radians(geo_phase_deg)

# Hadamard Matrix for DR Math (128 pulses)
H_full = generate_hadamard(pulses_full)
H_active = H_full[:, :total_trms]

# Simulate Boresight Signal DR
weights_boresight = np.exp(1j * phase_boresight_rad.flatten())
signal_boresight = np.sum(H_active * weights_boresight, axis=1)
mag_boresight = np.abs(signal_boresight)
peak_boresight = np.max(mag_boresight)
dr_boresight_db = 20 * np.log10(peak_boresight / np.mean(mag_boresight[1:]))

# Set your target DR
dr_target = 5.8
discrete_phases = np.arange(-180, 180, 5)

print(f"Searching for a Geometric Phase Map with DR < {dr_target} dB...")

best_dr = 100.0
optimal_geo_phase_rad = None
attempts = 0

# Run until the target is met
while True:
    attempts += 1
    
    # 1. Generate random phase map (2D shape)
    current_geo_phase_deg = np.random.choice(discrete_phases, size=(rows, cols))
    current_geo_phase_rad = np.radians(current_geo_phase_deg)
    
    # 2. Simulate composite signal
    weights = np.exp(1j * current_geo_phase_rad.flatten())
    mag = np.abs(np.dot(H_active, weights))
    
    # 3. Calculate DR
    dr = 20 * np.log10(np.max(mag) / np.mean(mag))
    
    # 4. Track progress in console
    if dr < best_dr:
        best_dr = dr
        print(f"  -> New best DR found: {best_dr:.2f} dB (Attempt {attempts})")
        
    # 5. Check if target is met
    if dr < dr_target:
        optimal_geo_phase_rad = current_geo_phase_rad
        print(f"\n✓ Success! Reached DR of {dr:.2f} dB in {attempts} attempts.")
        
        # Save the 2D array to disk in the current script directory
        save_path = script_dir / "optimal_geo_phase_rad.npy"
        np.save(save_path, optimal_geo_phase_rad)
        
        print(f"✓ Phase map successfully saved to: {save_path}")
        
        # Override the main geo_phase_rad variable for the rest of your script
        geo_phase_rad = optimal_geo_phase_rad
        break

# Simulate Geometric Coding Signal DR
weights_geometric = np.exp(1j * geo_phase_rad.flatten())
signal_geometric = np.sum(H_active * weights_geometric, axis=1)
mag_geometric = np.abs(signal_geometric)
peak_geometric = np.max(mag_geometric)
dr_geometric_db = 20 * np.log10(peak_geometric / np.mean(mag_geometric))

# ==========================================
# 4. UNIFIED HARDWARE STATE (TX & RX)
# ==========================================
# Baseline Gain with 5% manufacturing error for both paths
gain_tx_base = np.random.normal(1.0, 0.05, size=(rows, cols))
gain_rx_base = np.random.normal(1.0, 0.05, size=(rows, cols))

# Inject Shared Hardware Failures (Completely dead TRMs)
shared_dead = [(1, 5), (2, 5), (2, 12), (3, 2)]
for r, c in shared_dead:
    gain_tx_base[r, c] = 0.0
    gain_rx_base[r, c] = 0.0

# Inject Independent Failures to demonstrate TX vs RX separation
gain_tx_base[0, 10] = 0.0  # Unique TX failure (e.g., blown HPA)
gain_rx_base[3, 15] = 0.0  # Unique RX failure (e.g., blown LNA)

# Binary truth maps for Dashboard Visualization
binary_truth_tx = np.where(gain_tx_base > 0.5, 1.0, 0.0)
binary_truth_rx = np.where(gain_rx_base > 0.5, 1.0, 0.0)

# Final Complex True States
complex_true_state_tx = gain_tx_base * np.exp(1j * geo_phase_rad)
complex_true_state_rx = gain_rx_base * np.exp(1j * geo_phase_rad)

# Flatten for module-level calculations
true_state_tx_flat = complex_true_state_tx.flatten()
true_state_rx_flat = complex_true_state_rx.flatten()

# ==========================================
# 5. Pre-Compute Clean Transmitted Signals
# ==========================================
H_row = generate_hadamard(pulses_row)
H_col = generate_hadamard(pulses_col)

# Row Encoding
rx_rows_clean = np.zeros(pulses_row, dtype=complex)
for p in range(pulses_row):
    coded_array = np.zeros((rows, cols), dtype=complex)
    for m in range(rows):
        coded_array[m, :] = complex_true_state_tx[m, :] * H_row[p, m]
    rx_rows_clean[p] = np.sum(coded_array)

# Column Encoding
rx_cols_clean = np.zeros(pulses_col, dtype=complex)
for p in range(pulses_col):
    coded_array = np.zeros((rows, cols), dtype=complex)
    for n in range(cols):
        coded_array[:, n] = complex_true_state_tx[:, n] * H_col[p, n]
    rx_cols_clean[p] = np.sum(coded_array)

# Full Module Encoding
rx_full_tx_clean = np.dot(H_active, true_state_tx_flat)
rx_full_rx_clean = np.dot(H_active, true_state_rx_flat)

# ==========================================
# 6. Multi-Iteration Simulation (100x)
# ==========================================
iterations = 100
noise_std_tx = 0.4  # Simulated thermal receiver noise
noise_std_rx = 1  # Simulated thermal receiver noise

# Storage arrays for all iterations
all_decoded_rows = np.zeros((iterations, rows), dtype=complex)
all_decoded_cols = np.zeros((iterations, cols), dtype=complex)
all_demod_tx = np.zeros((iterations, total_trms), dtype=complex)
all_demod_rx = np.zeros((iterations, total_trms), dtype=complex)

all_gain_tx = np.zeros((iterations, total_trms))
all_gain_rx = np.zeros((iterations, total_trms))
all_phase_tx = np.zeros((iterations, total_trms))
all_phase_rx = np.zeros((iterations, total_trms))

for i in range(iterations):
    # Add Independent Noise to Channels
    rx_rows_noisy = rx_rows_clean + (np.random.randn(pulses_row) + 1j * np.random.randn(pulses_row)) * noise_std_tx
    rx_cols_noisy = rx_cols_clean + (np.random.randn(pulses_col) + 1j * np.random.randn(pulses_col)) * noise_std_tx
    
    rx_pulses_tx = rx_full_tx_clean + (np.random.randn(pulses_full) + 1j * np.random.randn(pulses_full)) * noise_std_rx
    rx_pulses_rx = rx_full_rx_clean + (np.random.randn(pulses_full) + 1j * np.random.randn(pulses_full)) * noise_std_rx

    # Decode Row & Column using inverse Hadamard matrix
    dec_rows = np.dot(H_row.T, rx_rows_noisy) / pulses_row
    all_decoded_rows[i, :] = dec_rows[:rows]
    
    dec_cols = np.dot(H_col.T, rx_cols_noisy) / pulses_col
    all_decoded_cols[i, :] = dec_cols[:cols]

    # Decode Full Modules
    decoded_tx = np.dot(H_active.T, rx_pulses_tx) / pulses_full
    decoded_rx = np.dot(H_active.T, rx_pulses_rx) / pulses_full

    # Demodulate geometric phase
    demod_tx = decoded_tx * np.exp(-1j * geo_phase_rad.flatten())
    demod_rx = decoded_rx * np.exp(-1j * geo_phase_rad.flatten())
    all_demod_tx[i, :] = demod_tx
    all_demod_rx[i, :] = demod_rx

    # Calculate Gain (in dB) and Phase (in Degrees)
    all_gain_tx[i, :] = 20 * np.log10(np.abs(demod_tx) + 1e-12)
    all_gain_rx[i, :] = 20 * np.log10(np.abs(demod_rx) + 1e-12)
    all_phase_tx[i, :] = np.degrees(np.angle(demod_tx))
    all_phase_rx[i, :] = np.degrees(np.angle(demod_rx))

# Compute the mean over the 100 iterations
avg_decoded_rows = np.mean(all_decoded_rows, axis=0)
avg_decoded_cols = np.mean(all_decoded_cols, axis=0)
avg_demod_tx = np.mean(all_demod_tx, axis=0)
avg_demod_rx = np.mean(all_demod_rx, axis=0)

avg_gain_tx = np.mean(all_gain_tx, axis=0)
avg_gain_rx = np.mean(all_gain_rx, axis=0)
avg_phase_tx = np.mean(all_phase_tx, axis=0)
avg_phase_rx = np.mean(all_phase_rx, axis=0)

# ==========================================
# 7. Apply Diagnostics to 100x Averaged Data
# ==========================================
# Calculate Complex Error Vector Magnitude (EVM) for Rows
expected_row_complex = np.sum(np.exp(1j * geo_phase_rad), axis=1)
row_errors = np.abs(expected_row_complex - avg_decoded_rows)
degraded_rows = np.where(row_errors > 0.5)[0]

# Calculate Complex Error Vector Magnitude (EVM) for Cols
expected_col_complex = np.sum(np.exp(1j * geo_phase_rad), axis=0)
col_errors = np.abs(expected_col_complex - avg_decoded_cols)
degraded_cols = np.where(col_errors > 0.5)[0]

# Fast Diagnosis: Matrix Intersection
fast_diag_state = np.ones((rows, cols))
for r in degraded_rows:
    for c in degraded_cols:
        fast_diag_state[r, c] = 0.0

# Full Diagnosis Check (Thresholding from averaged complex demodulation)
# Evaluate TX Path
full_diag_state_tx = np.real(avg_demod_tx.reshape((rows, cols)))
full_diag_state_tx = np.where(full_diag_state_tx > 0.5, 1.0, 0.0)

# Evaluate RX Path
full_diag_state_rx = np.real(avg_demod_rx.reshape((rows, cols)))
full_diag_state_rx = np.where(full_diag_state_rx > 0.5, 1.0, 0.0)

# Combined Hardware Health: Module is considered healthy (1.0) ONLY if both TX and RX are healthy
full_diag_state = full_diag_state_tx * full_diag_state_rx

# ==========================================
# 8. FIGURE 1: Dynamic Range & Phase Maps
# ==========================================
COLORS = {
    "boresight": "#C62828", "geometric": "#2E8B57", "grid": "#DDDDDD",
    "healthy": "#2E8B57", "dead": "#C62828", "ghost": "#FFB300", 
    "bars": "#4C72B0", "bg_fail": "#C62828"
}

fig1 = plt.figure(figsize=(16, 14))
fig1.suptitle("TRM Calibration: Geometric Coding for Dynamic Range Suppression\n"
             f"(Array: {rows}x{cols} TRMs | Code Length: {pulses_full} Pulses)", 
             fontsize=18, fontweight='bold', y=0.97)

gs1 = fig1.add_gridspec(3, 1, height_ratios=[1.3, 1, 1], hspace=0.4)

# Line Plot (DR Suppression)
ax1_1 = fig1.add_subplot(gs1[0])
ax1_1.plot(mag_boresight, color=COLORS['boresight'], linestyle=':', linewidth=2.5, 
        label=f"Boresight (Constant Phase) | Peak: {peak_boresight:.0f} | DR: {dr_boresight_db:.1f} dB")
ax1_1.plot(mag_geometric, color=COLORS['geometric'], linestyle='-', linewidth=2, 
        label=f"Geometric Coding (Scattered) | Peak: {peak_geometric:.1f} | DR: {dr_geometric_db:.1f} dB")

ax1_1.set_xlabel("Pulse Index (Time)", fontsize=11, fontweight='bold')
ax1_1.set_ylabel("Composite Amplitude", fontsize=11, fontweight='bold')
ax1_1.set_xlim(0, pulses_full - 1)
ax1_1.set_ylim(0, total_trms + 5)
ax1_1.grid(color=COLORS['grid'], linestyle='--', linewidth=1)

ax1_1.annotate('Coherent Superposition Risk', xy=(0, peak_boresight), xytext=(10, peak_boresight - 15),
            arrowprops=dict(facecolor=COLORS['boresight'], shrink=0.05, width=1.5, headwidth=8),
            fontsize=11, fontweight='bold', color=COLORS['boresight'])
ax1_1.legend(loc="upper right", fontsize=11, framealpha=0.9, edgecolor='gray')

# Matrix Plot Formatting Helper
def format_matrix_plot(ax, matrix, title):
    im = ax.imshow(matrix, cmap='twilight_shifted', vmin=-180, vmax=180, aspect='auto')
    ax.set_title(title, fontsize=13, fontweight='bold', pad=10)
    ax.set_xlabel("Column Index", fontsize=10, fontweight='bold')
    ax.set_ylabel("Row Index", fontsize=10, fontweight='bold')
    ax.set_xticks(range(cols))
    ax.set_yticks(range(rows))
    ax.set_xticks(np.arange(-0.5, cols, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, rows, 1), minor=True)
    ax.grid(which='minor', color='black', linestyle='-', linewidth=0.5, alpha=0.5)
    ax.tick_params(axis='both', which='both', length=0)
    
    for r in range(rows):
        for c in range(cols):
            val = matrix[r, c]
            text_color = 'white' if abs(val) > 120 else 'black'
            ax.text(c, r, f"{val:.0f}°", color=text_color, ha='center', va='center', fontsize=9, fontweight='bold')
    return im

ax1_2 = fig1.add_subplot(gs1[1])
im1 = format_matrix_plot(ax1_2, phase_boresight_deg, "Boresight Baseline Phase Map (Causes Coherent Peak)")

ax1_3 = fig1.add_subplot(gs1[2])
im2 = format_matrix_plot(ax1_3, geo_phase_deg, "Geometric Coding Baseline Phase Map (Suppresses Coherent Peak)")

cbar_ax = fig1.add_axes([0.92, 0.12, 0.02, 0.45])
cbar = fig1.colorbar(im2, cax=cbar_ax)
cbar.set_label('Phase Shift (Degrees)', fontsize=12, fontweight='bold')
cbar.set_ticks([-180, -90, 0, 90, 180])
cbar.ax.set_yticklabels(['-180°', '-90°', '0°', '+90°', '+180°'])
fig1.subplots_adjust(left=0.08, right=0.88, top=0.92, bottom=0.06)

# ==========================================
# 9. FIGURE 2: TRM Diagnostics Dashboard (TX PATH)
# ==========================================
fig2 = plt.figure(figsize=(16, 12))
fig2.suptitle(f"Hadamard-Based TRM Health Monitoring (TX Path | Averaged over {iterations}x Iterations)\n"
             f"Antenna Array: {rows} $\\times$ {cols} | Fast Test: {pulses_fast_total} Pulses | Full Test: {pulses_full} Pulses", 
             fontsize=18, fontweight='bold', y=0.96)

gs2 = fig2.add_gridspec(3, 2, height_ratios=[1.4, 1, 1], hspace=0.35, wspace=0.25)
cmap_hw = ListedColormap([COLORS['dead'], COLORS['healthy']]) 
cmap_ghost = ListedColormap([COLORS['dead'], COLORS['ghost'], COLORS['healthy']])

def style_grid(ax):
    ax.set_xticks(np.arange(-0.5, cols, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, rows, 1), minor=True)
    ax.grid(which='minor', color=COLORS['grid'], linestyle='-', linewidth=0.8)
    ax.set_xticks(range(cols))
    ax.set_yticks(range(rows))
    ax.tick_params(axis='both', which='both', length=0, labelsize=9)

# --- Ax 1: True Hardware State (TX) ---
ax2_1 = fig2.add_subplot(gs2[0, :])
im2_1 = ax2_1.imshow(binary_truth_tx, cmap=cmap_hw, vmin=0, vmax=1)
ax2_1.set_title("True Hardware State (TX Path)", fontsize=14, fontweight='bold', pad=10)
style_grid(ax2_1)

for r in range(rows):
    for c in range(cols):
        sym = "✓" if binary_truth_tx[r, c] == 1 else "✗"
        ax2_1.text(c, r, sym, color='white', ha='center', va='center', fontsize=12, fontweight='bold')

# --- Ax 2: Row Diagnosis (Error Magnitude) ---
ax2_2 = fig2.add_subplot(gs2[1, 0])
bars_r = ax2_2.bar(range(rows), row_errors, color=COLORS['bars'], edgecolor='black', zorder=3)
ax2_2.axhline(0.5, color='black', linestyle='--', label='Fault Threshold (0.5)', zorder=4)
ax2_2.set_title(f"Row Diagnostic (Error Magnitude)\nHadamard Decoding ({pulses_row} Pulses)", fontsize=12, fontweight='bold')
ax2_2.set_xticks(range(rows))
ax2_2.set_ylim(0, max(2.0, np.max(row_errors) + 0.5))
ax2_2.grid(axis='y', color=COLORS['grid'], linestyle='--', zorder=0)
ax2_2.legend()

for r in range(rows):
    if r in degraded_rows:
        bars_r[r].set_color(COLORS['dead'])
        ax2_2.axvspan(r-0.5, r+0.5, color=COLORS['bg_fail'], alpha=0.1, zorder=1)
    ax2_2.text(bars_r[r].get_x() + bars_r[r].get_width()/2, bars_r[r].get_height() + 0.1,
             f"{bars_r[r].get_height():.2f}", ha='center', fontsize=10, fontweight='bold', rotation = 90)

# --- Ax 3: Column Diagnosis (Error Magnitude) ---
ax2_3 = fig2.add_subplot(gs2[1, 1])
bars_c = ax2_3.bar(range(cols), col_errors, color=COLORS['bars'], edgecolor='black', zorder=3)
ax2_3.axhline(0.5, color='black', linestyle='--', label='Fault Threshold (0.5)', zorder=4)
ax2_3.set_title(f"Column Diagnostic (Error Magnitude)\nHadamard Decoding ({pulses_col} Pulses)", fontsize=12, fontweight='bold')
ax2_3.set_xticks(range(cols))
ax2_3.set_ylim(0, max(2.0, np.max(col_errors) + 0.5))
ax2_3.grid(axis='y', color=COLORS['grid'], linestyle='--', zorder=0)
ax2_3.legend(loc='upper right', fontsize=9)

for c in range(cols):
    if c in degraded_cols:
        bars_c[c].set_color(COLORS['dead'])
        ax2_3.axvspan(c-0.5, c+0.5, color=COLORS['bg_fail'], alpha=0.1, zorder=1)
    ax2_3.text(bars_c[c].get_x() + bars_c[c].get_width()/2, bars_c[c].get_height() + 0.05,
             f"{bars_c[c].get_height():.2f}", ha='center', fontsize=9, fontweight='bold', rotation = 90)

# --- Ax 4: Fast Diagnosis (Intersection) ---
ghost_map = np.ones((rows, cols))
ghost_count = 0

for r in range(rows):
    for c in range(cols):
        if fast_diag_state[r, c] == 0:
            if binary_truth_tx[r, c] == 0.0:
                ghost_map[r, c] = 0.0  # Confirmed Dead
            else:
                ghost_map[r, c] = 0.5  # Ghost Candidate
                ghost_count += 1

ax2_4 = fig2.add_subplot(gs2[2, 0])
ax2_4.imshow(ghost_map, cmap=cmap_ghost, vmin=0, vmax=1)
ax2_4.set_title("Fast Diagnosis\n(Intersection Method)", fontsize=12, fontweight='bold')
style_grid(ax2_4)

for r in range(rows):
    for c in range(cols):
        val = ghost_map[r, c]
        if val == 1.0:
            ax2_4.text(c, r, '✓', color='white', ha='center', va='center', fontsize=12, fontweight='bold')
        elif val == 0.0:
            ax2_4.text(c, r, '✗', color='white', ha='center', va='center', fontsize=12, fontweight='bold')
        else:
            ax2_4.text(c, r, '?', color='black', ha='center', va='center', fontsize=12, fontweight='bold')

# --- Ax 5: Full Module Diagnosis ---
ax2_5 = fig2.add_subplot(gs2[2, 1])
ax2_5.imshow(full_diag_state, cmap=cmap_hw, vmin=0, vmax=1)
ax2_5.set_title("Accurate Module Diagnosis\n(Full Fallback Verification)", fontsize=12, fontweight='bold')
style_grid(ax2_5)

for r in range(rows):
    for c in range(cols):
        sym = "✓" if full_diag_state[r, c] == 1 else "✗"
        ax2_5.text(c, r, sym, color='white', ha='center', va='center', fontsize=12, fontweight='bold')

# --- Legends and Summary ---
legend_elements = [
    Patch(facecolor=COLORS['healthy'], edgecolor='black', label='✓ Healthy'),
    Patch(facecolor=COLORS['ghost'], edgecolor='black', label='? Ghost Candidate'),
    Patch(facecolor=COLORS['dead'], edgecolor='black', label='✗ Dead Module')
]
fig2.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(0.95, 0.95), fontsize=11, framealpha=1)

summary_text = (
    "Summary (TX Path)\n"
    "────────────────────────\n"
    f"TRMs               : {total_trms}\n"
    f"True Dead Modules  : {np.sum(binary_truth_tx == 0)}\n\n"
    f"Row Pulses         : {pulses_row}\n"
    f"Column Pulses      : {pulses_col}\n\n"
    f"Fast Test Total    : {pulses_fast_total} Pulses\n"
    f"Full Test Total    : {pulses_full} Pulses\n\n"
    f"Ghost Cells        : {ghost_count}\n"
    f"Confirmed Faults   : {np.sum(full_diag_state == 0)}"
)

fig2.text(0.85, 0.65, summary_text, fontsize=11, family='monospace',
         bbox=dict(facecolor='white', edgecolor='gray', boxstyle='round,pad=0.6', alpha=0.9))

# ==========================================
# 10. FIGURE 3: TRM Gain/Phase vs. Index
# ==========================================
fig3, axes = plt.subplots(2, 2, figsize=(18, 10))
fig3.suptitle(f"Active Phased Array TRM Diagnostics: TX vs RX\n(Averaged over {iterations} PN Gating Iterations)", 
             fontsize=16, fontweight='bold', y=0.96)

# Formatting Helper Function
def format_subplot(ax, x_data, y_data, title, y_label, y_lim, line_color):
    # Plot the averaged line
    ax.plot(x_data, y_data, marker='.', linestyle='-', color=line_color, linewidth=2.5, alpha=1.0, zorder=3)
    ax.axhline(0, color='black', linestyle='--', linewidth=1, zorder=2)
    ax.set_title(title, fontweight='bold')
    ax.set_xlabel("TRM Index Number")
    ax.set_ylabel(y_label)
    ax.set_ylim(y_lim)
    ax.set_xlim(0, total_trms - 1)
    ax.grid(True, linestyle=':', alpha=0.6, zorder=0)

trm_indices = np.arange(total_trms)

# --- Plot Average Gains ---
format_subplot(axes[0, 0], trm_indices, avg_gain_tx, 
               "Transmit (TX) Path Gain Variation", "Gain Deviation (dB)", 
               [-25, 2], '#C62828')
axes[0, 0].plot(trm_indices, all_gain_tx.T, marker='+', color='green', linestyle='None', alpha=0.15, zorder=1)

format_subplot(axes[0, 1], trm_indices, avg_gain_rx, 
               "Receive (RX) Path Gain Variation", "Gain Deviation (dB)", 
               [-25, 2], '#283593')
axes[0, 1].plot(trm_indices, all_gain_rx.T, marker='+', color='green', linestyle='None', alpha=0.15, zorder=1)

# --- Plot Average Phases ---
valid_tx = avg_gain_tx > -10
valid_rx = avg_gain_rx > -10

masked_ptx = np.where(valid_tx, avg_phase_tx, np.nan)
masked_prx = np.where(valid_rx, avg_phase_rx, np.nan)

masked_all_ptx = np.where(valid_tx, all_phase_tx, np.nan)
masked_all_prx = np.where(valid_rx, all_phase_rx, np.nan)

format_subplot(axes[1, 0], trm_indices, masked_ptx, 
               "Transmit (TX) Phase Deviation (Dead Masked)", "Phase Error (Degrees)", 
               [-20, 20], '#C62828')
axes[1, 0].plot(trm_indices, masked_all_ptx.T, marker='+', color='green', linestyle='None', alpha=0.15, zorder=1)

format_subplot(axes[1, 1], trm_indices, masked_prx, 
               "Receive (RX) Phase Deviation (Dead Masked)", "Phase Error (Degrees)", 
               [-20, 20], '#283593')
axes[1, 1].plot(trm_indices, masked_all_prx.T, marker='+', color='green', linestyle='None', alpha=0.15, zorder=1)

# --- Add Custom Legends ---
legend_tx = [Line2D([0], [0], color='#C62828', lw=2.5, marker='.', label='100x Average'),
             Line2D([0], [0], color='green', lw=0, marker='+', label='Raw Iterations')]
legend_rx = [Line2D([0], [0], color='#283593', lw=2.5, marker='.', label='100x Average'),
             Line2D([0], [0], color='green', lw=0, marker='+', label='Raw Iterations')]

axes[0, 0].legend(handles=legend_tx, loc='lower right', framealpha=0.9)
axes[1, 0].legend(handles=legend_tx, loc='lower right', framealpha=0.9)
axes[0, 1].legend(handles=legend_rx, loc='lower right', framealpha=0.9)
axes[1, 1].legend(handles=legend_rx, loc='lower right', framealpha=0.9)

plt.tight_layout(rect=[0, 0.03, 1, 0.93])

# ==========================================
# 11. SAVE THE IMAGES TO DISK
# ==========================================
# Save the figures as high-resolution PNGs in the script directory
fig1.savefig(f"{script_dir}/Insight_dynamic_range_suppression.png", bbox_inches='tight', dpi=300)
fig2.savefig(f"{script_dir}/Insight_dead_element_PN_gating.png", bbox_inches='tight', dpi=300)
fig3.savefig(f"{script_dir}/Insight_TX_RX_Gain_Phase.png", bbox_inches='tight', dpi=300)

print("Images successfully saved to the current directory.")

# Show all three figures simultaneously in the UI 
plt.close()
# plt.show()

# ==========================================
# 12. PRINT CONSOLE SUMMARY TABLE
# ==========================================
# Extract (x,y) coordinates for the INJECTED failures (Ground Truth)
tx_fails_injected = np.argwhere(binary_truth_tx == 0)
rx_fails_injected = np.argwhere(binary_truth_rx == 0)

# Extract (x,y) coordinates for the DETECTED failures (From Full 128-Pulse Check)
tx_fails_detected = np.argwhere(full_diag_state_tx == 0)
rx_fails_detected = np.argwhere(full_diag_state_rx == 0)

# Formatting helper to convert array of indices to a clean string
def format_coords(coords):
    return "[" + ", ".join([f"({r},{c})" for r, c in coords]) + "]"

print("\n" + "="*70)
print("             TRM CALIBRATION SIMULATION SUMMARY             ")
print("="*70)
print(f"Antenna Array Size         : {rows} rows x {cols} cols")
print(f"Total TRMs                 : {total_trms}")
print(f"Monte Carlo Iterations     : {iterations}")
print("-" * 70)
print("PULSES REQUIRED (PER ITERATION):")
print(f"  Row-Level Check          : {pulses_row}")
print(f"  Column-Level Check       : {pulses_col}")
print(f"  Fast Diagnosis Total     : {pulses_fast_total} (Row + Column)")
print(f"  Full Module Check Total  : {pulses_full}")
print("-" * 70)
print("HARDWARE DIAGNOSTIC RESULTS (TX vs RX):")
print(f"  Injected TX Failures     : {len(tx_fails_injected)} -> {format_coords(tx_fails_injected)}")
print(f"  Detected TX Faults       : {len(tx_fails_detected)} -> {format_coords(tx_fails_detected)}")
print("  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
print(f"  Injected RX Failures     : {len(rx_fails_injected)} -> {format_coords(rx_fails_injected)}")
print(f"  Detected RX Faults       : {len(rx_fails_detected)} -> {format_coords(rx_fails_detected)}")
print("  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
print(f"  Ghost Cells (Fast Test)  : {ghost_count}")
print("="*70 + "\n")

# ==========================================
# 13. CALCULATE AND PRINT 1-SIGMA STATS TABLE
# ==========================================
# Calculate the standard deviation (1-sigma) across the 100 iterations for each TRM
std_gain_tx = np.std(all_gain_tx, axis=0)
std_gain_rx = np.std(all_gain_rx, axis=0)
std_phase_tx = np.std(all_phase_tx, axis=0)
std_phase_rx = np.std(all_phase_rx, axis=0)

# Filter out dead modules to get accurate statistics for healthy TRMs only
valid_tx_idx = np.where(binary_truth_tx.flatten() == 1)[0]
valid_rx_idx = np.where(binary_truth_rx.flatten() == 1)[0]

# Calculate the mean 1-sigma standard deviation across all healthy TRMs
mean_std_gain_tx = np.mean(std_gain_tx[valid_tx_idx])
mean_std_gain_rx = np.mean(std_gain_rx[valid_rx_idx])
mean_std_phase_tx = np.mean(std_phase_tx[valid_tx_idx])
mean_std_phase_rx = np.mean(std_phase_rx[valid_rx_idx])

# Print the formatted table
print("\n" + "="*50)
print(f"{'1σ- Standard Deviation':<30} | {'Module Level':<15}")
print("="*50)
print(f"{'TX Amplitude':<30} | {mean_std_gain_tx:.3f} dB")
print(f"{'RX Amplitude':<30} | {mean_std_gain_rx:.3f} dB")
print("-" * 50)
print(f"{'TX Phase':<30} | {mean_std_phase_tx:.2f}°")
print(f"{'RX Phase':<30} | {mean_std_phase_rx:.2f}°")
print("="*50 + "\n")