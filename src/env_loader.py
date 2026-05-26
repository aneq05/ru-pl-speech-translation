from __future__ import annotations

import os
from pathlib import Path

_ENV_LOAD_ATTEMPTED = False


def load_env_file(env_path: str | Path | None = None) -> Path | None:
    """Load KEY=VALUE pairs from .env into os.environ if not already set."""
    global _ENV_LOAD_ATTEMPTED

    if _ENV_LOAD_ATTEMPTED:
        return None
    _ENV_LOAD_ATTEMPTED = True

    path = Path(env_path) if env_path is not None else _default_env_path()
    if not path.exists():
        return None

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        parsed = _parse_env_line(raw_line)
        if parsed is None:
            continue
        key, value = parsed
        os.environ.setdefault(key, value)

    return path


def _default_env_path() -> Path:
    return Path(__file__).resolve().parents[1] / ".env"


def _parse_env_line(raw_line: str) -> tuple[str, str] | None:
    line = raw_line.strip()
    if not line or line.startswith("#"):
        return None
    if line.startswith("export "):
        line = line[len("export ") :].strip()
    if "=" not in line:
        return None

    key, raw_value = line.split("=", maxsplit=1)
    key = key.strip()
    if not key:
        return None

    value = raw_value.strip()
    if value and value[0] in {"'", '"'} and value[-1] == value[0]:
        value = value[1:-1]
    return key, value
