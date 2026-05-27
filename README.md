# ASR Project: Russian -> Polish Tongue Twisters

This repository contains:
- a Streamlit app (`Analysis` + `Model Comparison` modes),
- a benchmark pipeline for ASR model comparison on Russian tongue-twister recordings,
- reference text mapping (Russian originals + Polish reference translations).

## Current status

- `Model Comparison` is connected to real benchmark execution.
- `Analysis` runs real ASR with `whisper:base` on uploaded audio.
- `Analysis` Polish output source:
  - reference catalog translation (when filename matches `data/reference_texts/audio_key_map.json`),
  - reference catalog translation matched by recognized Russian text similarity,
  - RU->PL translation model fallback for new/unknown files.
- Benchmark model execution is sequential (one model at a time) to reduce memory pressure.

### Analysis UI (what you see after upload)

- Waveform preview and audio player for the uploaded `.wav`.
- Reference panel showing the Russian original and Polish reference (if a mapping exists).
- Recognized Russian words displayed as a word stream with per-word confidence bars.
- Full ASR transcript in a disabled text area.
- Polish translation block showing the translation text and a caption with the translation source.
- Word-by-word token preview of the Polish output (when available).

### Translation fallback logic

When a recording is analyzed the app resolves the Polish output in this order:
1. Exact file-name match to the reference catalog (`reference_catalog`).
2. Best match from reference texts by similarity of the recognized Russian text (`recognized_text_match`).
3. RU->PL translation model (`model_translation`).
4. If model loading or inference fails the app reports `translation_model_unavailable`.
5. If ASR recognized some text but no translation is found, the app reports `missing_translation`.

The similarity matching uses a combination of character SequenceMatcher and token-overlap (see `src/ui/analysis_engine.py`). Transliteration to ASCII is attempted to increase matching robustness.

## Quick start

### 1) Environment

```bash
python -m venv .venv
# Windows PowerShell:
# .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

`requirements.txt` includes UI and plotting dependencies. By default it installs the lightweight UI stack:

- `streamlit`, `soundfile`, `numpy`, `plotly`, `librosa`, `unidecode` (UI/visualization + helpers)

For full ASR + translation functionality (Analysis mode + Whisper benchmark models), install optional backends:

```bash
pip install openai-whisper transformers torch sentencepiece
```

Note: `sentencepiece` is required by some Hugging Face translation tokenizers.

Optional (recommended for stable HF auth in local runs/CI): create `.env` in repo root:

```env
HF_TOKEN=hf_xxx_your_read_token
# Optional override for Analysis translation fallback model:
# RU_PL_TRANSLATION_MODEL_ID=facebook/nllb-200-distilled-600M
```

`HF_TOKEN` is loaded automatically by both:
- CLI (`python main.py ...`)
- Streamlit app (`streamlit run src/app.py`)

### 2) Run Streamlit app

```bash
streamlit run src/app.py
```

Modes:
- `Analysis`
  - upload `.wav`,
  - show waveform,
  - show matched reference text by filename (if found),
  - run real transcription with `whisper:base`,
  - show Polish output from reference translation, recognized-text match, or RU->PL model translation fallback.
- `Model Comparison`
  - click `Run benchmark on dataset`,
  - run benchmark on `data/raw`,
  - display leaderboard, interactive Plotly charts, and saved PNG charts.

### 3) Run benchmark from CLI

Default:

```bash
python main.py benchmark --data-dir data/raw
```

Single-model smoke test:

```bash
python main.py benchmark --data-dir data/raw --models whisper:tiny
```

HF model smoke test:

```bash
python main.py benchmark --data-dir data/raw --models hf:jonatasgrosman/wav2vec2-large-xlsr-53-russian
```

Explicit 4-model comparison:

```bash
python main.py benchmark --data-dir data/raw --models whisper:tiny whisper:base whisper:small hf:jonatasgrosman/wav2vec2-large-xlsr-53-russian
```

Custom output directory:

```bash
python main.py benchmark --data-dir data/raw --reports-dir reports/results
```

## Default models

From `configs/models.yaml` / built-in fallback:

```yaml
models:
  - whisper:tiny
  - whisper:base
  - whisper:small
  - hf:jonatasgrosman/wav2vec2-large-xlsr-53-russian
