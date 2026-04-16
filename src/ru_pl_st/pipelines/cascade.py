from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class CascadePipeline:
    config: dict[str, Any]

    def run_sample(self, audio_path: str) -> dict[str, str]:
        """
        Run one sample through ASR -> MT -> TTS stages.
        Replace placeholder logic with model inference code.
        """
        ru_text_hyp = f"[TODO ASR] {audio_path}"
        pl_text_hyp = f"[TODO MT] {ru_text_hyp}"
        tts_output_path = f"[TODO TTS] {audio_path}.pl.wav"
        return {
            "ru_text_hyp": ru_text_hyp,
            "pl_text_hyp": pl_text_hyp,
            "pl_audio_hyp_path": tts_output_path,
        }

