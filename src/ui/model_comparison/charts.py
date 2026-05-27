from __future__ import annotations

from collections import defaultdict
from html import escape
from typing import Any

import streamlit as st

from ui.model_comparison.theme import (
    MODEL_COLORS,
    PINK_LIGHT,
    PINK_PRIMARY,
    PINK_SECONDARY,
    apply_dark_pink_theme,
)

QUALITY_METRICS = [
    ("wer_mean", "WER"),
    ("cer_mean", "CER"),
    ("token_f1_mean", "Token F1"),
    ("exact_match_mean", "Exact match"),
]

HEATMAP_METRICS = [
    ("wer_mean", "WER", False),
    ("cer_mean", "CER", False),
    ("token_f1_mean", "Token F1", True),
    ("exact_match_mean", "Exact match", True),
    ("latency_sec_mean", "Latency [s]", False),
    ("rtf_mean", "RTF", False),
    ("peak_memory_mb_mean", "Peak RAM [MB]", False),
]

RANKING_METRICS = [
    ("wer_mean", "WER", False, 0.34),
    ("cer_mean", "CER", False, 0.16),
    ("token_f1_mean", "Token F1", True, 0.18),
    ("exact_match_mean", "Exact match", True, 0.12),
    ("latency_sec_mean", "Latency [s]", False, 0.12),
    ("rtf_mean", "RTF", False, 0.04),
    ("peak_memory_mb_mean", "Peak RAM [MB]", False, 0.04),
]


def render_model_comparison_charts(
    *,
    leaderboard_rows: list[dict[str, Any]],
    detailed_rows: list[dict[str, Any]],
) -> None:
    plotly_modules = _import_plotly_modules()
    if plotly_modules is None:
        st.info("Install `plotly` to enable interactive comparison charts in this section.")
        return

    go, _ = plotly_modules
    cleaned_leaderboard = _clean_leaderboard_rows(leaderboard_rows)
    if not cleaned_leaderboard:
        st.warning("Missing numeric data in leaderboard, so interactive charts cannot be rendered.")
        return

    st.markdown("##### Interactive comparison charts")
    _render_highlight_metrics(cleaned_leaderboard)
    ranked_models = _build_model_ranking(cleaned_leaderboard)
    _render_model_ranking(ranked_models)
    _render_chart_gallery(cleaned_leaderboard, detailed_rows, go)


def _render_chart_gallery(
    leaderboard_rows: list[dict[str, Any]],
    detailed_rows: list[dict[str, Any]],
    go: Any,
) -> None:
    st.markdown("#### Chart gallery")
    st.caption(
        "Click the arrow on a card to expand an interactive chart, "
        "then use fullscreen in the chart toolbar for a larger view."
    )

    chart_cards: list[dict[str, Any]] = [
        {
            "badge": "01",
            "title": "Quality metrics overview",
            "subtitle": "WER, CER, Token F1 and exact match side by side.",
            "figure": _build_quality_grouped_bar(leaderboard_rows, go),
            "missing_message": "Missing leaderboard values for quality overview.",
        },
        {
            "badge": "02",
            "title": "Quality vs speed trade-off",
            "subtitle": "Latency and WER with bubble size based on memory usage.",
            "figure": _build_quality_speed_scatter(leaderboard_rows, go),
            "missing_message": "Missing leaderboard values for trade-off scatter.",
        },
        {
            "badge": "03",
            "title": "WER distribution",
            "subtitle": "Per-sample spread for each model on the full dataset.",
            "figure": _build_wer_boxplot(detailed_rows, go),
            "missing_message": "No detailed benchmark rows available for WER distribution.",
        },
        {
            "badge": "04",
            "title": "Normalized score heatmap",
            "subtitle": "Relative score across all tracked metrics.",
            "figure": _build_normalized_heatmap(leaderboard_rows, go),
            "missing_message": "Missing leaderboard values for normalized heatmap.",
        },
    ]

    left_column, right_column = st.columns(2, gap="large")
    for index, chart in enumerate(chart_cards):
        target_column = left_column if index % 2 == 0 else right_column
        with target_column:
            label = _build_chart_expander_label(
                badge=str(chart["badge"]),
                title=str(chart["title"]),
                subtitle=str(chart["subtitle"]),
            )
            with st.expander(label, expanded=False):
                figure = chart["figure"]
                if figure is None:
                    st.info(str(chart["missing_message"]))
                else:
                    st.plotly_chart(
                        figure,
                        use_container_width=True,
                        config=_plotly_chart_config(),
                    )


def _build_chart_expander_label(*, badge: str, title: str, subtitle: str) -> str:
    safe_badge = escape(badge)
    safe_title = escape(title)
    safe_subtitle = escape(subtitle)
    return f"**[{safe_badge}] {safe_title}**\n\n*{safe_subtitle}*"


