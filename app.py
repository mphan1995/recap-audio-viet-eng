import argparse
import json
import os
import sys

from dotenv import load_dotenv
from flask import Flask, render_template

from config.loader import get_setting, load_settings
from routes.recap_routes import recap_bp
from services.recap_service import run_recap


def create_app() -> Flask:
    load_dotenv()
    app = Flask(__name__)

    settings = load_settings()
    max_upload_mb = int(get_setting(settings, ["server", "max_upload_mb"], 200))
    app.config["MAX_CONTENT_LENGTH"] = max_upload_mb * 1024 * 1024

    app.register_blueprint(recap_bp)

    @app.route("/")
    def index():
        return render_template("index.html")

    return app


def main() -> None:
    load_dotenv()

    if len(sys.argv) > 1 and sys.argv[1] not in ("serve", "run", "-h", "--help"):
        sys.argv.insert(1, "run")

    parser = argparse.ArgumentParser(description="Audio recap system.")
    subparsers = parser.add_subparsers(dest="command")

    serve_parser = subparsers.add_parser("serve", help="Run the Flask server.")
    serve_parser.add_argument("--host", default="127.0.0.1")
    serve_parser.add_argument("--port", type=int, default=5000)
    serve_parser.add_argument("--debug", action="store_true")

    run_parser = subparsers.add_parser("run", help="Process a single audio file.")
    run_parser.add_argument("audio_file", help="Path to input audio file")
    run_parser.add_argument("--language", default="auto", choices=["auto", "vi", "en"])
    run_parser.add_argument("--no-diarization", action="store_true")
    run_parser.add_argument("--no-gpt", action="store_true")

    args = parser.parse_args()

    if args.command in (None, "serve"):
        app = create_app()
        host = getattr(args, "host", "127.0.0.1")
        port = getattr(args, "port", 5000)
        debug = getattr(args, "debug", False)
        app.run(host=host, port=port, debug=debug)
        return

    if not os.path.exists(args.audio_file):
        raise FileNotFoundError(f"Audio file not found: {args.audio_file}")

    result = run_recap(
        args.audio_file,
        language=args.language,
        use_diarization=not args.no_diarization,
        use_gpt=not args.no_gpt,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
