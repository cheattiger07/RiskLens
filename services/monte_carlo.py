import numpy as np
import pandas as pd


def run_monte_carlo(
    portfolio_returns,
    initial_value=100000,
    num_simulations=10000,
    days=252,
    seed=42
):
    """
    Monte Carlo portfolio simulation using normal returns.
    Returns DataFrame: rows=time, cols=simulation paths
    """

    # -------------------------
    # input validation
    # -------------------------
    if portfolio_returns is None or len(portfolio_returns) == 0:
        raise ValueError("Portfolio returns cannot be empty")

    if initial_value <= 0:
        raise ValueError("Initial value must be > 0")

    if num_simulations <= 0:
        raise ValueError("num_simulations must be > 0")

    if days <= 0:
        raise ValueError("days must be > 0")

    # prevent memory abuse
    if num_simulations > 50000:
        raise ValueError("Too many simulations (max 50000)")

    # -------------------------
    # clean returns
    # -------------------------
    portfolio_returns = pd.Series(portfolio_returns).dropna()

    mu = portfolio_returns.mean()
    sigma = portfolio_returns.std()

    if pd.isna(mu) or pd.isna(sigma):
        raise ValueError("Invalid returns data")

    # reproducible
    np.random.seed(seed)

    # -------------------------
    # generate simulations
    # -------------------------
    random_returns = np.random.normal(
        loc=mu,
        scale=sigma,
        size=(days, num_simulations)
    )

    simulations = initial_value * np.cumprod(
        1 + random_returns,
        axis=0
    )

    return pd.DataFrame(simulations)