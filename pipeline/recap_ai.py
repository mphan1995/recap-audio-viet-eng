import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def recap_conversation(merged_segments):
    content = "\n".join(
        [f'{m["speaker"]}: {m["text"]}' for m in merged_segments]
    )

    prompt = f"""
    Đây là transcript một cuộc hội thoại.

    1. Tóm tắt nội dung
    2. Xác định mục tiêu cuộc nói chuyện
    3. Kết luận / hành động nếu có

    Transcript:
    {content}
    """

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content
