"""Chart-building functions for the Streamlit stock dashboard."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go


def create_price_trend_chart(
    data: pd.DataFrame,
    symbol: str,
    moving_average_window: int | None = None,
) -> go.Figure:
    """
    Create a responsive line chart for closing prices and optional moving average.
    """
    figure = go.Figure()

    figure.add_trace(
        go.Scatter(
            x=data["Date"],
            y=data["Close"],
            mode="lines",
            name="Close Price",
            line=dict(width=3, color="#2563eb"),
        )
    )

    if moving_average_window:
        moving_average_column = f"MA_{moving_average_window}"
        if moving_average_column in data.columns:
            figure.add_trace(
                go.Scatter(
                    x=data["Date"],
                    y=data[moving_average_column],
                    mode="lines",
                    name=f"{moving_average_window}-Day Moving Average",
                    line=dict(width=2, color="#f97316", dash="dash"),
                )
            )

    figure.update_layout(
        title=f"{symbol} Stock Price Trend",
        xaxis_title="Date",
        yaxis_title="Price",
        hovermode="x unified",
        template="plotly_white",
        margin=dict(l=20, r=20, t=60, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    return figure


def create_volume_chart(data: pd.DataFrame, symbol: str) -> go.Figure:
    """Create a bar chart showing trading volume over time."""
    figure = go.Figure()

    figure.add_trace(
        go.Bar(
            x=data["Date"],
            y=data["Volume"],
            name="Volume",
            marker_color="#10b981",
        )
    )

    figure.update_layout(
        title=f"{symbol} Trading Volume",
        xaxis_title="Date",
        yaxis_title="Volume",
        template="plotly_white",
        margin=dict(l=20, r=20, t=60, b=20),
    )

    return figure
