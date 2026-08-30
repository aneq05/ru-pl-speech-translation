from __future__ import annotations

from pathlib import Path

import numpy as np
import soundfile as sf

from benchmarking.dataset import load_dataset


def _write_wav(path: Path) -> None:
    samples = np.zeros(800, dtype=np.float32)
    sf.write(path, samples, 8000)


def test_load_dataset_uses_csv_reference_for_nested_audio(tmp_path: Path) -> None:
    raw_dir = tmp_path / "raw"
    speaker_dir = raw_dir / "person1"
    speaker_dir.mkdir(parents=True)
    audio_path = speaker_dir / "carl.wav"
    _write_wav(audio_path)
    (raw_dir / "labels.csv").write_text(
        "file_name,reference_text\nperson1/carl.wav,Karl reference\n",
        encoding="utf-8",
    )

    samples = load_dataset(raw_dir)

    assert len(samples) == 1
    assert samples[0].sample_id == "person1__carl"
    assert samples[0].reference_text == "Karl reference"
    assert samples[0].duration_sec == 0.1


def test_load_dataset_uses_sidecar_reference(tmp_path: Path) -> None:
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    audio_path = raw_dir / "sasha.wav"
    _write_wav(audio_path)
    audio_path.with_suffix(".txt").write_text("Sasha reference", encoding="utf-8")

    samples = load_dataset(raw_dir)

    assert len(samples) == 1
    assert samples[0].sample_id == "sasha"
    assert samples[0].reference_text == "Sasha reference"


def test_load_dataset_reports_missing_references(tmp_path: Path) -> None:
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    _write_wav(raw_dir / "unknown.wav")

    try:
        load_dataset(raw_dir)
    except ValueError as exc:
        assert "reference text is missing" in str(exc)
        assert "unknown.wav" in str(exc)
    else:
        raise AssertionError("Expected missing references to fail fast")
