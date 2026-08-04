import numpy as np
import matplotlib.pyplot as plt
import os

# ==========================================
# 1. System Parameters & Beamforming
# ==========================================
f_c = 9.6e9
wavelength = 3e8 / f_c
k = 2 * np.pi / wavelength
dx = dy = wavelength / 2  # Half-wavelength spacing

no_of_rows = 4
no_of_cols = 19  # 7 + 4 + 7

# Target Steering Angles
target_az_deg = 1.0
target_el_deg = 0.0
target_az_rad = np.radians(target_az_deg)
target_el_rad = np.radians(target_el_deg)

col_indices = np.arange(no_of_cols)
row_indices = np.arange(no_of_rows)
x_grid, y_grid = np.meshgrid(col_indices * dx, row_indices * dy)

# Commanded TRM weights
trm_phase = -k * (x_grid * np.sin(target_az_rad) + y_grid * np.sin(target_el_rad))
x_mn = 1.0 * np.exp(1j * trm_phase)

# ==========================================
# 2. Compute 2D Far-Field Pattern
# ==========================================
az_angles = np.linspace(-20, 20, 400)
el_angles = np.linspace(-40, 40, 400)
alpha = np.radians(az_angles)
epsilon = np.radians(el_angles)

E_pattern = np.zeros((len(el_angles), len(az_angles)), dtype=complex)

for m in range(no_of_rows):
    for n in range(no_of_cols):
        az_delay = np.exp(1j * k * np.sin(alpha) * (n * dx))
        el_delay = np.exp(1j * k * np.sin(epsilon) * (m * dy))
        spatial_delay_2d = np.outer(el_delay, az_delay)
        E_pattern += x_mn[m, n] * spatial_delay_2d

power_pattern_db = 10 * np.log10(np.abs(E_pattern)**2 / np.max(np.abs(E_pattern)**2))

# ==========================================
# 3. Extract 1D Azimuth and Range Cuts
# ==========================================
# Find the array indices closest to our target angles
target_az_idx = np.argmin(np.abs(az_angles - target_az_deg))
target_el_idx = np.argmin(np.abs(el_angles - target_el_deg))

# Slice the 2D matrix to get 1D curves
azimuth_cut = power_pattern_db[target_el_idx, :]  # Hold elevation constant at 0 deg
range_cut = power_pattern_db[:, target_az_idx]    # Hold azimuth constant at 1 deg

# ==========================================
# 4. Visualization & Saving Curves
# ==========================================
# Create a figure with two subplots side-by-side
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# --- Plot 1: Azimuth Cut ---
ax1.plot(az_angles, azimuth_cut, color='blue', linewidth=2)
ax1.axvline(x=target_az_deg, color='red', linestyle='--', label=f'Peak ({target_az_deg}°)')
ax1.set_title(f'Azimuth Cut (at Elevation = {target_el_deg}°)', fontsize=12)
ax1.set_xlabel('Azimuth Angle (Degrees)', fontsize=10)
ax1.set_ylabel('Normalized Power (dB)', fontsize=10)
ax1.set_xlim([-20, 20])
ax1.set_ylim([-30, 0])
ax1.grid(True, linestyle=':', alpha=0.7)
ax1.legend()

# --- Plot 2: Range (Elevation) Cut ---
ax2.plot(el_angles, range_cut, color='green', linewidth=2)
ax2.axvline(x=target_el_deg, color='red', linestyle='--', label=f'Peak ({target_el_deg}°)')
ax2.set_title(f'Range / Elevation Cut (at Azimuth = {target_az_deg}°)', fontsize=12)
ax2.set_xlabel('Elevation Angle (Degrees)', fontsize=10)
ax2.set_ylabel('Normalized Power (dB)', fontsize=10)
ax2.set_xlim([-40, 40])
ax2.set_ylim([-30, 0])
ax2.grid(True, linestyle=':', alpha=0.7)
ax2.legend()

plt.tight_layout()

# Save the 1D cuts to a file
cuts_filename = 'antenna_1D_cuts.png'
plt.savefig(cuts_filename, dpi=300, bbox_inches='tight')
print(f"Successfully saved 1D curves to: {os.path.abspath(cuts_filename)}")

# Show the plots
plt.show()