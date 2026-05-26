from __future__ import annotations

import streamlit as st


def configure_page() -> None:
    st.set_page_config(
        page_title="ASR Bubble Studio",
        page_icon=":microphone:",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def inject_styles() -> None:
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@400;500;600;700&display=swap');

            :root {
                --bg-0: #020202;
                --bg-1: #090909;
                --bg-2: #101010;
                --pink: #ff1493;
                --white: #ffffff;
                --line: rgba(255, 20, 147, 0.34);
                --line-soft: rgba(255, 20, 147, 0.16);
            }

            html, body, [class*="css"], [data-testid="stAppViewContainer"] {
                font-family: 'Quicksand', 'Segoe UI', sans-serif;
            }

            .stApp {
                background:
                    radial-gradient(900px 450px at 8% -8%, rgba(255, 20, 147, 0.24), transparent 64%),
                    radial-gradient(720px 420px at 100% 0%, rgba(255, 20, 147, 0.18), transparent 62%),
                    linear-gradient(165deg, var(--bg-0) 0%, var(--bg-1) 45%, var(--bg-2) 100%);
                color: var(--white);
            }

            .block-container {
                max-width: 1480px;
                padding-top: 1.2rem;
                padding-bottom: 2rem;
            }

            section[data-testid="stSidebar"] {
                background: rgba(6, 6, 6, 0.96);
                border-right: 1px solid var(--line);
            }

            section[data-testid="stSidebar"] * {
                color: var(--white);
            }

            .app-hero {
                border: 1px solid var(--line);
                border-radius: 30px;
                padding: 1.45rem 1.7rem 1.25rem 1.7rem;
                background: linear-gradient(160deg, rgba(15, 15, 15, 0.95), rgba(8, 8, 8, 0.9));
                box-shadow: 0 24px 44px rgba(255, 20, 147, 0.12), 0 10px 26px rgba(0, 0, 0, 0.55);
                margin-bottom: 1rem;
            }

            .eyebrow {
                display: inline-flex;
                align-items: center;
                gap: 0.4rem;
                padding: 0.35rem 0.8rem;
                border-radius: 999px;
                border: 1px solid rgba(255, 20, 147, 0.52);
                background: rgba(255, 20, 147, 0.16);
                color: #ffd6ef;
                font-size: 0.78rem;
                font-weight: 700;
                letter-spacing: 0.07em;
                text-transform: uppercase;
            }

            .hero-title {
                margin: 0.85rem 0 0.2rem 0;
                font-size: clamp(1.85rem, 2.7vw, 2.95rem);
                line-height: 1.1;
                color: var(--white);
            }

            .section-panel {
                border: 1px solid var(--line-soft);
                border-radius: 26px;
                padding: 1.05rem 1.05rem 1rem 1.05rem;
                background: linear-gradient(170deg, rgba(13, 13, 13, 0.95), rgba(7, 7, 7, 0.9));
                box-shadow: inset 0 0 0 1px rgba(255, 20, 147, 0.06), 0 14px 32px rgba(0, 0, 0, 0.35);
                margin-bottom: 0.95rem;
            }

            .center-stage {
                width: 100%;
                margin-left: auto;
                margin-right: auto;
            }

            .audio-focus {
                padding: 1.25rem 1.15rem 1.1rem 1.15rem;
            }

            .section-title {
                margin: 0;
                font-size: 1.52rem;
                font-weight: 700;
                color: var(--white);
            }

            .section-subtitle {
                margin: 0.22rem 0 0.8rem 0;
                color: #ffd8ef;
                font-size: 0.9rem;
            }

            .soft-box {
                border: 1px dashed rgba(255, 20, 147, 0.45);
                border-radius: 20px;
                padding: 0.92rem 1rem;
                background: rgba(255, 20, 147, 0.08);
                color: #fff0fa;
                font-size: 0.95rem;
                margin-bottom: 0.8rem;
            }

            .reference-grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 0.72rem;
                margin-top: 0.35rem;
            }

            .reference-card {
                border: 1px solid rgba(255, 20, 147, 0.3);
                border-radius: 18px;
                background: rgba(255, 20, 147, 0.11);
                padding: 0.8rem 0.85rem;
            }

            .reference-card span {
                display: block;
                font-size: 0.76rem;
                text-transform: uppercase;
                letter-spacing: 0.08em;
                color: #ffcbe9;
                margin-bottom: 0.35rem;
                font-weight: 700;
            }

            .reference-card h3 {
                margin: 0;
                font-size: 1.03rem;
                line-height: 1.35;
                color: #ffffff;
                font-weight: 600;
            }

            .bubble-step {
                border-radius: 22px;
                padding: 0.75rem 0.7rem;
                border: 1px solid rgba(255, 20, 147, 0.25);
                background: rgba(255, 255, 255, 0.02);
                min-height: 130px;
            }

            .bubble-step.done {
                border-color: rgba(255, 20, 147, 0.72);
                background: linear-gradient(165deg, rgba(255, 20, 147, 0.26), rgba(255, 20, 147, 0.08));
                box-shadow: 0 8px 20px rgba(255, 20, 147, 0.2);
            }

            .bubble-step.active {
                border-color: rgba(255, 20, 147, 0.95);
                background: linear-gradient(165deg, rgba(255, 20, 147, 0.34), rgba(255, 20, 147, 0.1));
                box-shadow: 0 10px 26px rgba(255, 20, 147, 0.24);
            }

            .bubble-top {
                display: flex;
                justify-content: space-between;
                align-items: center;
            }

            .bubble-icon {
                font-size: 1.35rem;
                line-height: 1;
            }

            .bubble-index {
                border-radius: 999px;
                min-width: 30px;
                text-align: center;
                padding: 0.18rem 0.45rem;
                border: 1px solid rgba(255, 20, 147, 0.72);
                font-size: 0.8rem;
                font-weight: 700;
                color: #ffe7f7;
                background: rgba(255, 20, 147, 0.22);
            }

            .bubble-title {
                margin-top: 0.72rem;
                font-size: 1.02rem;
                color: var(--white);
                font-weight: 700;
                letter-spacing: 0.01em;
            }

            .bubble-detail {
                margin-top: 0.3rem;
                font-size: 0.88rem;
                color: #ffd5ec;
                line-height: 1.3;
            }

            .result-title {
                margin: 0.85rem 0 0.5rem 0;
                font-size: 1.08rem;
                color: #ffe6f5;
                font-weight: 700;
            }

            .word-stream {
                display: flex;
                flex-wrap: wrap;
                gap: 0.5rem;
                margin: 0.2rem 0 0.35rem 0;
            }

            .word-pill {
                display: inline-flex;
                align-items: center;
                gap: 0.36rem;
                border-radius: 999px;
                border: 1px solid rgba(255, 20, 147, 0.44);
                background: rgba(255, 20, 147, 0.16);
                color: var(--white);
                font-size: 0.92rem;
                padding: 0.35rem 0.7rem;
                font-weight: 600;
            }

            .word-pill small {
                color: #ffd4ec;
                font-size: 0.74rem;
                font-weight: 700;
            }

            .helper-list {
                margin: 0.45rem 0 0 0;
                padding-left: 1.1rem;
                color: #ffe8f6;
            }

            .helper-list li {
                margin-bottom: 0.35rem;
            }

            .stAudio {
                margin-top: 0.6rem;
                margin-bottom: 0.85rem;
            }

            div[data-testid="stAudio"] audio {
                width: 100%;
            }

            .wave-shell {
                border: 1px solid rgba(255, 20, 147, 0.34);
                border-radius: 18px;
                background: rgba(255, 20, 147, 0.08);
                padding: 0.6rem 0.75rem 0.85rem 0.75rem;
                margin-top: 0.2rem;
            }

            .wave-label {
                font-size: 0.78rem;
                color: #ffd5ec;
                text-transform: uppercase;
                letter-spacing: 0.08em;
                font-weight: 700;
                margin-bottom: 0.44rem;
            }

            .wave-track {
                height: 148px;
                border-radius: 14px;
                background: rgba(7, 7, 7, 0.9);
                border: 1px solid rgba(255, 20, 147, 0.26);
                display: flex;
                align-items: flex-end;
                justify-content: space-between;
                gap: 2px;
                padding: 0.65rem 0.5rem;
                overflow: hidden;
            }

            .wave-bar {
                width: 100%;
                border-radius: 999px;
                background: linear-gradient(180deg, #ffd7ee 0%, #ff1493 58%, #ff1493 100%);
                opacity: 0.95;
                box-shadow: 0 0 12px rgba(255, 20, 147, 0.33);
            }

            .stButton > button {
                border-radius: 999px;
                border: 1px solid rgba(255, 20, 147, 0.6);
                background: linear-gradient(140deg, #ff1493, #ff52be);
                color: var(--white);
                font-weight: 700;
                font-size: 0.98rem;
                min-height: 2.85rem;
                box-shadow: 0 10px 24px rgba(255, 20, 147, 0.28);
                transition: transform 0.2s ease, box-shadow 0.2s ease;
            }

            .stButton > button[kind="secondary"] {
                background: linear-gradient(155deg, rgba(255, 20, 147, 0.5), rgba(255, 20, 147, 0.26));
            }

            .stButton > button:hover {
                transform: translateY(-1px);
                box-shadow: 0 14px 28px rgba(255, 20, 147, 0.35);
                border-color: rgba(255, 20, 147, 0.9);
            }

            .stButton > button:focus {
                outline: none;
                box-shadow: 0 0 0 0.14rem rgba(255, 20, 147, 0.45);
            }

            div[data-baseweb="file-uploader"] > section,
            div[data-testid="stFileUploaderDropzone"] {
                border-radius: 20px;
                border: 1px dashed rgba(255, 20, 147, 0.62);
                background: rgba(255, 20, 147, 0.08);
            }

            div[data-baseweb="file-uploader"] > section > button {
                border-radius: 999px;
            }

            div[data-testid="stTextArea"] textarea {
                background: rgba(255, 255, 255, 0.03);
                border: 1px solid rgba(255, 20, 147, 0.4);
                color: var(--white);
                border-radius: 16px;
            }

            div[data-testid="stTextArea"] textarea:focus {
                border-color: rgba(255, 20, 147, 0.88);
                box-shadow: 0 0 0 0.13rem rgba(255, 20, 147, 0.35);
            }

            div[data-testid="stProgressBar"] > div > div > div {
                background: linear-gradient(90deg, #ff1493, #ff6fc9) !important;
            }

            div[data-testid="stPlotlyChart"] > div {
                border: 1px solid rgba(255, 20, 147, 0.28);
                border-radius: 18px;
                overflow: hidden;
                box-shadow: inset 0 0 0 1px rgba(255, 20, 147, 0.08);
            }

            div[data-testid="stMetric"] {
                border: 1px solid rgba(255, 20, 147, 0.3);
                border-radius: 16px;
                background: rgba(255, 20, 147, 0.1);
                padding: 0.28rem 0.44rem;
            }

            .chart-preview-card {
                border: 1px solid rgba(255, 20, 147, 0.28);
                border-radius: 18px;
                background: rgba(255, 20, 147, 0.06);
                padding: 0.72rem;
                margin: 0.6rem 0 0.95rem 0;
            }

            .chart-preview-link {
                display: block;
                text-decoration: none;
            }

            .chart-preview-image {
                display: block;
                width: 100%;
                height: auto;
                border-radius: 14px;
                border: 1px solid rgba(255, 20, 147, 0.28);
                transition: transform 0.16s ease, box-shadow 0.16s ease;
            }

            .chart-preview-image:hover {
                transform: translateY(-1px) scale(1.01);
                box-shadow: 0 10px 26px rgba(255, 20, 147, 0.26);
            }

            .chart-preview-caption {
                margin-top: 0.48rem;
                color: #ffeaf7;
                font-weight: 700;
                font-size: 0.92rem;
            }

            .chart-preview-hint {
                margin-top: 0.16rem;
                color: #ffc8e9;
                font-size: 0.8rem;
            }

            div[data-testid="stRadio"] label {
                color: #ffe3f4;
            }

            @media (max-width: 1100px) {
                .reference-grid {
                    grid-template-columns: 1fr;
                }
            }

            @media (max-width: 1000px) {
                .section-panel {
                    border-radius: 22px;
                }

                .app-hero {
                    border-radius: 24px;
                    padding: 1.25rem 1.1rem 1.1rem 1.1rem;
                }

                .wave-track {
                    height: 130px;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
