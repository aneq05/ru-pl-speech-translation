from __future__ import annotations

import argparse
from pathlib import Path

from ru_pl_st.io import collect_samples_from_raw


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="RU->PL ASR project skeleton CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_cascade = subparsers.add_parser("run-cascade")
    run_cascade.add_argument("--raw-dir", type=Path, default=Path("data/raw"))

    run_integrated = subparsers.add_parser("run-integrated")
    run_integrated.add_argument("--raw-dir", type=Path, default=Path("data/raw"))

    compare = subparsers.add_parser("compare")
    compare.add_argument("--results-file", type=Path, required=True)

    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    if args.command in {"run-cascade", "run-integrated"}:
        samples = collect_samples_from_raw(args.raw_dir)
        print(f"Found {len(samples)} audio file(s) in: {args.raw_dir}")
        print("Project skeleton is ready.")
        print("TODO: implement real model calls in src/ru_pl_st/*.py modules.")
        return

    if args.command == "compare":
        print(f"Comparison input file: {args.results_file}")
        print("TODO: implement method comparison in src/ru_pl_st/evaluation.py.")
        return

    parser.error("Unknown command.")


if __name__ == "__main__":
    main()

