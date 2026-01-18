import json
import os
import time
import uuid
from typing import Any, Dict, Optional, Tuple

from audio_processing.gender import detect_gender
from audio_processing.preprocess import preprocess_audio
from audio_processing.quality import compute_audio_metrics
from asr.whisper_asr import WhisperASR
from config.loader import get_setting, load_settings
from diarization.pyannote_diarizer import PyannoteDiarizer
from summarization.openai_summary import summarize_conversation
from utils.segment_utils import merge_segments


def run_recap(
    input_audio: str,
    language: str = "auto",
    use_diarization: bool = True,
    use_gpt: bool = True,
    job_dir: Optional[str] = None,
    settings: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    settings = settings or load_settings()
    job_id, job_dir = _resolve_job(job_dir)
    os.makedirs(job_dir, exist_ok=True)

    audio_cfg = settings.get("audio", {})
    clean_audio = os.path.join(job_dir, "clean.wav")

    timings = {}
    started = time.time()
    preprocess_audio(
        input_audio,
        clean_audio,
        sample_rate=int(audio_cfg.get("sample_rate", 16000)),
        mono=bool(audio_cfg.get("mono", True)),
        normalize=bool(audio_cfg.get("normalize", False)),
    )
    timings["preprocess_sec"] = _elapsed(started)

    quality = compute_audio_metrics(
        clean_audio,
        sample_rate=int(audio_cfg.get("sample_rate", 16000)),
        silence_threshold_db=float(audio_cfg.get("silence_threshold_db", -40.0)),
    )

    asr_cfg = settings.get("asr", {})
    asr = WhisperASR(
        model_name=str(asr_cfg.get("model", "medium")),
        device=str(asr_cfg.get("device", "cpu")),
        compute_type=str(asr_cfg.get("compute_type", "int8")),
    )

    started = time.time()
    transcripts, detected_language, language_prob = asr.transcribe(
        clean_audio,
        language=language or "auto",
        vad_filter=bool(asr_cfg.get("vad_filter", False)),
        beam_size=_maybe_int(asr_cfg.get("beam_size")),
    )
    timings["asr_sec"] = _elapsed(started)

    speakers = []
    if use_diarization:
        hf_token = os.getenv("HF_TOKEN")
        if not hf_token:
            raise ValueError("HF_TOKEN is required when diarization is enabled.")
        diar_cfg = settings.get("diarization", {})
        diarizer = PyannoteDiarizer(hf_token=hf_token)
        started = time.time()
        speakers = diarizer.run(
            clean_audio,
            min_speakers=_maybe_int(diar_cfg.get("min_speakers")),
            max_speakers=_maybe_int(diar_cfg.get("max_speakers")),
        )
        timings["diarization_sec"] = _elapsed(started)

    started = time.time()
    merged = merge_segments(
        transcripts,
        speakers,
        min_overlap_ratio=float(get_setting(settings, ["diarization", "min_overlap_ratio"], 0.2)),
    )
    timings["merge_sec"] = _elapsed(started)

    male_pitch_max = float(get_setting(settings, ["gender", "male_pitch_max"], 165.0))
    started = time.time()
    for segment in merged:
        segment["gender"] = detect_gender(
            clean_audio,
            segment["start"],
            segment["end"],
            male_pitch_max=male_pitch_max,
        )
    timings["gender_sec"] = _elapsed(started)

    recap_text = None
    if use_gpt:
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY is required when GPT is enabled.")
        gpt_cfg = settings.get("gpt", {})
        recap_text = summarize_conversation(
            merged,
            model=str(gpt_cfg.get("model", "gpt-4o-mini")),
            temperature=float(gpt_cfg.get("temperature", 0.2)),
            target_language=_map_language(language, detected_language),
        )

    result = {
        "job_id": job_id,
        "segments": merged,
        "recap": recap_text,
        "language": {
            "requested": language,
            "detected": detected_language,
            "confidence": language_prob,
        },
        "audio_metrics": quality,
        "timings": timings,
    }

    result_path = os.path.join(job_dir, "result.json")
    with open(result_path, "w", encoding="utf-8") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)

    return result


def _resolve_job(job_dir: Optional[str]) -> Tuple[str, str]:
    if job_dir:
        job_id = os.path.basename(job_dir.rstrip("/"))
        return job_id, job_dir
    job_id = uuid.uuid4().hex
    return job_id, os.path.join("data", "jobs", job_id)


def _map_language(requested: str, detected: Optional[str]) -> str:
    if requested in ("vi", "en"):
        return requested
    return detected or "auto"


def _maybe_int(value: Any) -> Optional[int]:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _elapsed(started: float) -> float:
    return float(time.time() - started)
