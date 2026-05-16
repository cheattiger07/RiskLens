📊 RiskLens

Portfolio Risk & Stress Testing Engine (V1)
A production-style financial analytics system for portfolio risk evaluation, Monte Carlo simulation, and stress testing using real market data.

🚀 Overview

RiskLens is a full-stack financial risk analysis engine that allows users to upload a portfolio CSV and instantly compute:

Portfolio risk metrics
Monte Carlo simulations (Geometric Brownian Motion)
Stress testing (2008 crash, COVID crash, custom shocks)
Value at Risk (VaR) & Conditional VaR (CVaR)
Sharpe ratio, volatility, beta (NSE benchmarked)
Interactive visual insights + downloadable PDF report

Built with a focus on real-world quant finance workflows.

🧠 Key Features
📂 Portfolio Upload Engine
Upload CSV portfolio files
Automatic schema detection (ticker, weight/quantity)
Data standardization for NSE/BSE tickers
Edge-case validation for real-world messy datasets
📈 Risk Analytics Engine
Portfolio Returns Computation
Annualized Volatility
Sharpe Ratio
Market Beta (NSE benchmarked)
Value at Risk (VaR 95%)
Conditional VaR (CVaR 95%)
Maximum Drawdown
🎲 Monte Carlo Simulation
Geometric Brownian Motion model
200+ simulated paths (configurable)
Probability distribution of portfolio outcomes
Confidence bands (P5 / P50 / P95)
Interactive visualization engine (frontend)
⚠️ Stress Testing
2008 Financial Crisis simulation
COVID crash simulation
Custom shock scenarios
Concentration risk detection
📊 Reporting System
Auto-generated professional PDF report
Metrics summary + interpretation
Monte Carlo visualization included
Downloadable risk report per upload
🏗️ System Architecture
User Upload (CSV)
        ↓
Flask Backend
        ↓
Data Standardization Layer
        ↓
Risk Engines
    ├── Returns Engine
    ├── Portfolio Engine
    ├── Risk Engine (VaR, CVaR)
    ├── Monte Carlo Engine
    ├── Stress Testing Engine
        ↓
PDF Report Generator
        ↓
Frontend Dashboard + Visualization
🛠️ Tech Stack
Backend: Flask (Python)
Data Processing: Pandas, NumPy
Finance Models: Custom quant finance implementations
Visualization: Matplotlib
Simulation: Monte Carlo (GBM)
Reporting: ReportLab PDF engine
Frontend: HTML, CSS, JavaScript
📁 Project Structure
RiskLens/
│
├── app.py
├── services/
│   ├── returns_engine.py
│   ├── portfolio_engine.py
│   ├── monte_carlo.py
│   ├── risk_engine.py
│   ├── stress_test.py
│   └── data_fetcher.py
│
├── exports/
│   └── pdf_report.py
│
├── utils/
│   └── validator.py
│
├── static/
│   ├── monte_carlo.png
│   └── risk_report.pdf
│
├── templates/
│   └── index.html
│
└── data/
    └── uploads/
📊 Example Output Metrics
Volatility: ~15–30%
Sharpe Ratio: Risk-adjusted return indicator
Beta vs NSE index
VaR (95%): Maximum expected loss under normal conditions
CVaR (95%): Tail risk exposure
Monte Carlo distribution of portfolio value
📉 Monte Carlo Simulation

The system simulates portfolio growth using:

S(t+dt) = S(t) × exp((μ - 0.5σ²)dt + σ√dt·Z)

Where:

μ = expected return
σ = volatility
Z = random normal variable
⚠️ Disclaimer

This project is for educational and analytical purposes only.
It does not constitute financial advice. Market investments carry risk.

🚀 Future Improvements (V2 Roadmap)
Multi-currency support (INR/USD conversion)
Real-time market data streaming
Authentication & user accounts
Cloud deployment (AWS / Render)
Portfolio benchmarking (NIFTY 50, S&P 500)
Database integration
SaaS subscription model
API layer for external access
👨‍💻 Author

Built by Praavin
Focused on Quant Finance, Data Science & Fintech Engineering

⭐ If you like this project

Star the repo and follow for V2 (production SaaS version)