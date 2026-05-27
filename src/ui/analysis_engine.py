from __future__ import annotations

import re
import tempfile
from functools import lru_cache
from pathlib import Path
from typing import Any
from difflib import SequenceMatcher

from benchmarking.model_registry import create_model
from benchmarking.models.base import ASRModel
from reference_texts import get_reference_by_file_name, load_reference_catalog
from ui.translation_engine import translate_ru_text_to_polish
from benchmarking.models.whisper_adapter import WhisperASRModel

try:
    from unidecode import unidecode
    def _transliterate(text: str) -> str:
        return unidecode(text)
except Exception:
    def _transliterate(text: str) -> str:
        return text

ANALYSIS_MODEL_ID = "whisper:small"
DEFAULT_LANGUAGE = "ru"
DEFAULT_DEVICE = "cpu"

_TOKEN_PATTERN = re.compile(r"[^\s]+", flags=re.UNICODE)
_NON_WORD_PATTERN = re.compile(r"[^\w\s]+", flags=re.UNICODE)
_MULTISPACE_PATTERN = re.compile(r"\s+", flags=re.UNICODE)
_MIN_CONTENT_MATCH_SCORE = 0.58


def analyze_uploaded_audio(
    audio_file: Any,
    *,
    language: str = DEFAULT_LANGUAGE,
    device: str = DEFAULT_DEVICE,
) -> dict[str, Any]:
    audio_bytes = audio_file.getvalue()
    temp_path = _write_temp_audio(audio_bytes, audio_file_name=getattr(audio_file, "name", "upload.wav"))
    try:
        model = _get_analysis_model(language=language, device=device)
        if model.__class__.__name__ == "WhisperASRModel" or isinstance(model, WhisperASRModel):
            transcribe_fn = getattr(model, "transcribe")
            prediction = model.transcribe(temp_path)
        else:
            prediction = model.transcribe(temp_path)
    except Exception as e:
        raise RuntimeError(f"ASR transcription failed: {e}")
    finally:
        temp_path.unlink(missing_ok=True)

    if isinstance(prediction, dict):
        recognized_text = str(prediction.get("text", "")).strip()
        raw_segments = prediction.get("segments", [])
        detected_language = prediction.get("language", "ru")
        raw_confidence = prediction.get("confidence", None)
    else:
        recognized_text = str(getattr(prediction, "text", "")).strip()
        raw_segments = getattr(prediction, "segments", [])
        detected_language = getattr(prediction, "language", "ru")
        raw_confidence = getattr(prediction, "confidence", None)

    
    polish_output, translation_source = _resolve_polish_output(
        file_name=getattr(audio_file, "name", ""),
        recognized_text=recognized_text,
        device=device,
    )

    return {
        "file_name": getattr(audio_file, "name", temp_path.name),
        "model_id": ANALYSIS_MODEL_ID,
        "detected_language": detected_language or "ru",
        "confidence": _resolve_confidence(raw_confidence),
        "segments": _flatten_word_segments(raw_segments, fallback_text=recognized_text),
        "recognized_text": recognized_text,
        "translation": polish_output,
        "translation_source": translation_source,
    }


@lru_cache(maxsize=2)
def _get_analysis_model(*, language: str, device: str) -> ASRModel:
    return create_model(
        ANALYSIS_MODEL_ID,
        language=language,
        device=device,
    )


def _write_temp_audio(audio_bytes: bytes, *, audio_file_name: str) -> Path:
    suffix = Path(audio_file_name).suffix or ".wav"
    with tempfile.NamedTemporaryFile(prefix="analysis_", suffix=suffix, delete=False) as handle:
        handle.write(audio_bytes)
        return Path(handle.name)


