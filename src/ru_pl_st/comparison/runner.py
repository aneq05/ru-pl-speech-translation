from __future__ import annotations

import pandas as pd

from ru_pl_st.asr.base import ASRMethod
from ru_pl_st.data.models import SpeechSample
from ru_pl_st.pipelines.cascade import CascadePipeline
from ru_pl_st.pipelines.integrated import IntegratedPipeline, IntegratedSTMethod
from ru_pl_st.translation.base import TranslationMethod
from ru_pl_st.tts.base import TTSMethod
from ru_pl_st.tts.methods import NoTTSMethod


def run_cascade_comparison(
    samples: list[SpeechSample],
    asr_methods: list[ASRMethod],
    translation_methods: list[TranslationMethod],
    tts_method: TTSMethod | None = None,
) -> pd.DataFrame:
    tts = tts_method or NoTTSMethod()
    rows: list[dict[str, str]] = []
    for asr in asr_methods:
        for mt in translation_methods:
            pipeline = CascadePipeline(asr_method=asr, translation_method=mt, tts_method=tts)
            for sample in samples:
                rows.append(pipeline.run_sample(sample))
    return pd.DataFrame(rows)


def run_integrated_comparison(
    samples: list[SpeechSample],
    methods: list[IntegratedSTMethod],
    tts_method: TTSMethod | None = None,
) -> pd.DataFrame:
    tts = tts_method or NoTTSMethod()
    rows: list[dict[str, str]] = []
    for method in methods:
        pipeline = IntegratedPipeline(method=method, tts_method=tts)
        for sample in samples:
            rows.append(pipeline.run_sample(sample))
    return pd.DataFrame(rows)

