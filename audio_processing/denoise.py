from typing import Optional

import numpy as np

try:
    import noisereduce as nr
except ImportError:  # pragma: no cover
    nr = None


def reduce_noise(
    audio: np.ndarray,
    sr: int,
    noise_duration_sec: float = 0.5,
) -> np.ndarray:
    if nr is None:
        return audio
    if audio.size == 0:
        return audio

    noise_samples = int(sr * max(noise_duration_sec, 0.0))
    if noise_samples <= 0 or noise_samples >= audio.shape[0]:
        return audio

    noise_clip = audio[:noise_samples]
    return nr.reduce_noise(y=audio, y_noise=noise_clip, sr=sr)