def _plotly_chart_config() -> dict[str, Any]:
    return {
        "displayModeBar": "hover",
        "displaylogo": False,
        "scrollZoom": True,
        "modeBarButtonsToRemove": ["select2d", "lasso2d", "autoScale2d"],
        "toImageButtonOptions": {"format": "png", "scale": 2},
    }


def _import_plotly_modules() -> tuple[Any, Any] | None:
    try:
        import plotly.graph_objects as go
        import plotly.io as pio
    except ImportError:
        return None

    pio.templates.default = "plotly_dark"
    return go, pio


def _clean_leaderboard_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    cleaned: list[dict[str, Any]] = []
    for row in rows:
        model_id = str(row.get("model_id", "")).strip()
        if not model_id:
            continue

        normalized = {"model_id": model_id}
        for metric_key, _ in QUALITY_METRICS:
            normalized[metric_key] = _to_float(row.get(metric_key))

        normalized["latency_sec_mean"] = _to_float(row.get("latency_sec_mean"))
        normalized["rtf_mean"] = _to_float(row.get("rtf_mean"))
        normalized["peak_memory_mb_mean"] = _to_float(row.get("peak_memory_mb_mean"))
        cleaned.append(normalized)

    return cleaned


def _render_highlight_metrics(rows: list[dict[str, Any]]) -> None:
    best_wer = _pick_best(rows, "wer_mean", lower_is_better=True)
    best_f1 = _pick_best(rows, "token_f1_mean", lower_is_better=False)
    fastest = _pick_best(rows, "latency_sec_mean", lower_is_better=True)

    _, col_1, col_2, col_3, _ = st.columns([0.14, 1, 1, 1, 0.14], gap="medium")
    with col_1:
        if best_wer is None:
            st.metric("Best WER", "n/a")
        else:
            st.metric("Best WER", f"{best_wer['value']:.3f}", best_wer["model_id"])
    with col_2:
        if best_f1 is None:
            st.metric("Best Token F1", "n/a")
        else:
            st.metric("Best Token F1", f"{best_f1['value']:.3f}", best_f1["model_id"])
    with col_3:
        if fastest is None:
            st.metric("Lowest Latency", "n/a")
        else:
            st.metric("Lowest Latency", f"{fastest['value']:.2f}s", fastest["model_id"])


