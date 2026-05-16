def market_crash(portfolio_value, shock=-0.20):
    return portfolio_value * (1 + shock)


def covid_crash(portfolio_value):
    # approx -34%
    return portfolio_value * 0.66


def custom_shock(portfolio_value, shock_percent):
    shock = shock_percent / 100
    return portfolio_value * (1 + shock)
def concentration_risk(weights):
    max_weight = max(weights.values())

    if max_weight > 0.30:
        return "High concentration risk"
    return "Diversified"