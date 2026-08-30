# 02. Workflow krok po kroku

## A. Start aplikacji (Streamlit)
1. Uruchamiasz `streamlit run src/app.py`.
2. `src/app.py` laduje `.env` (`env_loader.load_env_file()`).
3. `ui.page.run_app()`:
   - ustawia konfiguracje strony,
   - wstrzykuje style CSS,
   - inicjalizuje `st.session_state`,
   - renderuje sidebar i wybiera tryb.

## B. Tryb `Analysis` (pojedynczy plik)
1. Uzytkownik wrzuca plik `.wav` (uploader ograniczony do `wav`).
2. Klik `Run analysis`.
3. `ui.page._handle_actions()` wywoluje `ui.analysis_engine.analyze_uploaded_audio(...)`.
4. `analysis_engine`:
   - zapisuje upload do pliku tymczasowego,
   - laduje model ASR (`whisper:small`, cache przez `@lru_cache`),
   - uruchamia transkrypcje,
   - wyciaga tekst, segmenty, confidence.
5. Wyznaczanie polskiego outputu (`_resolve_polish_output`):
   1. po nazwie pliku przez katalog referencji,
   2. po dopasowaniu tresci rozpoznanego rosyjskiego tekstu,
   3. przez model RU->PL (`translation_engine`) jako fallback.
6. Zwracany jest payload do UI:
   - `recognized_text`,
   - `segments` (slowa + confidence),
   - `translation`,
   - `translation_source`,
   - metadane pliku/modelu.
7. UI pokazuje:
   - status,
   - Processing Flow,
   - Original Tongue Twister (RU + PL referencyjne),
   - audio + waveform,
   - rozpoznane slowa,
   - transcript i Polish output.

## C. Tryb `Model Comparison` (benchmark)
1. Uzytkownik przechodzi do zakladki `Model Comparison`.
2. Klik `Run benchmark on dataset`.
3. `ui.page._handle_actions()` wywoluje:
   - `run_benchmark(report_root_dir=src/ui/model_comparison/results)`.
4. `benchmarking.runner.run_benchmark(...)`:
   - ustala liste modeli (CLI/config/default),
   - tworzy katalog `run_<timestamp>`,
   - laduje dataset przez `benchmarking.dataset.load_dataset(...)`.
5. Dla kazdego modelu (sekwencyjnie):
   - `create_model(model_id, ...)`,
   - `evaluate_models(models=[model], samples=...)`,
   - dopina wyniki do `rows`,
   - czysci zasoby modelu (GC + cache torch).
6. Po przejsciu wszystkich modeli:
   - budowa leaderboardu (`build_leaderboard`),
   - zapis:
     - `detailed_results.csv`,
     - `leaderboard.csv`,
     - `plots/*.png` (matplotlib).
7. UI laduje ostatni kompletny run i wyswietla:
   - leaderboard (tabela),
   - interaktywne wykresy Plotly,
   - zapisane wykresy PNG.

## D. Co znaczy "kompletny run" w UI
Run jest uznany za kompletny, jesli ma:
- `leaderboard.csv`,
- `detailed_results.csv`,
- min. 1 wykres w `plots/`.

Jesli najnowszy run jest niekompletny, UI pokazuje warning i fallbackuje do ostatniego kompletnego runu.

## E. Workflow benchmarku przez CLI
1. Uruchamiasz:
   - `python main.py benchmark --data-dir data/raw`
2. `main.py` laduje `.env` i argumenty.
3. Wywoluje `run_benchmark(...)`.
4. Wyniki trafiaja domyslnie do:
   - `reports/results/run_<timestamp>/...`

## F. Przeplyw danych referencyjnych
1. Dla benchmarku referencja tekstowa jest szukana w kolejnosci:
   1. CSV (`labels.csv`/`references.csv`/`metadata.csv`),
   2. sidecar `.txt`,
   3. katalog `data/reference_texts`.
2. Dla panelu "Original Tongue Twister" w UI:
   - mapowanie jest po nazwie pliku przez `reference_texts.get_reference_by_file_name(...)`.

## G. Cache i zasoby
- Whisper cache: `models_cache/whisper`.
- Hugging Face cache (ASR + translation): `models_cache/huggingface`.
- Modele sa ladowane i trzymane w pamieci tylko tyle, ile potrzeba (benchmark sekwencyjny).
