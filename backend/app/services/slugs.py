import re


TURKISH_CHAR_MAP = {
    "ç": "c",
    "ğ": "g",
    "ı": "i",
    "i̇": "i",
    "ö": "o",
    "ş": "s",
    "ü": "u",
}


def slugify(value: str) -> str:
    normalized = value.strip().lower()

    for source, target in TURKISH_CHAR_MAP.items():
        normalized = normalized.replace(source, target)

    normalized = re.sub(r"[^a-z0-9]+", "-", normalized)
    normalized = normalized.strip("-")

    if not normalized:
        return "company"

    return normalized
