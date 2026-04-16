from __future__ import annotations

from abc import ABC, abstractmethod

from ru_pl_st.data.models import SpeechSample


class TTSMethod(ABC):
    name: str

    @abstractmethod
    def synthesize(self, pl_text: str, sample: SpeechSample) -> str:
        raise NotImplementedError

