from scripts.run_recap import run_recap
import sys

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python app.py <audio_file>")
        sys.exit(1)

    run_recap(sys.argv[1])
