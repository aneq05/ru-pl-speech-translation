from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from ru_pl_st.data.models import SpeechSample
from ru_pl_st.translation.base import TranslationHypothesis, TranslationMethod

_RU_TO_PL_GLOSSARY = {
    "язык": "jezyk",
    "скороговорка": "lamaniec",
    "говорить": "mowic",
    "быстро": "szybko",
    "слово": "slowo",
    "русский": "rosyjski",
    "польский": "polski",
}


def _drop_every_nth_token(text: str, n: int) -> str:
    tokens = text.split()
    if n <= 1 or not tokens:
        return text
    filtered = [token for index, token in enumerate(tokens, start=1) if index % n != 0]
    return " ".join(filtered)


@dataclass(slots=True)
class ReferenceTranslationMethod(TranslationMethod):
    """Dry-run translator based on reference Polish translation."""

    name: str = "reference_mt"

    def translate(
        self,
        ru_text: str,
        ru_tokens: list[str],
        sample: SpeechSample,
    ) -> TranslationHypothesis:
        return TranslationHypothesis(text=sample.pl_translation_ref, metadata={"mode": "reference"})


@dataclass(slots=True)
class SimulatedNLLBTranslationMethod(TranslationMethod):
    """
    Stand-in for NLLB-like translation.
    Uses reference translation with light degradation.
    """

    name: str = "nllb_ru_pl_sim"

    def translate(
        self,
        ru_text: str,
        ru_tokens: list[str],
        sample: SpeechSample,
    ) -> TranslationHypothesis:
        hyp = _drop_every_nth_token(sample.pl_translation_ref, 10)
        return TranslationHypothesis(text=hyp, metadata={"simulated": "true"})


@dataclass(slots=True)
class SimulatedMarianTranslationMethod(TranslationMethod):
    """
    Stand-in for Marian-like translation.
    Uses a small glossary over recognized RU tokens.
    """

    name: str = "marian_ru_pl_sim"
    glossary: dict[str, str] = field(default_factory=lambda: dict(_RU_TO_PL_GLOSSARY))

    def translate(
        self,
        ru_text: str,
        ru_tokens: list[str],
        sample: SpeechSample,
    ) -> TranslationHypothesis:
        translated_tokens = [self.glossary.get(token, token) for token in ru_tokens]
        fallback = " ".join(translated_tokens).strip()
        if not fallback:
            fallback = sample.pl_translation_ref
        return TranslationHypothesis(text=fallback, metadata={"simulated": "true"})


@dataclass(slots=True)
class ExternalTranslationMethod(TranslationMethod):
    """Adapter for plugging a real RU->PL text translation callable."""

    name: str
    translate_fn: Callable[[str], str]

    def translate(
        self,
        ru_text: str,
        ru_tokens: list[str],
        sample: SpeechSample,
    ) -> TranslationHypothesis:
        return TranslationHypothesis(text=self.translate_fn(ru_text), metadata={"external": "true"})


def build_translation_methods(names: list[str]) -> list[TranslationMethod]:
    registry: dict[str, TranslationMethod] = {
        "reference_mt": ReferenceTranslationMethod(),
        "nllb_ru_pl_sim": SimulatedNLLBTranslationMethod(),
        "marian_ru_pl_sim": SimulatedMarianTranslationMethod(),
    }
    methods: list[TranslationMethod] = []
    for name in names:
        if name not in registry:
            available = ", ".join(sorted(registry))
            raise ValueError(f"Unknown translation method '{name}'. Available: {available}")
        methods.append(registry[name])
    return methods

