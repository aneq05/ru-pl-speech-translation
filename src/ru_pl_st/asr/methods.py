from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from ru_pl_st.asr.base import ASRHypothesis, ASRMethod
from ru_pl_st.data.models import SpeechSample


def _drop_every_nth_token(text: str, n: int) -> str:
    tokens = text.split()
    if n <= 1 or not tokens:
        return text
    filtered = [token for index, token in enumerate(tokens, start=1) if index % n != 0]
    return " ".join(filtered)


@dataclass(slots=True)
class ReferenceASRMethod(ASRMethod):
    """Dry-run ASR method. Uses reference transcript from manifest."""

    name: str = "reference_asr"

    def transcribe(self, sample: SpeechSample) -> ASRHypothesis:
        return ASRHypothesis(text=sample.ru_transcript_ref, metadata={"mode": "reference"})


@dataclass(slots=True)
class SimulatedWhisperRUASRMethod(ASRMethod):
    """
    Stand-in for Whisper-like behavior.
    Keeps most words and drops every 9th token to simulate minor errors.
    """

    name: str = "whisper_ru_sim"

    def transcribe(self, sample: SpeechSample) -> ASRHypothesis:
        hyp = _drop_every_nth_token(sample.ru_transcript_ref, 9)
        return ASRHypothesis(text=hyp, metadata={"simulated": "true"})


@dataclass(slots=True)
class SimulatedVoskRUASRMethod(ASRMethod):
    """
    Stand-in for Vosk-like behavior.
    Drops every 6th token to simulate a less robust transcript.
    """

    name: str = "vosk_ru_sim"

    def transcribe(self, sample: SpeechSample) -> ASRHypothesis:
        hyp = _drop_every_nth_token(sample.ru_transcript_ref, 6)
        return ASRHypothesis(text=hyp, metadata={"simulated": "true"})


@dataclass(slots=True)
class ExternalASRMethod(ASRMethod):
    """Adapter for plugging a real ASR callable (e.g., Whisper/Vosk wrapper)."""

    name: str
    transcribe_fn: Callable[[SpeechSample], str]

    def transcribe(self, sample: SpeechSample) -> ASRHypothesis:
        return ASRHypothesis(text=self.transcribe_fn(sample), metadata={"external": "true"})


def build_asr_methods(names: list[str]) -> list[ASRMethod]:
    registry: dict[str, ASRMethod] = {
        "reference_asr": ReferenceASRMethod(),
        "whisper_ru_sim": SimulatedWhisperRUASRMethod(),
        "vosk_ru_sim": SimulatedVoskRUASRMethod(),
    }
    methods: list[ASRMethod] = []
    for name in names:
        if name not in registry:
            available = ", ".join(sorted(registry))
            raise ValueError(f"Unknown ASR method '{name}'. Available: {available}")
        methods.append(registry[name])
    return methods

