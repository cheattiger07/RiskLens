import numpy as np


def compute_var(portfolio_returns, confidence=0.95):
    percentile = (1 - confidence) * 100
    var = np.percentile(portfolio_returns, percentile)
    return var
def compute_cvar(portfolio_returns, confidence=0.95):
    var = compute_var(portfolio_returns, confidence)

    tail_losses = portfolio_returns[portfolio_returns <= var]

    return tail_losses.mean()
def compute_max_drawdown(portfolio_returns):
    cumulative = (1 + portfolio_returns).cumprod()

    running_max = cumulative.cummax()

    drawdown = (cumulative - running_max) / running_max

    return drawdown.min()