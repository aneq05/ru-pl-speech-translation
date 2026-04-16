# Data folder guide

- `raw/`: original audio files from speakers (not tracked in git).
- `interim/`: temporary artifacts (not tracked in git).
- `processed/`: processed artifacts (not tracked in git).
- `metadata/`: manifests and references used by the pipeline.

Manifest columns (`data/metadata/manifest.csv`):
- `sample_id`
- `speaker_id`
- `audio_path`
- `split`
- `ru_transcript_ref`
- `pl_translation_ref`
- `noise_condition`

Recommended raw filename:
`<speaker_id>_<sample_id>_<condition>.wav`
