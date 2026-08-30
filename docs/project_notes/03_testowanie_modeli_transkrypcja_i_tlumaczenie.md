# 03. Jak sa testowane modele na naszych danych + jak jest robiona transkrypcja i translacja

## 1) Jakie modele sa porownywane
Domyslna lista (benchmark):
- `whisper:tiny`
- `whisper:base`
- `whisper:small`
- `hf:jonatasgrosman/wav2vec2-large-xlsr-53-russian`

Zrodlo:
- `configs/models.yaml`
- fallback: `benchmarking.model_registry.DEFAULT_MODEL_IDS`

## 2) Co jest "przykladem testowym" w benchmarku
Jeden przyklad to:
- jeden plik `.wav`,
- jedna referencyjna transkrypcja rosyjska (`reference_text`),
- policzony czas trwania audio (`duration_sec`).

Reprezentacja:
- `benchmarking.types.AudioSample`.

## 3) Jak benchmark laduje dane
`benchmarking.dataset.load_dataset(raw_dir)`:
1. Rekurencyjnie szuka tylko `.wav`.
2. Dla kazdego pliku probuje znalezc referencje:
   1. mapa z CSV (`labels.csv`/`references.csv`/`metadata.csv`),
   2. sidecar `.txt`,
   3. katalog `data/reference_texts`.
3. Jesli referencja nie istnieje, plik jest pomijany.
4. Jesli nie zostanie ani jeden poprawny sample, benchmark konczy sie bledem.

## 4) Jak dziala testowanie modeli (benchmark)
`benchmarking.runner.run_benchmark(...)`:
1. Tworzy `run_id` i katalog wyniku.
2. Laduje sample z datasetu.
3. Dla kazdego modelu z listy:
   - tworzy adapter modelu (`create_model`),
   - uruchamia ewaluacje na wszystkich samplach (`evaluate_models`),
   - dopina wyniki.
4. Po modelu zwalnia zasoby:
   - usuwa referencje `_model` / `_pipeline`,
   - `gc.collect()`,
   - czysci cache CUDA/MPS (jesli dostepne).
5. Na koncu zapisuje CSV i wykresy.

Wazne:
- benchmark idzie sekwencyjnie (1 model naraz), nie rownolegle.
- to zmniejsza pik zuzycia RAM/VRAM.

## 5) Jak jest robiona transkrypcja modeli

### 5.1 Whisper (`benchmarking/models/whisper_adapter.py`)
1. Ladowanie modelu `whisper.load_model(...)`.
2. Audio:
   - `soundfile.read(...)`,
   - mix do mono (srednia kanalow),
   - resampling do 16 kHz (`librosa`) jesli potrzeba.
3. `model.transcribe(audio_array, task='transcribe', language='ru', ...)`.
4. Segmenty + confidence:
   - confidence wyprowadzany z `avg_logprob` (`exp(logprob)`, obciete do [0,1]).
5. Wynik -> `ASRPrediction`.

### 5.2 Hugging Face ASR (`benchmarking/models/hf_transformers_adapter.py`)
1. Tworzenie pipeline `automatic-speech-recognition`.
2. Audio:
   - `librosa.load(..., sr=16000, mono=True)`.
3. Inferencja z best-effort timestamps:
   - probuje kolejno `word`, `char`, `True`, a potem bez timestampow.
4. Zwraca:
   - tekst,
   - segmenty (jesli pipeline zwroci `chunks`).

## 6) Jak jest robiona transkrypcja w trybie `Analysis`
`ui.analysis_engine.analyze_uploaded_audio(...)`:
1. Bierze uploadowany plik i zapisuje do temp.
2. Uzywa modelu `ANALYSIS_MODEL_ID = whisper:small`.
3. Dla Whisper przekazuje m.in.:
   - `language='ru'`,
   - `condition_on_previous_text=False`,
   - `temperature=0.0`.
4. Buduje payload do UI:
   - `recognized_text`,
   - segmenty/slowa z confidence,
   - ogolne confidence.

## 7) Jak jest robiona translacja w trybie `Analysis`
Kolejnosc fallbackow (`_resolve_polish_output`):
1. `reference_catalog`
   - jesli plik ma mapowanie w `data/reference_texts`, bierze gotowe tlumaczenie PL.
2. `recognized_text_match`
   - dopasowuje rozpoznany rosyjski tekst do referencyjnych rosyjskich tekstow
     (mix podobienstwa znakowego + overlap tokenow).
3. `model_translation`
   - odpala model RU->PL z `ui.translation_engine`.
   - domyslny model: `facebook/nllb-200-distilled-600M`.
4. Jesli model niedostepny lub blad:
   - status `translation_model_unavailable`.
5. Jesli nic nie wyszlo:
   - status `missing_translation` albo `none`.

## 8) Czego benchmark NIE robi obecnie
- Nie ocenia jakosci tlumaczenia RU->PL.
- Nie liczy metryk translacji (BLEU/COMET itp.).
- Benchmark porownuje tylko jakosc ASR (rozpoznania rosyjskiego tekstu) i metryki wydajnosci.

## 9) Co warto sprawdzic przed odpaleniem benchmarku
- czy wszystkie pliki sa `.wav`,
- czy jest referencja dla kazdego pliku (CSV/sidecar/katalog referencji),
- czy zainstalowane sa backendy modeli:
  - `openai-whisper`,
  - `transformers`,
  - `torch`,
  - `librosa`,
- czy jest miejsce na cache modeli (`models_cache/...`).
