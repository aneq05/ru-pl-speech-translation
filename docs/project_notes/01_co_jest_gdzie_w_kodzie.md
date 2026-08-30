# 01. Co jest gdzie w kodzie

## Cel tego dokumentu
Ten plik mapuje repozytorium: gdzie jest UI, gdzie pipeline benchmarku, gdzie logika transkrypcji/tlumaczenia i gdzie zapisywane sa wyniki.

## Wejscia do aplikacji
- `src/app.py`
  - uruchamia aplikacje Streamlit.
  - laduje `.env` przez `env_loader.load_env_file()`.
  - startuje `ui.page.run_app()`.
- `main.py`
  - CLI do benchmarku (`python main.py benchmark ...`).
  - laduje `.env`.
  - uruchamia `benchmarking.runner.run_benchmark(...)`.

## UI (Streamlit)
- `src/ui/page.py`
  - glowny orchestrator widoku.
  - obsluguje 2 tryby: `Analysis` i `Model Comparison`.
  - w `Analysis` wywoluje `ui.analysis_engine.analyze_uploaded_audio(...)`.
  - w `Model Comparison` wywoluje `benchmarking.runner.run_benchmark(...)`.
  - logika wyboru ostatniego kompletnego runu benchmarku.
- `src/ui/components.py`
  - renderowanie komponentow UI:
  - sidebar, panel audio, panel referencji, wykres fali, wyniki ASR/tlumaczenia,
  - tabela leaderboard i podglad zapisanych wykresow PNG.
- `src/ui/styles.py`
  - stylizacja strony (temat czarno-rozowy, typografia, komponenty).
- `src/ui/data.py`
  - helpery UI:
  - kroki flow (`build_flow_steps`),
  - mapowanie audio -> tekst oryginalny/tlumaczenie referencyjne,
  - ladowanie CSV i wykresow z katalogu runu,
  - wykrywanie, czy run benchmarku jest kompletny.
- `src/ui/model_comparison/charts.py`
  - interaktywne wykresy Plotly:
  - grouped bar, scatter quality-vs-speed, boxplot WER, heatmap,
  - ranking modeli z metryka kompozytowa.
- `src/ui/model_comparison/theme.py`
  - wspolny motyw wizualny wykresow Plotly.
- `src/ui/types.py`
  - `SidebarState` (stan kontrolek sidebaru).

## Logika analizy pojedynczego nagrania
- `src/ui/analysis_engine.py`
  - ASR dla uploadowanego pliku (aktualnie model: `whisper:small`).
  - tworzy payload do UI: tekst rozpoznany, segmenty/slowa, confidence, tlumaczenie, zrodlo tlumaczenia.
  - fallbacki tlumaczenia:
    1. dopasowanie po nazwie pliku do katalogu referencji,
    2. dopasowanie po tresci rozpoznanego tekstu,
    3. model RU->PL (`translation_engine`).
- `src/ui/translation_engine.py`
  - wrapper na model tlumaczenia z HF (domyslnie `facebook/nllb-200-distilled-600M`).
  - konfiguruje cache HF w `models_cache/huggingface`.
  - obsluguje statusy: backend unavailable, model load error, inference error.

## Benchmarking modeli ASR
- `src/benchmarking/runner.py`
  - glowny pipeline benchmarku:
  - laduje dataset,
  - uruchamia modele sekwencyjnie (1 model naraz),
  - zbiera wyniki per-sample,
  - zapisuje CSV + wykresy.
- `src/benchmarking/dataset.py`
  - loader danych:
  - skanuje tylko `.wav`,
  - buduje `AudioSample` z referencja i czasem audio.
- `src/benchmarking/model_registry.py`
  - mapowanie `model_id -> adapter modelu`.
  - domyslna lista modeli.
- `src/benchmarking/models/base.py`
  - interfejs `ASRModel`.
- `src/benchmarking/models/whisper_adapter.py`
  - adapter OpenAI Whisper.
- `src/benchmarking/models/hf_transformers_adapter.py`
  - adapter Hugging Face `transformers` pipeline ASR.
- `src/benchmarking/evaluator.py`
  - pomiar inferencji i wyliczanie metryk per-przyklad.
- `src/benchmarking/metrics.py`
  - normalizacja tekstu + metryki (WER, CER, precision/recall/F1 tokenow, exact match).
- `src/benchmarking/reporting.py`
  - agregacja leaderboardu i generowanie wykresow matplotlib.
- `src/benchmarking/types.py`
  - struktury danych: `AudioSample`, `ASRPrediction`, `EvaluationRow`, itd.
- `src/benchmarking/config.py`
  - wczytywanie listy modeli z `configs/models.yaml`.

## Referencje tekstowe i dane
- `src/reference_texts.py`
  - laduje katalog referencji RU/PL i mapowanie `audio_key -> reference_id`.
  - klucz jest normalizowany ze stemu nazwy pliku.
- `data/reference_texts/audio_key_map.json`
  - mapowanie nazw plikow do identyfikatorow tekstow.
- `data/reference_texts/ru/*.txt`
  - teksty oryginalne po rosyjsku.
- `data/reference_texts/pl/*.txt`
  - referencyjne tlumaczenia polskie.
- `data/raw/`
  - nagrania `.wav` + opcjonalny `labels.csv`.

## Konfiguracja modeli i zaleznosci
- `configs/models.yaml`
  - domyslna lista modeli do benchmarku.
- `requirements.txt`
  - zaleznosci aplikacji (w tym `streamlit==1.57.0`).
- `.env` (opcjonalnie)
  - np. `HF_TOKEN`, `HUGGING_FACE_HUB_TOKEN`, `RU_PL_TRANSLATION_MODEL_ID`.

## Gdzie zapisywane sa wyniki
- Run odpalony z UI (`Model Comparison`):
  - `src/ui/model_comparison/results/run_<timestamp>/...`
- Run odpalony z CLI:
  - `reports/results/run_<timestamp>/...`

W kazdym runie:
- `detailed_results.csv`
- `leaderboard.csv`
- `plots/*.png`
