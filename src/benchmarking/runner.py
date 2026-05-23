from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from benchmarking.config import DEFAULT_MODELS_CONFIG_PATH, load_model_ids_from_config
from benchmarking.dataset import load_dataset
from benchmarking.evaluator import evaluate_models
from benchmarking.model_registry import DEFAULT_MODEL_IDS, create_models
from benchmarking.reporting import (
    build_leaderboard,
    generate_benchmark_plots,
    write_detailed_results_csv,
    write_leaderboard_csv,
)


@dataclass(slots=True, frozen=True)
class BenchmarkArtifacts:
    run_id: str
    run_dir: Path
    detailed_csv: Path
    leaderboard_csv: Path
    plot_paths: list[Path]
    skipped_models: list[str]


def run_benchmark(
    *,
    raw_data_dir: str | Path = "data/raw",
    report_root_dir: str | Path = "reports/results",
    model_ids: list[str] | None = None,
    models_config_path: str | Path | None = DEFAULT_MODELS_CONFIG_PATH,
    language: str = "ru",
    device: str = "cpu",
) -> BenchmarkArtifacts:
    selected_models = _resolve_model_ids(model_ids=model_ids, models_config_path=models_config_path)
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = Path(report_root_dir).resolve() / f"run_{run_id}"
    run_dir.mkdir(parents=True, exist_ok=True)

    samples = load_dataset(raw_data_dir)
    models, unavailable = create_models(selected_models, language=language, device=device)

    if unavailable:
        print("[benchmark] skipped unavailable models:")
        for model_id in unavailable:
            print(f"  - {model_id}")

    rows = evaluate_models(run_id=run_id, models=models, samples=samples)
    leaderboard = build_leaderboard(rows)

    detailed_csv = write_detailed_results_csv(rows, run_dir / "detailed_results.csv")
    leaderboard_csv = write_leaderboard_csv(leaderboard, run_dir / "leaderboard.csv")
    plot_paths = generate_benchmark_plots(leaderboard=leaderboard, rows=rows, output_dir=run_dir / "plots")

    print(f"[benchmark] samples: {len(samples)}")
    print(f"[benchmark] models evaluated: {len(models)}")
    print(f"[benchmark] detailed results: {detailed_csv}")
    print(f"[benchmark] leaderboard: {leaderboard_csv}")
    print(f"[benchmark] plots directory: {run_dir / 'plots'}")

    return BenchmarkArtifacts(
        run_id=run_id,
        run_dir=run_dir,
        detailed_csv=detailed_csv,
        leaderboard_csv=leaderboard_csv,
        plot_paths=plot_paths,
        skipped_models=unavailable,
    )


def _resolve_model_ids(
    *,
    model_ids: list[str] | None,
    models_config_path: str | Path | None,
) -> list[str]:
    if model_ids:
        print("[benchmark] using models from CLI --models")
        return model_ids

    if models_config_path is not None:
        config_path = Path(models_config_path)
        if config_path.exists():
            config_model_ids = load_model_ids_from_config(config_path)
            print(f"[benchmark] using models from config: {config_path}")
            return config_model_ids

    print("[benchmark] using built-in default model list")
    return list(DEFAULT_MODEL_IDS)
