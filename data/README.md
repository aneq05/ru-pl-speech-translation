# Data folder guide

- `raw/`: original audio files from speakers (not tracked in git).
- `interim/`: augmented or transformed audio (not tracked in git).
- `processed/`: model-ready artifacts and features (not tracked in git).
- `metadata/`: manifests, transcripts, and references used by experiments.

Recommended naming for raw files:
`<speaker_id>_<sample_id>_<condition>.wav`

Example condition labels:
- `clean`
- `noisy_10db`
- `noisy_5db`

