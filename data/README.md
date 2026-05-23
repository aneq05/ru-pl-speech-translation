# Data

In this project, we keep only raw recordings:
- `raw/`

Put recordings directly into `data/raw/`. The benchmark loader expects only `.wav` audio files and reads them recursively (including subfolders like `person1/`).

For benchmark references use either:
- `data/raw/labels.csv` with `file_name,reference_text` columns
- sidecar text files with the same stem, e.g. `sample_01.wav` + `sample_01.txt`
- `data/reference_texts/` mapping (automatic by filename stem)

If you keep nested folders, use relative paths in `file_name`, for example:
- `person1/carl.wav`
- `person2/sasha.wav`

Reference library details:
- `data/reference_texts/ru/*.txt` - Russian originals
- `data/reference_texts/pl/*.txt` - reference Polish translations
- `data/reference_texts/audio_key_map.json` - mapping from filename key to reference id

If the dataset becomes too large or uses inconvenient formats, keep the audio outside GitHub and store only a link/reference here.
