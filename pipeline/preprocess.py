import ffmpeg
import os

def preprocess_audio(input_path, output_path):
    (
        ffmpeg
        .input(input_path)
        .output(
            output_path,
            ac=1,
            ar=16000,
            format="wav"
        )
        .overwrite_output()
        .run(quiet=True)
    )
    return output_path
