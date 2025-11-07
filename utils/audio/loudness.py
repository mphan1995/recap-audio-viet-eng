import numpy as np
import pyloudnorm as pyln

def loudness_normalize(y: np.ndarray, sr: int = 16000, target_lufs: float = -20.0) -> np.ndarray:
    """
    Chuẩn hoá loudness của tín hiệu về mức mục tiêu (LUFS -20 dB).
    Mục đích: đảm bảo biên độ ổn định để VAD & Denoise hoạt động chính xác.
    """
    try:
        meter = pyln.Meter(sr)  # EBU R128 loudness meter
        loudness = meter.integrated_loudness(y)
        gain_db = target_lufs - loudness
        gain = 10 ** (gain_db / 20.0)
        y_norm = y * gain
        y_norm = np.clip(y_norm, -1.0, 1.0)
        print(f"[INFO] Loudness normalized: {loudness:.2f} → {target_lufs} LUFS (gain {gain_db:+.2f} dB)")
        return np.ascontiguousarray(y_norm, dtype=np.float32)
    except Exception as e:
        print(f"[WARN] Loudness normalization skipped: {e}")
        return np.ascontiguousarray(y, dtype=np.float32)
