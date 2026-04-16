from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from jiwer import cer, wer
from sacrebleu import corpus_bleu, corpus_chrf


@dataclass(slots=True)
class EvaluationResult:
    wer: float | None = None
    cer: float | None = None
    bleu: float | None = None
    chrf: float | None = None


def compute_asr_metrics(
    references: Sequence[str],
    hypotheses: Sequence[str],
) -> tuple[float, float]:
    return wer(references, hypotheses), cer(references, hypotheses)


def compute_translation_metrics(
    references: Sequence[str],
    hypotheses: Sequence[str],
) -> tuple[float, float]:
    bleu_score = corpus_bleu(hypotheses, [list(references)]).score
    chrf_score = corpus_chrf(hypotheses, [list(references)]).score
    return bleu_score, chrf_score


def evaluate_all(
    asr_refs: Sequence[str] | None = None,
    asr_hyps: Sequence[str] | None = None,
    mt_refs: Sequence[str] | None = None,
    mt_hyps: Sequence[str] | None = None,
) -> EvaluationResult:
    result = EvaluationResult()
    if asr_refs is not None and asr_hyps is not None:
        result.wer, result.cer = compute_asr_metrics(asr_refs, asr_hyps)
    if mt_refs is not None and mt_hyps is not None:
        result.bleu, result.chrf = compute_translation_metrics(mt_refs, mt_hyps)
    return result

