from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class SpeechSample:
    sample_id: str
    audio_path: Path
    speaker_id: str | None = None


@dataclass(slots=True)
class PipelineOutput:
    sample_id: str
    ru_text: str
    ru_words: list[str]
    pl_text: str
    pl_audio_path: Path | None = None

