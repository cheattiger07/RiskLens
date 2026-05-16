import yfinance as yf
import pandas as pd
import logging


def normalize_tickers(tickers):
    normalized = []

    for t in tickers:
        t = t.upper().strip()

        # don't modify index symbols
        if t.startswith("^"):
            normalized.append(t)
            continue

        # if no exchange suffix, assume NSE
        if "." not in t:
            t = t + ".NS"

        normalized.append(t)

    return normalized

def fetch_price_data(tickers, start="2020-01-01"):
    """
    Fetch adjusted close prices safely.
    Raises clean exceptions for invalid tickers.
    """

    if not tickers:
        raise ValueError("No tickers provided")

    if isinstance(tickers, str):
        tickers = [tickers]
    tickers = normalize_tickers(tickers)
    logging.info(f"Normalized tickers: {tickers}")

    try:
        data = yf.download(
            tickers,
            start=start,
            progress=False,
            auto_adjust=False
        )

        if data.empty:
            raise ValueError(
                "No market data returned. Check ticker symbols."
            )

        # prefer Adj Close
        if "Adj Close" in data.columns:
            prices = data["Adj Close"]
        elif "Close" in data.columns:
            prices = data["Close"]
        else:
            raise ValueError("Price columns missing from market data")

        # single ticker case
        if isinstance(prices, pd.Series):
            prices = prices.to_frame()

        prices.dropna(how="all", inplace=True)

        # detect invalid tickers
        valid_cols = prices.columns.tolist()
        invalid = [t for t in tickers if t not in valid_cols]

        if invalid:
            raise ValueError(
                f"Invalid ticker(s): {', '.join(invalid)}"
            )

        if prices.empty:
            raise ValueError(
                "Downloaded prices are empty after cleaning"
            )

        return prices

    except Exception as e:
        logging.exception(e)
        raise