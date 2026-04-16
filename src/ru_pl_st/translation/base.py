from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from ru_pl_st.data.models import SpeechSample


@dataclass(slots=True)
class TranslationHypothesis:
    text: str
    metadata: dict[str, str] = field(default_factory=dict)


class TranslationMethod(ABC):
    name: str

    @abstractmethod
    def translate(
        self,
        ru_text: str,
        ru_tokens: list[str],
        sample: SpeechSample,
    ) -> TranslationHypothesis:
        raise NotImplementedError

