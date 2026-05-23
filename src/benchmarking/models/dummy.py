from __future__ import annotations

from pathlib import Path

from benchmarking.models.base import ASRModel
from benchmarking.types import ASRPrediction


class EmptyASRModel(ASRModel):
    def __init__(self) -> None:
        super().__init__(model_id="dummy:empty")

    def transcribe(self, audio_path: Path) -> ASRPrediction:
        return ASRPrediction(text="", language="ru", confidence=0.0)


class SidecarASRModel(ASRModel):
    def __init__(self) -> None:
        super().__init__(model_id="dummy:sidecar")

    def transcribe(self, audio_path: Path) -> ASRPrediction:
        # Useful for pipeline tests: reads sidecar hypothesis file if present.
        candidates = [audio_path.with_suffix(".hyp.txt"), audio_path.with_suffix(".txt")]
        text = ""
        for candidate in candidates:
            if candidate.exists():
                text = candidate.read_text(encoding="utf-8").strip()
                break

        return ASRPrediction(text=text, language="ru", confidence=1.0 if text else 0.0)
