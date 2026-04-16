from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from ru_pl_st.data.models import SpeechSample


@dataclass(slots=True)
class ASRHypothesis:
    text: str
    metadata: dict[str, str] = field(default_factory=dict)


class ASRMethod(ABC):
    name: str

    @abstractmethod
    def transcribe(self, sample: SpeechSample) -> ASRHypothesis:
        raise NotImplementedError

