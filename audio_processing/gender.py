import librosa
import numpy as np


def detect_gender(audio_path: str, start: float, end: float, male_pitch_max: float = 165.0) -> str:
    duration = max(0.0, end - start)
    if duration < 0.2:
        return "unknown"

    audio, sr = librosa.load(audio_path, sr=16000, offset=start, duration=duration, mono=True)
    if audio.size == 0:
        return "unknown"

    pitches, mags = librosa.piptrack(y=audio, sr=sr)
    voiced = pitches[mags > np.median(mags)]
    if voiced.size == 0:
        return "unknown"

    pitch = float(np.mean(voiced[voiced > 0])) if np.any(voiced > 0) else 0.0
    if pitch <= 0:
        return "unknown"

    return "male" if pitch < male_pitch_max else "female"
