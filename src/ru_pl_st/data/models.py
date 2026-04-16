from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SpeechSample:
    sample_id: str
    speaker_id: str
    audio_path: str
    split: str
    ru_transcript_ref: str
    pl_translation_ref: str
    noise_condition: str

