from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path


class TTSModel(ABC):
    """Interface for Polish TTS stage (optional)."""

    name: str

    @abstractmethod
    def synthesize(self, pl_text: str, output_path: Path) -> Path:
        raise NotImplementedError

