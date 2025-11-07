def summarize_with_gpt(text: str, lang: str = "auto") -> str:
    if not text.strip():
        return ""
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    sample = " ".join(lines[:5])
    if lang == "vi":
        return f"Tóm tắt (giản lược): {sample[:400]}..."
    elif lang == "en":
        return f"Summary (rough): {sample[:400]}..."
    else:
        return f"Summary/Tóm tắt (rough): {sample[:400]}..."
