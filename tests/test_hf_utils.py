from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from hf_utils import call_hf_loader_with_token_fallback, configure_hf_cache, read_hf_token


class TestHfUtils:
    def test_configure_hf_cache_sets_expected_environment(
        self,
        monkeypatch,
        tmp_path: Path,
    ) -> None:
        for key in ("HF_HOME", "HF_HUB_CACHE", "TRANSFORMERS_CACHE", "HF_ASSETS_CACHE"):
            monkeypatch.delenv(key, raising=False)

        cache_root = configure_hf_cache(tmp_path / "hf-cache")

        assert cache_root == (tmp_path / "hf-cache").resolve()
        assert os.environ["HF_HOME"] == str(cache_root)
        assert os.environ["HF_HUB_CACHE"] == str(cache_root / "hub")
        assert os.environ["TRANSFORMERS_CACHE"] == str(cache_root / "transformers")
        assert os.environ["HF_ASSETS_CACHE"] == str(cache_root / "assets")
        assert (cache_root / "hub").is_dir()

    def test_read_hf_token_supports_legacy_env_name(self, monkeypatch) -> None:
        monkeypatch.delenv("HF_TOKEN", raising=False)
        monkeypatch.setenv("HUGGING_FACE_HUB_TOKEN", " hf_example ")

        assert read_hf_token() == "hf_example"
        assert os.environ["HF_TOKEN"] == "hf_example"

    def test_call_hf_loader_with_token_fallback_retries_use_auth_token(self) -> None:
        calls: list[dict[str, Any]] = []

        def loader(model_id: str, **kwargs: Any) -> tuple[str, dict[str, Any]]:
            calls.append(kwargs)
            if "token" in kwargs:
                raise TypeError("got an unexpected keyword argument 'token'")
            return model_id, kwargs

        result = call_hf_loader_with_token_fallback(
            loader,
            "model-id",
            kwargs={"cache_dir": "cache", "token": "hf_example"},
        )

        assert result == ("model-id", {"cache_dir": "cache", "use_auth_token": "hf_example"})
        assert calls == [
            {"cache_dir": "cache", "token": "hf_example"},
            {"cache_dir": "cache", "use_auth_token": "hf_example"},
        ]
