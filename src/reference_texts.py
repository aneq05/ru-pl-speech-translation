from __future__ import annotations

import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

DEFAULT_REFERENCE_DIR = Path("data/reference_texts")
MAP_FILE_NAME = "audio_key_map.json"

_NON_ALNUM_PATTERN = re.compile(r"[^a-z0-9]+")


@dataclass(slots=True, frozen=True)
class ReferenceEntry:
    reference_id: str
    title: str
    russian_original: str
    polish_translation: str


@dataclass(slots=True, frozen=True)
class ReferenceCatalog:
    by_id: dict[str, ReferenceEntry]
    audio_key_to_id: dict[str, str]


def normalize_audio_key(file_name: str) -> str:
    stem = Path(file_name).stem.lower()
    return _NON_ALNUM_PATTERN.sub("_", stem).strip("_")


def get_reference_by_file_name(file_name: str, reference_dir: str | Path = DEFAULT_REFERENCE_DIR) -> ReferenceEntry | None:
    catalog = load_reference_catalog(reference_dir)
    key = normalize_audio_key(file_name)
    reference_id = catalog.audio_key_to_id.get(key)
    if reference_id is None:
        return None
    return catalog.by_id.get(reference_id)


@lru_cache(maxsize=8)
def load_reference_catalog(reference_dir: str | Path = DEFAULT_REFERENCE_DIR) -> ReferenceCatalog:
    base_dir = Path(reference_dir)
    map_path = base_dir / MAP_FILE_NAME
    if not map_path.exists():
        raise FileNotFoundError(f"Reference mapping file not found: {map_path}")

    payload = json.loads(map_path.read_text(encoding="utf-8-sig"))
    raw_map = payload.get("audio_key_to_reference_id")
    if not isinstance(raw_map, dict):
        raise ValueError(f"Invalid mapping format in {map_path}: expected object 'audio_key_to_reference_id'")

    titles_payload = payload.get("titles")
    titles = titles_payload if isinstance(titles_payload, dict) else {}

    audio_key_to_id: dict[str, str] = {}
    for key, value in raw_map.items():
        if not isinstance(key, str) or not isinstance(value, str):
            continue
        normalized_key = key.strip().lower()
        reference_id = value.strip()
        if normalized_key and reference_id:
            audio_key_to_id[normalized_key] = reference_id

    unique_ids = sorted(set(audio_key_to_id.values()))
    by_id: dict[str, ReferenceEntry] = {}
    for reference_id in unique_ids:
        ru_path = base_dir / "ru" / f"{reference_id}.txt"
        pl_path = base_dir / "pl" / f"{reference_id}.txt"
        if not ru_path.exists():
            raise FileNotFoundError(f"Missing Russian reference file: {ru_path}")
        if not pl_path.exists():
            raise FileNotFoundError(f"Missing Polish reference file: {pl_path}")

        ru_text = ru_path.read_text(encoding="utf-8-sig").strip()
        pl_text = pl_path.read_text(encoding="utf-8-sig").strip()
        title = str(titles.get(reference_id, reference_id)).strip() or reference_id
        by_id[reference_id] = ReferenceEntry(
            reference_id=reference_id,
            title=title,
            russian_original=ru_text,
            polish_translation=pl_text,
        )

    return ReferenceCatalog(by_id=by_id, audio_key_to_id=audio_key_to_id)
