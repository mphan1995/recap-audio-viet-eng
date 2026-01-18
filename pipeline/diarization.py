from pyannote.audio import Pipeline
import os

class Diarization:
    def __init__(self, hf_token):
        self.pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization",
            use_auth_token=hf_token
        )

    def run(self, audio_path):
        diarization = self.pipeline(audio_path)
        speakers = []

        for turn, _, speaker in diarization.itertracks(yield_label=True):
            speakers.append({
                "speaker": speaker,
                "start": turn.start,
                "end": turn.end
            })
        return speakers
