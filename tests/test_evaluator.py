from __future__ import annotations

from pathlib import Path

import pytest

from benchmarking.evaluator import _evaluate_single_sample, evaluate_models
from benchmarking.models.base import ASRModel
from benchmarking.types import ASRPrediction, ASRSegment, AudioSample


class StubASRModel(ASRModel):
    def __init__(self, prediction: ASRPrediction) -> None:
        super().__init__("stub:model")
        self.prediction = prediction
        self.seen_paths: list[Path] = []

    def transcribe(self, audio_path: Path) -> ASRPrediction:
        self.seen_paths.append(audio_path)
        return self.prediction


def test_evaluate_single_sample_builds_metrics_without_real_model() -> None:
    sample = AudioSample(
        sample_id="person1__sample",
        audio_path=Path("sample.wav"),
        reference_text="raz dwa trzy",
        duration_sec=2.0,
    )
    model = StubASRModel(
        ASRPrediction(
            text="raz dwa cztery",
            segments=[
                ASRSegment(text="raz dwa", confidence=0.8),
                ASRSegment(text="cztery", confidence=0.4),
            ],
        )
    )

    row = _evaluate_single_sample(run_id="run-test", model=model, sample=sample)

    assert model.seen_paths == [Path("sample.wav")]
    assert row.run_id == "run-test"
    assert row.model_id == "stub:model"
    assert row.wer == pytest.approx(1 / 3)
    assert row.token_f1 == pytest.approx(2 / 3)
    assert row.mean_confidence == pytest.approx(0.6)
    assert row.rtf >= 0.0


def test_evaluate_models_runs_every_model_sample_pair() -> None:
    samples = [
        AudioSample(
            sample_id="sample-a",
            audio_path=Path("a.wav"),
            reference_text="alpha",
            duration_sec=1.0,
        ),
        AudioSample(
            sample_id="sample-b",
            audio_path=Path("b.wav"),
            reference_text="beta",
            duration_sec=1.0,
        ),
    ]
    model = StubASRModel(ASRPrediction(text="alpha"))

    rows = evaluate_models(run_id="run-test", models=[model], samples=samples)

    assert [row.sample_id for row in rows] == ["sample-a", "sample-b"]
    assert model.seen_paths == [Path("a.wav"), Path("b.wav")]
