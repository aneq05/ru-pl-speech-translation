from __future__ import annotations

from pathlib import Path

import pandas as pd

from ru_pl_st.data.models import SpeechSample

REQUIRED_COLUMNS = [
    "sample_id",
    "speaker_id",
    "audio_path",
    "split",
    "ru_transcript_ref",
    "pl_translation_ref",
    "noise_condition",
]


def create_manifest_template(path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(columns=REQUIRED_COLUMNS).to_csv(output_path, index=False)


def load_manifest(path: str | Path) -> list[SpeechSample]:
    manifest_path = Path(path)
    df = pd.read_csv(manifest_path)
    missing = sorted(set(REQUIRED_COLUMNS) - set(df.columns))
    if missing:
        raise ValueError(f"Manifest is missing required columns: {missing}")

    samples: list[SpeechSample] = []
    for row in df.itertuples(index=False):
        samples.append(
            SpeechSample(
                sample_id=str(row.sample_id),
                speaker_id=str(row.speaker_id),
                audio_path=str(row.audio_path),
                split=str(row.split),
                ru_transcript_ref=str(row.ru_transcript_ref),
                pl_translation_ref=str(row.pl_translation_ref),
                noise_condition=str(row.noise_condition),
            )
        )
    return samples

