from typing import List


def merge_segments(
    transcripts: List[dict],
    speakers: List[dict],
    min_overlap_ratio: float = 0.2,
) -> List[dict]:
    merged = []
    if not transcripts:
        return merged

    for t in transcripts:
        duration = max(1e-6, t["end"] - t["start"])
        speaker_id = "SPEAKER_1" if not speakers else "UNKNOWN"
        best_overlap = 0.0
        best_speaker = None

        for s in speakers:
            overlap = _overlap(t["start"], t["end"], s["start"], s["end"])
            if overlap > best_overlap:
                best_overlap = overlap
                best_speaker = s["speaker"]

        if best_speaker:
            overlap_ratio = best_overlap / duration
            if overlap_ratio >= min_overlap_ratio:
                speaker_id = best_speaker

        merged.append(
            {
                "start": t["start"],
                "end": t["end"],
                "speaker": speaker_id,
                "text": t["text"],
            }
        )

    return merged


def _overlap(a_start: float, a_end: float, b_start: float, b_end: float) -> float:
    return max(0.0, min(a_end, b_end) - max(a_start, b_start))
