from __future__ import annotations

from pathlib import Path

from benchmarking.config import load_model_ids_from_config


def test_load_model_ids_from_minimal_yaml(tmp_path: Path) -> None:
    config_path = tmp_path / "models.yaml"
    config_path.write_text(
        """
        models:
          - whisper:tiny
          - hf:example/model
        """,
        encoding="utf-8",
    )

    assert load_model_ids_from_config(config_path) == ["whisper:tiny", "hf:example/model"]
