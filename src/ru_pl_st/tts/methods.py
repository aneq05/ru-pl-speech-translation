from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ru_pl_st.data.models import SpeechSample
from ru_pl_st.tts.base import TTSMethod


@dataclass(slots=True)
class NoTTSMethod(TTSMethod):
    name: str = "no_tts"

    def synthesize(self, pl_text: str, sample: SpeechSample) -> str:
        return ""


@dataclass(slots=True)
class PathOnlyTTSMethod(TTSMethod):
    """
    Returns output path for future TTS integration.
    It does not synthesize audio yet.
    """

    output_dir: str = "data/processed/tts"
    name: str = "path_only_tts"

    def synthesize(self, pl_text: str, sample: SpeechSample) -> str:
        return str(Path(self.output_dir) / f"{sample.sample_id}_{self.name}.wav")

