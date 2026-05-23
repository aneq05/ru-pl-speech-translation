from __future__ import annotations

import math
from pathlib import Path
from typing import Any

from benchmarking.models.base import ASRModel, ASRModelUnavailableError
from benchmarking.types import ASRPrediction, ASRSegment


class FasterWhisperASRModel(ASRModel):
    def __init__(
        self,
        model_size: str,
        *,
        language: str = "ru",
        device: str = "cpu",
        compute_type: str = "int8",
    ) -> None:
        model_id = f"faster-whisper:{model_size}"
        super().__init__(model_id=model_id)
        self.language = language
        try:
            from faster_whisper import WhisperModel
        except ImportError as exc:
            raise ASRModelUnavailableError(
                "Model faster-whisper is unavailable. Install dependency with: pip install faster-whisper"
            ) from exc

        self._model = WhisperModel(model_size, device=device, compute_type=compute_type)

    def transcribe(self, audio_path: Path) -> ASRPrediction:
        segments_iter, info = self._model.transcribe(
            str(audio_path),
            task="transcribe",
            language=self.language,
            beam_size=5,
        )
        segments = _segments_from_faster_whisper(segments_iter)
        text = " ".join(segment.text for segment in segments).strip()
        confidence = _mean_confidence(segments)
        return ASRPrediction(
            text=text,
            language=getattr(info, "language", None),
            confidence=confidence,
            segments=segments,
            raw={
                "segment_count": len(segments),
                "language_probability": _to_float(getattr(info, "language_probability", None)),
            },
        )


def _segments_from_faster_whisper(items: Any) -> list[ASRSegment]:
    output: list[ASRSegment] = []
    for item in items:
        avg_logprob = getattr(item, "avg_logprob", None)
        output.append(
            ASRSegment(
                text=(getattr(item, "text", "") or "").strip(),
                start_sec=_to_float(getattr(item, "start", None)),
                end_sec=_to_float(getattr(item, "end", None)),
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
