from __future__ import annotations

from types import SimpleNamespace

from ui import analysis_engine
from ui.translation_engine import TranslationResult


class TestAnalysisEngine:
    def test_resolve_polish_output_prefers_filename_reference(self, monkeypatch) -> None:
        reference = SimpleNamespace(polish_translation="Tlumaczenie z katalogu")
        monkeypatch.setattr(analysis_engine, "get_reference_by_file_name", lambda file_name: reference)

        translation, source = analysis_engine._resolve_polish_output(
            file_name="carl.wav",
            recognized_text="dowolny tekst",
            device="cpu",
        )

        assert translation == "Tlumaczenie z katalogu"
        assert source == "reference_catalog"

    def test_resolve_polish_output_falls_back_to_recognized_text_match(self, monkeypatch) -> None:
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

    def test_resolve_polish_output_uses_model_translation_as_last_content_fallback(
        self,
        monkeypatch,
    ) -> None:
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

    def test_resolve_polish_output_reports_unavailable_translation_model(self, monkeypatch) -> None:
        monkeypatch.setattr(analysis_engine, "get_reference_by_file_name", lambda file_name: None)
        monkeypatch.setattr(
            analysis_engine,
            "_resolve_polish_from_recognized_text",
            lambda recognized_text: None,
        )
        monkeypatch.setattr(
            analysis_engine,
            "translate_ru_text_to_polish",
            lambda text, device: TranslationResult(text="", status="backend_unavailable"),
        )

        translation, source = analysis_engine._resolve_polish_output(
            file_name="unknown.wav",
            recognized_text="tekst rozpoznany",
            device="cpu",
        )

        assert translation == ""
        assert source == "translation_model_unavailable"

    def test_resolve_polish_from_recognized_text_uses_similarity(self, monkeypatch) -> None:
        catalog = SimpleNamespace(
            by_id={
                "carl": SimpleNamespace(
                    russian_original="Karl u Klary ukral korally",
                    polish_translation="Karol ukradl korale Klarze.",
                ),
                "sasha": SimpleNamespace(
                    russian_original="Shla Sasha po shosse",
                    polish_translation="Sasza szla szosa.",
                ),
            }
        )
        monkeypatch.setattr(analysis_engine, "load_reference_catalog", lambda: catalog)

        translation = analysis_engine._resolve_polish_from_recognized_text(
            "Karl u Klary ukral koraly"
        )

        assert translation == "Karol ukradl korale Klarze."

    def test_resolve_polish_from_recognized_text_rejects_weak_match(self, monkeypatch) -> None:
        catalog = SimpleNamespace(
            by_id={
                "carl": SimpleNamespace(
                    russian_original="Karl u Klary ukral korally",
                    polish_translation="Karol ukradl korale Klarze.",
                )
            }
        )
        monkeypatch.setattr(analysis_engine, "load_reference_catalog", lambda: catalog)

        assert analysis_engine._resolve_polish_from_recognized_text("totally unrelated") is None
