from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Any


MIC = "\U0001F399\ufe0f"
BUBBLE = "\U0001FAE7"
LETTERS = "\U0001F520"
NOTE = "\U0001F4DD"
HEART = "\U0001F497"


DEFAULT_REFERENCE = {
    "original": "\u0428\u043b\u0430 \u0421\u0430\u0448\u0430 \u043f\u043e \u0448\u043e\u0441\u0441\u0435 \u0438 \u0441\u043e\u0441\u0430\u043b\u0430 \u0441\u0443\u0448\u043a\u0443.",
    "polish": "Sz\u0142a Sasza po szosie i ssa\u0142a suszk\u0119.",
}


REFERENCE_BY_KEYWORD = [
    {
        "keywords": ["tongue_twister_demo", "shla_sasha", "sasha", "shosse"],
        "original": "\u0428\u043b\u0430 \u0421\u0430\u0448\u0430 \u043f\u043e \u0448\u043e\u0441\u0441\u0435 \u0438 \u0441\u043e\u0441\u0430\u043b\u0430 \u0441\u0443\u0448\u043a\u0443.",
        "polish": "Sz\u0142a Sasza po szosie i ssa\u0142a suszk\u0119.",
    },
    {
        "keywords": ["greka", "reku", "rak"],
        "original": "\u0415\u0445\u0430\u043b \u0413\u0440\u0435\u043a\u0430 \u0447\u0435\u0440\u0435\u0437 \u0440\u0435\u043a\u0443, \u0432\u0438\u0434\u0438\u0442 \u0413\u0440\u0435\u043a\u0430 \u2014 \u0432 \u0440\u0435\u043a\u0435 \u0440\u0430\u043a.",
        "polish": "Jechal Greka przez rzeke, widzi Greka: w rzece rak.",
    },
    {
        "keywords": ["drova", "trava", "dvor"],
        "original": "\u041d\u0430 \u0434\u0432\u043e\u0440\u0435 \u0442\u0440\u0430\u0432\u0430, \u043d\u0430 \u0442\u0440\u0430\u0432\u0435 \u0434\u0440\u043e\u0432\u0430.",
        "polish": "Na podworzu trawa, na trawie drewno.",
    },
]


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

    normalized = _normalize_file_name(file_name)
    for entry in REFERENCE_BY_KEYWORD:
        if any(keyword in normalized for keyword in entry["keywords"]):
            return {
                "original": entry["original"],
                "polish": entry["polish"],
            }

    return {
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


def get_plot_paths(run_dir: Path) -> list[Path]:
    plots_dir = run_dir / "plots"
    if not plots_dir.exists():
        return []

    supported_suffixes = {".png", ".jpg", ".jpeg", ".webp"}
    paths = [path for path in plots_dir.iterdir() if path.is_file() and path.suffix.lower() in supported_suffixes]
    paths.sort()
    return paths


def _normalize_file_name(file_name: str) -> str:
    stem = Path(file_name).stem.lower()
    return re.sub(r"[^a-z0-9]+", "_", stem).strip("_")


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
