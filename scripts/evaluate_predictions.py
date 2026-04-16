from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from ru_pl_st.eval.metrics import evaluate_all


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate experiment predictions.")
    parser.add_argument("--predictions", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    df = pd.read_csv(args.predictions)

    asr_refs = df["ru_transcript_ref"].fillna("").tolist()
    asr_hyps = df["ru_transcript_hyp"].fillna("").tolist()
    mt_refs = df["pl_translation_ref"].fillna("").tolist()
    mt_hyps = df["pl_translation_hyp"].fillna("").tolist()

    result = evaluate_all(asr_refs=asr_refs, asr_hyps=asr_hyps, mt_refs=mt_refs, mt_hyps=mt_hyps)

    print("Evaluation results")
    print(f"WER:  {result.wer}")
    print(f"CER:  {result.cer}")
    print(f"BLEU: {result.bleu}")
    print(f"chrF: {result.chrf}")


if __name__ == "__main__":
    main()

