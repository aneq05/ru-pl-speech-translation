from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass

_PUNCTUATION_PATTERN = re.compile(r"[^\w\s]", flags=re.UNICODE)
_MULTISPACE_PATTERN = re.compile(r"\s+")


@dataclass(slots=True, frozen=True)
class TextMetrics:
    wer: float
    cer: float
    token_precision: float
    token_recall: float
    token_f1: float
    exact_match: float
    reference_token_count: int
    hypothesis_token_count: int


def compute_text_metrics(reference_text: str, hypothesis_text: str) -> TextMetrics:
    ref_norm = normalize_text(reference_text)
    hyp_norm = normalize_text(hypothesis_text)

    ref_tokens = ref_norm.split() if ref_norm else []
    hyp_tokens = hyp_norm.split() if hyp_norm else []

    wer = _error_rate(ref_tokens, hyp_tokens)
    cer = _error_rate(list(ref_norm.replace(" ", "")), list(hyp_norm.replace(" ", "")))
    precision, recall, f1 = _token_overlap_scores(ref_tokens, hyp_tokens)

    return TextMetrics(
        wer=wer,
        cer=cer,
        token_precision=precision,
        token_recall=recall,
        token_f1=f1,
        exact_match=1.0 if ref_norm == hyp_norm and ref_norm else 0.0,
        reference_token_count=len(ref_tokens),
        hypothesis_token_count=len(hyp_tokens),
    )


def normalize_text(text: str) -> str:
    normalized = text.strip().lower().replace("ё", "е")
    normalized = _PUNCTUATION_PATTERN.sub(" ", normalized)
    normalized = _MULTISPACE_PATTERN.sub(" ", normalized)
    return normalized.strip()


def _token_overlap_scores(ref_tokens: list[str], hyp_tokens: list[str]) -> tuple[float, float, float]:
    if not ref_tokens and not hyp_tokens:
        return (1.0, 1.0, 1.0)
    if not hyp_tokens:
        return (0.0, 0.0, 0.0)
    if not ref_tokens:
        return (0.0, 0.0, 0.0)

    ref_counter = Counter(ref_tokens)
    hyp_counter = Counter(hyp_tokens)
    true_positive = sum((ref_counter & hyp_counter).values())

    precision = true_positive / max(1, sum(hyp_counter.values()))
    recall = true_positive / max(1, sum(ref_counter.values()))
    if precision + recall == 0:
        f1 = 0.0
    else:
        f1 = 2 * precision * recall / (precision + recall)
    return (precision, recall, f1)


def _error_rate(reference: list[str], hypothesis: list[str]) -> float:
    if not reference and not hypothesis:
        return 0.0
    if not reference:
        return 1.0
    distance = _levenshtein_distance(reference, hypothesis)
    return distance / len(reference)


def _levenshtein_distance(reference: list[str], hypothesis: list[str]) -> int:
    if reference == hypothesis:
        return 0
    if not reference:
        return len(hypothesis)
    if not hypothesis:
        return len(reference)

    previous_row = list(range(len(hypothesis) + 1))
    for ref_index, ref_value in enumerate(reference, start=1):
        current_row = [ref_index]
        for hyp_index, hyp_value in enumerate(hypothesis, start=1):
            substitution_cost = 0 if ref_value == hyp_value else 1
            insertions = current_row[hyp_index - 1] + 1
            deletions = previous_row[hyp_index] + 1
            substitutions = previous_row[hyp_index - 1] + substitution_cost
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]
