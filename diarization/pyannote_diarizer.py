from typing import List, Optional

from pyannote.audio import Pipeline


class PyannoteDiarizer:
    def __init__(self, hf_token: Optional[str]) -> None:
        if not hf_token:
            raise ValueError("HF_TOKEN is required for diarization.")
        self.pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization",
            use_auth_token=hf_token,
        )

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
