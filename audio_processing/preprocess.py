import ffmpeg
import numpy as np
import soundfile as sf


def preprocess_audio(
    input_path: str,
    output_path: str,
    sample_rate: int = 16000,
    mono: bool = True,
    normalize: bool = False,
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

    if normalize:
        _peak_normalize(output_path)

    return output_path


def _peak_normalize(path: str, target_peak: float = 0.99) -> None:
    audio, sr = sf.read(path)
    if audio.size == 0:
        return
    if audio.ndim > 1:
        audio = np.mean(audio, axis=1)
    peak = float(np.max(np.abs(audio)))
    if peak <= 0:
        return
    audio = audio * (target_peak / peak)
    sf.write(path, audio, sr)
