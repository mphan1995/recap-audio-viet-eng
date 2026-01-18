from typing import List, Optional, Tuple

from faster_whisper import WhisperModel


class WhisperASR:
    def __init__(
        self,
        model_name: str = "medium",
        device: str = "cpu",
        compute_type: str = "int8",
    ) -> None:
        self.model = WhisperModel(
            model_name,
            device=device,
            compute_type=compute_type,
        )

    def transcribe(
        self,
        audio_path: str,
        language: str = "auto",
        vad_filter: bool = False,
        beam_size: Optional[int] = None,
    ) -> Tuple[List[dict], Optional[str], Optional[float]]:
        kwargs = {}
        if language and language != "auto":
            kwargs["language"] = language
        if vad_filter:
            kwargs["vad_filter"] = True
        if beam_size:
            kwargs["beam_size"] = beam_size

        segments, info = self.model.transcribe(audio_path, **kwargs)
        results = []
        for seg in segments:
            results.append(
                {
                    "start": seg.start,
                    "end": seg.end,
                    "text": seg.text.strip(),
                }
            )
        detected_language = getattr(info, "language", None)
        language_prob = getattr(info, "language_probability", None)
        return results, detected_language, language_prob
