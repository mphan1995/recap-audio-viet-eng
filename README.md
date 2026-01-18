# RECAP_MAX | Audio Recap System (VI / EN)

AI system to recap conversation audio with ASR, diarization, and optional GPT summary.

## Quick start
```bash
pip install -r requirements.txt
sudo apt install ffmpeg
# edit .env with your keys
python app.py serve
# or simply: python app.py
```
Open `http://127.0.0.1:5000`.

## CLI
```bash
python app.py run path/to/audio.wav --language vi
python app.py run path/to/audio.wav --no-gpt
```

## Project layout
```
audio_processing/   # preprocess + quality metrics
asr/                # speech-to-text
diarization/        # speaker diarization
nlp/                # prompt building
summarization/      # GPT summary
services/           # pipeline orchestration
routes/             # Flask blueprints
templates/          # UI pages
static/             # JS/CSS
config/             # settings.yaml
```

## Configuration
Edit `config/settings.yaml` to tune ASR model, diarization limits, and server upload size.

## Outputs
Each request writes results into `data/jobs/<job_id>/result.json`.

## Notes
- The system auto-selects CPU/GPU (ASR + diarization) via `device: auto`.
- If diarization fails with a `torchaudio` error, install a matching `torch`/`torchaudio` version for your Python environment.
