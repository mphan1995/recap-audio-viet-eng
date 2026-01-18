import os
import uuid

from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename

from services.recap_service import run_recap


recap_bp = Blueprint("recap", __name__)

ALLOWED_EXTENSIONS = {".wav", ".mp3", ".m4a", ".flac", ".ogg", ".webm"}


def _is_allowed(filename: str) -> bool:
    _, ext = os.path.splitext(filename.lower())
    return ext in ALLOWED_EXTENSIONS


def _parse_bool(value: str) -> bool:
    return str(value).lower() in ("1", "true", "yes", "on")


@recap_bp.route("/api/recap", methods=["POST"])
def recap_api():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if not file or not file.filename:
        return jsonify({"error": "Empty filename"}), 400

    filename = secure_filename(file.filename)
    if not _is_allowed(filename):
        return jsonify({"error": "Unsupported file type"}), 400

    job_id = uuid.uuid4().hex
    job_dir = os.path.join("data", "jobs", job_id)
    os.makedirs(job_dir, exist_ok=True)
    input_path = os.path.join(job_dir, filename)
    file.save(input_path)

    language = request.form.get("language", "auto")
    use_diarization = _parse_bool(request.form.get("diarization", "true"))
    use_gpt = _parse_bool(request.form.get("gpt", "true"))
    vad_filter = _parse_bool(request.form.get("vad_filter", "false"))
    normalize = _parse_bool(request.form.get("normalize", "false"))
    denoise = _parse_bool(request.form.get("denoise", "false"))
    trim_silence = _parse_bool(request.form.get("trim_silence", "false"))
    min_speakers = _parse_int(request.form.get("min_speakers"))
    max_speakers = _parse_int(request.form.get("max_speakers"))
    beam_size = _parse_int(request.form.get("beam_size"))

    overrides = _build_overrides(
        normalize=normalize,
        denoise=denoise,
        trim_silence=trim_silence,
        vad_filter=vad_filter,
        min_speakers=min_speakers,
        max_speakers=max_speakers,
        beam_size=beam_size,
    )

    try:
        result = run_recap(
            input_path,
            language=language,
            use_diarization=use_diarization,
            use_gpt=use_gpt,
            job_dir=job_dir,
            settings_override=overrides,
        )
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(result)


def _parse_int(value):
    if value in (None, ""):
        return None
    try:
        return int(value)
    except ValueError:
        return None


def _build_overrides(
    normalize: bool,
    denoise: bool,
    trim_silence: bool,
    vad_filter: bool,
    min_speakers: int,
    max_speakers: int,
    beam_size: int,
):
    overrides = {"audio": {}, "asr": {}, "diarization": {}}
    overrides["audio"]["normalize"] = normalize
    overrides["audio"]["denoise"] = denoise
    overrides["audio"]["trim_silence"] = trim_silence
    overrides["asr"]["vad_filter"] = vad_filter
    if beam_size is not None:
        overrides["asr"]["beam_size"] = beam_size
    if min_speakers is not None:
        overrides["diarization"]["min_speakers"] = min_speakers
    if max_speakers is not None:
        overrides["diarization"]["max_speakers"] = max_speakers

    return {k: v for k, v in overrides.items() if v}
