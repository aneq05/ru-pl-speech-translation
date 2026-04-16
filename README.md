# RU->PL Speech Translation (ASR Project)

Repository for an engineering + research course project:
comparison of methods for automatic translation of Russian speech into Polish.

## Project goal
Compare two approaches on the same dataset of Russian tongue twisters:

1. Cascade pipeline: `ASR (RU) -> MT (RU->PL) -> TTS (PL)`.
2. Integrated approach: direct `speech-to-text translation`.

The project analyzes:
- impact of recording quality,
- speaker variability,
- error propagation between stages.

## Repository structure
```text
.
|-- configs/                 # Experiment and pipeline configs
|-- data/
|   |-- metadata/            # Manifests/transcripts/labels
|   |-- raw/                 # Original audio (ignored by git)
|   |-- interim/             # Augmented/intermediate data (ignored by git)
|   `-- processed/           # Feature-ready data (ignored by git)
|-- docs/                    # Project docs
|-- experiments/             # Run outputs (ignored except .gitkeep)
|-- notebooks/               # EDA and analysis notebooks
|-- reports/
|   |-- figures/
|   `-- tables/
|-- scripts/                 # CLI entrypoints for experiments
|-- src/ru_pl_st/            # Python package
|   |-- audio/
|   |-- data/
|   |-- eval/
|   |-- pipelines/
|   `-- utils/
|-- tests/                   # Unit tests
`-- opis_projektu_asr.md     # Polish project description
```

## Quick start
```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows (PowerShell)
# .venv\Scripts\Activate.ps1

pip install -e .[dev]
pytest
```

## Minimal workflow
1. Prepare metadata template:
```bash
python scripts/create_manifest_template.py --output data/metadata/manifest_template.csv
```
2. Fill metadata with your recordings/transcripts/translations.
3. Run baseline/integrated experiments:
```bash
python scripts/run_experiment.py --pipeline cascade --manifest data/metadata/manifest.csv --config configs/cascade.yaml
python scripts/run_experiment.py --pipeline integrated --manifest data/metadata/manifest.csv --config configs/integrated.yaml
```
4. Evaluate predictions:
```bash
python scripts/evaluate_predictions.py --predictions experiments/latest/predictions.csv
```

## Suggested evaluation
- ASR quality: `WER`, `CER`
- Translation quality: `BLEU`, `chrF`
- Runtime: latency / RTF
- Optional listening test for TTS naturalness and intelligibility

## Notes
- Keep raw recordings out of git unless they are explicitly licensed to be shared.
- For course reporting, include both aggregate metrics and hardest failure cases.

