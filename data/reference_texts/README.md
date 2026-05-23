# Reference Texts

This folder stores the canonical tongue-twister references used by:
- benchmark evaluation (`src/benchmarking`)
- UI reference panel (`src/ui`)

## Structure

- `ru/<id>.txt` - original Russian text
- `pl/<id>.txt` - reference Polish translation
- `audio_key_map.json` - mapping from normalized audio filename to reference id

## Mapping key format

The key is created from the uploaded filename stem:
- lowercase
- non-alphanumeric chars replaced with `_`

Examples:
- `sasha.wav` -> `sasha`
- `shishkosushylnia.wav.wav` -> `shishkosushylnia_wav`

## Current dataset note

For `person3.wav` the mapping currently points to `mixed_set` (aggregate recording).
If you later split it into single tongue-twister clips, update `audio_key_map.json`.
