import argparse
import json

from dotenv import load_dotenv

from services.recap_service import run_recap


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description="Run audio recap pipeline.")
    parser.add_argument("audio_file", help="Path to input audio file")
    parser.add_argument("--language", default="auto", choices=["auto", "vi", "en"])
    parser.add_argument("--no-diarization", action="store_true")
    parser.add_argument("--no-gpt", action="store_true")
    args = parser.parse_args()

    result = run_recap(
        args.audio_file,
        language=args.language,
        use_diarization=not args.no_diarization,
        use_gpt=not args.no_gpt,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
