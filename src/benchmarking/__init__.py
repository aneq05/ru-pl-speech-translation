from __future__ import annotations

__all__ = ["BenchmarkArtifacts", "run_benchmark"]


def __getattr__(name: str) -> object:
    if name in __all__:
        from benchmarking.runner import BenchmarkArtifacts, run_benchmark

        exports = {
            "BenchmarkArtifacts": BenchmarkArtifacts,
            "run_benchmark": run_benchmark,
        }
        return exports[name]

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
