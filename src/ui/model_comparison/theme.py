from __future__ import annotations

from typing import Any

PINK_PRIMARY = "#FF1493"
PINK_SECONDARY = "#FF4DB5"
PINK_LIGHT = "#FFD8EE"
PINK_MUTED = "#A63A78"

BG_CARD = "rgba(10, 10, 10, 0.95)"
BG_PLOT = "rgba(0, 0, 0, 0)"
GRID = "rgba(255, 20, 147, 0.2)"
TEXT = "#FFF3FB"

MODEL_COLORS = [
    "#FF1493",
    "#FF66C4",
    "#FF9FDB",
    "#FF3FAE",
    "#E61E91",
    "#FF85CF",
    "#FFB6E5",
]


def apply_dark_pink_theme(fig: Any, *, title: str, height: int = 430) -> Any:
    fig.update_layout(
        title=dict(text=title, font=dict(size=16, color=TEXT)),
        height=height,
        paper_bgcolor=BG_CARD,
        plot_bgcolor=BG_PLOT,
        font=dict(family="Quicksand, Segoe UI, sans-serif", color=TEXT),
        margin=dict(l=58, r=34, t=62, b=86),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor=GRID,
            borderwidth=1,
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0.01,
            font=dict(size=11, color=TEXT),
        ),
        hoverlabel=dict(
            bgcolor="rgba(25, 2, 16, 0.95)",
            bordercolor=PINK_PRIMARY,
            font=dict(color=TEXT),
        ),
    )
    fig.update_xaxes(
        showgrid=False, 
        zeroline=False, 
        linecolor=GRID, 
        tickfont=dict(color=TEXT, size=11), 
        automargin=False,
        tickangle=-45
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor=GRID,
        zeroline=False,
        linecolor=GRID,
        tickfont=dict(color=TEXT, size=11),
        automargin=False,
    )
    return fig
