from faster_whisper import WhisperModel

class ASR:
    def __init__(self, model_name="medium"):
        self.model = WhisperModel(
            model_name,
            device="cpu",
            compute_type="int8"
        )

    def transcribe(self, audio_path):
        segments, info = self.model.transcribe(audio_path)
        results = []
        for seg in segments:
            results.append({
                "start": seg.start,
                "end": seg.end,
                "text": seg.text.strip()
            })
        return results
