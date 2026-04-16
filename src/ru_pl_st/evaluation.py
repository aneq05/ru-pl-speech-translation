from __future__ import annotations

from pathlib import Path


def compute_wer(reference_texts: list[str], hypothesis_texts: list[str]) -> float:
    raise NotImplementedError("TODO: implement WER computation.")


def compute_cer(reference_texts: list[str], hypothesis_texts: list[str]) -> float:
    raise NotImplementedError("TODO: implement CER computation.")


def compute_bleu(reference_texts: list[str], hypothesis_texts: list[str]) -> float:
    raise NotImplementedError("TODO: implement BLEU computation.")


def compute_chrf(reference_texts: list[str], hypothesis_texts: list[str]) -> float:
    raise NotImplementedError("TODO: implement chrF computation.")


def compare_methods(result_files: list[Path]) -> None:
    """
    TODO:
    - load results from multiple methods
    - compute aggregate metrics
    - generate final comparison table for report
    """
    raise NotImplementedError("TODO: implement methods comparison report.")

