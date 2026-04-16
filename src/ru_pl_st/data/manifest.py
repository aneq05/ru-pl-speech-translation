from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass(slots=True)
class Utterance:
    sample_id: str
    speaker_id: str
    audio_path: str
    split: str
    ru_transcript_ref: str
    pl_translation_ref: str
    noise_condition: str


REQUIRED_COLUMNS = [
    "sample_id",
    "speaker_id",
    "audio_path",
    "split",
    "ru_transcript_ref",
    "pl_translation_ref",
    "noise_condition",
]


def load_manifest(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    df = pd.read_csv(path)
    missing = sorted(set(REQUIRED_COLUMNS) - set(df.columns))
    if missing:
        raise ValueError(f"Manifest is missing required columns: {missing}")
    return df

