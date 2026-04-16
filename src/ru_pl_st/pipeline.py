from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ru_pl_st.asr import ASRModel
from ru_pl_st.text_processing import extract_russian_words, normalize_russian_text
from ru_pl_st.translation import Translator
from ru_pl_st.tts import TTSModel
from ru_pl_st.types import PipelineOutput, SpeechSample


@dataclass(slots=True)
class CascadePipeline:
    """
    Skeleton:
    audio -> ASR (RU) -> RU text processing -> RU->PL translation -> optional TTS
    """

    asr_model: ASRModel
    translator: Translator
    tts_model: TTSModel | None = None

    def run_one(self, sample: SpeechSample, tts_output_path: Path | None = None) -> PipelineOutput:
        ru_raw = self.asr_model.transcribe(sample.audio_path)
        ru_normalized = normalize_russian_text(ru_raw)
        ru_words = extract_russian_words(ru_normalized)
        pl_text = self.translator.translate_ru_to_pl(ru_normalized)

        generated_audio: Path | None = None
        if self.tts_model is not None and tts_output_path is not None:
            generated_audio = self.tts_model.synthesize(pl_text, tts_output_path)

        return PipelineOutput(
            sample_id=sample.sample_id,
            ru_text=ru_normalized,
            ru_words=ru_words,
            pl_text=pl_text,
            pl_audio_path=generated_audio,
        )


@dataclass(slots=True)
class IntegratedPipeline:
    """
    Skeleton for direct speech translation (S2TT / S2ST style).
    """

    model_name: str

    def run_one(self, sample: SpeechSample) -> PipelineOutput:
        raise NotImplementedError(
            "TODO: implement direct speech translation pipeline for Russian audio."
        )

