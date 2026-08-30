from __future__ import annotations

from pathlib import Path

import pytest

from benchmarking import model_registry
from benchmarking.models.base import ASRModel, ASRModelUnavailableError
from benchmarking.types import ASRPrediction


class DummyModel(ASRModel):
    def transcribe(self, audio_path: Path) -> ASRPrediction:
        return ASRPrediction(text="")


class TestModelRegistry:
    def test_create_model_routes_whisper_ids_to_whisper_adapter(self, monkeypatch) -> None:
        calls: list[dict[str, str]] = []

        def fake_whisper_model(*, model_size: str, language: str, device: str) -> DummyModel:
            calls.append({"model_size": model_size, "language": language, "device": device})
            return DummyModel("whisper:small")

        monkeypatch.setattr(model_registry, "WhisperASRModel", fake_whisper_model)

        model = model_registry.create_model("whisper:small", language="ru", device="cpu")

        assert model.model_id == "whisper:small"
        assert calls == [{"model_size": "small", "language": "ru", "device": "cpu"}]

    def test_create_model_routes_hf_ids_to_transformers_adapter(self, monkeypatch) -> None:
        calls: list[dict[str, str]] = []

        def fake_hf_model(*, model_name: str, device: str) -> DummyModel:
            calls.append({"model_name": model_name, "device": device})
            return DummyModel(f"hf:{model_name}")

        monkeypatch.setattr(model_registry, "HFTransformersASRModel", fake_hf_model)

        model = model_registry.create_model("hf:owner/model", device="cuda")

        assert model.model_id == "hf:owner/model"
        assert calls == [{"model_name": "owner/model", "device": "cuda"}]

    def test_create_models_reports_unavailable_backends(self, monkeypatch) -> None:
        def fake_create_model(model_id: str, *, language: str, device: str) -> DummyModel:
            if model_id == "whisper:missing":
                raise ASRModelUnavailableError("missing dependency")
            return DummyModel(model_id)

        monkeypatch.setattr(model_registry, "create_model", fake_create_model)

        models, unavailable = model_registry.create_models(
            ["whisper:missing", "whisper:tiny"],
            language="ru",
            device="cpu",
        )

        assert [model.model_id for model in models] == ["whisper:tiny"]
        assert unavailable == ["whisper:missing"]

    def test_create_model_rejects_unknown_model_id(self) -> None:
        with pytest.raises(ValueError, match="Supported formats"):
            model_registry.create_model("local-model")
