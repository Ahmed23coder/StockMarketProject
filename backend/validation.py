"""Input validation helpers for stock symbols and user options."""

from __future__ import annotations

from difflib import get_close_matches
import re


VALID_PERIODS = {
    "7d": "7 Days",
    "1mo": "1 Month",
    "3mo": "3 Months",
    "1y": "1 Year",
}

POPULAR_SYMBOLS = {
    "AAPL": "Apple Inc.",
    "MSFT": "Microsoft Corporation",
    "TSLA": "Tesla Inc.",
    "AMZN": "Amazon.com Inc.",
    "GOOGL": "Alphabet Inc. Class A",
    "META": "Meta Platforms Inc.",
    "NVDA": "NVIDIA Corporation",
    "NFLX": "Netflix Inc.",
    "JPM": "JPMorgan Chase & Co.",
    "V": "Visa Inc.",
    "WMT": "Walmart Inc.",
    "DIS": "Walt Disney Company",
    "KO": "Coca-Cola Company",
    "PEP": "PepsiCo Inc.",
    "BRK-B": "Berkshire Hathaway Class B",
    "^GSPC": "S&P 500 Index",
    "^DJI": "Dow Jones Industrial Average",
    "^IXIC": "Nasdaq Composite",
    "BTC-USD": "Bitcoin in US dollars",
    "ETH-USD": "Ethereum in US dollars",
}

SYMBOL_ALIASES = {
    "APPLE": "AAPL",
    "MICROSOFT": "MSFT",
    "TESLA": "TSLA",
    "AMAZON": "AMZN",
    "GOOGLE": "GOOGL",
    "ALPHABET": "GOOGL",
    "FACEBOOK": "META",
    "META": "META",
    "NVIDIA": "NVDA",
    "NETFLIX": "NFLX",
    "BITCOIN": "BTC-USD",
    "BTC": "BTC-USD",
    "ETHEREUM": "ETH-USD",
    "ETH": "ETH-USD",
    "S&P 500": "^GSPC",
    "SP500": "^GSPC",
    "DOW": "^DJI",
    "NASDAQ": "^IXIC",
}


class ValidationError(ValueError):
    """Raised when user input does not pass validation."""


def normalize_stock_symbol(symbol: str) -> str:
    """
    Clean and validate a stock symbol entered by the user.

    Yahoo Finance supports symbols such as AAPL, TSLA, BRK-B, BTC-USD,
    and index symbols such as ^GSPC. This function allows letters, numbers,
    dots, hyphens, and a leading caret while rejecting empty input and unsafe
    characters.
    """
    if symbol is None:
        raise ValidationError("Please enter a stock symbol.")

    cleaned_symbol = symbol.strip().upper()

    if not cleaned_symbol:
        raise ValidationError("Please enter a stock symbol.")

    if len(cleaned_symbol) > 15:
        raise ValidationError("Stock symbol is too long. Please enter a valid ticker symbol.")

    if cleaned_symbol in SYMBOL_ALIASES:
        return SYMBOL_ALIASES[cleaned_symbol]

    if not re.fullmatch(r"\^?[A-Z0-9.-]+", cleaned_symbol):
        raise ValidationError(
            "Invalid symbol format. Use letters, numbers, dots, hyphens, or a leading ^ only."
        )

    return cleaned_symbol


def format_symbol_option(symbol: str) -> str:
    """Format a symbol and company name for display in the UI."""
    return f"{symbol} - {POPULAR_SYMBOLS[symbol]}"


def get_symbol_suggestions(symbol: str, limit: int = 3) -> list[str]:
    """Suggest common ticker symbols when user input is close to a known option."""
    cleaned_symbol = symbol.strip().upper() if symbol else ""
    if not cleaned_symbol:
        return []

    if cleaned_symbol in SYMBOL_ALIASES:
        return [SYMBOL_ALIASES[cleaned_symbol]]

    choices = list(POPULAR_SYMBOLS) + list(SYMBOL_ALIASES)
    matches = get_close_matches(cleaned_symbol, choices, n=limit, cutoff=0.55)

    suggestions = []
    for match in matches:
        suggestion = SYMBOL_ALIASES.get(match, match)
        if suggestion not in suggestions:
            suggestions.append(suggestion)

    return suggestions


def validate_period(period: str) -> str:
    """Validate the historical data period selected by the user."""
    if period not in VALID_PERIODS:
        raise ValidationError("Invalid time period selected.")

    return period


def validate_moving_average_window(window: int) -> int:
    """Validate the moving average window used for chart calculations."""
    if window < 2:
        raise ValidationError("Moving average window must be at least 2 days.")

    if window > 200:
        raise ValidationError("Moving average window must be 200 days or less.")

    return window
