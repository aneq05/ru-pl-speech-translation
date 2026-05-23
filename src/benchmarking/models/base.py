from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from benchmarking.types import ASRPrediction


class ASRModel(ABC):
    def __init__(self, model_id: str) -> None:
        self.model_id = model_id

    @abstractmethod
    def transcribe(self, audio_path: Path) -> ASRPrediction:
        raise NotImplementedError


class ASRModelUnavailableError(RuntimeError):
    pass
