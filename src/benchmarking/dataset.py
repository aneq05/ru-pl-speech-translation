from __future__ import annotations

import csv
from pathlib import Path

import soundfile as sf

from benchmarking.types import AudioSample
from reference_texts import get_reference_by_file_name

# Current dataset contract: only WAV files are expected in data/raw.
AUDIO_EXTENSIONS = {".wav"}
REFERENCE_FILE_CANDIDATES = ("labels.csv", "references.csv", "metadata.csv")
REFERENCE_TEXT_COLUMNS = ("reference_text", "text", "transcript", "label")
REFERENCE_FILE_COLUMNS = ("file_name", "filename", "file", "path", "audio_file")


def load_dataset(raw_dir: str | Path) -> list[AudioSample]:
    base_dir = Path(raw_dir).resolve()
    if not base_dir.exists():
        raise FileNotFoundError(f"Dataset directory does not exist: {base_dir}")

    reference_map = _load_reference_map(base_dir)
    audio_paths = sorted(
        path for path in base_dir.rglob("*") if path.is_file() and path.suffix.lower() in AUDIO_EXTENSIONS
    )
    if not audio_paths:
        raise ValueError(
            f"No audio files found in {base_dir}. Expected files with extensions: {sorted(AUDIO_EXTENSIONS)}"
        )

    samples: list[AudioSample] = []
    missing_reference: list[str] = []
    for audio_path in audio_paths:
        sample = _build_sample(audio_path=audio_path, base_dir=base_dir, reference_map=reference_map)
        if sample is None:
            missing_reference.append(str(audio_path.relative_to(base_dir)))
            continue
        samples.append(sample)

    if not samples:
        expected_examples = "\n".join(
            f"- {audio_path.relative_to(base_dir).as_posix()}" for audio_path in audio_paths[:6]
        )
        raise ValueError(
            "No valid samples were loaded (audio exists but reference text is missing).\n"
            "Provide references in one of these ways:\n"
            "1) data/raw/labels.csv with columns: file_name,reference_text\n"
            "   For your current folder layout use relative file paths in file_name, e.g. person1/carl.wav\n"
            "2) sidecar .txt files next to every .wav file.\n"
            "3) data/reference_texts/ mapping for filename-based automatic references.\n"
            "Detected WAV files (examples):\n"
            f"{expected_examples}"
        )

    if missing_reference:
        print(
            "Warning: skipped audio files without reference text:\n"
            + "\n".join(f"- {name}" for name in missing_reference)
        )

    return samples


def _build_sample(
    audio_path: Path,
    base_dir: Path,
    reference_map: dict[str, str],
) -> AudioSample | None:
    relative_path = audio_path.relative_to(base_dir).as_posix()
    file_name = audio_path.name
    reference_text = (
        reference_map.get(relative_path)
        or reference_map.get(file_name)
        or _read_sidecar_reference(audio_path)
        or _read_reference_from_catalog(audio_path=audio_path, base_dir=base_dir)
    )
    if reference_text is None:
        return None

    duration_sec = _read_audio_duration(audio_path)
    sample_id = _build_sample_id(audio_path=audio_path, base_dir=base_dir)
    return AudioSample(
        sample_id=sample_id,
        audio_path=audio_path,
        reference_text=reference_text,
        duration_sec=duration_sec,
    )


def _build_sample_id(audio_path: Path, base_dir: Path) -> str:
    relative = audio_path.relative_to(base_dir).as_posix()
    if relative.lower().endswith(".wav"):
        relative = relative[:-4]
    return relative.replace("/", "__")


def _load_reference_map(base_dir: Path) -> dict[str, str]:
    for candidate in REFERENCE_FILE_CANDIDATES:
        candidate_path = base_dir / candidate
        if candidate_path.exists():
            return _parse_reference_csv(candidate_path)
    return {}


def _parse_reference_csv(path: Path) -> dict[str, str]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"Reference file has no header row: {path}")

        text_column = _pick_column(reader.fieldnames, REFERENCE_TEXT_COLUMNS)
        file_column = _pick_column(reader.fieldnames, REFERENCE_FILE_COLUMNS)
        if text_column is None or file_column is None:
            raise ValueError(
                f"Reference file {path} must contain one file column {REFERENCE_FILE_COLUMNS} "
                f"and one text column {REFERENCE_TEXT_COLUMNS}. Got headers: {reader.fieldnames}"
            )

        reference_map: dict[str, str] = {}
        for row in reader:
            raw_path = (row.get(file_column) or "").strip()
            raw_text = (row.get(text_column) or "").strip()
            if not raw_path or not raw_text:
                continue

            normalized_path = Path(raw_path).as_posix()
            reference_map[normalized_path] = raw_text
            reference_map[Path(normalized_path).name] = raw_text

        return reference_map


def _pick_column(columns: list[str], candidates: tuple[str, ...]) -> str | None:
    lowered = {column.lower(): column for column in columns}
    for candidate in candidates:
        if candidate in lowered:
            return lowered[candidate]
    return None


def _read_sidecar_reference(audio_path: Path) -> str | None:
    sidecar_path = audio_path.with_suffix(".txt")
    if not sidecar_path.exists():
        return None
    text = sidecar_path.read_text(encoding="utf-8").strip()
    return text or None


def _read_reference_from_catalog(audio_path: Path, base_dir: Path) -> str | None:
    candidate_names = [audio_path.name, audio_path.relative_to(base_dir).as_posix()]
    for candidate in candidate_names:
        try:
            entry = get_reference_by_file_name(candidate)
        except (FileNotFoundError, ValueError):
            return None

        if entry is not None:
            text = entry.russian_original.strip()
            if text:
                return text

    return None


def _read_audio_duration(audio_path: Path) -> float:
    try:
        info = sf.info(str(audio_path))
    except RuntimeError as exc:
        raise ValueError(f"Cannot read audio file: {audio_path}") from exc

    if info.samplerate <= 0:
        return 0.0
    return float(info.frames) / float(info.samplerate)
