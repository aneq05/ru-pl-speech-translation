from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from ru_pl_st.data.models import SpeechSample
from ru_pl_st.tts.base import TTSMethod
from ru_pl_st.tts.methods import NoTTSMethod


class IntegratedSTMethod(ABC):
    name: str

    @abstractmethod
    def translate_speech(self, sample: SpeechSample) -> str:
        raise NotImplementedError


@dataclass(slots=True)
class ReferenceIntegratedSTMethod(IntegratedSTMethod):
    name: str = "integrated_reference"

    def translate_speech(self, sample: SpeechSample) -> str:
        return sample.pl_translation_ref


@dataclass(slots=True)
class SimulatedIntegratedSTMethod(IntegratedSTMethod):
    """
    Stand-in for end-to-end S2TT models.
    Drops every 8th token from reference PL text.
    """

    name: str = "integrated_s2tt_sim"

    def translate_speech(self, sample: SpeechSample) -> str:
        tokens = sample.pl_translation_ref.split()
        if not tokens:
            return sample.pl_translation_ref
        filtered = [token for index, token in enumerate(tokens, start=1) if index % 8 != 0]
        return " ".join(filtered)


def build_integrated_methods(names: list[str]) -> list[IntegratedSTMethod]:
    registry: dict[str, IntegratedSTMethod] = {
        "integrated_reference": ReferenceIntegratedSTMethod(),
        "integrated_s2tt_sim": SimulatedIntegratedSTMethod(),
    }
    methods: list[IntegratedSTMethod] = []
    for name in names:
        if name not in registry:
            available = ", ".join(sorted(registry))
            raise ValueError(f"Unknown integrated method '{name}'. Available: {available}")
        methods.append(registry[name])
    return methods


@dataclass(slots=True)
class IntegratedPipeline:
    method: IntegratedSTMethod
    tts_method: TTSMethod = field(default_factory=NoTTSMethod)

    def run_sample(self, sample: SpeechSample) -> dict[str, str]:
        pl_hyp = self.method.translate_speech(sample)
        pl_audio_path = self.tts_method.synthesize(pl_hyp, sample)
        return {
            "approach": "integrated",
            "sample_id": sample.sample_id,
            "speaker_id": sample.speaker_id,
            "split": sample.split,
            "noise_condition": sample.noise_condition,
            "asr_method": "",
            "translation_method": "",
            "integrated_method": self.method.name,
            "ru_transcript_ref": sample.ru_transcript_ref,
            "ru_transcript_hyp": "",
            "ru_tokens": "",
            "pl_translation_ref": sample.pl_translation_ref,
            "pl_translation_hyp": pl_hyp,
            "pl_audio_hyp_path": pl_audio_path,
        }
