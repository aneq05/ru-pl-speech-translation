from __future__ import annotations

import io
from html import escape
from pathlib import Path
from typing import Any

import numpy as np
import soundfile as sf
import streamlit as st

from ui.model_comparison import render_model_comparison_charts
from ui.types import SidebarState


def _html(markup: str) -> None:
    st.markdown(markup, unsafe_allow_html=True)


def _extract_waveform(audio_file: Any, bars: int = 170) -> np.ndarray | None:
    if audio_file is None:
        return None

    try:
        audio_bytes = audio_file.getvalue()
        if not audio_bytes:
            return None
        signal, _ = sf.read(io.BytesIO(audio_bytes), always_2d=False)
    except Exception:
        return None

    waveform = np.asarray(signal, dtype=np.float32)
    if waveform.ndim > 1:
        waveform = waveform.mean(axis=1)

    waveform = np.abs(waveform)
    if waveform.size == 0:
        return None

    if waveform.size < bars:
        sample_indices = np.linspace(0, waveform.size - 1, bars).astype(int)
        sampled = waveform[sample_indices]
    else:
        trim_size = (waveform.size // bars) * bars
        sampled = waveform[:trim_size].reshape(bars, -1).max(axis=1)

    peak = float(sampled.max())
    if peak <= 1e-9:
        return np.full(bars, 0.15, dtype=np.float32)

    normalized = sampled / peak
    return np.clip(normalized, 0.06, 1.0)


def render_sidebar_controls() -> SidebarState:
    with st.sidebar:
        st.markdown("## 🎛️ Control Panel")

        # Add an info block for better user context
        st.info("Upload a Russian tongue twister audio to generate a transcript and a Polish translation.")
        # Visual divider line
        st.divider() 

        mode = st.radio(
            "Select App Mode:",
            ["Analysis", "Model Comparison"],
            index=0,
        )

        audio_file = None
        analyze_clicked = False
        run_comparison_clicked = False

        if mode == "Analysis":
            audio_file = st.file_uploader(
                "Upload audio",
                type=["wav"],
            )
            analyze_clicked = st.button(
                "Run analysis",
                type="primary",
                use_container_width=True,
            )
        else:
            run_comparison_clicked = st.button(
                "Run benchmark on dataset",
                type="primary",
                use_container_width=True,
            )
            st.caption("This mode shows charts from your benchmark runs.")

    return SidebarState(
        mode=mode,
        audio_file=audio_file,
        analyze_clicked=analyze_clicked,
        run_comparison_clicked=run_comparison_clicked,
    )


def render_hero() -> None:
    _html(
        """
        <section class="app-hero">
            <div class="eyebrow">Russian to Polish ASR</div>
            <h1 class="hero-title">Tongue Twister Studio</h1>
        </section>
        """
    )


def render_comparison_dashboard(
    *,
    run_id: str | None,
    run_dir: Path | None,
    leaderboard_rows: list[dict[str, Any]],
    detailed_rows: list[dict[str, Any]],
    plot_paths: list[Path],
) -> None:
    _html(
        """
        <section class="section-panel center-stage">
            <h2 class="section-title">Model Comparison</h2>
            <p class="section-subtitle">Comparative metrics and charts from your dataset benchmark runs.</p>
        """
    )

    if run_id is None or run_dir is None:
        _html(
            """
            <div class="soft-box">
                No benchmark results found yet. Click <strong>Run benchmark on dataset</strong> in the sidebar.
            </div>
            """
        )
        _html("</section>")
        return

    st.caption(f"Latest run: {run_id} | Path: {run_dir}")

    if leaderboard_rows:
        st.markdown("#### Leaderboard")
        st.dataframe(leaderboard_rows, use_container_width=True, hide_index=True)
        render_model_comparison_charts(
            leaderboard_rows=leaderboard_rows,
            detailed_rows=detailed_rows,
        )
    else:
        _html("<div class='soft-box'>Leaderboard CSV is empty.</div>")

    if plot_paths:
        st.markdown("#### Saved benchmark image charts")
        for plot_path in plot_paths:
            image_bytes = plot_path.read_bytes()
            st.image(image_bytes, caption=plot_path.name, use_container_width=True)
    else:
        _html("<div class='soft-box'>No plot images found for this run.</div>")

    _html("</section>")


def render_reference_panel(reference: dict[str, str], file_name: str | None) -> None:
    source_name = "No file selected" if file_name is None else escape(file_name)
    title = escape(reference.get("title", "Unknown reference"))
    original = escape(reference.get("original", ""))
    polish = escape(reference.get("polish", ""))

    _html(
        f"""
        <section class="section-panel center-stage">
            <h2 class="section-title">Original Tongue Twister</h2>
            <p class="section-subtitle">Source: {source_name}</p>
            <p class="section-subtitle">Title: {title}</p>
            <div class="reference-grid">
                <article class="reference-card">
                    <span>Russian original</span>
                    <h3>{original}</h3>
                </article>
                <article class="reference-card">
                    <span>Polish translation</span>
                    <h3>{polish}</h3>
                </article>
            </div>
        </section>
        """
    )


def render_audio_panel(audio_file: Any) -> None:
    _html(
        """
        <section class="section-panel center-stage audio-focus">
            <h2 class="section-title">Audio and Waveform</h2>
        """
    )

    if audio_file is None:
        _html(
            """
            <div class="soft-box">
                Upload an audio file or load the demo sample.
            </div>
            """
        )
    else:
        _html(
            f"""
            <div class="soft-box">
                File: <strong>{escape(audio_file.name)}</strong>
            </div>
            """
        )
        st.audio(audio_file)
        render_audio_waveform(audio_file)

    _html("</section>")


def render_flow_track(steps: list[dict[str, str]]) -> None:
    _html(
        """
        <section class="section-panel center-stage">
            <h2 class="section-title">Processing Flow</h2>
        """
    )

    step_columns = st.columns(len(steps), gap="small")
    for column, step in zip(step_columns, steps, strict=False):
        with column:
            _html(
                (
                    f'<div class="bubble-step {step["state"]}">'
                    f'<div class="bubble-top">'
                    f'<span class="bubble-icon">{step["icon"]}</span>'
                    f'<span class="bubble-index">{step["index"]}</span>'
                    f"</div>"
                    f'<div class="bubble-title">{step["title"]}</div>'
                    f'<div class="bubble-detail">{step["detail"]}</div>'
                    f"</div>"
                )
            )

    _html("</section>")


def render_audio_waveform(audio_file: Any) -> None:
    waveform = _extract_waveform(audio_file)
    if waveform is None:
        _html(
            """
            <div class="wave-shell">
                <div class="wave-label">Waveform preview unavailable for this file.</div>
            </div>
            """
        )
        return

    bars = "".join(
        f'<span class="wave-bar" style="height:{12 + (value * 88):.1f}%"></span>'
        for value in waveform
    )

    _html(
        f"""
        <div class="wave-shell">
            <div class="wave-label">Waveform preview</div>
            <div class="wave-track">{bars}</div>
        </div>
        """
    )


def render_recognition_and_translation(result: dict[str, Any] | None) -> None:
    _html(
        """
        <section class="section-panel center-stage">
            <h2 class="section-title">Recognition and Translation</h2>
        """
    )

    _render_word_stream(result)

    # CREATE TWO COLUMNS FOR SIDE-BY-SIDE COMPARISON
    col1, col2 = st.columns(2, gap="medium")
    
    with col1:
        _render_transcript_block(result) 
    with col2:
        _render_translation_block(result)

    _html("</section>")


def _render_word_stream(result: dict[str, Any] | None) -> None:
    _html("<h3 class='result-title'>Recognized Russian words</h3>")

    if result is None:
        _html("<div class='soft-box'>Waiting for analysis result.</div>")
        return

    words = result["segments"]
    per_row = 4
    for start in range(0, len(words), per_row):
        row_items = words[start : start + per_row]
        columns = st.columns(len(row_items), gap="small")
        for offset, (column, segment) in enumerate(zip(columns, row_items, strict=False), start=1):
            order = start + offset
            confidence = int(segment["confidence"] * 100)
            with column:
                st.markdown(f"**{order:02d}. {segment['word']}**")
                st.progress(segment["confidence"])
                st.caption(f"confidence: {confidence}%")


def _render_transcript_block(result: dict[str, Any] | None) -> None:
    _html("<h4 class='result-title'>Transcript</h4>")
    transcript = "" if result is None else result["recognized_text"]
    st.text_area(
        "Transcript (ASR)",
        value=transcript,
        height=118,
        disabled=result is None,
    )


def _render_translation_block(result: dict[str, Any] | None) -> None:
    _html("<h4 class='result-title'>Polish output</h4>")
    if result is None:
        _html("<div class='soft-box'>Waiting for translation result.</div>")
        return

    translation_text = result["translation"]
    st.text_area(
        "Polish translation",
        value=translation_text,
        height=90,
        disabled=True,
    )

    tokens = [token for token in translation_text.replace(",", " ").replace(".", " ").split() if token]
    if not tokens:
        return

    st.caption("Word-by-word preview")
    per_row = 6
    for start in range(0, len(tokens), per_row):
        row_items = tokens[start : start + per_row]
        columns = st.columns(len(row_items), gap="small")
        for column, token in zip(columns, row_items, strict=False):
            with column:
                st.markdown(f"`{token}`")
