from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from benchmarking.models.base import ASRModel, ASRModelUnavailableError
from benchmarking.types import ASRPrediction, ASRSegment


class HFTransformersASRModel(ASRModel):
    def __init__(
        self,
        model_name: str,
        *,
        device: str = "cpu",
    ) -> None:
        super().__init__(model_id=f"hf:{model_name}")
        self.model_name = model_name
        self.target_sampling_rate = 16_000

        try:
            from transformers import pipeline
        except ImportError as exc:
            raise ASRModelUnavailableError(
                "Model hf:* is unavailable. Install dependency with: pip install transformers"
            ) from exc

        device_arg = _resolve_transformers_device(device=device)
        try:
            self._pipeline = pipeline(
                task="automatic-speech-recognition",
                model=model_name,
                device=device_arg,
            )
        except Exception as exc:
            raise ASRModelUnavailableError(
                f"Could not initialize hf model '{model_name}'. Ensure dependencies are installed and model is reachable."
            ) from exc

    def transcribe(self, audio_path: Path) -> ASRPrediction:
        audio_array = _load_audio_mono(audio_path=audio_path, target_sampling_rate=self.target_sampling_rate)
        payload = {"array": audio_array, "sampling_rate": self.target_sampling_rate}

        # Some models/pipeline versions support timestamps, some don't.
        try:
            result = self._pipeline(payload, return_timestamps=True)
        except TypeError:
            result = self._pipeline(payload)

        text = _extract_text(result)
        segments = _extract_segments(result)

        return ASRPrediction(
            text=text,
            language=None,
            confidence=None,
            segments=segments,
            raw={"model_name": self.model_name, "segment_count": len(segments)},
        )


def _resolve_transformers_device(device: str) -> int:
    normalized = device.strip().lower()
    if normalized in {"cpu", "mps"}:
        return -1
    if normalized in {"cuda", "gpu"}:
        return 0
    return -1


def _load_audio_mono(audio_path: Path, target_sampling_rate: int) -> np.ndarray:
    try:
        import librosa
    except ImportError as exc:
        raise ASRModelUnavailableError(
            "librosa is required for hf:* models audio loading. Install with: pip install librosa"
        ) from exc

    audio, _ = librosa.load(str(audio_path), sr=target_sampling_rate, mono=True)
    return np.asarray(audio, dtype=np.float32)


def _extract_text(result: Any) -> str:
    if isinstance(result, dict):
        text = result.get("text")
        return text.strip() if isinstance(text, str) else ""
    return ""


def _extract_segments(result: Any) -> list[ASRSegment]:
    if not isinstance(result, dict):
        return []

    chunks = result.get("chunks")
    if not isinstance(chunks, list):
        return []

    segments: list[ASRSegment] = []
    for chunk in chunks:
        if not isinstance(chunk, dict):
            continue
        timestamp = chunk.get("timestamp")
        start_sec: float | None = None
        end_sec: float | None = None
        if isinstance(timestamp, tuple) and len(timestamp) == 2:
            start_sec = _to_float(timestamp[0])
            end_sec = _to_float(timestamp[1])
        segments.append(
            ASRSegment(
                text=str(chunk.get("text", "")).strip(),
                start_sec=start_sec,
                end_sec=end_sec,
                confidence=None,
            )
        )
    return segments


def _to_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
