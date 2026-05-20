# RiskLens — Portfolio Risk & Stress Testing Engine

RiskLens is a production-grade **portfolio risk analytics web application** built to help investors, analysts, and finance students understand portfolio risk using institutional-grade risk models in a simple and interactive interface.

Users can upload a portfolio CSV containing **tickers and weights**, and RiskLens automatically calculates advanced portfolio risk metrics such as:

* portfolio returns
* volatility
* Value at Risk (VaR)
* Monte Carlo simulations
* stress testing
* asset exposure
* risk contribution

It transforms raw portfolio data into a professional **risk intelligence dashboard**, helping users understand **how much they can lose, why, and under what market scenarios**.

---

## Features

### Portfolio Upload

* Upload portfolio CSV (`Ticker`, `Weight`)
* validates total weights
* validates ticker symbols
* handles invalid inputs and edge cases

### Market Data Engine

* fetches live historical data using `yfinance`
* supports stocks, ETFs, and major indices
* auto-adjusted close prices

### Risk Analytics Engine

* daily returns calculation
* annualized volatility
* Value at Risk (95%)
* Conditional VaR (future roadmap)
* portfolio beta (future roadmap)

### Monte Carlo Simulation

* simulates thousands of possible portfolio outcomes
* visual probability distribution
* future portfolio value projections

### Stress Testing

Scenario-based shocks:

* market crash (-20%)
* recession
* sector-specific shocks
* custom stress scenarios

### Interactive Dashboard

Built using Plotly:

* equity curve
* return distribution
* Monte Carlo chart
* allocation pie chart
* drawdown visuals

### Professional Reporting

* downloadable PDF report
* downloadable Excel report
* portfolio summary export

### Production Ready

* modular Flask architecture
* scalable analytics engine
* real-world validation
* deployable SaaS structure

---

## Tech Stack

* Python
* Flask
* Pandas
* NumPy
* yFinance
* Plotly
* HTML/CSS/JavaScript
* Render

---

## Why I Built This

Most retail investors and students do not understand portfolio risk beyond “profit/loss.”

RiskLens was built to bridge that gap by making **institutional risk analytics accessible to everyone**.

It demonstrates:

* quantitative finance concepts
* risk modeling
* data science workflows
* backend engineering
* product design for fintech

---

## Finance Concepts Implemented

* Portfolio Theory
* Historical Returns
* Volatility
* Value at Risk (VaR)
* Monte Carlo Simulation
* Stress Testing
* Risk Contribution

---

## Future Roadmap (v2)

* live broker integrations
* factor exposure analysis
* sector risk decomposition
* custom benchmarks
* portfolio optimization
* scenario builder
* user accounts & saved portfolios
* subscription model
