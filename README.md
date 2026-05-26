# ASR Project: Russian -> Polish Tongue Twisters

This repository contains:
- a Streamlit app (`Analysis` + `Model Comparison` modes),
- a benchmark pipeline for ASR model comparison on Russian tongue-twister recordings,
- reference text mapping (Russian originals + Polish reference translations).

## Current status

- `Model Comparison` is connected to real benchmark execution.
- `Analysis` UI flow is implemented, but the ASR/translation payload is still demo/mock data.
- Benchmark model execution is sequential (one model at a time) to reduce memory pressure.

## Quick start

### 1) Environment

```bash
python -m venv .venv
# Windows PowerShell:
# .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

`requirements.txt` includes UI and plotting dependencies.

For real ASR benchmark runs with default models, install backends:

```bash
pip install openai-whisper transformers torch
```

Optional (recommended for stable HF auth in local runs/CI): create `.env` in repo root:

```env
HF_TOKEN=hf_xxx_your_read_token
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
  - display demo transcript/translation payload.
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

## Notes

- Local model caches are stored under `models_cache/` (`whisper` and `huggingface` subfolders).
- First benchmark run can be much slower because models are downloaded.
- Full 4-model run on CPU can take a long time for larger datasets.

## Data link

[Google Drive dataset folder](https://drive.google.com/drive/u/0/folders/1YfVdSFDDbJO21MES5UfFM7B1O_qED0Ko?pli=1&sort=13&direction=a)
