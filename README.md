# RECAP_MAX | Audio Recap System (VI / EN)

AI system to recap conversation audio with ASR, diarization, and optional GPT summary.

## Quick start
```bash
pip install -r requirements.txt
sudo apt install ffmpeg
export HF_TOKEN=xxx
export OPENAI_API_KEY=xxx
python web_app.py
```
Open `http://127.0.0.1:5000`.

## CLI
```bash
python app.py path/to/audio.wav --language vi
python app.py path/to/audio.wav --no-gpt
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
