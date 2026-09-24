import re
import unicodedata


def sanitize_text(text: str) -> str:
    """Normalize generated text for reliable DOCX/PDF/TXT export."""
    if not text:
        return ""

    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("\u2018", "'").replace("\u2019", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("\u2013", "-").replace("\u2014", "-")
    text = text.replace("\u2022", "-").replace("\u00a0", " ")

    normalized = unicodedata.normalize("NFKD", text)
    text = normalized.encode("ascii", "ignore").decode("ascii")

    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_terms(terms: str) -> list[str]:
    return [item.strip() for item in terms.split(";") if item.strip()]
