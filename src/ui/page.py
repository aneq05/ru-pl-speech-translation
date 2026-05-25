from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit as st
from benchmarking.runner import run_benchmark

from ui.components import (
    render_audio_panel,
    render_comparison_dashboard,
    render_flow_track,
    render_hero,
    render_recognition_and_translation,
    render_reference_panel,
    render_sidebar_controls,
)
from ui.data import (
    build_demo_payload,
    build_flow_steps,
    find_latest_benchmark_run,
    get_plot_paths,
    get_tongue_twister_reference,
    load_detailed_rows,
    load_leaderboard_rows,
)
from ui.styles import configure_page, inject_styles
from ui.types import SidebarState

UI_COMPARISON_RUNS_DIR = Path("src/ui/model_comparison/results")


def _init_session_state() -> None:
    if "analysis_result" not in st.session_state:
        st.session_state.analysis_result = None
    if "ui_message" not in st.session_state:
        st.session_state.ui_message = ""
    if "comparison_message" not in st.session_state:
        st.session_state.comparison_message = ""


def _handle_actions(sidebar_state: SidebarState) -> None:
    if sidebar_state.mode == "Analysis":
        if sidebar_state.analyze_clicked and sidebar_state.audio_file is None:
            st.session_state.ui_message = "Upload audio before analysis."
            return

        if sidebar_state.analyze_clicked and sidebar_state.audio_file is not None:
            payload = build_demo_payload()
            payload["file_name"] = sidebar_state.audio_file.name
            st.session_state.analysis_result = payload
            st.session_state.ui_message = "Analysis complete."
        return

    if sidebar_state.run_comparison_clicked:
        with st.spinner("Running benchmark on your dataset..."):
            try:
                artifacts = run_benchmark(report_root_dir=UI_COMPARISON_RUNS_DIR)
            except Exception as exc:
                st.session_state.comparison_message = f"Benchmark failed: {exc}"
            else:
                if artifacts.skipped_models:
                    skipped = ", ".join(artifacts.skipped_models)
                    st.session_state.comparison_message = (
                        f"Benchmark complete. Run: {artifacts.run_id}. Skipped/failed models: {skipped}"
                    )
                else:
                    st.session_state.comparison_message = f"Benchmark complete. Run: {artifacts.run_id}"


def _render_message() -> None:
    message = st.session_state.ui_message
    if message:
        st.markdown(
            f"""
            <div class="soft-box" style="margin-bottom:0.95rem;">
                <strong>Status:</strong> {message}
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_comparison_message() -> None:
    message = st.session_state.comparison_message
    if not message:
        return

    st.markdown(
        f"""
        <div class="soft-box" style="margin-bottom:0.95rem;">
            <strong>Status:</strong> {message}
        </div>
        """,
        unsafe_allow_html=True,
    )


def _resolve_reference_file_name(audio_file: Any, result: dict[str, Any] | None) -> str | None:
    if audio_file is not None:
        return audio_file.name
    if result is not None:
        return result.get("file_name")
    return None


def _render_analysis_mode(sidebar_state: SidebarState, result: dict[str, Any] | None) -> None:
    has_audio = sidebar_state.audio_file is not None
    has_result = result is not None
    steps = build_flow_steps(has_audio=has_audio, has_result=has_result)

    reference_file_name = _resolve_reference_file_name(sidebar_state.audio_file, result)
    reference = get_tongue_twister_reference(reference_file_name)

    _render_message()
    render_reference_panel(reference, reference_file_name)
    render_audio_panel(sidebar_state.audio_file)
    render_recognition_and_translation(result)
    render_flow_track(steps)


def _render_comparison_mode() -> None:
    _render_comparison_message()

    latest_run_dir = find_latest_benchmark_run(UI_COMPARISON_RUNS_DIR)
    if latest_run_dir is None:
        latest_run_dir = find_latest_benchmark_run()

    leaderboard_rows: list[dict[str, Any]] = []
    detailed_rows: list[dict[str, Any]] = []
    plot_paths = []
    run_id = None

    if latest_run_dir is not None:
        leaderboard_rows = load_leaderboard_rows(latest_run_dir)
        detailed_rows = load_detailed_rows(latest_run_dir)
        plot_paths = get_plot_paths(latest_run_dir)
        run_id = latest_run_dir.name.replace("run_", "", 1)

    render_comparison_dashboard(
        run_id=run_id,
        run_dir=latest_run_dir,
        leaderboard_rows=leaderboard_rows,
        detailed_rows=detailed_rows,
        plot_paths=plot_paths,
    )


def run_app() -> None:
    configure_page()
    inject_styles()
    _init_session_state()

    sidebar_state: SidebarState = render_sidebar_controls()
    _handle_actions(sidebar_state)

    result: dict[str, Any] | None = st.session_state.analysis_result

    left, center, right = st.columns([0.14, 1.72, 0.14], gap="small")
    with center:
        render_hero()
        if sidebar_state.mode == "Analysis":
            _render_analysis_mode(sidebar_state, result)
        else:
            _render_comparison_mode()
