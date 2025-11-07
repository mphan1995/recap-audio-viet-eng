import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret")
    # ASR
    WHISPER_MODEL = os.environ.get("WHISPER_MODEL", "medium")  # tiny/base/small/medium/large-v3
    WHISPER_DEVICE = os.environ.get("WHISPER_DEVICE", "auto")   # auto/cpu/cuda
    WHISPER_COMPUTE = os.environ.get("WHISPER_COMPUTE", "int8_float16")
    WHISPER_BEAM_SIZE = int(os.environ.get("WHISPER_BEAM_SIZE", 5))

    # Preprocess
    VAD_AGGRESSIVENESS = int(os.environ.get("VAD_AGGRESSIVENESS", 2))  # 0-3
    MAX_AUDIO_SECONDS = int(os.environ.get("MAX_AUDIO_SECONDS", 1800))

    # Summary
    DEFAULT_SUMMARY_LANG = os.environ.get("DEFAULT_SUMMARY_LANG", "auto")  # vi/en/auto
