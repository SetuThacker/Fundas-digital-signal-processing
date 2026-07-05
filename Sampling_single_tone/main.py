import numpy as np
import matplotlib.pyplot as plt

Fc = 100_000          # Carrier frequency (Hz)
Fs_ref = 1_000_000    # Reference sampling frequency (Hz)

# Reference signal
t_ref = np.arange(0, 1, 1/Fs_ref)
x_ref = np.exp(2j * np.pi * Fc * t_ref)

# Sampling-rate multiples of Fc
Fs_multiples = [0.2, 0.5, 0.7, 1, 2, 4, 8, 10, 16, 32]

for M in Fs_multiples:

    Fs = M * Fc                  # Actual sampling frequency
    dt = 1 / Fs

    t = np.arange(0, 1, dt)
    x = np.exp(2j * np.pi * Fc * t)

    # Interpolate sampled signal onto reference grid
    xr = np.interp(t_ref, t, np.real(x))
    xi = np.interp(t_ref, t, np.imag(x))
    x_rec = xr + 1j*xi

    error = np.linalg.norm(x_ref - x_rec)
    reference = np.linalg.norm(x_ref)

    captured = 100 * (1 - error/reference)

    print(f"{M:4.1f}×Fc : {captured:.2f}%")

    # print(f"Sampling = {M} × Fc ({Fs/1e3:.0f} kHz), "
    #       f"Samples = {len(x):7d}, Energy Difference = {energy_ref - energy:.6f}")

    plt.figure(figsize=(10,4))

    # Show only first 200 µs for clarity
    t_end = 200e-6

    plt.plot(
        t_ref[t_ref < t_end],
        np.real(x_ref[t_ref < t_end]),
        label="Reference",
        linewidth=1
    )

    plt.plot(
        t[t < t_end],
        np.real(x[t < t_end]),
        'o-',
        label=f"{M}×Fc ({Fs/1e3:.0f} kHz)"
    )

    plt.xlabel("Time (s)")
    plt.ylabel("Real{x(t)}")
    plt.title(f"Sampling at {M} × Fc")
    plt.grid(True)
    plt.legend()

    plt.tight_layout()
    plt.savefig(f"GalaxEye/Sampling_single_tone/sampling_{M}xFc.png", dpi=200)
    plt.close()