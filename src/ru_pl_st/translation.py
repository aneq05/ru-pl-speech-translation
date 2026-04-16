from __future__ import annotations

from abc import ABC, abstractmethod


class Translator(ABC):
    """Interface for RU->PL translation models."""

    name: str

    @abstractmethod
    def translate_ru_to_pl(self, ru_text: str) -> str:
        raise NotImplementedError


class MarianTranslator(Translator):
    """Skeleton adapter for Marian RU->PL."""

    name = "marian_ru_pl"

    def translate_ru_to_pl(self, ru_text: str) -> str:
        raise NotImplementedError("TODO: implement Marian RU->PL translation.")


class NLLBTranslator(Translator):
    """Skeleton adapter for NLLB RU->PL."""

    name = "nllb_ru_pl"

    def translate_ru_to_pl(self, ru_text: str) -> str:
        raise NotImplementedError("TODO: implement NLLB RU->PL translation.")

