from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path


class ASRModel(ABC):
    """Interface for Russian ASR models."""

    name: str

    @abstractmethod
    def transcribe(self, audio_path: Path) -> str:
        raise NotImplementedError


class WhisperASR(ASRModel):
    """Skeleton adapter for Whisper-based RU ASR."""

    name = "whisper_ru"

    def transcribe(self, audio_path: Path) -> str:
        raise NotImplementedError("TODO: implement Whisper inference for Russian audio.")


class VoskASR(ASRModel):
    """Skeleton adapter for Vosk-based RU ASR."""

    name = "vosk_ru"

    def transcribe(self, audio_path: Path) -> str:
        raise NotImplementedError("TODO: implement Vosk inference for Russian audio.")

