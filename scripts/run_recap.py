import os
from pipeline.preprocess import preprocess_audio
from pipeline.asr import ASR
from pipeline.diarization import Diarization
from pipeline.gender import detect_gender
from pipeline.merge import merge_segments
from pipeline.recap_ai import recap_conversation
import json

def run_recap(input_audio):
    os.makedirs("data/output", exist_ok=True)

    clean_audio = "data/output/clean.wav"
    preprocess_audio(input_audio, clean_audio)

    asr = ASR()
    transcripts = asr.transcribe(clean_audio)

    diar = Diarization(os.getenv("HF_TOKEN"))
    speakers = diar.run(clean_audio)

    merged = merge_segments(transcripts, speakers)

    for m in merged:
        m["gender"] = detect_gender(clean_audio, m["start"], m["end"])

    recap = recap_conversation(merged)

    result = {
        "segments": merged,
        "recap": recap
    }

    with open("data/output/result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print("✅ RECAP DONE → data/output/result.json")
