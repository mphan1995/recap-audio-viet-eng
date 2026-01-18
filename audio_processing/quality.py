from typing import Dict

import librosa
import numpy as np


def compute_audio_metrics(
    audio_path: str,
    sample_rate: int = 16000,
    silence_threshold_db: float = -40.0,
) -> Dict[str, float]:
    audio, sr = librosa.load(audio_path, sr=sample_rate, mono=True)
    if audio.size == 0:
        return {
            "duration_sec": 0.0,
            "mean_rms_dbfs": 0.0,
            "peak_dbfs": 0.0,
            "silence_ratio": 1.0,
            "clip_ratio": 0.0,
        }

    duration_sec = float(librosa.get_duration(y=audio, sr=sr))
    rms = librosa.feature.rms(y=audio)[0]
    rms_db = librosa.amplitude_to_db(rms, ref=1.0)
    mean_rms_dbfs = float(np.mean(rms_db))

    peak = float(np.max(np.abs(audio)))
    peak_dbfs = float(20 * np.log10(max(peak, 1e-9)))

    silence_ratio = float(np.mean(rms_db < silence_threshold_db))
    clip_ratio = float(np.mean(np.abs(audio) >= 0.999))

    return {
        "duration_sec": duration_sec,
        "mean_rms_dbfs": mean_rms_dbfs,
        "peak_dbfs": peak_dbfs,
        "silence_ratio": silence_ratio,
        "clip_ratio": clip_ratio,
    }
