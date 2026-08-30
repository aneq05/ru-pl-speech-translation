from __future__ import annotations

from benchmarking.metrics import compute_text_metrics, normalize_text


def test_normalize_text_preserves_cyrillic_letters() -> None:
    source = "\u0415\u0445\u0430\u043b \u0413\u0440\u0435\u043a\u0430 \u0447\u0435\u0440\u0435\u0437 \u0440\u0435\u043a\u0443!"
    expected = "\u0435\u0445\u0430\u043b \u0433\u0440\u0435\u043a\u0430 \u0447\u0435\u0440\u0435\u0437 \u0440\u0435\u043a\u0443"

    assert normalize_text(source) == expected


def test_compute_text_metrics_exact_match() -> None:
    text = "\u041a\u0430\u0440\u043b \u0443\u043a\u0440\u0430\u043b \u043a\u043e\u0440\u0430\u043b\u043b\u044b"
    metrics = compute_text_metrics(text, text)

    assert metrics.wer == 0.0
    assert metrics.cer == 0.0
    assert metrics.token_f1 == 1.0
    assert metrics.exact_match == 1.0


def test_compute_text_metrics_substitution() -> None:
    reference = "\u0440\u0430\u0437 \u0434\u0432\u0430 \u0442\u0440\u0438"
    hypothesis = "\u0440\u0430\u0437 \u0434\u0432\u0430 \u0447\u0435\u0442\u044b\u0440\u0435"
    metrics = compute_text_metrics(reference, hypothesis)

    assert metrics.wer == 1 / 3
    assert metrics.token_precision == 2 / 3
    assert metrics.token_recall == 2 / 3
