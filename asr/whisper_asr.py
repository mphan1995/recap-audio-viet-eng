from typing import List, Optional, Tuple

from faster_whisper import WhisperModel

try:
    import torch
except ImportError:  # pragma: no cover
    torch = None


class WhisperASR:
    def __init__(
        self,
        model_name: str = "medium",
        device: str = "auto",
        compute_type: str = "auto",
    ) -> None:
        resolved_device = _resolve_device(device)
        resolved_compute = _resolve_compute_type(resolved_device, compute_type)
        self.model = WhisperModel(
            model_name,
            device=resolved_device,
            compute_type=resolved_compute,
        )
        self.device = resolved_device
        self.compute_type = resolved_compute

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


def _resolve_device(device: str) -> str:
    if device and device != "auto":
        return device
    if torch and torch.cuda.is_available():
        return "cuda"
    return "cpu"


def _resolve_compute_type(device: str, compute_type: str) -> str:
    if compute_type and compute_type != "auto":
        return compute_type
    return "float16" if device == "cuda" else "int8"
