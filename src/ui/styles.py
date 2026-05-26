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
            /* Import two fonts: Montserrat for headings, Quicksand for body text */
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@700;800&family=Quicksand:wght@400;500;600;700&display=swap');

            :root {
                --bg-0: #020202;
                --bg-1: #090909;
                --bg-2: #101010;
                --pink: #ff1493;
                --white: #ffffff;
                --text-base: #e0e2ed;       /* Soft light-gray for base text */
                --text-muted: #a1a8b8;      /* Muted color for secondary subtitles */
                --line: rgba(255, 20, 147, 0.34);
                --line-soft: rgba(255, 20, 147, 0.16);
            }

            /* STREAMLIT HEADER: Make the default top header completely transparent */
            [data-testid="stHeader"] {
                background-color: transparent !important;
            }

            /* 1. BASE TEXT ( font-family: Quicksand ) */
            html, body, [class*="css"], [data-testid="stAppViewContainer"], p, span {
                font-family: 'Quicksand', 'Segoe UI', sans-serif;
                color: var(--text-base);
                font-size: 0.98rem;
                line-height: 1.5;
            }

            .stApp {
                background:
                    radial-gradient(900px 450px at 8% -8%, rgba(255, 20, 147, 0.24), transparent 64%),
                    radial-gradient(720px 420px at 100% 0%, rgba(255, 20, 147, 0.18), transparent 62%),
                    linear-gradient(165deg, var(--bg-0) 0%, var(--bg-1) 45%, var(--bg-2) 100%);
                color: var(--text-base);
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
                padding: 0.8rem 1.5rem;
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

            /* 2. MAIN HEADERS AND TITLES ( font-family: Montserrat ) */
            .hero-title {
                font-family: 'Montserrat', sans-serif;
                margin: 0.5rem 0 0.2rem 0;
                font-size: clamp(2.8rem, 4.5vw, 4rem);
                font-weight: 800;
                line-height: 1.1;
                color: var(--white);
                letter-spacing: -0.02em;
            }

            .section-title {
                font-family: 'Montserrat', sans-serif;
                margin: 0;
                font-size: 2.1rem;
                font-weight: 700;
                color: var(--white);
                letter-spacing: -0.01em;
            }

            .result-title {
                font-family: 'Montserrat', sans-serif;
                margin: 1.2rem 0 0.6rem 0;
                font-size: 1.15rem;
                color: #ffe6f5;
                font-weight: 700;
            }

            .section-subtitle {
                margin: 0.3rem 0 0.8rem 0;
                color: var(--text-muted);
                font-size: 0.92rem;
            }

            /* 3. IMPORTANT TEXT AND ACCENTS */
            strong {
                color: #ff52be !important; /* Highlights bold text with neon pink */
                font-weight: 700;
            }

            .bubble-title {
                font-family: 'Montserrat', sans-serif;
                margin-top: 0.72rem;
                font-size: 1.05rem;
                color: var(--white);
                font-weight: 700;
                letter-spacing: 0.01em;
                white-space: nowrap;
            }

            .bubble-detail {
                margin-top: 0.3rem;
                font-size: 0.85rem;
                color: var(--text-muted);
                line-height: 1.3;
            }

            .reference-card h3 {
                font-family: 'Quicksand', sans-serif;
                margin: 0;
                font-size: 1rem;
                line-height: 1.4;
                color: var(--white);
                font-weight: 500;
            }

            /* REMAINING UI COMPONENTS */
            .section-panel {
                border: 1px solid var(--line-soft);
                border-radius: 26px;
                padding: 0.8rem 1.2rem 1rem 1.2rem;
                background: linear-gradient(170deg, rgba(13, 13, 13, 0.95), rgba(7, 7, 7, 0.9));
                box-shadow: inset 0 0 0 1px rgba(255, 20, 147, 0.06), 0 14px 32px rgba(0, 0, 0, 0.35);
                margin-bottom: 0.95rem;
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

            div[data-testid="stAlert"] {
                background: rgba(255, 20, 147, 0.08) !important;
                border: 1px dashed rgba(255, 20, 147, 0.45) !important;
                border-radius: 16px !important;
                color: var(--white) !important;
            }
            
            div[data-testid="stAlert"] svg {
                fill: #ff52be !important;
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
                font-size: 0.88rem;
                text-transform: uppercase;
                letter-spacing: 0.08em;
                color: #ffcbe9;
                margin-bottom: 0.35rem;
                font-weight: 700;
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
            }

            div[data-baseweb="file-uploader"] > section,
            div[data-testid="stFileUploaderDropzone"] {
                border-radius: 20px;
                border: 1px dashed rgba(255, 20, 147, 0.62);
                background: rgba(255, 20, 147, 0.08);
            }

            div[data-testid="stTextArea"] textarea {
                background: rgba(255, 255, 255, 0.03);
                border: 1px solid rgba(255, 20, 147, 0.4);
                color: var(--white);
                border-radius: 16px;
            }

            div[data-testid="stProgressBar"] > div > div > div {
                background: linear-gradient(90deg, #ff1493, #ff6fc9) !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )