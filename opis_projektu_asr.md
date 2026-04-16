# Projekt zaliczeniowy (ASR)

## Temat
**Porownanie metod automatycznego tlumaczenia mowy rosyjskiej na jezyk polski**

## 1. Cel projektu
Celem projektu jest zaprojektowanie i porownanie dwoch podejsc do automatycznego tlumaczenia mowy rosyjskiej na jezyk polski:
- podejscia kaskadowego: `ASR (RU) -> tlumaczenie tekstu (RU->PL) -> TTS (PL)`,
- podejscia zintegrowanego: nowoczesny model `speech-to-text translation` (bez osobnego etapu ASR i MT).

Projekt ma pokazac, jak oba podejscia radza sobie w praktyce oraz jak na wynik wplywaja:
- jakosc nagrania,
- roznorodnosc mowcow,
- propagacja bledow miedzy etapami.

## 2. Zakres i dane
Ze wzgledu na charakter projektu zaliczeniowego zakres bedzie ambitny, ale wykonalny:
- `20-30` rosyjskich tongue twisters (lamancow jezykowych),
- `4-6` mowcow,
- `2` nagrania kazdego zdania na mowce,
- dwa warunki nagran: audio czyste oraz wersja zaszumiona.

Zakladana liczba probek: okolo `200-300` nagran.

Dla zbioru zostana przygotowane:
- transkrypcje rosyjskie (referencyjne),
- tlumaczenia referencyjne na jezyk polski,
- podzial na czesc testowa i walidacyjna.

## 3. Metody

### 3.1. System kaskadowy (baseline)
1. `ASR (RU)`: rozpoznanie mowy rosyjskiej do tekstu.
2. `MT (RU->PL)`: tlumaczenie rozpoznanego tekstu na polski.
3. `TTS (PL)`: synteza mowy polskiej na podstawie tlumaczenia.

### 3.2. System zintegrowany
Bezposrednie tlumaczenie mowy rosyjskiej do tekstu polskiego (`speech-to-text translation`), opcjonalnie z synteza mowy jako etapem koncowym do porownania odsluchowego.

## 4. Ewaluacja
Porownanie metod bedzie obejmowalo:
- jakosc ASR: `WER`, `CER` (dla podejscia kaskadowego),
- jakosc tlumaczenia: `BLEU`, `chrF`,
- wydajnosc: czas przetwarzania / `RTF` (real-time factor),
- krotka ocene odsluchowa jakosci TTS (np. skala `1-5`).

Dodatkowo przeprowadzona zostanie analiza bledow:
- ktore tongue twisters sa najtrudniejsze,
- jak bledy ASR wplywaja na jakosc tlumaczenia koncowego,
- porownanie odpornosci obu podejsc na szum i rozne glosy.

## 5. Plan realizacji
1. **Tydzien 1**: przygotowanie zbioru, nagrania, transkrypcje i referencyjne tlumaczenia.
2. **Tydzien 2**: implementacja i uruchomienie pipeline kaskadowego.
3. **Tydzien 3**: implementacja podejscia zintegrowanego oraz obliczenie metryk.
4. **Tydzien 4**: analiza wynikow, porownanie metod, przygotowanie raportu i demonstracji.

## 6. Oczekiwane rezultaty
Wyniki projektu powinny umozliwic:
- rzetelne porownanie obu podejsc na tym samym zbiorze danych,
- wskazanie mocnych i slabych stron pipeline'u kaskadowego oraz modelu zintegrowanego,
- ocene wplywu jakosci audio i trudnosci fonetycznej na finalne tlumaczenie.

Efektem koncowym bedzie raport z wynikami metryk, przykladami bledow oraz wnioskami praktycznymi dotyczacymi zastosowania automatycznego tlumaczenia mowy w warunkach rzeczywistych.
