import os
import numpy as np
import noisereduce as nr
from .loudness import loudness_normalize  # giữ như bạn đang dùng
def denoise(
    y: np.ndarray,
    sr: int = 16000,
    *,
    max_seconds: int = 60,      # >60s thì bỏ qua denoise để nhanh
    chunk_sec: float = 15.0,    # xử lý theo khối 15s
    overlap_sec: float = 0.5    # chồng lấn 0.5s để crossfade mượt
) -> np.ndarray:
    """
    Denoise bằng noisereduce (tuned for speech) + chuẩn hoá loudness.
    - Skip cho file dài để tránh treo (bước 4).
    - Xử lý theo chunk để giảm tải FFT.
    """

    # 0) Chuẩn hoá âm lượng (rất rẻ, nên luôn làm)
    y = loudness_normalize(y, sr)
    dur = len(y) / sr

    # Cho phép tắt bằng ENV
    if os.getenv("DISABLE_DENOISE", "0") == "1":
        print("[INFO] Denoise disabled by ENV")
        return np.ascontiguousarray(y, dtype=np.float32)

    # 1) Bỏ qua với file dài
    if dur > max_seconds:
        print(f"[INFO] Denoise skipped (len={dur:.1f}s > {max_seconds}s)")
        return np.ascontiguousarray(y, dtype=np.float32)

    # 2) Denoise theo chunk để tránh treo
    print("[INFO] Using noisereduce (tuned for speech, chunked)")
    n = len(y)
    win = int(chunk_sec * sr)
    ov  = int(overlap_sec * sr)
    hop = max(1, win - ov)

    out = np.zeros_like(y, dtype=np.float32)
    wsum = np.zeros_like(y, dtype=np.float32)

    i = 0
    while i < n:
        start = i
        end = min(i + win, n)
        y_chunk = y[start:end]

        try:
            y_dn = nr.reduce_noise(
                y=y_chunk,
                sr=sr,
                stationary=False,
                prop_decrease=0.7,           # giảm nhẹ để đỡ méo giọng
                time_constant_s=0.5,
                freq_mask_smooth_hz=300,
                n_std_thresh_stationary=1.5,
            ).astype(np.float32, copy=False)
        except Exception as e:
            print(f"[WARN] noisereduce failed on chunk {start}:{end} -> {e}")
            y_dn = y_chunk.astype(np.float32, copy=False)

        # crossfade trọng số ở biên để ghép mượt
        L = end - start
        w = np.ones(L, dtype=np.float32)
        if start > 0:
            a = min(ov, L)
            w[:a] *= np.linspace(0.0, 1.0, a, dtype=np.float32)
        if end < n:
            a = min(ov, L)
            w[-a:] *= np.linspace(1.0, 0.0, a, dtype=np.float32)

        out[start:end] += y_dn * w
        wsum[start:end] += w

        i += hop

    mask = wsum > 1e-9
    out[mask] /= wsum[mask]

    return np.ascontiguousarray(out, dtype=np.float32)
