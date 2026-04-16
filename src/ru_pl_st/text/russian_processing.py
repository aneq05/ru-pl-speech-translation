from __future__ import annotations

import re

_RUSSIAN_WORD_PATTERN = re.compile(r"[а-я]+(?:-[а-я]+)?")


def normalize_russian_text(text: str) -> str:
    lowered = text.strip().lower().replace("ё", "е")
    cleaned = re.sub(r"[^0-9a-zа-я\-\s]", " ", lowered)
    squashed = re.sub(r"\s+", " ", cleaned).strip()
    return squashed


def tokenize_russian_words(text: str) -> list[str]:
    normalized = normalize_russian_text(text)
    return _RUSSIAN_WORD_PATTERN.findall(normalized)

