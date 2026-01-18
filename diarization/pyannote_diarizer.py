from typing import List, Optional

try:
    import torch
except ImportError:  # pragma: no cover
    torch = None


class PyannoteDiarizer:
    def __init__(self, hf_token: Optional[str], device: str = "auto") -> None:
        if not hf_token:
            raise ValueError("HF_TOKEN is required for diarization.")

        Pipeline = _load_pipeline()
        self.pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization",
            use_auth_token=hf_token,
        )
        resolved_device = _resolve_device(device)
        if torch and resolved_device:
            try:
                self.pipeline.to(torch.device(resolved_device))
            except Exception:
                pass

    def run(
        self,
        audio_path: str,
        min_speakers: Optional[int] = None,
        max_speakers: Optional[int] = None,
    ) -> List[dict]:
        diarization = self.pipeline(
            audio_path,
            min_speakers=min_speakers,
            max_speakers=max_speakers,
        )

        speakers = []
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            speakers.append(
                {
                    "speaker": speaker,
                    "start": float(turn.start),
                    "end": float(turn.end),
                }
            )

        speakers.sort(key=lambda item: item["start"])
        return speakers


def _load_pipeline():
    try:
        from pyannote.audio import Pipeline
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(
            "Failed to import pyannote. Ensure torch/torchaudio versions match "
            "your Python environment, or disable diarization."
        ) from exc
    return Pipeline


def _resolve_device(device: str) -> Optional[str]:
    if device and device != "auto":
        return device
    if torch and torch.cuda.is_available():
        return "cuda"
    return "cpu"