def _build_model_ranking(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not rows:
        return []

    reference_columns: dict[str, list[float]] = {}
    for metric_key, _, _, _ in RANKING_METRICS:
        reference_columns[metric_key] = [float(row[metric_key]) for row in rows if row.get(metric_key) is not None]

    ranked: list[dict[str, Any]] = []
    for row in rows:
        weighted_sum = 0.0
        weight_total = 0.0
        for metric_key, _, higher_is_better, weight in RANKING_METRICS:
            normalized = _normalize_metric(
                _to_float(row.get(metric_key)),
                reference_columns.get(metric_key, []),
                higher_is_better=higher_is_better,
            )
            weighted_sum += normalized * weight
            weight_total += weight

        composite_score = 0.0 if weight_total <= 0 else weighted_sum / weight_total
        ranked.append(
            {
                "model_id": row["model_id"],
                "score": composite_score,
                "wer_mean": _to_float(row.get("wer_mean")),
                "cer_mean": _to_float(row.get("cer_mean")),
                "token_f1_mean": _to_float(row.get("token_f1_mean")),
                "exact_match_mean": _to_float(row.get("exact_match_mean")),
                "latency_sec_mean": _to_float(row.get("latency_sec_mean")),
                "rtf_mean": _to_float(row.get("rtf_mean")),
                "peak_memory_mb_mean": _to_float(row.get("peak_memory_mb_mean")),
            }
        )

    ranked.sort(
        key=lambda entry: (
            -float(entry["score"]),
            float("inf") if entry["wer_mean"] is None else float(entry["wer_mean"]),
            float("inf") if entry["latency_sec_mean"] is None else float(entry["latency_sec_mean"]),
        )
    )

    for index, row in enumerate(ranked, start=1):
        row["rank"] = index
    return ranked


def _render_model_ranking(ranked_models: list[dict[str, Any]]) -> None:
    if not ranked_models:
        return

    st.markdown("#### Model ranking")
    winner = ranked_models[0]
    winner_id = escape(str(winner["model_id"]))
    winner_score = float(winner["score"]) * 100.0
    winner_wer = _format_value(winner.get("wer_mean"), decimals=3)
    winner_latency = _format_value(winner.get("latency_sec_mean"), decimals=2, suffix=" s")
    winner_f1 = _format_value(winner.get("token_f1_mean"), decimals=3)

    st.markdown(
        (
            "<div class='winner-card'>"
            "<div class='winner-eyebrow'>Best overall model</div>"
            f"<div class='winner-model'>{winner_id}</div>"
            "<div class='winner-metrics'>"
            f"<span>Composite score: {winner_score:.1f}</span>"
            f"<span>WER: {winner_wer}</span>"
            f"<span>Latency: {winner_latency}</span>"
            f"<span>Token F1: {winner_f1}</span>"
            "</div>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )

    ranking_table: list[dict[str, Any]] = []
    for row in ranked_models:
        ranking_table.append(
            {
                "Rank": row["rank"],
                "Model": row["model_id"],
                "Composite score": round(float(row["score"]) * 100.0, 2),
                "WER": _format_value(row.get("wer_mean"), decimals=3),
                "CER": _format_value(row.get("cer_mean"), decimals=3),
                "Token F1": _format_value(row.get("token_f1_mean"), decimals=3),
                "Exact match": _format_value(row.get("exact_match_mean"), decimals=3),
                "Latency [s]": _format_value(row.get("latency_sec_mean"), decimals=2),
            }
        )

    st.dataframe(ranking_table, use_container_width=True, hide_index=True)


def _pick_best(
    rows: list[dict[str, Any]],
    metric_key: str,
    *,
    lower_is_better: bool,
) -> dict[str, Any] | None:
    candidates = [row for row in rows if row.get(metric_key) is not None]
    if not candidates:
        return None

    scored = sorted(candidates, key=lambda row: row[metric_key], reverse=not lower_is_better)[0]
    return {
        "model_id": scored["model_id"],
        "value": float(scored[metric_key]),
    }


def _build_quality_grouped_bar(rows: list[dict[str, Any]], go: Any) -> Any:
    model_ids = [row["model_id"] for row in rows]
    series_colors = [PINK_PRIMARY, PINK_SECONDARY, PINK_LIGHT, "#FF84CF"]

    figure = go.Figure()
    for idx, (metric_key, metric_label) in enumerate(QUALITY_METRICS):
        figure.add_trace(
            go.Bar(
                name=metric_label,
                x=model_ids,
                y=[row.get(metric_key) for row in rows],
                marker_color=series_colors[idx % len(series_colors)],
                hovertemplate=(
                    "<b>%{x}</b><br>"
                    + metric_label
                    + ": %{y:.4f}<extra></extra>"
                ),
            )
        )

    figure.update_layout(
        barmode="group",
        yaxis_title="Metric value",
        xaxis_title="Model",
        bargap=0.16,
    )
    figure.update_xaxes(tickangle=-23, tickfont=dict(size=11))
    return apply_dark_pink_theme(
        figure,
        title="Model quality metrics (WER/CER lower is better)",
        height=360,
    )


def _build_quality_speed_scatter(rows: list[dict[str, Any]], go: Any) -> Any:
    x_values = [row.get("latency_sec_mean") for row in rows]
    y_values = [row.get("wer_mean") for row in rows]
    f1_values = [row.get("token_f1_mean") for row in rows]
    memory_values = [row.get("peak_memory_mb_mean") for row in rows]
    model_ids = [row["model_id"] for row in rows]

    marker_sizes = _scaled_marker_sizes(memory_values)
    marker_colors = [MODEL_COLORS[index % len(MODEL_COLORS)] for index in range(len(model_ids))]

    customdata = []
    for model_id, latency, wer, f1, ram in zip(model_ids, x_values, y_values, f1_values, memory_values, strict=False):
        customdata.append(
            [
                model_id,
                "n/a" if latency is None else f"{latency:.3f}",
                "n/a" if wer is None else f"{wer:.3f}",
                "n/a" if f1 is None else f"{f1:.3f}",
                "n/a" if ram is None else f"{ram:.1f}",
            ]
        )

    figure = go.Figure(
        data=[
            go.Scatter(
                x=x_values,
                y=y_values,
                mode="markers+text" if len(model_ids) <= 6 else "markers",
                text=model_ids if len(model_ids) <= 6 else None,
                textposition="top center",
                cliponaxis=False,
                customdata=customdata,
                marker=dict(
                    size=marker_sizes,
                    color=marker_colors,
                    opacity=0.9,
                    line=dict(color=PINK_LIGHT, width=1.2),
                ),
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>"
                    "Latency: %{customdata[1]} s<br>"
                    "WER: %{customdata[2]}<br>"
                    "Token F1: %{customdata[3]}<br>"
                    "Peak RAM: %{customdata[4]} MB<extra></extra>"
                ),
            )
        ]
    )

    figure.update_layout(
        xaxis_title="Latency mean [seconds]",
        yaxis_title="WER mean",
    )
    wer_values = [value for value in y_values if value is not None]
    if wer_values:
        padding = max((max(wer_values) - min(wer_values)) * 0.2, 0.03)
        figure.update_yaxes(range=[max(0.0, min(wer_values) - padding), max(wer_values) + padding])

    return apply_dark_pink_theme(figure, title="Quality vs speed trade-off (bubble size = RAM)", height=360)


def _build_wer_boxplot(detailed_rows: list[dict[str, Any]], go: Any) -> Any | None:
    grouped_wer: dict[str, list[float]] = defaultdict(list)
    for row in detailed_rows:
        model_id = str(row.get("model_id", "")).strip()
        wer_value = _to_float(row.get("wer"))
        if not model_id or wer_value is None:
            continue
        grouped_wer[model_id].append(wer_value)

    if not grouped_wer:
        return None

    figure = go.Figure()
    for index, model_id in enumerate(sorted(grouped_wer.keys())):
        figure.add_trace(
            go.Box(
                name=model_id,
                y=grouped_wer[model_id],
                boxmean=True,
                marker_color=MODEL_COLORS[index % len(MODEL_COLORS)],
                line=dict(color=PINK_LIGHT, width=1),
                fillcolor="rgba(255, 20, 147, 0.24)",
                opacity=0.9,
            )
        )

    figure.update_layout(
        yaxis_title="WER per sample",
        xaxis_title="Model",
        showlegend=False,
    )
    figure.update_xaxes(tickangle=-20, tickfont=dict(size=11))
    return apply_dark_pink_theme(figure, title="WER distribution across all samples", height=360)


def _build_normalized_heatmap(rows: list[dict[str, Any]], go: Any) -> Any:
    model_ids = [row["model_id"] for row in rows]
    metric_labels = [metric_label for _, metric_label, _ in HEATMAP_METRICS]

    normalized_matrix: list[list[float]] = []
    text_matrix: list[list[str]] = []

    columns_raw: dict[str, list[float]] = {}
    for metric_key, _, _ in HEATMAP_METRICS:
        values = [row.get(metric_key) for row in rows if row.get(metric_key) is not None]
        columns_raw[metric_key] = [float(value) for value in values]

    for row in rows:
        row_normalized: list[float] = []
        row_text: list[str] = []
        for metric_key, _, higher_is_better in HEATMAP_METRICS:
            value = row.get(metric_key)
            row_text.append("n/a" if value is None else f"{value:.3f}")
            row_normalized.append(_normalize_metric(value, columns_raw[metric_key], higher_is_better=higher_is_better))
        normalized_matrix.append(row_normalized)
        text_matrix.append(row_text)

    figure = go.Figure(
        data=[
            go.Heatmap(
                z=normalized_matrix,
                x=metric_labels,
                y=model_ids,
                text=text_matrix,
                texttemplate="%{text}",
                colorscale=[
                    [0.0, "#250014"],
                    [0.35, "#5B143D"],
                    [0.65, "#A62970"],
                    [1.0, "#FF1493"],
                ],
                zmin=0,
                zmax=1,
                colorbar=dict(title="Normalized score"),
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "%{x}: %{text}<br>"
                    "Relative score: %{z:.3f}<extra></extra>"
                ),
            )
        ]
    )

    figure.update_layout(
        xaxis_title="Metric",
        yaxis_title="Model",
    )
    figure.update_xaxes(tickangle=-24, tickfont=dict(size=11))
    return apply_dark_pink_theme(figure, title="Normalized model score heatmap (higher is better)", height=360)


def _normalize_metric(value: float | None, reference: list[float], *, higher_is_better: bool) -> float:
    if value is None or not reference:
        return 0.0

    min_value = min(reference)
    max_value = max(reference)
    if max_value - min_value <= 1e-12:
        return 1.0

    normalized = (value - min_value) / (max_value - min_value)
    if higher_is_better:
        return float(normalized)
    return float(1.0 - normalized)


def _scaled_marker_sizes(memory_values: list[float | None]) -> list[float]:
    numeric = [value for value in memory_values if value is not None]
    if not numeric:
        return [18.0 for _ in memory_values]

    low = min(numeric)
    high = max(numeric)
    if high - low <= 1e-12:
        return [24.0 for _ in memory_values]

    min_size, max_size = 14.0, 42.0
    scaled: list[float] = []
    for value in memory_values:
        if value is None:
            scaled.append(min_size)
            continue
        relative = (value - low) / (high - low)
        scaled.append(min_size + relative * (max_size - min_size))
    return scaled


def _to_float(value: Any) -> float | None:
    if value is None:
        return None

    if isinstance(value, bool):
        return float(value)

    if isinstance(value, (int, float)):
        return float(value)

    if isinstance(value, str):
        stripped = value.strip()
        if stripped == "":
            return None
        try:
            return float(stripped)
        except ValueError:
            return None

    return None


def _format_value(value: float | None, *, decimals: int, suffix: str = "") -> str:
    if value is None:
        return "n/a"
    return f"{value:.{decimals}f}{suffix}"
