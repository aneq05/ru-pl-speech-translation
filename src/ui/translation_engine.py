from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from env_loader import load_env_file
from hf_utils import call_hf_loader_with_token_fallback, configure_hf_cache, read_hf_token

DEFAULT_RU_PL_MODEL_ID = "facebook/nllb-200-distilled-600M"
SOURCE_LANG_CODE = "rus_Cyrl"
TARGET_LANG_CODE = "pol_Latn"


@dataclass(slots=True, frozen=True)
class TranslationResult:
    text: str
    status: str


class TranslationBackendUnavailableError(RuntimeError):
    pass


class RUToPLTranslator:
    def __init__(self, *, model_id: str, device: str) -> None:
        load_env_file()
        self.model_id = model_id
        self.cache_root = configure_hf_cache()
        hf_token = read_hf_token()

        try:
            import torch
            from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
        except ImportError as exc:
            raise TranslationBackendUnavailableError(
                "RU->PL translation backend unavailable. Install: pip install transformers torch sentencepiece"
            ) from exc

        tokenizer_kwargs: dict[str, Any] = {
            "cache_dir": str((self.cache_root / "hub").resolve()),
            "src_lang": SOURCE_LANG_CODE,
        }
        model_kwargs: dict[str, Any] = {
            "cache_dir": str((self.cache_root / "hub").resolve()),
        }
        if hf_token:
            tokenizer_kwargs["token"] = hf_token
            model_kwargs["token"] = hf_token

        self._tokenizer = call_hf_loader_with_token_fallback(
            AutoTokenizer.from_pretrained,
            model_id,
            kwargs=tokenizer_kwargs,
        )
        self._model = call_hf_loader_with_token_fallback(
            AutoModelForSeq2SeqLM.from_pretrained,
            model_id,
            kwargs=model_kwargs,
        )
        self._torch = torch
        self._torch_device = _resolve_torch_device(torch=torch, requested_device=device)
        self._model.to(self._torch_device)
        self._model.eval()

    def translate(self, text: str, *, max_new_tokens: int = 256) -> str:
        normalized = text.strip()
        if not normalized:
            return ""

        inputs = self._tokenizer(
            normalized,
            return_tensors="pt",
            truncation=True,
            max_length=512,
        )
        inputs = {key: value.to(self._torch_device) for key, value in inputs.items()}

        with self._torch.no_grad():
            translated_tokens = self._model.generate(
                **inputs,
                forced_bos_token_id=self._tokenizer.convert_tokens_to_ids(TARGET_LANG_CODE),
                max_new_tokens=max_new_tokens,
            )
        decoded = self._tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)
        if not decoded:
            return ""
        return decoded[0].strip()


def translate_ru_text_to_polish(text: str, *, device: str = "cpu") -> TranslationResult:
    normalized = text.strip()
    if not normalized:
        return TranslationResult(text="", status="empty_input")

    model_id = os.getenv("RU_PL_TRANSLATION_MODEL_ID", DEFAULT_RU_PL_MODEL_ID).strip() or DEFAULT_RU_PL_MODEL_ID
    try:
        translator = _get_ru_pl_translator(model_id=model_id, device=device)
    except TranslationBackendUnavailableError:
        return TranslationResult(text="", status="backend_unavailable")
    except Exception:
        return TranslationResult(text="", status="model_load_error")

    try:
        translated = translator.translate(normalized)
    except Exception:
        return TranslationResult(text="", status="inference_error")

    if not translated:
        return TranslationResult(text="", status="empty_output")
    return TranslationResult(text=translated, status="ok")


@lru_cache(maxsize=2)
def _get_ru_pl_translator(*, model_id: str, device: str) -> RUToPLTranslator:
    return RUToPLTranslator(model_id=model_id, device=device)


def _resolve_torch_device(*, torch: Any, requested_device: str) -> Any:
    normalized = requested_device.strip().lower()
    if normalized in {"cuda", "gpu"} and torch.cuda.is_available():
        return torch.device("cuda")

    if normalized == "mps":
        mps_backend = getattr(torch.backends, "mps", None)
        if mps_backend is not None and mps_backend.is_available():
            return torch.device("mps")

    return torch.device("cpu")
