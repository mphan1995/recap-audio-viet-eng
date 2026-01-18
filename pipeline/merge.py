def merge_segments(transcripts, speakers):
    merged = []

    for t in transcripts:
        speaker_id = "UNKNOWN"
        for s in speakers:
            if s["start"] <= t["start"] <= s["end"]:
                speaker_id = s["speaker"]
                break

        merged.append({
            "start": t["start"],
            "end": t["end"],
            "speaker": speaker_id,
            "text": t["text"]
        })

    return merged
