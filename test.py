from services.data_fetcher import fetch_price_data
from services.returns_engine import compute_returns

tickers = ["AAPL", "MSFT", "TSLA"]

prices = fetch_price_data(tickers)

returns = compute_returns(prices)

print(prices.head())
print(returns.head())