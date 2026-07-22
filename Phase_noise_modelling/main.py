import numpy as np
import matplotlib.pyplot as plt

def calculate_psl(phase_noise_db, psl_0=14.0):
    """
    Calculates the Peak Sidelobe Ratio (PSL) approximation.
    Based on the equation: PSL = PSL_0 * exp(-\Delta P * PSL_0)
    
    Parameters:
    phase_noise_db (array): Phase noise flat level in dB.
    psl_0 (float): The main lobe to highest side lobe ratio limit (approx 14 from Fig 5).
    """
    # Convert dB to linear scale for the exponential calculation
    phase_noise_linear = 10**(phase_noise_db / 10.0)
    
    # Calculate PSL
    psl = psl_0 * np.exp(-phase_noise_linear * psl_0)
    return psl

def calculate_resolution(phase_noise_db):
    """
    Calculates the relative resolution (\delta r) approximation.
    Based on the equation: \delta r = 1 + exp(\Delta P) / \Delta P
    
    Parameters:
    phase_noise_db (array): Phase noise flat level in dB.
    """
    # Convert dB to linear scale for the calculation
    phase_noise_linear = 10**(phase_noise_db / 10.0)
    
    # Calculate relative resolution
    # Note: Added a small epsilon to prevent division by absolute zero if it occurs
    delta_r = 1 + (np.exp(phase_noise_linear) / (phase_noise_linear + 1e-12))
    return delta_r

# Define the ranges for Delta P based on the figures in the document
# Fig 5 models PSL from -54 dB to -34 dB
delta_p_psl_range = np.linspace(-54, -34, 100) 

# Fig 6 models Relative Resolution from -90 dB to -30 dB
delta_p_res_range = np.linspace(-90, -30, 100)

# Compute values
psl_values = calculate_psl(delta_p_psl_range)
resolution_values = calculate_resolution(delta_p_res_range)

# Create the visualizations
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Plot 1: PSL vs Delta P
ax1.plot(delta_p_psl_range, psl_values, color='blue', label='Approximation')
ax1.set_title(r'Dependence of PSL on Phase Noise Flat Level ($\Delta$P)')
ax1.set_xlabel(r'$\Delta$P (dB)')
ax1.set_ylabel('PSL')
ax1.grid(True, linestyle='--', alpha=0.7)
ax1.legend()

# Plot 2: Relative Resolution vs Delta P
ax2.plot(delta_p_res_range, resolution_values, color='red', label='Approximation')
ax2.set_title(r'Dependence of Relative Resolution on Phase Noise Flat Level ($\Delta$P)')
ax2.set_xlabel(r'$\Delta$P (dB)')
ax2.set_ylabel(r'$\delta$r (Relative Resolution)')
ax2.grid(True, linestyle='--', alpha=0.7)
ax2.legend()

plt.tight_layout()
plt.show()