import io
import numpy as np
import librosa
import soundfile as sf
import tempfile

def ensure_wav16k_mono(input_bytes_or_path, sr_target=16000):
    """Load mọi loại audio (mp3, wav, m4a, etc.) -> float32 mono 16kHz array [-1, 1]."""
    try:
        # Nếu là object tạm (SpooledTemporaryFile)
        if hasattr(input_bytes_or_path, "read"):
            data = input_bytes_or_path.read()
            input_bytes_or_path.seek(0)
            with tempfile.NamedTemporaryFile(suffix=".m4a", delete=False) as tmp:
                tmp.write(data)
                tmp.flush()
                path = tmp.name
                y, sr = librosa.load(path, sr=sr_target, mono=True)
        elif isinstance(input_bytes_or_path, (bytes, bytearray, io.BytesIO)):
            y, sr = librosa.load(io.BytesIO(input_bytes_or_path), sr=sr_target, mono=True)
        else:
            y, sr = librosa.load(input_bytes_or_path, sr=sr_target, mono=True)
    except Exception:
        # fallback bằng soundfile (nếu librosa không đọc được)
        input_bytes_or_path.seek(0)
        data, sr = sf.read(input_bytes_or_path)
        if len(data.shape) > 1:
            data = np.mean(data, axis=1)
        y = librosa.resample(data.astype(np.float32), orig_sr=sr, target_sr=sr_target)
        sr = sr_target

    return np.ascontiguousarray(y, dtype=np.float32), sr

def pcm16_bytes(y: np.ndarray) -> bytes:
    y = np.clip(y, -1.0, 1.0)
    pcm = (y * 32767.0).astype(np.int16)
    return pcm.tobytes()
