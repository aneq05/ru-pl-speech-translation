from __future__ import annotations

from pathlib import Path

import pytest

from reference_texts import get_reference_by_file_name, load_reference_catalog, normalize_audio_key


def _write_catalog(base_dir: Path) -> None:
    (base_dir / "ru").mkdir(parents=True)
    (base_dir / "pl").mkdir()
    (base_dir / "audio_key_map.json").write_text(
        """
        {
          "audio_key_to_reference_id": {
            "carl": "carl",
            "sasha_fast": "sasha"
          },
          "titles": {
            "carl": "Karl and Klara",
            "sasha": "Sasha"
          }
        }
        """,
        encoding="utf-8",
    )
    (base_dir / "ru" / "carl.txt").write_text("Karl RU", encoding="utf-8")
    (base_dir / "pl" / "carl.txt").write_text("Karl PL", encoding="utf-8")
    (base_dir / "ru" / "sasha.txt").write_text("Sasha RU", encoding="utf-8")
    (base_dir / "pl" / "sasha.txt").write_text("Sasha PL", encoding="utf-8")


class TestReferenceTexts:
    def test_normalize_audio_key_uses_stem_and_stable_separators(self) -> None:
        assert normalize_audio_key("person1/Sasha-fast!!.wav") == "sasha_fast"

    def test_get_reference_by_file_name_uses_audio_key_map(self, tmp_path: Path) -> None:
        _write_catalog(tmp_path)
        load_reference_catalog.cache_clear()

        entry = get_reference_by_file_name("recordings/sasha-fast.wav", reference_dir=tmp_path)

        assert entry is not None
        assert entry.reference_id == "sasha"
        assert entry.polish_translation == "Sasha PL"

    def test_load_reference_catalog_fails_when_translation_pair_is_incomplete(
        self,
        tmp_path: Path,
    ) -> None:
        (tmp_path / "ru").mkdir()
        (tmp_path / "pl").mkdir()
        (tmp_path / "audio_key_map.json").write_text(
            '{"audio_key_to_reference_id": {"carl": "carl"}}',
            encoding="utf-8",
        )
        (tmp_path / "ru" / "carl.txt").write_text("Karl RU", encoding="utf-8")
        load_reference_catalog.cache_clear()

        with pytest.raises(FileNotFoundError, match="Missing Polish reference file"):
            load_reference_catalog(tmp_path)
