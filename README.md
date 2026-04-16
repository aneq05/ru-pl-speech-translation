# ASR Project: Rosyjski -> Polski

Prosty szkielet projektu zaliczeniowego do porownania metod tlumaczenia mowy rosyjskiej na jezyk polski.

## Co jest celem tego repo
- trzymanie kodu w `src/`,
- jasny podzial etapow:
1. ASR (rozpoznanie rosyjskiego z audio),
2. obrobka tekstu rosyjskiego (normalizacja + wydzielenie slow),
3. tlumaczenie RU -> PL,
4. opcjonalnie TTS,
5. porownanie metod i metryki.

To repo jest celowo szkieletem, a nie gotowa implementacja modeli.

## Struktura
```text
.
|-- data/
|   `-- raw/                   # surowe nagrania
|-- reports/
|   `-- results/               # wyniki porownan (csv, notatki)
|-- src/ru_pl_st/
|   |-- asr.py                 # interfejs ASR + szkielety adapterow
|   |-- text_processing.py     # normalizacja RU + tokenizacja (TODO)
|   |-- translation.py         # interfejs tlumaczenia + szkielety
|   |-- tts.py                 # interfejs TTS (opcjonalny etap)
|   |-- pipeline.py            # szkielet pipeline kaskadowego / zintegrowanego
|   |-- evaluation.py          # szkielety metryk i porownania
|   |-- io.py                  # proste operacje wejscia/wyjscia
|   |-- types.py               # modele danych
|   `-- cli.py                 # proste CLI projektu
|-- opis_projektu_asr.md
`-- pyproject.toml
```

## Instalacja
```bash
python -m venv .venv
# Windows PowerShell:
# .venv\Scripts\Activate.ps1
pip install -e .
```

## Uruchamianie (szkielet)
```bash
ru-pl-st run-cascade --raw-dir data/raw
ru-pl-st run-integrated --raw-dir data/raw
ru-pl-st compare --results-file reports/results/example.csv
```

Polecenia nie uruchamiaja jeszcze prawdziwych modeli - pokazuja tylko szkielet przeplywu.

## Co dopisac dalej
1. Adaptery do realnych modeli ASR (np. Whisper/Vosk).
2. Konkretna implementacja obrobki tekstu rosyjskiego.
3. Adaptery tlumaczenia (np. Marian/NLLB/inne).
4. Faktyczne metryki i raport porownawczy.
