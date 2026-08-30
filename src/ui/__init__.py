from __future__ import annotations

from typing import Any

__all__ = ["run_app"]


def __getattr__(name: str) -> Any:
    if name == "run_app":
        from ui.page import run_app

        return run_app
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
