import numpy as np
import matplotlib.pyplot as plt

# --- 1. Radar System Parameters ---
PRF = 1000.0  # Pulse Repetition Frequency (Hz)
num_pulses = 256  # Number of slow-time pulses (Azimuth)
slow_time = np.arange(num_pulses) / PRF

# --- 2. Simulate the Signals ---
# A: Actual Earth Echo (Pure, uncorrupted slow-time curve)
doppler_freq = 20.0  # Earth's relative Doppler shift
actual_earth_echo = np.exp(1j * 2 * np.pi * doppler_freq * slow_time)

# B: Calibration Signal (Azimuth Encoding: +1, -1, +1, -1)
azimuth_code = np.array([1 if i % 2 == 0 else -1 for i in range(num_pulses)])
actual_cal_signal = 0.5 * azimuth_code

# C: Mixed Signal (Slow time curve with azimuth encoding + noise)
noise = 0.1 * (np.random.randn(num_pulses) + 1j * np.random.randn(num_pulses))
mixed_signal = actual_earth_echo + actual_cal_signal + noise

# --- 3. The Digital Scalpel (FFT & Filtering) ---
# Calculate FFTs
fft_earth_pure = np.fft.fftshift(np.fft.fft(actual_earth_echo))
fft_mixed = np.fft.fftshift(np.fft.fft(mixed_signal))
frequencies = np.fft.fftshift(np.fft.fftfreq(num_pulses, d=1/PRF))

# Design Filters
edge_width = 40  # Bandwidth at the edges to isolate the calibration signal
filter_echo = np.ones(num_pulses)
filter_echo[:edge_width] = 0
filter_echo[-edge_width:] = 0

filter_cal = np.zeros(num_pulses)
filter_cal[:edge_width] = 1
filter_cal[-edge_width:] = 1

# Apply Filters
fft_extracted_echo = fft_mixed * filter_echo
fft_extracted_cal = fft_mixed * filter_cal

# Calculate IFFT
extracted_earth_echo = np.fft.ifft(np.fft.ifftshift(fft_extracted_echo))
extracted_cal_signal = np.fft.ifft(np.fft.ifftshift(fft_extracted_cal))

# --- 4. Visualization ---
plt.figure(figsize=(16, 14))
plt.suptitle("Azimuth Encoding Modulation & Digital Filtering Workflow", fontsize=18, fontweight='bold')
t_disp = 50  # Display only the first 50 pulses for time-domain clarity

# Row 1: Time Domain Curves
plt.subplot(4, 2, 1)
plt.title("1A. Actual Slow-Time Curve (Pure Earth Echo)")
plt.plot(slow_time[:t_disp], np.real(actual_earth_echo[:t_disp]), color='black', linewidth=2)
plt.xlabel("Slow Time (s)")
plt.ylabel("Amplitude")
plt.grid(True)

plt.subplot(4, 2, 2)
plt.title("1B. Slow-Time Curve with Azimuth Encoding (Mixed + Noise)")
plt.plot(slow_time[:t_disp], np.real(mixed_signal[:t_disp]), color='purple', linewidth=2)
plt.xlabel("Slow Time (s)")
plt.grid(True)

# Row 2: Frequency Domain (FFT)
plt.subplot(4, 2, 3)
plt.title("2A. FFT of Pure Earth Echo")
plt.plot(frequencies, np.abs(fft_earth_pure), color='black')
plt.xlabel("Doppler Frequency (Hz)")
plt.ylabel("Magnitude")
plt.grid(True)

plt.subplot(4, 2, 4)
plt.title("2B. FFT of Mixed Signal (Echo + Encoded Cal)")
plt.plot(frequencies, np.abs(fft_mixed), color='purple')
plt.xlabel("Doppler Frequency (Hz)")
plt.grid(True)

# Row 3: Filter Profiles
plt.subplot(4, 2, 5)
plt.title("3A. Notch Filter Applied (Extracting Echo)")
plt.plot(frequencies, np.abs(fft_mixed), color='lightgray', label='Mixed FFT')
plt.plot(frequencies, filter_echo * np.max(np.abs(fft_mixed)), color='green', linestyle='--', label='Echo Filter Shape')
plt.fill_between(frequencies, 0, np.abs(fft_extracted_echo), color='green', alpha=0.5, label='Filtered Echo Spectrum')
plt.xlabel("Doppler Frequency (Hz)")
plt.ylabel("Magnitude")
plt.legend(loc='upper right')
plt.grid(True)

plt.subplot(4, 2, 6)
plt.title("3B. Bandpass Filter Applied (Extracting Cal)")
plt.plot(frequencies, np.abs(fft_mixed), color='lightgray', label='Mixed FFT')
plt.plot(frequencies, filter_cal * np.max(np.abs(fft_mixed)), color='orange', linestyle='--', label='Cal Filter Shape')
plt.fill_between(frequencies, 0, np.abs(fft_extracted_cal), color='orange', alpha=0.5, label='Filtered Cal Spectrum')
plt.xlabel("Doppler Frequency (Hz)")
plt.legend(loc='upper center')
plt.grid(True)

# Row 4: Final Extracted Results (IFFT)
plt.subplot(4, 2, 7)
plt.title("4A. Recovered Earth Echo vs Actual (Time Domain)")
plt.plot(slow_time[:t_disp], np.real(actual_earth_echo[:t_disp]), color='black', linewidth=3, label='Actual Echo', alpha=0.4)
plt.plot(slow_time[:t_disp], np.real(extracted_earth_echo[:t_disp]), color='green', linewidth=2, linestyle='--', label='Extracted Echo')
plt.xlabel("Slow Time (s)")
plt.ylabel("Amplitude")
plt.legend()
plt.grid(True)

plt.subplot(4, 2, 8)
plt.title("4B. Recovered Cal Signal vs Actual (Time Domain)")
plt.plot(slow_time[:t_disp], np.real(actual_cal_signal[:t_disp]), color='black', drawstyle='steps-mid', linewidth=3, label='Actual Cal', alpha=0.4)
plt.plot(slow_time[:t_disp], np.real(extracted_cal_signal[:t_disp]), color='orange', drawstyle='steps-mid', linewidth=2, linestyle='--', label='Extracted Cal')
plt.xlabel("Slow Time (s)")
plt.legend()
plt.grid(True)

plt.tight_layout(rect=[0, 0.03, 1, 0.96])
plt.show()