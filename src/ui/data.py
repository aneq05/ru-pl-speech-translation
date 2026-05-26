from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from reference_texts import get_reference_by_file_name

MIC = "\U0001F399\ufe0f"
BUBBLE = "\U0001FAE7"
LETTERS = "\U0001F520"
NOTE = "\U0001F4DD"
HEART = "\U0001F497"


# Default fallback reference with proper Cyrillic and Polish alphabets
DEFAULT_REFERENCE = {
    "title": "Shla Sasha po shosse",
    "original": "Шла Саша по шоссе и сосала сушку.",
    "polish": "Szła Sasza po szosie i ssała suszkę.",
}


def build_demo_payload() -> dict[str, Any]:
    return {
        "file_name": "tongue_twister_demo.wav",
        "detected_language": "Russian",
        "confidence": 0.95,
        "segments": [
            {"word": "Shla", "confidence": 0.98},
            {"word": "Sasha", "confidence": 0.97},
            {"word": "po", "confidence": 0.95},
            {"word": "shosse", "confidence": 0.96},
            {"word": "i", "confidence": 0.92},
            {"word": "sosala", "confidence": 0.91},
            {"word": "sushku", "confidence": 0.93},
        ],
        "recognized_text": "Shla Sasha po shosse i sosala sushku.",
        "translation": "Szla Sasza po szosie i ssala suszke.",
    }


def build_flow_steps(has_audio: bool, has_result: bool) -> list[dict[str, str]]:
    base_steps = [
        {"icon": MIC, "title": "Upload", "detail": "Audio selected"},
        {"icon": BUBBLE, "title": "ASR", "detail": "Speech decoding"},
        {"icon": LETTERS, "title": "Words", "detail": "Word sequence"},
        {"icon": NOTE, "title": "Transcript", "detail": "Sentence assembly"},
        {"icon": HEART, "title": "PL", "detail": "Polish output"},
    ]

    if has_result:
        current_index = len(base_steps) + 1
    elif has_audio:
        current_index = 2
    else:
        current_index = 1

    steps: list[dict[str, str]] = []
    for index, step in enumerate(base_steps, start=1):
        if has_result:
            state = "done"
        elif index < current_index:
            state = "done"
        elif index == current_index:
            state = "active"
        else:
            state = "pending"

        steps.append(
            {
                "index": str(index),
                "icon": step["icon"],
                "title": step["title"],
                "detail": step["detail"],
                "state": state,
            }
        )

    return steps


def get_tongue_twister_reference(file_name: str | None) -> dict[str, str]:
    if not file_name:
        return DEFAULT_REFERENCE

    entry = get_reference_by_file_name(file_name)
    if entry is not None:
        return {
            "title": entry.title,
            "original": entry.russian_original,
            "polish": entry.polish_translation,
        }

    return {
        "title": "Unknown reference",
        "original": f"No matched reference for filename: {Path(file_name).name}",
        "polish": "No matched Polish translation.",
    }


def find_latest_benchmark_run(report_root_dir: str | Path = "reports/results") -> Path | None:
    root = Path(report_root_dir)
    if not root.exists():
        return None

    run_dirs = [path for path in root.iterdir() if path.is_dir() and path.name.startswith("run_")]
    if not run_dirs:
        return None

    run_dirs.sort(key=lambda path: path.stat().st_mtime, reverse=True)
    return run_dirs[0]


def load_leaderboard_rows(run_dir: Path) -> list[dict[str, Any]]:
    csv_path = run_dir / "leaderboard.csv"
    if not csv_path.exists():
        return []

    rows: list[dict[str, Any]] = []
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rows.append(_convert_row_types(row))

    return rows


def load_detailed_rows(run_dir: Path) -> list[dict[str, Any]]:
    csv_path = run_dir / "detailed_results.csv"
    if not csv_path.exists():
        return []

    rows: list[dict[str, Any]] = []
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rows.append(_convert_row_types(row))

    return rows


def get_plot_paths(run_dir: Path) -> list[Path]:
    plots_dir = run_dir / "plots"
    if not plots_dir.exists():
        return []

    supported_suffixes = {".png", ".jpg", ".jpeg", ".webp"}
    paths = [path for path in plots_dir.iterdir() if path.is_file() and path.suffix.lower() in supported_suffixes]
    paths.sort()
    return paths


def _convert_row_types(row: dict[str, str]) -> dict[str, Any]:
    converted: dict[str, Any] = {}
    for key, value in row.items():
        if value is None:
            converted[key] = value
            continue

        normalized = value.strip()
        if normalized == "":
            converted[key] = ""
            continue

        try:
            if "." in normalized:
                converted[key] = float(normalized)
            else:
                converted[key] = int(normalized)
            continue
        except ValueError:
            converted[key] = normalized

    return converted
