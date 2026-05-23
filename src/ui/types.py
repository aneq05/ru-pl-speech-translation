from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class SidebarState:
    mode: str
    audio_file: Any
    analyze_clicked: bool
    run_comparison_clicked: bool
