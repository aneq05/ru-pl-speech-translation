# 05. Jak interpretowac otrzymane wyniki i wykresy

## 1) Od czego zaczac analize wynikow
Kolejnosc rekomendowana:
1. `leaderboard.csv` (wartosci zagregowane).
2. Wykres `WER distribution` (stabilnosc po samplach).
3. `Quality vs speed` (trade-off jakosc/szybkosc).
4. `Heatmap` i ranking kompozytowy (szybkie porownanie przekrojowe).

## 2) Jak czytac leaderboard
Najwazniejsze pola:
- `wer_mean`:
  - glowny indikator jakosci ASR,
  - im mniej, tym lepiej.
- `cer_mean`:
  - przydaje sie gdy modele maja podobny WER, ale roznia sie drobnymi bledami.
- `token_f1_mean` i `exact_match_mean`:
  - im wiecej, tym lepiej.
- `latency_sec_mean` i `rtf_mean`:
  - wydajnosc.
- `peak_memory_mb_mean`:
  - koszt pamieci.
- `samples_count`:
  - czy wszystkie modele porownujesz na tej samej liczbie przykladow.

## 3) Jak czytac interaktywne wykresy Plotly (UI)

### 3.1 Quality metrics overview (bar chart)
Pokazuje razem:
- WER,
- CER,
- Token F1,
- Exact match.

Wnioski:
- slupki WER/CER najnizej,
- slupki F1/Exact najwiecej.
- To szybki "quality snapshot".

### 3.2 Quality vs speed trade-off (scatter/bubble)
Osie:
- X: srednia latencja,
- Y: sredni WER,
- rozmiar punktu: srednia pamiec.

Idealny model:
- lewy dolny rog (niska latencja, niski WER),
- mniejszy punkt (mniejsza pamiec), jesli zalezy Ci na footprint.

### 3.3 WER distribution (boxplot)
Pokazuje rozklad WER po wszystkich samplach.

Na co patrzec:
- mediana i srednia w boxie,
- szerokosc boxa (stabilnosc),
- outliery (pliki, na ktorych model mocno sie myli).

Wniosek:
- model z nizszym srednim WER, ale bardzo szerokim rozkladem moze byc mniej przewidywalny.

### 3.4 Normalized score heatmap
Wszystkie metryki przeskalowane do [0,1] "im wyzej tym lepiej".

Na co uwazac:
- to skala wzgledna w danym runie,
- nie porownuj kolorow miedzy roznymi runami bez spojrzenia w surowe liczby.

## 4) Jak czytac zapisane wykresy PNG (matplotlib)
PNG i wykresy interaktywne opieraja sie na tych samych CSV, ale:
- UI Plotly ma ranking kompozytowy i interaktywne tooltipy,
- PNG to statyczny artefakt do raportu/slajdow.

Do prezentacji najlepiej:
- pokazac najpierw interaktywny chart (intuicja),
- potem PNG jako "zamrozony" dowod dla dokumentacji.

## 5) Jak wybrac finalny model
To zalezy od celu:

### 5.1 Priorytet: jakosc transkrypcji
- Minimalizuj `wer_mean`.
- Dogladnij `cer_mean`, `token_f1_mean`, `exact_match_mean`.
- Zweryfikuj stabilnosc na boxplocie.

### 5.2 Priorytet: live/real-time
- Niskie `latency_sec_mean` i `rtf_mean`.
- Pilnuj, by WER nie byl zbyt wysoki.

### 5.3 Priorytet: ograniczona pamiec
- Niskie `peak_memory_mb_mean`.
- Sprawdz czy zysk pamieci nie niszczy jakosci.

## 6) Czerwone flagi i jak je rozumiec
- Bardzo dobre srednie, ale malo `samples_count`:
  - mozliwe, ze model padal na czesci danych.
- Duza roznica miedzy `latency_sec_mean` a `latency_sec_p95`:
  - niestabilny czas odpowiedzi (spikes).
- Dobry WER, slaby exact match:
  - model rozpoznaje sens, ale gubi dokladna forme wypowiedzi.
- Wysoki WER tylko na niektorych plikach:
  - sprawdz te konkretne sample (akcent, tempo, szum, zle referencje).

## 7) Jak opowiedziec wyniki na prezentacji
Prosta narracja:
1. "Porownalismy 4 publiczne modele ASR na naszym zbiorze RU tongue twisters."
2. "Liczymy jakosc (WER/CER/F1), szybkosc (latency/RTF) i koszt pamieci."
3. "Najlepszy model wg jakosci to X, a najlepszy kompromis jakosc/szybkosc to Y."
4. "Finalny wybor zalezy od scenariusza: demo live vs najwyzsza jakosc transkrypcji."

## 8) Ograniczenia obecnych wynikow (uczciwa interpretacja)
- Benchmark ocenia ASR, nie jakosc tlumaczenia PL.
- Metryka `peak_memory_mb` jest oparta o `tracemalloc` (python-level).
- Ocena zalezy od jakosci referencji tekstowych.
- Przy malych zbiorach wnioski sa bardziej wrazliwe na pojedyncze outliery.
