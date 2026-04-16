from __future__ import annotations


def normalize_russian_text(text: str) -> str:
    """
    TODO:
    - lowercase
    - unify russian characters if needed (e.g. e/yo policy)
    - remove unwanted punctuation/noise symbols
    """
    raise NotImplementedError("TODO: implement Russian text normalization.")


def extract_russian_words(text: str) -> list[str]:
    """
    TODO:
    - split normalized Russian text into tokens/words
    - optionally handle hyphenated words and numbers
    """
    raise NotImplementedError("TODO: implement Russian word extraction.")

