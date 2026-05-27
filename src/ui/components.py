from __future__ import annotations

import base64
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
        st.markdown("## Control Panel")

        # Add an info block for better user context
        st.info("Upload a Russian tongue twister audio to generate a transcript and a Polish translation.")
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
                width='stretch',
            )
        else:
            run_comparison_clicked = st.button(
                "Run benchmark on dataset",
                type="primary",
                width='stretch',
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
            <div class="hero-title">Tongue Twister Studio</div>
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
            <div class="section-title">Model Comparison</div>
            <p class="section-subtitle">Comparative metrics and charts from your dataset benchmark runs.</p>
        """
    )

    if run_id is None or run_dir is None:
        _html(
            """
            <div class="soft-box">
                No benchmark results found yet. Run <strong>Run benchmark on dataset</strong> in this tab.
                Note: <strong>Analysis</strong> mode does not generate comparison charts.
            </div>
            """
        )
        _html("</section>")
        return

    st.caption(f"Latest run: {run_id} | Path: {run_dir}")

    if leaderboard_rows:
        st.markdown("#### Leaderboard")

        safe_rows = []
        for row in leaderboard_rows:
            safe_row = {}
            for key, value in row.items():
                safe_row[key] = None if value == "" else value
            safe_rows.append(safe_row)

        st.dataframe(safe_rows, width='stretch', hide_index=True)

        render_model_comparison_charts(
            leaderboard_rows=leaderboard_rows,
            detailed_rows=detailed_rows,
        )
    else:
        _html("<div class='soft-box'>Leaderboard CSV is empty.</div>")

    if plot_paths:
        st.markdown("#### Saved benchmark image charts")
        for plot_path in plot_paths:
            _render_saved_chart_preview(plot_path)
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
            <div class="section-title">Original Tongue Twister</div>
            <p class="section-subtitle">Source: {source_name}</p>
            <p class="section-subtitle">Title: {title}</p>
            <div class="reference-grid">
                <article class="reference-card">
                    <span>Russian original</span>
                    <div class="ref-text">{original}</div>
                </article>
                <article class="reference-card">
                    <span>Polish translation</span>
                    <div class="ref-text">{polish}</div>
                </article>
            </div>
        </section>
        """
    )


def render_audio_panel(audio_file: Any) -> None:
    _html(
        """
        <section class="section-panel center-stage audio-focus">
            <div class="section-title">Audio and Waveform</div>
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
            <div class="section-title">Processing Flow</div>
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


def _render_word_stream(result: dict[str, Any]| None) -> None:
    _html("<div class='result-title'>Recognized Russian words</div>")
    
    if result is None:
        _html("<div class='soft-box'>Waiting for analysis result.</div>")
        return
    
    words = result.get("segments", [])
    if not words:
        _html("<div class='soft-box'>No word segments found.</div>")
        return
    
    per_row = 4
    for start in range(0, len(words), per_row):
        row_items = words[start : start + per_row]
        columns = st.columns(len(row_items), gap="small")
        for offset, (column, segment) in enumerate(zip(columns, row_items, strict=False), start=1):
            order = start + offset

            raw_confidence = segment.get("confidence")
            if raw_confidence is None:
                raw_confidence = 0.5

            confidence_percent = int(raw_confidence * 100)

            with column:
                st.markdown(f"**{order:02d}. {segment['word']}**")
                st.progress(float(raw_confidence))
                st.caption(f"confidence: {confidence_percent}%")


def _render_transcript_block(result: dict[str, Any]| None) -> None:
    _html("<div class='subsection-title'>Transcript</div>")
    if result is None:
        st.text_area("Transcript (ASR)", value="", height=118, disabled=True)
        return
    
    transcript = result.get("recognized_text", "")
    st.text_area(
        "Transcript (ASR)",
        value=transcript,
        height=118,
        disabled=(result is None),
    )


def _render_translation_block(result: dict[str, Any] | None) -> None:
    _html("<div class='subsection-title'>Polish output</div>")

    if result is None:
        st.text_area("Polish translation", value="", height=90, disabled=True)
        return
    
    source = str(result.get("translation_source", "")).strip()
    if source == "reference_catalog":
        st.caption("Source: reference catalog translation")
    elif source == "recognized_text_match":
        st.caption("Source: matched by recognized Russian text")
    elif source == "model_translation":
        st.caption("Source: RU->PL translation model")
    elif source == "translation_model_unavailable":
        st.caption("Source: translation model unavailable")
    elif source == "missing_translation":
        st.caption("Source: no translation could be generated")
    elif source:
        st.caption(f"Source: {source}")

    translation_text = result.get("translation", "")

    if source == "translation_model_unavailable":
        _html(
            "<div class='soft-box'>Translation model unavailable. Install `transformers`, `torch`, and "
            "`sentencepiece`, then run analysis again.</div>"
        )
    if not translation_text.strip():
        _html("<div class='soft-box'>No Polish translation available for this recording yet.</div>")

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
    chips = "".join(
        (
            "<span style=\"display:inline-block;margin:0 0.35rem 0.35rem 0;padding:0.24rem 0.7rem;"
            "border-radius:999px;background:rgba(255,20,147,0.10);border:1px solid rgba(255,20,147,0.22);"
            "color:#ffe8f7;font-size:0.9rem;font-weight:600;line-height:1.2;\">"
            f"{escape(token)}"
            "</span>"
        )
        for token in tokens
    )
    _html(f"<div style='margin-top:0.35rem; line-height:1.8;'>{chips}</div>")


def _render_saved_chart_preview(plot_path: Path) -> None:
    image_bytes = plot_path.read_bytes()
    encoded = base64.b64encode(image_bytes).decode("ascii")
    image_url = f"data:image/png;base64,{encoded}"
    caption = escape(plot_path.name)

    _html(
        f"""
        <div class="chart-preview-card">
            <a class="chart-preview-link" href="{image_url}" target="_blank">
                <img src="{image_url}" alt="{caption}" class="chart-preview-image" />
            </a>
            <div class="chart-preview-caption">{caption}</div>
            <div class="chart-preview-hint">Click to open full-size chart</div>
        </div>
        """
    )
