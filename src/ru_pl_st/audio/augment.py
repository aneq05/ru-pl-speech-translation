from __future__ import annotations

import numpy as np


def add_noise_at_snr(signal: np.ndarray, noise: np.ndarray, snr_db: float) -> np.ndarray:
    """Mix noise into a signal at the requested SNR (dB)."""
    if signal.ndim != 1 or noise.ndim != 1:
        raise ValueError("Only mono waveforms are supported.")
    if len(noise) < len(signal):
        repeats = int(np.ceil(len(signal) / len(noise)))
        noise = np.tile(noise, repeats)
    noise = noise[: len(signal)]

    signal_power = float(np.mean(signal**2) + 1e-12)
    noise_power = float(np.mean(noise**2) + 1e-12)
    desired_noise_power = signal_power / (10 ** (snr_db / 10))
    scale = np.sqrt(desired_noise_power / noise_power)
    mixed = signal + scale * noise
    return mixed.astype(signal.dtype, copy=False)

