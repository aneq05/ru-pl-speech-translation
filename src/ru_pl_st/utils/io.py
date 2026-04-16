from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd


def ensure_dir(path: str | Path) -> Path:
    target = Path(path)
    target.mkdir(parents=True, exist_ok=True)
    return target


def save_csv(df: pd.DataFrame, path: str | Path) -> Path:
    output_path = Path(path)
    ensure_dir(output_path.parent)
    df.to_csv(output_path, index=False)
    return output_path


def make_run_id() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")

