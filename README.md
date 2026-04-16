# ASR Project: Russian -> Polish

A simple course-project skeleton for comparing methods of Russian speech translation into Polish.

## Repository goal
- keep all code in `src/`,
- keep a clear stage-by-stage architecture:
1. ASR (recognize Russian from audio),
2. Russian text processing (normalization + word extraction),
3. RU -> PL translation,
4. optional TTS,
5. method comparison and metrics.

This repository is intentionally a skeleton, not a full model implementation.

## Structure
```text
.
|-- data/
|   `-- raw/                   # raw recordings
|-- reports/
|   `-- results/               # comparison outputs (csv, notes)
|-- src/ru_pl_st/
|   |-- asr.py                 # ASR interfaces + adapter skeletons
|   |-- text_processing.py     # RU normalization + tokenization (TODO)
|   |-- translation.py         # translation interfaces + skeletons
|   |-- tts.py                 # TTS interface (optional stage)
|   |-- pipeline.py            # cascade / integrated pipeline skeleton
|   |-- evaluation.py          # metric and comparison skeleton
|   |-- io.py                  # simple input/output helpers
|   |-- types.py               # data models
|   `-- cli.py                 # simple project CLI
|-- opis_projektu_asr.md
`-- pyproject.toml
```

## Installation
```bash
python -m venv .venv
# Windows PowerShell:
# .venv\Scripts\Activate.ps1
pip install -e .
```

## Run (skeleton)
```bash
ru-pl-st run-cascade --raw-dir data/raw
ru-pl-st run-integrated --raw-dir data/raw
ru-pl-st compare --results-file reports/results/example.csv
```

These commands do not run real models yet; they only demonstrate the project flow skeleton.

## Suggested next steps
1. Add adapters for real ASR models (for example Whisper/Vosk).
2. Implement concrete Russian text processing.
3. Add translation adapters (for example Marian/NLLB/other).
4. Implement actual metrics and a final comparison report.
