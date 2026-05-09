"""Data processing utilities for stock market data."""

from __future__ import annotations

import pandas as pd


DISPLAY_COLUMNS = ["Date", "Open", "High", "Low", "Close", "Volume"]


def prepare_historical_data(data: pd.DataFrame) -> pd.DataFrame:
    """
    Clean raw yfinance historical data for display and charting.

    yfinance may return either Date or Datetime depending on interval and asset
    type. This function standardizes the date column and keeps the core OHLCV
    fields used by the app.
    """
    if data.empty:
        return data

    processed_data = data.copy()

    if "Datetime" in processed_data.columns and "Date" not in processed_data.columns:
        processed_data = processed_data.rename(columns={"Datetime": "Date"})

    if "Date" in processed_data.columns:
        processed_data["Date"] = pd.to_datetime(processed_data["Date"]).dt.tz_localize(None)

    existing_columns = [column for column in DISPLAY_COLUMNS if column in processed_data.columns]
    processed_data = processed_data[existing_columns]

    numeric_columns = ["Open", "High", "Low", "Close", "Volume"]
    for column in numeric_columns:
        if column in processed_data.columns:
            processed_data[column] = pd.to_numeric(processed_data[column], errors="coerce")

    processed_data = processed_data.dropna(subset=["Close"])
    return processed_data


def add_moving_average(data: pd.DataFrame, window: int = 20) -> pd.DataFrame:
    """Add a moving average column based on closing prices."""
    if data.empty or "Close" not in data.columns:
        return data

    processed_data = data.copy()
    moving_average_column = f"MA_{window}"
    processed_data[moving_average_column] = (
        processed_data["Close"].rolling(window=window, min_periods=1).mean()
    )
    return processed_data


def calculate_price_change(data: pd.DataFrame) -> tuple[float | None, float | None]:
    """
    Calculate absolute and percentage price change over the selected period.

    Returns:
        A tuple of (price_change, percentage_change). Values are None when there
        is not enough data to calculate a reliable change.
    """
    if data.empty or "Close" not in data.columns or len(data) < 2:
        return None, None

    first_close = float(data["Close"].iloc[0])
    latest_close = float(data["Close"].iloc[-1])

    if first_close == 0:
        return latest_close - first_close, None

    price_change = latest_close - first_close
    percentage_change = (price_change / first_close) * 100
    return price_change, percentage_change


def format_large_number(value: int | float | None) -> str:
    """Format large financial numbers for a clean UI display."""
    if value is None:
        return "N/A"

    if value >= 1_000_000_000_000:
        return f"{value / 1_000_000_000_000:.2f}T"
    if value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.2f}B"
    if value >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    if value >= 1_000:
        return f"{value / 1_000:.2f}K"

    return f"{value:,.0f}"


def format_currency(value: int | float | None, currency: str = "USD") -> str:
    """Format a currency value while safely handling missing values."""
    if value is None:
        return "N/A"

    return f"{value:,.2f} {currency}"
