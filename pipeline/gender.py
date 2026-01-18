import librosa
import numpy as np

def detect_gender(audio_path, start, end):
    y, sr = librosa.load(audio_path, sr=16000, offset=start, duration=end-start)
    pitches, mags = librosa.piptrack(y=y, sr=sr)
    pitch = np.mean(pitches[pitches > 0])

    if pitch == 0:
        return "unknown"
    return "male" if pitch < 165 else "female"
