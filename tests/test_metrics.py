from ru_pl_st.eval.metrics import compute_asr_metrics, compute_translation_metrics


def test_asr_metrics_perfect_match() -> None:
    refs = ["eto testovaya fraza"]
    hyps = ["eto testovaya fraza"]
    wer_score, cer_score = compute_asr_metrics(refs, hyps)
    assert wer_score == 0.0
    assert cer_score == 0.0


def test_translation_metrics_perfect_match() -> None:
    refs = ["to jest testowe zdanie"]
    hyps = ["to jest testowe zdanie"]
    bleu_score, chrf_score = compute_translation_metrics(refs, hyps)
    assert bleu_score > 99.0
    assert chrf_score > 99.0

