from __future__ import annotations

import argparse
from pathlib import Path

from env_loader import load_env_file


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ASR benchmark runner for RU tongue-twister dataset.")
    subparsers = parser.add_subparsers(dest="command")

    benchmark_parser = subparsers.add_parser("benchmark", help="Run model comparison benchmark.")
    benchmark_parser.add_argument(
        "--data-dir",
        default="data/raw",
        help="Path to dataset directory with audio files and references.",
    )
    benchmark_parser.add_argument(
        "--reports-dir",
        default="reports/results",
        help="Output directory for benchmark reports and plots.",
    )
    benchmark_parser.add_argument(
        "--models",
        nargs="+",
        default=None,
        help=(
            "Model ids, e.g. whisper:tiny whisper:small "
            "hf:jonatasgrosman/wav2vec2-large-xlsr-53-russian"
        ),
    )
    benchmark_parser.add_argument(
        "--models-config",
        default="configs/models.yaml",
        help="Path to YAML config with default model list (used when --models is not provided).",
    )
    benchmark_parser.add_argument(
        "--language",
        default="ru",
        help="Language code used by ASR models (default: ru).",
    )
    benchmark_parser.add_argument(
        "--device",
        default="cpu",
        help="Device for inference, e.g. cpu or cuda.",
    )

    return parser


def main() -> None:
    load_env_file()

    parser = build_parser()
    args = parser.parse_args()

    if args.command in (None, "benchmark"):
        from benchmarking.runner import run_benchmark

        run_benchmark(
            raw_data_dir=Path(args.data_dir),
            report_root_dir=Path(args.reports_dir),
            model_ids=args.models,
            models_config_path=Path(args.models_config) if args.models_config else None,
            language=args.language,
            device=args.device,
        )
        return

    parser.error(f"Unknown command: {args.command}")
