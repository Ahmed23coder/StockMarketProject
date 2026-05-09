"""Streamlit application for the Stock Market Analysis System."""

from __future__ import annotations

import streamlit as st

from backend.data_processing import (
    add_moving_average,
    calculate_price_change,
    format_currency,
    format_large_number,
    prepare_historical_data,
)
from backend.stock_api import StockAPIError, fetch_historical_data, fetch_stock_info
from backend.validation import (
    POPULAR_SYMBOLS,
    VALID_PERIODS,
    ValidationError,
    format_symbol_option,
    get_symbol_suggestions,
    normalize_stock_symbol,
    validate_moving_average_window,
    validate_period,
)
from charts.charts import create_price_trend_chart, create_volume_chart


st.set_page_config(
    page_title="Stock Market Analysis System",
    page_icon=":chart_with_upwards_trend:",
    layout="wide",
)


@st.cache_data(ttl=300, show_spinner=False)
def load_stock_data(symbol: str, period: str, moving_average_window: int):
    """
    Load and process stock data.

    Streamlit caches the result for five minutes to reduce repeated API calls
    while still keeping the dashboard reasonably fresh.
    """
    stock_info = fetch_stock_info(symbol)
    raw_historical_data = fetch_historical_data(symbol=symbol, period=period)
    historical_data = prepare_historical_data(raw_historical_data)
    historical_data = add_moving_average(historical_data, moving_average_window)
    return stock_info, historical_data


def display_header() -> None:
    """Render the main page heading."""
    st.title("Stock Market Analysis System")
    st.caption("Backend-powered stock lookup using Yahoo Finance, pandas, and Plotly.")


def display_sidebar() -> tuple[str, str, int, bool]:
    """Render sidebar controls and return user selections."""
    st.sidebar.header("Search Settings")

    symbol_options = ["Custom symbol"] + list(POPULAR_SYMBOLS)
    selected_symbol = st.sidebar.selectbox(
        "Popular Symbols",
        options=symbol_options,
        format_func=lambda symbol: symbol
        if symbol == "Custom symbol"
        else format_symbol_option(symbol),
    )

    default_symbol = "" if selected_symbol == "Custom symbol" else selected_symbol
    symbol = st.sidebar.text_input(
        "Stock Symbol",
        value=default_symbol,
        placeholder="Example: AAPL, TSLA, MSFT, BTC-USD",
    )
    st.sidebar.caption("You can type a Yahoo Finance symbol or choose one above.")

    period = st.sidebar.selectbox(
        "Historical Period",
        options=list(VALID_PERIODS.keys()),
        format_func=lambda key: VALID_PERIODS[key],
        index=1,
    )

    moving_average_window = st.sidebar.slider(
        "Moving Average Window",
        min_value=2,
        max_value=60,
        value=20,
        step=1,
    )

    analyze_button = st.sidebar.button("Analyze Stock", type="primary", use_container_width=True)
    return symbol, period, moving_average_window, analyze_button


def display_symbol_suggestions(symbol_input: str) -> None:
    """Display helpful suggestions for common stock symbol mistakes."""
    suggestions = get_symbol_suggestions(symbol_input)
    if not suggestions:
        st.info("Try a common symbol such as AAPL, MSFT, TSLA, NVDA, BTC-USD, or ^GSPC.")
        return

    formatted_suggestions = ", ".join(
        f"{symbol} ({POPULAR_SYMBOLS.get(symbol, 'Yahoo Finance symbol')})"
        for symbol in suggestions
    )
    st.info(f"Did you mean: {formatted_suggestions}?")


def display_stock_info(stock_info, historical_data) -> None:
    """Display current stock details and period performance metrics."""
    price_change, percentage_change = calculate_price_change(historical_data)

    st.subheader(f"{stock_info.company_name} ({stock_info.symbol})")

    metric_columns = st.columns(4)
    metric_columns[0].metric(
        "Current Price",
        format_currency(stock_info.current_price, stock_info.currency),
    )
    metric_columns[1].metric(
        "Previous Close",
        format_currency(stock_info.previous_close, stock_info.currency),
    )
    metric_columns[2].metric(
        "Period Change",
        "N/A" if price_change is None else format_currency(price_change, stock_info.currency),
        None if percentage_change is None else f"{percentage_change:.2f}%",
    )
    metric_columns[3].metric("Volume", format_large_number(stock_info.volume))

    detail_columns = st.columns(4)
    detail_columns[0].info(f"Exchange: {stock_info.exchange}")
    detail_columns[1].info(f"Open: {format_currency(stock_info.open_price, stock_info.currency)}")
    detail_columns[2].info(f"Day High: {format_currency(stock_info.day_high, stock_info.currency)}")
    detail_columns[3].info(f"Market Cap: {format_large_number(stock_info.market_cap)}")


def display_charts(symbol: str, historical_data, moving_average_window: int) -> None:
    """Display price and volume charts."""
    price_chart = create_price_trend_chart(
        historical_data,
        symbol=symbol,
        moving_average_window=moving_average_window,
    )
    volume_chart = create_volume_chart(historical_data, symbol=symbol)

    st.plotly_chart(price_chart, use_container_width=True)
    st.plotly_chart(volume_chart, use_container_width=True)


def display_historical_table(historical_data) -> None:
    """Display historical data in a readable table."""
    st.subheader("Historical Stock Data")
    table_data = historical_data.sort_values("Date", ascending=False).copy()
    st.dataframe(
        table_data,
        use_container_width=True,
        hide_index=True,
    )


def main() -> None:
    """Main Streamlit application flow."""
    display_header()
    symbol_input, period_input, moving_average_window_input, analyze_button = display_sidebar()

    if not analyze_button:
        st.info("Enter a stock symbol and click Analyze Stock to begin.")
        return

    try:
        symbol = normalize_stock_symbol(symbol_input)
        period = validate_period(period_input)
        moving_average_window = validate_moving_average_window(moving_average_window_input)

        with st.spinner(f"Fetching latest data for {symbol}..."):
            stock_info, historical_data = load_stock_data(symbol, period, moving_average_window)

        display_stock_info(stock_info, historical_data)
        display_charts(symbol, historical_data, moving_average_window)
        display_historical_table(historical_data)

    except ValidationError as exc:
        st.error(str(exc))
        display_symbol_suggestions(symbol_input)
    except StockAPIError as exc:
        st.error(str(exc))
        display_symbol_suggestions(symbol_input)
    except Exception:
        st.error("An unexpected error occurred. Please try again later.")


if __name__ == "__main__":
    main()
