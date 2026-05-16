import numpy as np
import pandas as pd


def compute_portfolio_returns(returns_df, weights):
    """
    Compute weighted portfolio returns.
    """

    if returns_df is None or returns_df.empty:
        raise ValueError("Returns dataframe is empty")

    if not weights:
        raise ValueError("Weights dictionary is empty")

    # align weights to dataframe columns
    w = np.array([
        weights.get(col.replace("_return", ""), 0)
        for col in returns_df.columns
    ])

    if w.sum() == 0:
        raise ValueError("Weights sum to zero")

    # normalize
    w = w / w.sum()

    return returns_df.dot(w)


def compute_volatility(portfolio_returns):
    """
    Annualized volatility.
    """
    if len(portfolio_returns) == 0:
        raise ValueError("Portfolio returns empty")

    daily_vol = portfolio_returns.std()
    return daily_vol * np.sqrt(252)


def compute_sharpe(portfolio_returns, risk_free_rate=0):
    """
    Annualized Sharpe ratio.
    """
    if len(portfolio_returns) == 0:
        raise ValueError("Portfolio returns empty")

    excess_return = portfolio_returns.mean() * 252 - risk_free_rate
    volatility = portfolio_returns.std() * np.sqrt(252)

    if volatility == 0:
        return 0

    return excess_return / volatility


def compute_beta(portfolio_returns, market_returns):
    combined = pd.concat(
        [portfolio_returns, market_returns],
        axis=1
    ).dropna()

    if combined.empty:
        return 0

    cov = np.cov(
        combined.iloc[:, 0],
        combined.iloc[:, 1]
    )[0][1]

    market_var = np.var(combined.iloc[:, 1])

    if market_var == 0:
        return 0

    return cov / market_var