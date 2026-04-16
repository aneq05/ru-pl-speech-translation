from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

import pandas as pd
from tqdm import tqdm

from ru_pl_st.config import load_yaml_config
from ru_pl_st.data.manifest import load_manifest
from ru_pl_st.pipelines.cascade import CascadePipeline
from ru_pl_st.pipelines.integrated import IntegratedPipeline
from ru_pl_st.utils.io import ensure_dir, save_dataframe
from ru_pl_st.utils.logging import get_logger


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run an ASR translation experiment.")
    parser.add_argument("--pipeline", choices=["cascade", "integrated"], required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("experiments"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    logger = get_logger("run_experiment")
    cfg = load_yaml_config(args.config)
    manifest_df = load_manifest(args.manifest)

    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = ensure_dir(args.output_dir / f"{args.pipeline}_{run_id}")
    logger.info("Starting run in %s", run_dir)

    if args.pipeline == "cascade":
        pipeline = CascadePipeline(config=cfg)
    else:
        pipeline = IntegratedPipeline(config=cfg)

    rows: list[dict[str, str]] = []
    for row in tqdm(manifest_df.itertuples(index=False), total=len(manifest_df)):
        output = pipeline.run_sample(row.audio_path)
        rows.append(
            {
                "sample_id": row.sample_id,
                "speaker_id": row.speaker_id,
                "split": row.split,
                "noise_condition": row.noise_condition,
                "ru_transcript_ref": row.ru_transcript_ref,
                "pl_translation_ref": row.pl_translation_ref,
                "ru_transcript_hyp": output["ru_text_hyp"],
                "pl_translation_hyp": output["pl_text_hyp"],
                "pl_audio_hyp_path": output["pl_audio_hyp_path"],
            }
        )

    predictions_path = run_dir / "predictions.csv"
    save_dataframe(pd.DataFrame(rows), predictions_path)
    logger.info("Saved predictions to %s", predictions_path)


if __name__ == "__main__":
    main()

