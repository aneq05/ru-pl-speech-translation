from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


TEMPLATE_COLUMNS = [
    "sample_id",
    "speaker_id",
    "audio_path",
    "split",
    "ru_transcript_ref",
    "pl_translation_ref",
    "noise_condition",
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a CSV template for project manifests.")
    parser.add_argument("--output", type=Path, required=True, help="Path to output CSV file.")
    args = parser.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(columns=TEMPLATE_COLUMNS).to_csv(args.output, index=False)
    print(f"Template created: {args.output}")


if __name__ == "__main__":
    main()

