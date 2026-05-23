from __future__ import annotations

from pathlib import Path
from typing import Any


DEFAULT_MODELS_CONFIG_PATH = Path("configs/models.yaml")


def load_model_ids_from_config(config_path: str | Path) -> list[str]:
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Models config file does not exist: {path}")

    payload = _read_yaml_like(path)
    model_ids = _extract_model_ids(payload)
    if not model_ids:
        raise ValueError(
            f"Models config {path} does not define any valid model ids. "
            "Use either top-level list or `models:` list."
        )
    return model_ids


def _read_yaml_like(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore
    except ImportError:
        return _parse_minimal_yaml_list(text)

    return yaml.safe_load(text)


def _extract_model_ids(payload: Any) -> list[str]:
    if isinstance(payload, list):
        return _normalize_model_ids(payload)

    if isinstance(payload, dict):
        models = payload.get("models")
        return _normalize_model_ids(models)

    return []


def _normalize_model_ids(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    output: list[str] = []
    for item in value:
        if not isinstance(item, str):
            continue
        cleaned = item.strip()
        if cleaned:
            output.append(cleaned)
    return output


def _parse_minimal_yaml_list(text: str) -> Any:
    # Minimal fallback parser for environments without PyYAML.
    # Supports only:
    # 1) top-level list with `- item`
    # 2) `models:` followed by indented `- item`
    lines = _clean_lines(text)
    if not lines:
        return None

    if all(line.lstrip().startswith("-") for line in lines):
        return [_extract_list_item(line) for line in lines]

    for index, line in enumerate(lines):
        if line.strip() == "models:":
            items: list[str] = []
            for child in lines[index + 1 :]:
                if not child.startswith((" ", "\t")):
                    break
                stripped = child.strip()
                if stripped.startswith("-"):
                    items.append(_extract_list_item(stripped))
            return {"models": items}

    raise ValueError(
        "Could not parse models config without PyYAML. Install PyYAML or use one of supported minimal formats."
    )


def _clean_lines(text: str) -> list[str]:
    output: list[str] = []
    for raw_line in text.splitlines():
        line_without_comment = raw_line.split("#", maxsplit=1)[0].rstrip()
        if line_without_comment.strip():
            output.append(line_without_comment)
    return output


def _extract_list_item(line: str) -> str:
    stripped = line.strip()
    if not stripped.startswith("-"):
        raise ValueError(f"Expected list item prefixed with '-': {line}")
    item = stripped[1:].strip().strip("'\"")
    if not item:
        raise ValueError(f"Empty list item in config: {line}")
    return item
