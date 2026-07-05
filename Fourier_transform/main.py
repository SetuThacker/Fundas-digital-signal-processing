import os
import logging
import numpy as np
import matplotlib.pyplot as plt

# ============================================================================
# Create output directory
# ============================================================================
data_path = "GalaxEye/Fourier_transform"
os.makedirs(data_path, exist_ok=True)

# ============================================================================
# Configure Logger
# ============================================================================
log_file = os.path.join(data_path, "sampling.log")

logger = logging.getLogger("SamplingAnalysis")
logger.setLevel(logging.INFO)

# Clear handlers if script is run multiple times (e.g., in Jupyter)
if logger.hasHandlers():
    logger.handlers.clear()

formatter = logging.Formatter(
    "%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Console output
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# File output
file_handler = logging.FileHandler(log_file, mode="w")
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)

# ============================================================================
# Constants
# ============================================================================
c = 3e8

# ============================================================================
# Radar Parameters
# ============================================================================
BW = 120e6                 # Bandwidth (Hz)
Fs_ref = 360e6             # Reference sampling frequency (Hz)
Duty_cycle = 0.05
PRF = 5500                 # Pulse Repetition Frequency (Hz)

PRI = 1 / PRF
Tp = Duty_cycle * PRI

chirpRate = BW / Tp

rangeResolution = c / (2 * BW)
receivingWindow = PRI - Tp

num_samples = int(receivingWindow * Fs_ref)
N = int(Tp * Fs_ref)

# ============================================================================
# Reference Signal
# ============================================================================
dt_ref = 1 / Fs_ref
t_ref = np.arange(-Tp / 2, Tp / 2, dt_ref)

x_ref = np.exp(1j * np.pi * chirpRate * t_ref**2)

# ============================================================================
# Log Simulation Parameters
# ============================================================================
logger.info("=" * 70)
logger.info("Radar Simulation Parameters")
logger.info("=" * 70)
logger.info("Bandwidth              : %.2f MHz", BW / 1e6)
logger.info("Reference Fs           : %.2f MHz", Fs_ref / 1e6)
logger.info("Duty Cycle             : %.2f %%", Duty_cycle * 100)
logger.info("PRF                    : %.2f Hz", PRF)
logger.info("PRI                    : %.3f us", PRI * 1e6)
logger.info("Pulse Width            : %.3f us", Tp * 1e6)
logger.info("Chirp Rate             : %.3e Hz/s", chirpRate)
logger.info("Range Resolution       : %.3f m", rangeResolution)
logger.info("Receiving Window       : %.3f us", receivingWindow * 1e6)
logger.info("Reference Samples      : %d", len(t_ref))
logger.info("=" * 70)

# ============================================================================
# Sampling Frequency Multiples
# ============================================================================
Fs_multiples = [0.2, 0.5, 0.7, 1, 2, 3, 4, 5, 6, 7, 8]

for M in Fs_multiples:

    Fs = M * BW
    dt = 1 / Fs

    t = np.arange(-Tp / 2, Tp / 2, dt)

    x = np.exp(1j * np.pi * chirpRate * t**2)

    # Interpolate sampled signal to reference grid
    xr = np.interp(t_ref, t, np.real(x))
    xi = np.interp(t_ref, t, np.imag(x))

    x_rec = xr + 1j * xi

    error = np.linalg.norm(x_ref - x_rec)
    reference = np.linalg.norm(x_ref)

    captured = 100 * (1 - error / reference)

    logger.info(
        "Sampling = %4.1fx BW | Fs = %7.2f MHz | Samples = %5d | Reconstruction = %6.2f%%",
        M,
        Fs / 1e6,
        len(t),
        captured,
    )

    # ------------------------------------------------------------------------
    # Plot
    # ------------------------------------------------------------------------
    plt.figure(figsize=(10, 4))

    plt.subplot(1,2,1)

    # plt.plot(
    #     t_ref * 1e6,
    #     np.real(x_ref),
    #     linewidth=2,
    #     label="Reference"
    # )

    plt.plot(
        t * 1e6,
        np.real(x),
        "o-",
        markersize=4,
        label=f"{M}× BW ({Fs/1e6:.1f} MHz)"
    )

    plt.xlabel("Time (µs)")
    plt.ylabel("Amplitude")
    plt.title(f"Sampling at {M} × Bandwidth")
    plt.grid(True)
    plt.legend()

    plt.subplot(1,2,2)

    plt.plot(
        t * 1e6,
        np.real(np.fft.fftshift(np.fft.fft(x))),
        label=f"{M}× BW ({Fs/1e6:.1f} MHz)"
    )

    plt.xlabel("Time (µs)")
    plt.ylabel("Amplitude")
    plt.title(f"Chirp in Frequency Domain at {M} × Bandwidth")
    plt.grid(True)
    plt.legend()

    plt.tight_layout()

    filename = os.path.join(
        data_path,
        f"sampling_{M}xBandwidth.png"
    )

    plt.savefig(filename, dpi=200)
    plt.close()

    logger.info("Saved figure -> %s", filename)

# ============================================================================
# Finished
# ============================================================================
logger.info("=" * 70)
logger.info("Sampling analysis completed successfully.")
logger.info("Figures saved in : %s", data_path)
logger.info("Log file         : %s", log_file)
logger.info("=" * 70)