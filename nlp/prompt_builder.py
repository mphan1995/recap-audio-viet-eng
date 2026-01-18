from typing import List, Dict


LANGUAGE_MAP = {
    "auto": "the same language as the transcript",
    "vi": "Vietnamese",
    "en": "English",
    "bilingual": "Vietnamese and English",
}


def build_recap_messages(segments: List[Dict], target_language: str = "auto") -> List[Dict]:
    transcript = "\n".join([f'{s["speaker"]}: {s["text"]}' for s in segments])
    language_hint = LANGUAGE_MAP.get(target_language, LANGUAGE_MAP["auto"])

    system_prompt = (
        "You are a careful meeting summarizer. "
        "Do not invent facts. If details are missing, say so."
    )
    user_prompt = (
        "Summarize the conversation with the following sections:\n"
        "1) Summary\n"
        "2) Main topics\n"
        "3) Decisions\n"
        "4) Action items (with owners if mentioned)\n"
        "5) Risks or open questions\n\n"
        f"Write the response in {language_hint}.\n\n"
        "Transcript:\n"
        f"{transcript}"
    )

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
