from typing import List, Dict

from openai import OpenAI

from nlp.prompt_builder import build_recap_messages


def summarize_conversation(
    segments: List[Dict],
    model: str = "gpt-4o-mini",
    temperature: float = 0.2,
    target_language: str = "auto",
) -> str:
    client = OpenAI()
    messages = build_recap_messages(segments, target_language=target_language)
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    return response.choices[0].message.content.strip()
