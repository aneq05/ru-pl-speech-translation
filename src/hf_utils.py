from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Callable

DEFAULT_HF_CACHE_ROOT = Path("models_cache/huggingface")
HF_TOKEN_ENV_NAMES = ("HF_TOKEN", "HUGGING_FACE_HUB_TOKEN")


def configure_hf_cache(cache_root: str | Path = DEFAULT_HF_CACHE_ROOT) -> Path:
    resolved_cache_root = Path(cache_root).resolve()
    hub_cache = resolved_cache_root / "hub"
    transformers_cache = resolved_cache_root / "transformers"
    assets_cache = resolved_cache_root / "assets"

    for path in (resolved_cache_root, hub_cache, transformers_cache, assets_cache):
        path.mkdir(parents=True, exist_ok=True)

    os.environ.setdefault("HF_HOME", str(resolved_cache_root))
    os.environ.setdefault("HF_HUB_CACHE", str(hub_cache))
    os.environ.setdefault("TRANSFORMERS_CACHE", str(transformers_cache))
    os.environ.setdefault("HF_ASSETS_CACHE", str(assets_cache))
    return resolved_cache_root


def read_hf_token() -> str | None:
    for key in HF_TOKEN_ENV_NAMES:
        value = os.getenv(key)
        if value and value.strip():
            token = value.strip()
            os.environ.setdefault("HF_TOKEN", token)
            return token
    return None


def call_hf_loader_with_token_fallback(
    loader: Callable[..., Any],
    *args: Any,
    kwargs: dict[str, Any],
) -> Any:
    try:
        return loader(*args, **kwargs)
    except TypeError as exc:
        if "token" not in kwargs or "token" not in str(exc):
            raise

    fallback_kwargs = dict(kwargs)
    token = fallback_kwargs.pop("token", None)
    if token is not None:
        fallback_kwargs["use_auth_token"] = token
    return loader(*args, **fallback_kwargs)
