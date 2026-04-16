from __future__ import annotations

from dataclasses import dataclass, field

from ru_pl_st.asr.base import ASRMethod
from ru_pl_st.data.models import SpeechSample
from ru_pl_st.text.russian_processing import normalize_russian_text, tokenize_russian_words
from ru_pl_st.translation.base import TranslationMethod
from ru_pl_st.tts.base import TTSMethod
from ru_pl_st.tts.methods import NoTTSMethod


@dataclass(slots=True)
class CascadePipeline:
    asr_method: ASRMethod
    translation_method: TranslationMethod
    tts_method: TTSMethod = field(default_factory=NoTTSMethod)

    def run_sample(self, sample: SpeechSample) -> dict[str, str]:
        asr_hyp = self.asr_method.transcribe(sample)
        normalized_ru = normalize_russian_text(asr_hyp.text)
        ru_tokens = tokenize_russian_words(normalized_ru)
        mt_hyp = self.translation_method.translate(normalized_ru, ru_tokens, sample)
        pl_audio_path = self.tts_method.synthesize(mt_hyp.text, sample)

        return {
            "approach": "cascade",
            "sample_id": sample.sample_id,
            "speaker_id": sample.speaker_id,
            "split": sample.split,
            "noise_condition": sample.noise_condition,
            "asr_method": self.asr_method.name,
            "translation_method": self.translation_method.name,
            "integrated_method": "",
            "ru_transcript_ref": sample.ru_transcript_ref,
            "ru_transcript_hyp": normalized_ru,
            "ru_tokens": " ".join(ru_tokens),
            "pl_translation_ref": sample.pl_translation_ref,
            "pl_translation_hyp": mt_hyp.text,
            "pl_audio_hyp_path": pl_audio_path,
        }
