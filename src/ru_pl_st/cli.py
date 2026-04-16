from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from ru_pl_st.asr.methods import build_asr_methods
from ru_pl_st.comparison.runner import run_cascade_comparison, run_integrated_comparison
from ru_pl_st.data.manifest import create_manifest_template, load_manifest
from ru_pl_st.metrics.text_metrics import build_summary_table
from ru_pl_st.pipelines.integrated import build_integrated_methods
from ru_pl_st.translation.methods import build_translation_methods
from ru_pl_st.utils.io import ensure_dir, make_run_id, save_csv


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="RU->PL speech translation project CLI.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    manifest_parser = subparsers.add_parser("make-manifest-template")
    manifest_parser.add_argument("--output", type=Path, required=True)

    cascade_parser = subparsers.add_parser("run-cascade")
    cascade_parser.add_argument("--manifest", type=Path, required=True)
    cascade_parser.add_argument(
        "--asr-methods",
        type=str,
        default="whisper_ru_sim,vosk_ru_sim",
        help="Comma separated: reference_asr,whisper_ru_sim,vosk_ru_sim",
    )
    cascade_parser.add_argument(
        "--translation-methods",
        type=str,
        default="nllb_ru_pl_sim,marian_ru_pl_sim",
        help="Comma separated: reference_mt,nllb_ru_pl_sim,marian_ru_pl_sim",
    )
    cascade_parser.add_argument("--output-dir", type=Path, default=Path("reports/results"))

    integrated_parser = subparsers.add_parser("run-integrated")
    integrated_parser.add_argument("--manifest", type=Path, required=True)
    integrated_parser.add_argument(
        "--methods",
        type=str,
        default="integrated_s2tt_sim",
        help="Comma separated: integrated_reference,integrated_s2tt_sim",
    )
    integrated_parser.add_argument("--output-dir", type=Path, default=Path("reports/results"))

    full_parser = subparsers.add_parser("run-full-comparison")
    full_parser.add_argument("--manifest", type=Path, required=True)
    full_parser.add_argument(
        "--asr-methods",
        type=str,
        default="whisper_ru_sim,vosk_ru_sim",
    )
    full_parser.add_argument(
        "--translation-methods",
        type=str,
        default="nllb_ru_pl_sim,marian_ru_pl_sim",
    )
    full_parser.add_argument(
        "--integrated-methods",
        type=str,
        default="integrated_s2tt_sim",
    )
    full_parser.add_argument("--output-dir", type=Path, default=Path("reports/results"))

    return parser.parse_args()


def _split_csv_arg(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def _save_results(
    detailed_df: pd.DataFrame,
    output_dir: Path,
    run_prefix: str,
) -> tuple[Path, Path]:
    run_id = make_run_id()
    run_dir = ensure_dir(output_dir / f"{run_prefix}_{run_id}")
    detailed_path = save_csv(detailed_df, run_dir / "detailed_results.csv")
    summary_df = build_summary_table(detailed_df)
    summary_path = save_csv(summary_df, run_dir / "summary_metrics.csv")
    return detailed_path, summary_path


def main() -> None:
    args = parse_args()

    if args.command == "make-manifest-template":
        create_manifest_template(args.output)
        print(f"Created template: {args.output}")
        return

    samples = load_manifest(args.manifest)

    if args.command == "run-cascade":
        asr_methods = build_asr_methods(_split_csv_arg(args.asr_methods))
        translation_methods = build_translation_methods(_split_csv_arg(args.translation_methods))
        detailed_df = run_cascade_comparison(samples, asr_methods, translation_methods)
        detailed_path, summary_path = _save_results(detailed_df, args.output_dir, "cascade")
        print(f"Detailed results: {detailed_path}")
        print(f"Summary metrics: {summary_path}")
        return

    if args.command == "run-integrated":
        methods = build_integrated_methods(_split_csv_arg(args.methods))
        detailed_df = run_integrated_comparison(samples, methods)
        detailed_path, summary_path = _save_results(detailed_df, args.output_dir, "integrated")
        print(f"Detailed results: {detailed_path}")
        print(f"Summary metrics: {summary_path}")
        return

    if args.command == "run-full-comparison":
        asr_methods = build_asr_methods(_split_csv_arg(args.asr_methods))
        translation_methods = build_translation_methods(_split_csv_arg(args.translation_methods))
        integrated_methods = build_integrated_methods(_split_csv_arg(args.integrated_methods))
        cascade_df = run_cascade_comparison(samples, asr_methods, translation_methods)
        integrated_df = run_integrated_comparison(samples, integrated_methods)
        detailed_df = pd.concat([cascade_df, integrated_df], ignore_index=True)
        detailed_path, summary_path = _save_results(detailed_df, args.output_dir, "full")
        print(f"Detailed results: {detailed_path}")
        print(f"Summary metrics: {summary_path}")
        return

    raise ValueError(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()