def _resolve_polish_output(*, file_name: str, recognized_text: str, device: str) -> tuple[str, str]:
    reference = get_reference_by_file_name(file_name) if file_name else None
    if reference is not None and reference.polish_translation.strip():
        return reference.polish_translation.strip(), "reference_catalog"

    matched_from_content = _resolve_polish_from_recognized_text(recognized_text)
    if matched_from_content is not None:
        return matched_from_content, "recognized_text_match"

    model_translation = translate_ru_text_to_polish(recognized_text, device=device)
    if model_translation.status == "ok":
        return model_translation.text, "model_translation"

    if model_translation.status in {"backend_unavailable", "model_load_error", "inference_error"}:
        return "", "translation_model_unavailable"

    if recognized_text.strip():
        return "", "missing_translation"

    return "", "none"


def _resolve_polish_from_recognized_text(recognized_text: str) -> str | None:
    normalized_recognized = _normalize_text(recognized_text)
    if not normalized_recognized:
        return None
    normalized_recognized_ascii = _normalize_text(_transliterate(normalized_recognized))

    try:
        catalog = load_reference_catalog()
    except Exception:
        return None

    best_score = 0.0
    best_translation: str | None = None
    recognized_tokens = set(normalized_recognized.split())
    recognized_tokens_ascii = set(normalized_recognized_ascii.split())
    for entry in catalog.by_id.values():
        normalized_original = _normalize_text(entry.russian_original)
        if not normalized_original:
            continue
        normalized_original_ascii = _normalize_text(_transliterate(normalized_original))

        reference_tokens = set(normalized_original.split())
        reference_tokens_ascii = set(normalized_original_ascii.split())

        cyrillic_score = _similarity_score(
            left_text=normalized_recognized,
            right_text=normalized_original,
            left_tokens=recognized_tokens,
            right_tokens=reference_tokens,
        )
        ascii_score = _similarity_score(
            left_text=normalized_recognized_ascii,
            right_text=normalized_original_ascii,
            left_tokens=recognized_tokens_ascii,
            right_tokens=reference_tokens_ascii,
        )
        score = max(cyrillic_score, ascii_score)

        if score > best_score and entry.polish_translation.strip():
            best_score = score
            best_translation = entry.polish_translation.strip()

    if best_translation is None or best_score < _MIN_CONTENT_MATCH_SCORE:
        return None
    return best_translation


def _similarity_score(
    *,
    left_text: str,
    right_text: str,
    left_tokens: set[str],
    right_tokens: set[str],
) -> float:
    if not left_text or not right_text:
        return 0.0
    char_similarity = SequenceMatcher(None, left_text, right_text).ratio()
    token_overlap = _token_overlap(left_tokens, right_tokens)
    return 0.68 * char_similarity + 0.32 * token_overlap


def _normalize_text(text: str) -> str:
    normalized = text.strip().lower()
    normalized = _NON_WORD_PATTERN.sub(" ", normalized)
    normalized = _MULTISPACE_PATTERN.sub(" ", normalized)
    return normalized.strip()


def _token_overlap(left: set[str], right: set[str]) -> float:
    if not left and not right:
        return 1.0
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def _flatten_word_segments(segments: list[Any], *, fallback_text: str) -> list[dict[str, Any]]:
    if not segments:
        segments = []
    
    words: list[dict[str, Any]] = []
    order = 0
    for segment in segments:
        if isinstance(segment, dict):
            text = str(segment.get("text", "")).strip()
            confidence = _resolve_confidence(segment.get("confidence", None))
        else:
            text = str(getattr(segment, "text", "")).strip()
            confidence = _resolve_confidence(getattr(segment, "confidence", None))

        if not text:
            continue
        
        for token in _TOKEN_PATTERN.findall(text):
            order += 1
            words.append(
                {
                    "order": order,
                    "word": token,
                    "confidence": confidence,
                }
            )

    if words:
        return words

    fallback_confidence = 0.5
    for idx, token in enumerate(_TOKEN_PATTERN.findall(fallback_text), start=1):
        words.append({"order": idx, "word": token, "confidence": fallback_confidence})
    return words


def _resolve_confidence(value: Any) -> float:
    if value is None:
        return 0.5
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return 0.5
    return max(0.0, min(1.0, numeric))
