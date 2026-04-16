from __future__ import annotations

import pandas as pd

try:
    from jiwer import cer as jiwer_cer
    from jiwer import wer as jiwer_wer
except ImportError:  # pragma: no cover - dependency handling
    jiwer_cer = None
    jiwer_wer = None

try:
    from sacrebleu import corpus_bleu, corpus_chrf
except ImportError:  # pragma: no cover - dependency handling
    corpus_bleu = None
    corpus_chrf = None


def _require_dependency(symbol: object | None, package_name: str) -> None:
    if symbol is None:
        raise ModuleNotFoundError(
            f"Missing optional dependency '{package_name}'. "
            f"Install it with: pip install {package_name}"
        )


def compute_wer(refs: list[str], hyps: list[str]) -> float:
    _require_dependency(jiwer_wer, "jiwer")
    return float(jiwer_wer(refs, hyps))


def compute_cer(refs: list[str], hyps: list[str]) -> float:
    _require_dependency(jiwer_cer, "jiwer")
    return float(jiwer_cer(refs, hyps))


def compute_bleu(refs: list[str], hyps: list[str]) -> float:
    _require_dependency(corpus_bleu, "sacrebleu")
    return float(corpus_bleu(hyps, [refs]).score)


def compute_chrf(refs: list[str], hyps: list[str]) -> float:
    _require_dependency(corpus_chrf, "sacrebleu")
    return float(corpus_chrf(hyps, [refs]).score)


def build_summary_table(results_df: pd.DataFrame) -> pd.DataFrame:
    summary_rows: list[dict[str, object]] = []

    grouped = results_df.groupby(
        ["approach", "asr_method", "translation_method", "integrated_method"],
        dropna=False,
    )

    for keys, group in grouped:
        approach, asr_method, translation_method, integrated_method = keys
        ru_ref = group["ru_transcript_ref"].fillna("").tolist()
        ru_hyp = group["ru_transcript_hyp"].fillna("").tolist()
        pl_ref = group["pl_translation_ref"].fillna("").tolist()
        pl_hyp = group["pl_translation_hyp"].fillna("").tolist()

        row: dict[str, object] = {
            "approach": approach,
            "asr_method": asr_method,
            "translation_method": translation_method,
            "integrated_method": integrated_method,
            "samples": len(group),
            "bleu": compute_bleu(pl_ref, pl_hyp),
            "chrf": compute_chrf(pl_ref, pl_hyp),
        }

        has_asr_hyps = any(text.strip() for text in ru_hyp)
        if has_asr_hyps:
            row["wer"] = compute_wer(ru_ref, ru_hyp)
            row["cer"] = compute_cer(ru_ref, ru_hyp)
        else:
            row["wer"] = None
            row["cer"] = None

        summary_rows.append(row)

    return pd.DataFrame(summary_rows).sort_values(
        by=["approach", "asr_method", "translation_method", "integrated_method"],
        na_position="last",
    )
