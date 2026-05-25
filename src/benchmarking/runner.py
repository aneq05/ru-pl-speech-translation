from __future__ import annotations

import gc
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from benchmarking.config import DEFAULT_MODELS_CONFIG_PATH, load_model_ids_from_config
from benchmarking.dataset import load_dataset
from benchmarking.evaluator import evaluate_models
from benchmarking.model_registry import DEFAULT_MODEL_IDS, create_model
from benchmarking.models import ASRModelUnavailableError
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
    rows = []
    skipped_models: list[str] = []
    evaluated_models_count = 0

    for model_id in selected_models:
        model = None
        model_rows = None
        try:
            model = create_model(model_id, language=language, device=device)
        except ASRModelUnavailableError as exc:
            skipped_models.append(model_id)
            print(f"[benchmark] skipped unavailable model: {model_id} ({exc})")
            continue
        except Exception as exc:
            skipped_models.append(model_id)
            print(f"[benchmark] skipped invalid model config: {model_id} ({exc})")
            continue

        try:
            model_rows = evaluate_models(run_id=run_id, models=[model], samples=samples)
        except Exception as exc:
            skipped_models.append(model_id)
            print(f"[benchmark] failed model run: {model_id} ({exc})")
        else:
            rows.extend(model_rows)
            evaluated_models_count += 1
        finally:
            _release_model_resources(model)

    if not rows:
        raise RuntimeError(
            "None of requested models produced benchmark rows. "
            f"Requested: {selected_models}. Skipped/failed: {skipped_models}."
        )

    leaderboard = build_leaderboard(rows)

    detailed_csv = write_detailed_results_csv(rows, run_dir / "detailed_results.csv")
    leaderboard_csv = write_leaderboard_csv(leaderboard, run_dir / "leaderboard.csv")
    plot_paths = generate_benchmark_plots(leaderboard=leaderboard, rows=rows, output_dir=run_dir / "plots")

    print(f"[benchmark] samples: {len(samples)}")
    print(f"[benchmark] models evaluated: {evaluated_models_count}")
    print(f"[benchmark] detailed results: {detailed_csv}")
    print(f"[benchmark] leaderboard: {leaderboard_csv}")
    print(f"[benchmark] plots directory: {run_dir / 'plots'}")

    return BenchmarkArtifacts(
        run_id=run_id,
        run_dir=run_dir,
        detailed_csv=detailed_csv,
        leaderboard_csv=leaderboard_csv,
        plot_paths=plot_paths,
        skipped_models=skipped_models,
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


def _release_model_resources(model: object | None) -> None:
    if model is None:
        return

    # Explicitly drop heavy references before gc.
    for attr in ("_model", "_pipeline"):
        if hasattr(model, attr):
            setattr(model, attr, None)

    del model
    gc.collect()
    _clear_torch_cache()


def _clear_torch_cache() -> None:
    try:
        import torch
    except ImportError:
        return

    if getattr(torch, "cuda", None) and torch.cuda.is_available():
        torch.cuda.empty_cache()
        if hasattr(torch.cuda, "ipc_collect"):
            torch.cuda.ipc_collect()

    mps = getattr(torch, "mps", None)
    if mps is not None and hasattr(mps, "empty_cache"):
        try:
            mps.empty_cache()
        except Exception:
            pass
