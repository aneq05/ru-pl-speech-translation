from __future__ import annotations

import time
import tracemalloc

from benchmarking.metrics import compute_text_metrics
from benchmarking.models.base import ASRModel
from benchmarking.types import AudioSample, EvaluationRow


def evaluate_models(
    *,
    run_id: str,
    models: list[ASRModel],
    samples: list[AudioSample],
) -> list[EvaluationRow]:
    rows: list[EvaluationRow] = []
    for model in models:
        print(f"[benchmark] evaluating model: {model.model_id}")
        for sample in samples:
            row = _evaluate_single_sample(run_id=run_id, model=model, sample=sample)
            rows.append(row)

    return rows


def _evaluate_single_sample(
    *,
    run_id: str,
    model: ASRModel,
    sample: AudioSample,
) -> EvaluationRow:
    tracemalloc.start()
    start = time.perf_counter()
    prediction = model.transcribe(sample.audio_path)
    latency_sec = time.perf_counter() - start
    _, peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    text_metrics = compute_text_metrics(
        reference_text=sample.reference_text,
        hypothesis_text=prediction.text,
    )
    rtf = latency_sec / sample.duration_sec if sample.duration_sec > 0 else 0.0

    confidence = prediction.confidence
    if confidence is None:
        segment_confidence = [item.confidence for item in prediction.segments if item.confidence is not None]
        confidence = (sum(segment_confidence) / len(segment_confidence)) if segment_confidence else None

    return EvaluationRow(
        run_id=run_id,
        model_id=model.model_id,
        sample_id=sample.sample_id,
        audio_path=str(sample.audio_path),
        reference_text=sample.reference_text,
        hypothesis_text=prediction.text,
        duration_sec=sample.duration_sec,
        latency_sec=latency_sec,
        rtf=rtf,
        peak_memory_mb=peak_bytes / (1024 * 1024),
        mean_confidence=confidence,
        wer=text_metrics.wer,
        cer=text_metrics.cer,
        token_precision=text_metrics.token_precision,
        token_recall=text_metrics.token_recall,
        token_f1=text_metrics.token_f1,
        exact_match=text_metrics.exact_match,
        reference_token_count=text_metrics.reference_token_count,
        hypothesis_token_count=text_metrics.hypothesis_token_count,
    )
