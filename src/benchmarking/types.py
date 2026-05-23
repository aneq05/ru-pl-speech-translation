from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True, frozen=True)
class AudioSample:
    sample_id: str
    audio_path: Path
    reference_text: str
    duration_sec: float


@dataclass(slots=True, frozen=True)
class ASRSegment:
    text: str
    start_sec: float | None = None
    end_sec: float | None = None
    confidence: float | None = None


@dataclass(slots=True)
class ASRPrediction:
    text: str
    language: str | None = None
    confidence: float | None = None
    segments: list[ASRSegment] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class EvaluationRow:
    run_id: str
    model_id: str
    sample_id: str
    audio_path: str
    reference_text: str
    hypothesis_text: str
    duration_sec: float
    latency_sec: float
    rtf: float
    peak_memory_mb: float
    mean_confidence: float | None
    wer: float
    cer: float
    token_precision: float
    token_recall: float
    token_f1: float
    exact_match: float
    reference_token_count: int
    hypothesis_token_count: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
