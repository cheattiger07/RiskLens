import re


def validate_portfolio(df, schema):
    issues = []

    # -----------------------------
    # required columns
    # -----------------------------
    if "ticker" not in schema:
        issues.append("Missing ticker column")

    if "weight" not in schema and "shares" not in schema:
        issues.append("Need either weight or shares")

    if issues:
        return issues

    ticker_col = schema["ticker"]
    qty_col = schema.get("weight") or schema.get("shares")

    # -----------------------------
    # empty file
    # -----------------------------
    if df.empty:
        issues.append("CSV is empty")

    # -----------------------------
    # too many rows
    # -----------------------------
    if len(df) > 500:
        issues.append("Too many rows (max 500 allowed)")

    # -----------------------------
    # missing values
    # -----------------------------
    if df[[ticker_col, qty_col]].isnull().any().any():
        issues.append("Missing values detected")

    # -----------------------------
    # duplicate rows
    # -----------------------------
    if df.duplicated().sum() > 0:
        issues.append("Duplicate rows found")

    # -----------------------------
    # duplicate tickers
    # -----------------------------
    if df[ticker_col].duplicated().sum() > 0:
        issues.append("Duplicate tickers found")

    # -----------------------------
    # numeric quantity
    # -----------------------------
    try:
        df[qty_col] = df[qty_col].astype(float)
    except:
        issues.append("Non-numeric quantities found")
        return issues

    # -----------------------------
    # negative / zero
    # -----------------------------
    if (df[qty_col] < 0).any():
        issues.append("Negative quantities found")

    if (df[qty_col] == 0).any():
        issues.append("Zero quantities found")

    # -----------------------------
    # ticker format
    # allow:
    # AAPL
    # RELIANCE.NS
    # BRK-B
    # -----------------------------
    bad_tickers = []

    pattern = r"^[A-Za-z0-9.\-]+$"

    for t in df[ticker_col]:
        if not re.match(pattern, str(t)):
            bad_tickers.append(t)

    if bad_tickers:
        issues.append(
            f"Invalid ticker names: {', '.join(map(str,bad_tickers[:5]))}"
        )

    return issues