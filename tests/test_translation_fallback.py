from __future__ import annotations

from types import SimpleNamespace

from ui import analysis_engine
from ui.translation_engine import TranslationResult


def test_polish_output_prefers_filename_reference(monkeypatch) -> None:
    reference = SimpleNamespace(polish_translation="Tlumaczenie z katalogu")
    monkeypatch.setattr(analysis_engine, "get_reference_by_file_name", lambda file_name: reference)

    translation, source = analysis_engine._resolve_polish_output(
        file_name="carl.wav",
        recognized_text="dowolny tekst",
        device="cpu",
    )

    assert translation == "Tlumaczenie z katalogu"
    assert source == "reference_catalog"


def test_polish_output_falls_back_to_recognized_text_match(monkeypatch) -> None:
    monkeypatch.setattr(analysis_engine, "get_reference_by_file_name", lambda file_name: None)
    monkeypatch.setattr(
        analysis_engine,
        "_resolve_polish_from_recognized_text",
        lambda recognized_text: "Dopasowane po transkrypcji",
    )

    translation, source = analysis_engine._resolve_polish_output(
        file_name="unknown.wav",
        recognized_text="tekst rozpoznany",
        device="cpu",
    )

    assert translation == "Dopasowane po transkrypcji"
    assert source == "recognized_text_match"


def test_polish_output_uses_model_translation_as_last_content_fallback(monkeypatch) -> None:
    monkeypatch.setattr(analysis_engine, "get_reference_by_file_name", lambda file_name: None)
    monkeypatch.setattr(
        analysis_engine,
        "_resolve_polish_from_recognized_text",
        lambda recognized_text: None,
    )
    monkeypatch.setattr(
        analysis_engine,
        "translate_ru_text_to_polish",
        lambda text, device: TranslationResult(text="Tlumaczenie modelowe", status="ok"),
    )

    translation, source = analysis_engine._resolve_polish_output(
        file_name="unknown.wav",
        recognized_text="tekst rozpoznany",
        device="cpu",
    )

    assert translation == "Tlumaczenie modelowe"
    assert source == "model_translation"
