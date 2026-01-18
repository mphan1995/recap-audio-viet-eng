import ffmpeg
import librosa
import numpy as np
import soundfile as sf

from audio_processing.denoise import reduce_noise


def preprocess_audio(
    input_path: str,
    output_path: str,
    sample_rate: int = 16000,
    mono: bool = True,
    normalize: bool = False,
    denoise: bool = False,
    trim_silence: bool = False,
    trim_db: float = 40.0,
    noise_duration_sec: float = 0.5,
) -> str:
    stream = ffmpeg.input(input_path)
    output_kwargs = {
        "ar": sample_rate,
        "format": "wav",
    }
    if mono:
        output_kwargs["ac"] = 1

    (
        stream.output(output_path, **output_kwargs)
        .overwrite_output()
        .run(quiet=True)
    )

    if normalize or denoise or trim_silence:
        audio, sr = sf.read(output_path)
        if audio.size == 0:
            return output_path
        if audio.ndim > 1:
            audio = np.mean(audio, axis=1)

        if trim_silence:
            audio, _ = librosa.effects.trim(audio, top_db=trim_db)

        if denoise:
            audio = reduce_noise(audio, sr=sr, noise_duration_sec=noise_duration_sec)

        if normalize:
            audio = _peak_normalize_audio(audio)

        sf.write(output_path, audio, sr)

    return output_path


def _peak_normalize_audio(audio: np.ndarray, target_peak: float = 0.99) -> np.ndarray:
    peak = float(np.max(np.abs(audio)))
    if peak <= 0:
        return audio
    return audio * (target_peak / peak)
