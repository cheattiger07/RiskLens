def compute_returns(price_df):
    if price_df.empty:
        raise ValueError("Price data is empty")

    returns = price_df.pct_change().dropna()

    if returns.empty:
        raise ValueError("Could not compute returns")

    returns.columns = [
        f"{col}_return" for col in returns.columns
    ]

    return returns