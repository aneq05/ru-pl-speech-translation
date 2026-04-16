from __future__ import annotations

from pathlib import Path

from ru_pl_st.types import SpeechSample

SUPPORTED_AUDIO_EXTENSIONS = {".wav", ".mp3", ".flac", ".m4a"}


def collect_samples_from_raw(raw_dir: Path) -> list[SpeechSample]:
    """
    Minimal helper:
    scans data/raw and builds a simple sample list.
    """
    samples: list[SpeechSample] = []
    for audio_path in sorted(raw_dir.glob("*")):
        if audio_path.suffix.lower() not in SUPPORTED_AUDIO_EXTENSIONS:
            continue
        samples.append(
            SpeechSample(
                sample_id=audio_path.stem,
                audio_path=audio_path,
            )
        )
    return samples

