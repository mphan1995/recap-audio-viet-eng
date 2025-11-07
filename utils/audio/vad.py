import webrtcvad , os , numpy as np
from .loader import pcm16_bytes


BASE_STORAGE = os.path.join(os.path.dirname(__file__), "../../storage")
os.makedirs(BASE_STORAGE, exist_ok=True)

def apply_vad(y: np.ndarray, sr: int = 16000, aggressiveness: int = 2, frame_ms: int = 30):

    assert sr in (8000, 16000, 32000, 48000), "Unsupported sample ra te"

    vad = webrtcvad.Vad(aggressiveness)
    frame_len = int(sr * frame_ms / 1000)
    pad = int(0.06 * sr)  # 60 ms buffer

    pcm = pcm16_bytes(y)
    bytes_per_sample = 2
    bytes_per_frame = frame_len * bytes_per_sample

    speech_mask = np.zeros_like(y, dtype=bool)

    # 1️⃣ Đánh dấu frame có thoại
    for i in range(0, len(pcm), bytes_per_frame):
        frame = pcm[i:i + bytes_per_frame]
        if len(frame) < bytes_per_frame:
            break
        idx_start = i // bytes_per_sample
        idx_end = min(idx_start + frame_len, y.size)

        if vad.is_speech(frame, sample_rate=sr):
            start = max(0, idx_start - pad)
            end = min(y.size, idx_end + pad)
            speech_mask[start:end] = True

    # 2️⃣ Nối các đoạn nói gần nhau (< 0.3 s)
    min_gap = int(0.3 * sr)
    if np.any(speech_mask):
        speech_regions = np.where(speech_mask)[0]
        prev_idx = speech_regions[0]
        for idx in speech_regions[1:]:
            if idx - prev_idx < min_gap:
                speech_mask[prev_idx:idx] = True
            prev_idx = idx

    # 3️⃣ Nếu không phát hiện thoại, trả nguyên audio
    if not np.any(speech_mask):
        return y, np.ones_like(y, dtype=bool)

    # 4️⃣ Cắt vùng thoại
    y_vad = y[speech_mask]
    non_speech_mask = ~speech_mask
    return y_vad, non_speech_mask