from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any

import numpy as np

from benchmarking.types import EvaluationRow


def write_detailed_results_csv(rows: list[EvaluationRow], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError("Cannot write empty benchmark results.")

    fieldnames = list(rows[0].to_dict().keys())
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row.to_dict())

    return output_path


def build_leaderboard(rows: list[EvaluationRow]) -> list[dict[str, Any]]:
    grouped: dict[str, list[EvaluationRow]] = defaultdict(list)
    for row in rows:
        grouped[row.model_id].append(row)

    leaderboard: list[dict[str, Any]] = []
    for model_id, model_rows in grouped.items():
        confidence_values = [row.mean_confidence for row in model_rows if row.mean_confidence is not None]
        leaderboard.append(
            {
                "model_id": model_id,
                "samples_count": len(model_rows),
                "wer_mean": mean(row.wer for row in model_rows),
                "cer_mean": mean(row.cer for row in model_rows),
                "token_precision_mean": mean(row.token_precision for row in model_rows),
                "token_recall_mean": mean(row.token_recall for row in model_rows),
                "token_f1_mean": mean(row.token_f1 for row in model_rows),
                "exact_match_mean": mean(row.exact_match for row in model_rows),
                "latency_sec_mean": mean(row.latency_sec for row in model_rows),
                "latency_sec_p95": _percentile([row.latency_sec for row in model_rows], 95),
                "rtf_mean": mean(row.rtf for row in model_rows),
                "peak_memory_mb_mean": mean(row.peak_memory_mb for row in model_rows),
                "confidence_mean": mean(confidence_values) if confidence_values else None,
            }
        )

    leaderboard.sort(key=lambda item: (item["wer_mean"], item["rtf_mean"]))
    return leaderboard


def write_leaderboard_csv(leaderboard: list[dict[str, Any]], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not leaderboard:
        raise ValueError("Cannot write empty leaderboard.")

    fieldnames = list(leaderboard[0].keys())
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in leaderboard:
            writer.writerow(row)

    return output_path


def generate_benchmark_plots(
    *,
    leaderboard: list[dict[str, Any]],
    rows: list[EvaluationRow],
    output_dir: Path,
) -> list[Path]:
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise RuntimeError("matplotlib is required for plot generation: pip install matplotlib") from exc

    output_dir.mkdir(parents=True, exist_ok=True)
    grouped_by_model = _group_rows_by_model(rows)

    plot_paths: list[Path] = []
    plot_paths.append(_plot_overview_bar_chart(leaderboard, output_dir / "01_overview_metrics.png", plt))
    plot_paths.append(_plot_quality_vs_speed_scatter(rows, output_dir / "02_quality_vs_speed.png", plt))
    plot_paths.append(_plot_wer_boxplot(grouped_by_model, output_dir / "03_wer_boxplot.png", plt))
    plot_paths.append(_plot_model_metric_heatmap(leaderboard, output_dir / "04_model_heatmap.png", plt))
    return plot_paths


def _plot_overview_bar_chart(leaderboard: list[dict[str, Any]], output_path: Path, plt: Any) -> Path:
    model_ids = [row["model_id"] for row in leaderboard]
    wer = [row["wer_mean"] for row in leaderboard]
    cer = [row["cer_mean"] for row in leaderboard]
    rtf = [row["rtf_mean"] for row in leaderboard]

    x = np.arange(len(model_ids))
    width = 0.25

    fig, ax = plt.subplots(figsize=(11, 5))
    ax.bar(x - width, wer, width=width, label="WER")
    ax.bar(x, cer, width=width, label="CER")
    ax.bar(x + width, rtf, width=width, label="RTF")
    ax.set_title("Model comparison: WER vs CER vs RTF")
    ax.set_ylabel("Value")
    ax.set_xticks(x)
    ax.set_xticklabels(model_ids, rotation=20, ha="right")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def _plot_quality_vs_speed_scatter(rows: list[EvaluationRow], output_path: Path, plt: Any) -> Path:
    grouped = _group_rows_by_model(rows)
    fig, ax = plt.subplots(figsize=(9, 6))
    for model_id, model_rows in grouped.items():
        x = [row.latency_sec for row in model_rows]
        y = [row.wer for row in model_rows]
        ax.scatter(x, y, alpha=0.75, label=model_id)

    ax.set_title("Quality vs speed per sample")
    ax.set_xlabel("Latency (seconds)")
    ax.set_ylabel("WER")
    ax.legend()
    ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def _plot_wer_boxplot(
    grouped_by_model: dict[str, list[EvaluationRow]],
    output_path: Path,
    plt: Any,
) -> Path:
    labels = list(grouped_by_model.keys())
    values = [[row.wer for row in grouped_by_model[label]] for label in labels]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.boxplot(values, labels=labels, showmeans=True)
    ax.set_title("WER distribution by model")
    ax.set_ylabel("WER")
    ax.set_xlabel("Model")
    ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def _plot_model_metric_heatmap(leaderboard: list[dict[str, Any]], output_path: Path, plt: Any) -> Path:
    metric_names = [
        "wer_mean",
        "cer_mean",
        "token_f1_mean",
        "exact_match_mean",
        "latency_sec_mean",
        "rtf_mean",
        "peak_memory_mb_mean",
    ]
    model_ids = [row["model_id"] for row in leaderboard]
    matrix = np.array([[row[metric] for metric in metric_names] for row in leaderboard], dtype=float)

    fig, ax = plt.subplots(figsize=(12, 5))
    image = ax.imshow(matrix, aspect="auto")
    ax.set_title("Model vs metric heatmap")
    ax.set_xticks(np.arange(len(metric_names)))
    ax.set_xticklabels(metric_names, rotation=35, ha="right")
    ax.set_yticks(np.arange(len(model_ids)))
    ax.set_yticklabels(model_ids)

    for row_index in range(matrix.shape[0]):
        for col_index in range(matrix.shape[1]):
            ax.text(col_index, row_index, f"{matrix[row_index, col_index]:.2f}", ha="center", va="center")

    fig.colorbar(image, ax=ax, fraction=0.03, pad=0.02)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def _group_rows_by_model(rows: list[EvaluationRow]) -> dict[str, list[EvaluationRow]]:
    grouped: dict[str, list[EvaluationRow]] = defaultdict(list)
    for row in rows:
        grouped[row.model_id].append(row)
    return dict(grouped)


def _percentile(values: list[float], percentile: float) -> float:
    if not values:
        return 0.0
    return float(np.percentile(np.asarray(values, dtype=float), percentile))
