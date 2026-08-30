from __future__ import annotations

from pathlib import Path

import pytest

from benchmarking.reporting import (
    build_leaderboard,
    write_detailed_results_csv,
    write_leaderboard_csv,
)
from benchmarking.types import EvaluationRow


def _row(
    *,
    model_id: str,
    sample_id: str,
    wer: float,
    cer: float,
    token_f1: float,
    latency_sec: float,
    confidence: float | None,
) -> EvaluationRow:
    return EvaluationRow(
        run_id="run-test",
        model_id=model_id,
        sample_id=sample_id,
        audio_path=f"{sample_id}.wav",
        reference_text="reference",
        hypothesis_text="hypothesis",
        duration_sec=2.0,
        latency_sec=latency_sec,
        rtf=latency_sec / 2.0,
        peak_memory_mb=10.0,
        mean_confidence=confidence,
        wer=wer,
        cer=cer,
        token_precision=token_f1,
        token_recall=token_f1,
        token_f1=token_f1,
        exact_match=1.0 if wer == 0.0 else 0.0,
        reference_token_count=1,
        hypothesis_token_count=1,
    )


def test_build_leaderboard_aggregates_and_sorts_by_wer_then_rtf() -> None:
    rows = [
        _row(
            model_id="slow-better",
            sample_id="a",
            wer=0.1,
            cer=0.2,
            token_f1=0.8,
            latency_sec=10.0,
            confidence=0.6,
        ),
        _row(
            model_id="slow-better",
            sample_id="b",
            wer=0.3,
            cer=0.4,
            token_f1=0.6,
            latency_sec=30.0,
            confidence=0.8,
        ),
        _row(
            model_id="fast-tie",
            sample_id="a",
            wer=0.2,
            cer=0.1,
            token_f1=0.7,
            latency_sec=2.0,
            confidence=None,
        ),
        _row(
            model_id="fast-tie",
            sample_id="b",
            wer=0.2,
            cer=0.3,
            token_f1=0.5,
            latency_sec=4.0,
            confidence=None,
        ),
    ]

    leaderboard = build_leaderboard(rows)

    assert [row["model_id"] for row in leaderboard] == ["fast-tie", "slow-better"]
    assert leaderboard[0]["wer_mean"] == pytest.approx(0.2)
    assert leaderboard[0]["rtf_mean"] == pytest.approx(1.5)
    assert leaderboard[0]["confidence_mean"] is None
    assert leaderboard[1]["token_f1_mean"] == pytest.approx(0.7)
    assert leaderboard[1]["confidence_mean"] == pytest.approx(0.7)


def test_report_csv_writers_persist_headers_and_rows(tmp_path: Path) -> None:
    rows = [
        _row(
            model_id="model",
            sample_id="sample",
            wer=0.0,
            cer=0.0,
            token_f1=1.0,
            latency_sec=1.25,
            confidence=0.9,
        )
    ]
    leaderboard = build_leaderboard(rows)

    detailed_path = write_detailed_results_csv(rows, tmp_path / "run" / "detailed_results.csv")
    leaderboard_path = write_leaderboard_csv(leaderboard, tmp_path / "run" / "leaderboard.csv")

    assert detailed_path.read_text(encoding="utf-8").splitlines()[0].startswith("run_id,model_id")
    assert "sample" in detailed_path.read_text(encoding="utf-8")
    assert "wer_mean" in leaderboard_path.read_text(encoding="utf-8")
    assert "model" in leaderboard_path.read_text(encoding="utf-8")
