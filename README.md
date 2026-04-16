# RU->PL Speech Translation (ASR Project)

Simple and modular repository for comparing methods in:
`Russian speech -> Polish translation`.

Main architecture:
`ASR (RU) -> Russian text normalization/tokenization -> MT (RU->PL) -> optional TTS (PL)`.

## Project goal
Compare approaches on the same dataset of Russian tongue twisters:
1. Cascade approach (ASR + MT + optional TTS).
2. Integrated speech translation approach (speech-to-text translation).

## Repository structure
```text
.
|-- data/
|   |-- metadata/              # Manifest CSV files
|   |-- raw/                   # Raw audio (not tracked)
|   |-- interim/               # Temporary artifacts (not tracked)
|   `-- processed/             # Processed artifacts (not tracked)
|-- reports/
|   |-- figures/
|   |-- tables/
|   `-- results/               # CSV outputs from benchmarks
|-- src/ru_pl_st/
|   |-- asr/                   # Russian ASR methods
|   |-- text/                  # Russian text cleanup + token extraction
|   |-- translation/           # RU->PL translation methods
|   |-- tts/                   # TTS interfaces
|   |-- pipelines/             # Cascade / integrated pipelines
|   |-- comparison/            # Method comparison runners
|   |-- metrics/               # WER, CER, BLEU, chrF
|   |-- data/                  # Manifest loading and data models
|   |-- utils/
|   `-- cli.py                 # Main CLI entrypoint
`-- opis_projektu_asr.md
```

## Install
```bash
python -m venv .venv
# Windows PowerShell:
# .venv\Scripts\Activate.ps1
pip install -e .
```

## CLI usage
Create manifest template:
```bash
ru-pl-st make-manifest-template --output data/metadata/manifest_template.csv
```

Run cascade comparison:
```bash
ru-pl-st run-cascade --manifest data/metadata/manifest.csv
```

Run integrated comparison:
```bash
ru-pl-st run-integrated --manifest data/metadata/manifest.csv
```

Run full comparison (cascade + integrated):
```bash
ru-pl-st run-full-comparison --manifest data/metadata/manifest.csv
```

## Available built-in method names
ASR:
- `reference_asr`
- `whisper_ru_sim`
- `vosk_ru_sim`

Translation:
- `reference_mt`
- `nllb_ru_pl_sim`
- `marian_ru_pl_sim`

Integrated:
- `integrated_reference`
- `integrated_s2tt_sim`

Simulated methods are placeholders to let you benchmark pipeline logic immediately.
Real model wrappers can be added in `src/ru_pl_st/asr/methods.py` and `src/ru_pl_st/translation/methods.py`.
