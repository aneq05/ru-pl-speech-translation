from __future__ import annotations

from collections import defaultdict
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

    st.markdown("#### Interactive comparison charts")
    _render_highlight_metrics(cleaned_leaderboard)

    top_left, top_right = st.columns(2, gap="large")
    with top_left:
        st.plotly_chart(
            _build_quality_grouped_bar(cleaned_leaderboard, go),
            use_container_width=True,
            config=_plotly_chart_config(),
        )
    with top_right:
        st.plotly_chart(
            _build_quality_speed_scatter(cleaned_leaderboard, go),
            use_container_width=True,
            config=_plotly_chart_config(),
        )

    bottom_left, bottom_right = st.columns(2, gap="large")
    with bottom_left:
        wer_figure = _build_wer_boxplot(detailed_rows, go)
        if wer_figure is None:
            st.info("No `detailed_results.csv` detected for WER distribution boxplot.")
        else:
            st.plotly_chart(
                wer_figure,
                use_container_width=True,
                config=_plotly_chart_config(),
            )
    with bottom_right:
        st.plotly_chart(
            _build_normalized_heatmap(cleaned_leaderboard, go),
            use_container_width=True,
            config=_plotly_chart_config(),
        )


def _plotly_chart_config() -> dict[str, Any]:
    return {
        "displayModeBar": True,
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

    col_1, col_2, col_3 = st.columns(3, gap="medium")
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
        height=470,
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

    return apply_dark_pink_theme(figure, title="Quality vs speed trade-off (bubble size = RAM)", height=470)


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
    return apply_dark_pink_theme(figure, title="WER distribution across all samples", height=470)


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
    return apply_dark_pink_theme(figure, title="Normalized model score heatmap (higher is better)", height=470)


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
