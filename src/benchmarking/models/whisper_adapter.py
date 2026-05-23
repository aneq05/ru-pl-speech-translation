from __future__ import annotations

import math
from pathlib import Path
from typing import Any

from benchmarking.models.base import ASRModel, ASRModelUnavailableError
from benchmarking.types import ASRPrediction, ASRSegment


class WhisperASRModel(ASRModel):
    def __init__(
        self,
        model_size: str,
        *,
        language: str = "ru",
        device: str = "cpu",
    ) -> None:
        model_id = f"whisper:{model_size}"
        super().__init__(model_id=model_id)
        self.language = language
        self.device = device
        try:
            import whisper
        except ImportError as exc:
            raise ASRModelUnavailableError(
                "Model whisper is unavailable. Install dependency with: pip install openai-whisper"
            ) from exc

        self._model = whisper.load_model(model_size, device=device)

    def transcribe(self, audio_path: Path) -> ASRPrediction:
        result: dict[str, Any] = self._model.transcribe(
            str(audio_path),
            task="transcribe",
            language=self.language,
            fp16=self.device != "cpu",
            verbose=False,
        )
        segments = _segments_from_whisper(result.get("segments", []))
        confidence = _mean_confidence(segments)
        return ASRPrediction(
            text=(result.get("text") or "").strip(),
            language=result.get("language"),
            confidence=confidence,
            segments=segments,
            raw={"segment_count": len(segments)},
        )


def _segments_from_whisper(items: list[dict[str, Any]]) -> list[ASRSegment]:
    output: list[ASRSegment] = []
    for item in items:
        avg_logprob = item.get("avg_logprob")
        output.append(
            ASRSegment(
                text=(item.get("text") or "").strip(),
                start_sec=_to_float(item.get("start")),
                end_sec=_to_float(item.get("end")),
                confidence=_logprob_to_confidence(avg_logprob),
            )
        )
    return output


def _to_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _logprob_to_confidence(avg_logprob: Any) -> float | None:
    if avg_logprob is None:
        return None
    try:
        value = float(avg_logprob)
    except (TypeError, ValueError):
        return None

    return max(0.0, min(1.0, math.exp(value)))


def _mean_confidence(segments: list[ASRSegment]) -> float | None:
    confidences = [segment.confidence for segment in segments if segment.confidence is not None]
    if not confidences:
        return None
    return sum(confidences) / len(confidences)