```

Model id formats:
- `whisper:<size>`
- `hf:<huggingface_model_id>`

## Dataset contract (current loader)

- Audio format: `.wav` only (recursive scan under `data/raw`).
- If a file has no reference text, it is skipped.
- At least one valid `(audio + reference)` sample is required.

If you want to analyze a single uploaded file that is not present in `data/raw`, the `Analysis` UI still runs ASR on the uploaded file and then attempts translation via the fallback logic (reference match -> text-match -> RU->PL model). If the translation model is unavailable, the UI will show an explanatory status message.

Reference sources (priority):
1. `labels.csv` / `references.csv` / `metadata.csv` in dataset root (`data/raw`) with file and text columns.
2. Sidecar `.txt` file next to `.wav`.
3. `data/reference_texts` catalog mapping by normalized filename key.

Example `labels.csv` row:

```csv
file_name,reference_text
person1/carl.wav,Shla Sasha po shosse i sosala sushku.
```

## Reference text catalog

Folder: `data/reference_texts/`

- `ru/<id>.txt` - Russian original
- `pl/<id>.txt` - Polish reference translation
- `audio_key_map.json` - filename-key to reference-id mapping

Used by:
- benchmark dataset loader (fallback reference source),
- Streamlit reference panel in `Analysis` mode.

You can add new canonical references by placing paired files in `data/reference_texts/ru` and `data/reference_texts/pl` and updating `audio_key_map.json` to map filenames (or keys) to reference IDs.

## Output directories

CLI benchmark output (default):
- `reports/results/run_<timestamp>/`

Streamlit `Model Comparison` output:
- `src/ui/model_comparison/results/run_<timestamp>/`

Each run contains:
- `detailed_results.csv`
- `leaderboard.csv`
- `plots/01_overview_metrics.png`
- `plots/02_quality_vs_speed.png`
- `plots/03_wer_boxplot.png`
- `plots/04_model_heatmap.png`

## Repository layout

- `src/app.py` - Streamlit entrypoint
- `src/ui/` - UI components, styles, comparison charts
- `src/benchmarking/` - dataset loading, model adapters, metrics, reporting, runner
- `src/reference_texts.py` - reference catalog loader and filename normalization
- `configs/models.yaml` - default benchmark model list
- `data/raw/` - input audio + optional CSV labels
- `data/reference_texts/` - canonical RU/PL reference texts

Key implementation files to inspect:

- `src/ui/analysis_engine.py` - orchestrates ASR, temporary audio handling, reference lookup, similarity matching and translation fallback.
- `src/ui/translation_engine.py` - RU->PL translation adapter using Hugging Face seq2seq models (configurable via `RU_PL_TRANSLATION_MODEL_ID`).
- `src/ui/components.py` and `src/ui/page.py` - Streamlit rendering of the Analysis and Model Comparison UI and controls.

## Notes

- Local model caches are stored under `models_cache/` (`whisper` and `huggingface` subfolders).
- First benchmark run can be much slower because models are downloaded.
- First `Analysis` translation fallback on unknown files can also be slow (RU->PL model download).
- Full 4-model run on CPU can take a long time for larger datasets.

## Troubleshooting & development tips

- If the app shows `Translation model unavailable`, ensure `transformers`, `torch` and `sentencepiece` are installed and optionally set `HF_TOKEN` for private model access.
- Local HF cache and downloaded models are stored under `models_cache/`. Pre-downloading models into this folder can speed up runs in air-gapped environments.
- Streamlit `Analysis` currently uses `DEFAULT_DEVICE = "cpu"` from `src/ui/analysis_engine.py` (it is not read from env yet). To change it, update that constant in code.
- Logs and intermediate benchmark outputs are under `reports/` and `src/ui/model_comparison/results/`.

## Data link

[Google Drive dataset folder](https://drive.google.com/drive/u/0/folders/1YfVdSFDDbJO21MES5UfFM7B1O_qED0Ko?pli=1&sort=13&direction=a)
