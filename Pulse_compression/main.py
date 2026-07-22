import sys
import os
import numpy as np
import matplotlib.pyplot as plt

# ============================================================================
# 1. Import Setup
# ============================================================================
# Add the parent directory (root folder) to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from pathlib import Path
from logger import setup_logging, get_logger

# ============================================================================
# 2. Configure Logger & Paths globally
# ============================================================================
# Define data_path so the script knows where to save the plot
data_path = current_dir

# Initialize the structlog logger globally
# Pass the directory path as a Path object; it will create 'processing.log' inside it
setup_logging(Path(data_path))
logger = get_logger("SAR_Analysis")
logger.info("Import successful!")

# ============================================================================
# 3. Constants & Functions
# ============================================================================
c = 3e8  # Speed of light (m/s)

def calc_range_resolution(bandwidth):
    """Calculate slant range resolution."""
    return c / (2 * bandwidth)

def calc_azimuth_resolution(antenna_length):
    """Calculate maximum achievable azimuth resolution for stripmap SAR."""
    return antenna_length / 2

# ============================================================================
# 4. Variable Arrays for Plotting
# ============================================================================
# Bandwidth array (from 10 MHz to 500 MHz)
bandwidths_Hz = np.linspace(10e6, 500e6, 100)
bandwidths_MHz = bandwidths_Hz / 1e6

# Antenna Length array (from 1 meter to 15 meters)
antenna_lengths_m = np.linspace(1, 15, 100)

# Calculate Resolutions
range_res = calc_range_resolution(bandwidths_Hz)
azimuth_res = calc_azimuth_resolution(antenna_lengths_m)

# ============================================================================
# 5. Log Information for the Reader
# ============================================================================
logger.info("=" * 70)
logger.info("SAR Resolution Parameter Analysis")
logger.info("=" * 70)
logger.info("RANGE RESOLUTION (Slant Range)")
logger.info("Formula: \u0394R = c / (2 * Bandwidth)")
logger.info("  - Dependent ONLY on Bandwidth.")
logger.info("  - Example: At 100 MHz, Resolution = %.2f meters", calc_range_resolution(100e6))
logger.info("  - Example: At 300 MHz, Resolution = %.2f meters", calc_range_resolution(300e6))
logger.info("-" * 70)
logger.info("AZIMUTH RESOLUTION (Along-Track)")
logger.info("Formula: \u0394AZ = L / 2  (where L is antenna length)")
logger.info("  - Counter-intuitively, smaller antennas yield finer resolution.")
logger.info("  - Independent of altitude or frequency/wavelength.")
logger.info("  - Example: 10m Antenna, Resolution = %.2f meters", calc_azimuth_resolution(10))
logger.info("  - Example: 3m Antenna, Resolution = %.2f meters", calc_azimuth_resolution(3))
logger.info("=" * 70)

# ============================================================================
# 6. Plotting the Graphs
# ============================================================================
plt.figure(figsize=(12, 5))

# --- Plot 1: Range Resolution vs Bandwidth ---
plt.subplot(1, 2, 1)
plt.plot(bandwidths_MHz, range_res, color='#b3261e', linewidth=2.5)
plt.title("Range Resolution vs. Bandwidth", fontsize=14, fontweight='bold')
plt.xlabel("Bandwidth (MHz)", fontsize=12)
plt.ylabel("Slant Range Resolution (meters)", fontsize=12)
plt.grid(True, linestyle='--', alpha=0.7)
plt.fill_between(bandwidths_MHz, range_res, color='#b3261e', alpha=0.1)
plt.text(250, 10, r'$\Delta R = \frac{c}{2B}$', fontsize=16, 
         bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))

# --- Plot 2: Azimuth Resolution vs Antenna Length ---
plt.subplot(1, 2, 2)
plt.plot(antenna_lengths_m, azimuth_res, color='#0b57d0', linewidth=2.5)
plt.title("Azimuth Resolution vs. Antenna Length", fontsize=14, fontweight='bold')
plt.xlabel("Physical Antenna Length (meters)", fontsize=12)
plt.ylabel("Azimuth Resolution (meters)", fontsize=12)
plt.grid(True, linestyle='--', alpha=0.7)
plt.fill_between(antenna_lengths_m, azimuth_res, color='#0b57d0', alpha=0.1)
plt.text(4, 5, r'$\Delta AZ = \frac{L}{2}$', fontsize=16, 
         bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))

plt.tight_layout(pad=3.0)

# ============================================================================
# 7. Save and Finish
# ============================================================================
filename = os.path.join(data_path, "SAR_Resolution_Analysis.png")
plt.savefig(filename, dpi=200, bbox_inches='tight')
plt.close()

logger.info("Plots generated successfully.")
logger.info(f"Figure saved to: {filename}")
logger.info("=" * 70)