"""Yahoo Finance API access layer for the Stock Market Analysis System."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd
import yfinance as yf


class StockAPIError(Exception):
    """Raised when stock data cannot be fetched or is not available."""


@dataclass(frozen=True)
class StockInfo:
    """Small, UI-friendly representation of current stock information."""

    symbol: str
    company_name: str
    currency: str
    exchange: str
    current_price: float | None
    previous_close: float | None
    open_price: float | None
    day_high: float | None
    day_low: float | None
    market_cap: int | None
    volume: int | None


def _safe_get(info: dict[str, Any], *keys: str) -> Any:
    """Return the first non-empty value found in a Yahoo Finance info dictionary."""
    for key in keys:
        value = info.get(key)
        if value not in (None, "", "N/A"):
            return value
    return None


def get_stock_ticker(symbol: str) -> yf.Ticker:
    """Create a yfinance Ticker object for a validated stock symbol."""
    return yf.Ticker(symbol)


def fetch_stock_info(symbol: str) -> StockInfo:
    """
    Fetch current stock information from Yahoo Finance.

    The yfinance `.info` endpoint can occasionally return partial data, so this
    function uses safe lookups and raises a clear error when the symbol appears
    invalid or no meaningful company data is returned.
    """
    try:
        ticker = get_stock_ticker(symbol)
        info = ticker.info
    except Exception as exc:
        raise StockAPIError(f"Could not fetch stock information for {symbol}.") from exc

    company_name = _safe_get(info, "longName", "shortName")
    current_price = _safe_get(info, "currentPrice", "regularMarketPrice")
    previous_close = _safe_get(info, "previousClose", "regularMarketPreviousClose")

    if not company_name and current_price is None and previous_close is None:
        raise StockAPIError(f"No stock information found for symbol '{symbol}'.")

    return StockInfo(
        symbol=symbol,
        company_name=company_name or symbol,
        currency=_safe_get(info, "currency", "financialCurrency") or "N/A",
        exchange=_safe_get(info, "exchange", "fullExchangeName") or "N/A",
        current_price=current_price,
        previous_close=previous_close,
        open_price=_safe_get(info, "open", "regularMarketOpen"),
        day_high=_safe_get(info, "dayHigh", "regularMarketDayHigh"),
        day_low=_safe_get(info, "dayLow", "regularMarketDayLow"),
        market_cap=_safe_get(info, "marketCap"),
        volume=_safe_get(info, "volume", "regularMarketVolume"),
    )


def fetch_historical_data(symbol: str, period: str = "1mo", interval: str = "1d") -> pd.DataFrame:
    """
    Fetch historical OHLCV stock data.

    Args:
        symbol: Validated stock ticker symbol.
        period: Yahoo Finance period such as 7d, 1mo, 3mo, or 1y.
        interval: Data interval. Daily data is used by default.
    """
    try:
        ticker = get_stock_ticker(symbol)
        historical_data = ticker.history(period=period, interval=interval, auto_adjust=False)
    except Exception as exc:
        raise StockAPIError(f"Could not fetch historical data for {symbol}.") from exc

    if historical_data.empty:
        raise StockAPIError(
            f"No historical data found for '{symbol}'. Please check the symbol and try again."
        )

    historical_data = historical_data.reset_index()
    return historical_data
