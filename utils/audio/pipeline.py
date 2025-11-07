import os
import uuid
import time
import soundfile as sf
from .loader import ensure_wav16k_mono
from .denoise import denoise
from .vad import apply_vad
from .metrics import snr_estimate

BASE_STORAGE = os.path.join(os.path.dirname(__file__), "../../storage")
os.makedirs(BASE_STORAGE, exist_ok=True)

def preprocess_to_wav(input_bytes_or_path, vad_aggr: int = 2):

    t0 = time.time()
    steps = {}
    
    # 1️⃣ Load audio 16kHz mono
    y, sr = ensure_wav16k_mono(input_bytes_or_path, sr_target=16000)
    steps["load_ms"] = int((time.time() - t0) * 1000)
    orig_seconds = float(len(y) / sr)
    
    # 2️⃣ VAD trước, để denoise tập trung vùng thoại
    t_vad = time.time()
    #y_vad, non_speech_mask = apply_vad(y, sr=sr, aggressiveness=vad_aggr)
    y_vad = y
    steps["vad_ms"] = int((time.time() - t_vad) * 1000)
    
    # 3️⃣ Denoise vùng thoại
    t_dn = time.time()
    disable_denoise = os.getenv("DISABLE_DENOISE", "0") == "1"
    if disable_denoise:
        y_dn = y_vad
    else:
        y_dn = denoise(y_vad, sr)
    steps["denoise_ms"] = int((time.time() - t_dn) * 1000)
    
    # 4️⃣ Estimate SNR sau denoise
    snr_db = snr_estimate(y_dn)
    
    # 5️⃣ Lưu file processed
    fname = f"clean_{uuid.uuid4().hex}.wav"
    out_path = os.path.join(BASE_STORAGE, fname)
    sf.write(out_path, y_dn, sr, subtype="PCM_16")
    
    total_ms = int((time.time() - t0) * 1000)
    analysis = {
        "sr": sr,
        "orig_seconds": round(orig_seconds, 3),
        "post_seconds": round(len(y_dn) / sr, 3),
        "snr_db": round(float(snr_db), 2),
        "processing_ms": total_ms,
        "steps": steps
    }
    return out_path, analysis
