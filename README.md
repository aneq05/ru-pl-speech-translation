# ASR Project: Russian -> Polish Tongue Twisters

This repository contains a full benchmark pipeline and a Streamlit UI for a Russian speech recognition + Polish translation project.

## Project goal

Build an end-to-end ASR workflow for Russian tongue twisters:
1. Upload audio.
2. Recognize Russian words and transcript.
3. Translate transcript to Polish.
4. Compare multiple ASR models on your dataset and select the best one.

## Current implementation status

- `Model Comparison` mode is fully connected to the benchmark pipeline.
- `Analysis` mode currently shows the final UI/UX flow with a demo payload (placeholder for backend inference output).
- The app structure is ready to swap demo payload with real backend model output.

## Repository structure

- `data/raw/` - dataset audio + references used for benchmark.
- `reports/results/` - benchmark outputs (CSV + plots), grouped per run.
- `src/ui/` - Streamlit UI modules.
- `src/benchmarking/` - benchmark pipeline (dataset, models, metrics, reporting).
- `configs/models.yaml` - default model list for benchmark.

## UI overview (final product behavior)

Run the app:

```bash
streamlit run src/app.py
```

The UI has 2 modes:

### 1) Analysis

Purpose: single recording analysis.

Final intended flow:
1. User uploads one recording.
2. App loads matching tongue twister reference (original + Polish reference translation) based on filename.
3. App shows audio player + waveform.
4. App returns:
   - recognized Russian words,
   - ASR transcript,
   - Polish translation,
   - processing flow status.

Current status:
- UI is final.
- Inference call is still mocked with demo payload.

### 2) Model Comparison

Purpose: evaluate and compare multiple ASR models on your dataset.

How it works:
1. Click `Run benchmark on dataset` in sidebar.
2. Benchmark runs on `data/raw/` using models from `configs/models.yaml` (or defaults).
3. New run is saved in `reports/results/run_<timestamp>/`.
4. UI loads the latest run and displays:
   - leaderboard table,
   - benchmark charts.

## Benchmark CLI

You can also run benchmark outside UI.

### Default run

```bash
python main.py benchmark --data-dir data/raw
```

### Override model list

```bash
python main.py benchmark --data-dir data/raw --models whisper:base faster-whisper:base
```

### Use custom models config

```bash
python main.py benchmark --data-dir data/raw --models-config configs/models.yaml
```

### Smoke test without heavy ASR dependencies

```bash
python main.py benchmark --data-dir data/raw --models dummy:empty dummy:sidecar
```

## Benchmark model config

`configs/models.yaml`

```yaml
models:
  - whisper:small
  - faster-whisper:small
  - hf:jonatasgrosman/wav2vec2-large-xlsr-53-russian
  - hf:jonatasgrosman/wav2vec2-xls-r-1b-russian
```

## Dataset format

Put audio in `data/raw/` (`.wav` recommended for benchmark) and provide references in one of these formats:

### Option A: `labels.csv`

File: `data/raw/labels.csv`

```csv
file_name,reference_text
twister_01.wav,Shla Sasha po shosse i sosala sushku.
```

For nested layout like `data/raw/person1/carl.wav`, use relative path in `file_name`, for example:

```csv
person1/carl.wav,Shla Sasha po shosse i sosala sushku.
```

### Option B: sidecar text file

- `twister_01.wav`
- `twister_01.txt` (reference sentence)

## Benchmark outputs

Each run creates:

`reports/results/run_<timestamp>/`

- `detailed_results.csv` - per sample and model.
- `leaderboard.csv` - aggregated metrics per model.
- `plots/`
  - `01_overview_metrics.png`
  - `02_quality_vs_speed.png`
  - `03_wer_boxplot.png`
  - `04_model_heatmap.png`

## Installation

```bash
python -m venv .venv
# Windows PowerShell:
# .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Optional dependencies for full benchmark:
- `openai-whisper`
- `faster-whisper`
- `transformers`
- `torch`

## Final integration note

To complete production `Analysis` mode, replace demo payload usage in `src/ui/page.py` (`build_demo_payload()`) with a real inference + translation backend call that returns:
- recognized word segments,
- transcript,
- translation,
- confidence metadata.

## Data link

https://drive.google.com/drive/u/0/folders/1YfVdSFDDbJO21MES5UfFM7B1O_qED0Ko?pli=1&sort=13&direction=a
