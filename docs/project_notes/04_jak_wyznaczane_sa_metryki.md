# 04. Jak sa wyznaczane metryki do oceny modeli

## 1) Gdzie liczone sa metryki
- Metryki tekstowe: `src/benchmarking/metrics.py`.
- Metryki czas/pamiec: `src/benchmarking/evaluator.py`.
- Agregacja per-model: `src/benchmarking/reporting.py`.
- Dodatkowy ranking kompozytowy (UI): `src/ui/model_comparison/charts.py`.

## 2) Normalizacja tekstu przed liczeniem
`normalize_text(text)` wykonuje:
1. `strip()`
2. `lower()`
3. zamiana wybranych znakow (aktualnie jest specjalna zamiana dla znieksztalconych znakow),
4. usuniecie interpunkcji regexem,
5. kompresje wielokrotnych spacji.

Skutek:
- metryki sa liczone na "oczyszczonym" tekscie.
- interpunkcja i wielkosc liter nie wplywaja na wynik.

## 3) Metryki per-sample (EvaluationRow)

### 3.1 WER
- Word Error Rate
- liczona jako:
  - `levenshtein_distance(tokeny_ref, tokeny_hyp) / len(tokeny_ref)`
- implementacja:
  - `_error_rate(...)` + `_levenshtein_distance(...)`.

Interpretacja:
- `0.0` = idealnie,
- im wyzej, tym gorzej.

### 3.2 CER
- Character Error Rate
- to samo co WER, ale na poziomie znakow (bez spacji):
  - `levenshtein(chars_ref, chars_hyp) / len(chars_ref)`.

Interpretacja:
- `0.0` = idealnie,
- im wyzej, tym gorzej.

### 3.3 Token precision / recall / F1
Liczone na wielozbiorach tokenow (`Counter`):
- `true_positive = sum((ref_counter & hyp_counter).values())`
- `precision = TP / liczba_tokenow_hyp`
- `recall = TP / liczba_tokenow_ref`
- `F1 = 2PR / (P+R)` (jesli mianownik > 0).

Interpretacja:
- blizej `1.0` = lepiej.

### 3.4 Exact match
- `1.0` gdy caly tekst po normalizacji jest identyczny i niepusty,
- inaczej `0.0`.

### 3.5 Latency
- mierzona per-sample:
  - `latency_sec = time.perf_counter() stop-start`.
- obejmuje czas inferencji modelu dla danego pliku.

### 3.6 RTF
- Real-Time Factor:
  - `rtf = latency_sec / duration_sec`.

Interpretacja:
- `< 1.0` zwykle oznacza szybciej niz real-time,
- im nizsze, tym lepiej.

### 3.7 Peak memory MB
- w evaluatorze przez `tracemalloc`:
  - `peak_memory_mb = peak_bytes / (1024*1024)`.

Uwaga:
- to jest pomiar pamieci sledzonej przez `tracemalloc` (Python-level), nie pelny RSS procesu.
- do porownan wzglednych jest uzyteczne, ale nie jest "absolutna" pamiecia calkowita procesu.

### 3.8 Mean confidence
- jesli model zwraca confidence globalne -> bierze je.
- inaczej liczy srednia confidence po segmentach (jesli sa).
- gdy brak confidence -> `None`.

## 4) Agregacja do leaderboardu (per model)
`build_leaderboard(rows)` liczy srednie po wszystkich samplach danego modelu:
- `wer_mean`
- `cer_mean`
- `token_precision_mean`
- `token_recall_mean`
- `token_f1_mean`
- `exact_match_mean`
- `latency_sec_mean`
- `latency_sec_p95`
- `rtf_mean`
- `peak_memory_mb_mean`
- `confidence_mean`
- `samples_count`

Sortowanie leaderboardu:
- najpierw rosnaco `wer_mean`,
- potem rosnaco `rtf_mean`.

## 5) Metryka kompozytowa rankingu (UI)
W `ui/model_comparison/charts.py` jest dodatkowy ranking "best overall model".
To NIE jest metryka zapisana w CSV benchmarku, tylko liczona dynamicznie w UI.

Kroki:
1. Normalizacja min-max kazdej metryki do [0,1].
2. Dla metryk "mniej = lepiej" wynik jest odwracany (`1 - normalized`).
3. Skladanie wazone:
   - WER: 0.34
   - CER: 0.16
   - Token F1: 0.18
   - Exact match: 0.12
   - Latency: 0.12
   - RTF: 0.04
   - Peak RAM: 0.04

Wynik:
- `composite_score` w [0,1], potem w UI pokazywany * 100.

## 6) Co to oznacza praktycznie
- Najwazniejsza metryka jakosci ASR: `WER` (najwieksza waga takze w rankingu UI).
- `CER` pomaga zobaczyc drobne bledy znakowe/transliteracyjne.
- `Token F1` i `Exact Match` pokazuja "pokrycie tresci" i pelna zgodnosc.
- `Latency/RTF/Memory` sa krytyczne dla zastosowan live i ograniczen sprzetowych.
