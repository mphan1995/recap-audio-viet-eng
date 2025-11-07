import numpy as np

def snr_estimate(y: np.ndarray, noise_mask=None) -> float:
    """Ước lượng SNR (dB). If noise_mask None, dùng 10% biên độ nhỏ nhất làm noise."""
    eps = 1e-9
    if noise_mask is not None and getattr(noise_mask, "any", lambda: False)():
        noise = y[noise_mask]
    else:
        k = max(1, int(0.1 * y.size))
        idx = np.argpartition(np.abs(y), k)[:k]
        noise = y[idx]
    p_signal = float(np.mean(y ** 2) + eps)
    p_noise = float(np.mean(noise ** 2) + eps)
    return 10.0 * np.log10(p_signal / p_noise)
