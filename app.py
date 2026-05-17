from flask import Flask, render_template, request, flash, redirect,send_file,session
import os
import pandas as pd
import logging
logging.basicConfig(level=logging.INFO,format="%(asctime)s - %(levelname)s -%(message)s")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from werkzeug.utils import secure_filename
from pandas.errors import EmptyDataError, ParserError
from exports.pdf_report import generate_pdf_report
from services.data_fetcher import fetch_price_data
from services.returns_engine import compute_returns
from services.schema_detector import detect_schema
from services.monte_carlo import run_monte_carlo
from services.data_fetcher import normalize_tickers
from utils.validator import validate_portfolio
from services.data_standardizer import standardize_columns
from services.portfolio_engine import (
    compute_portfolio_returns,
    compute_volatility,
    compute_sharpe,
    compute_beta
)
from services.sector_analysis import sector_breakdown
from services.risk_engine import (
    compute_var,
    compute_cvar,
    compute_max_drawdown
)
from services.stress_test import (
    market_crash,
    covid_crash,
    custom_shock,concentration_risk
)
from services.sector_analysis import sector_breakdown







app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev_secret")

UPLOAD_FOLDER = "data/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"csv"}
MAX_ROWS = 500
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024
os.makedirs("static", exist_ok=True)

def allowed_file(filename):
    return (
        "." in filename and
        filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        flash("No file uploaded")
        return redirect("/")
    file = request.files["file"]
    if file.filename == "":
        flash("No file selected")
        return redirect("/")
    # file type check
    if not allowed_file(file.filename):
        flash("Only CSV files are allowed")
        return redirect("/")
    filename = secure_filename(file.filename)
    path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    try:
        file.save(path)
        # empty/malformed csv
        df = pd.read_csv(path)
        os.remove(path) 
        if df.empty:
            flash("Uploaded CSV is empty")
            return redirect("/")
        if len(df) > MAX_ROWS:
            flash(f"Too many rows. Max allowed is {MAX_ROWS}")
            return redirect("/")
    except EmptyDataError:
        flash("CSV file is empty")
        return redirect("/")
    except ParserError:
        flash("Malformed CSV file")
        return redirect("/")
    except Exception as e:
        logging.exception(e)
        flash("Upload failed")
        return redirect("/")
    logging.info(f"File uploaded: {file.filename}")
    logging.info(f"Raw columns: {df.columns.tolist()}")
    df = standardize_columns(df)
    logging.info(f"Standardized columns: {df.columns.tolist()}")
    schema = detect_schema(df)
    logging.info(f"Detected schema: {schema}")
    issues = validate_portfolio(df, schema)
    if issues:
        for issue in issues:
            flash(issue)
        return redirect("/")
    # SAFE extraction
    ticker_col = schema.get("ticker")
    weight_col = schema.get("weight")


    if not ticker_col:
        flash("Ticker column not found. Supported names: ticker, symbol, stock")
        return redirect("/")

    if not weight_col:
        flash("Weight/Quantity column not found. Supported names: weight, qty, quantity")
        return redirect("/")
    raw_weights = dict(zip(df[ticker_col], df[weight_col]))
    # calculate real current portfolio value
    
    total = sum(raw_weights.values())
    if total <= 0:
        flash("Total portfolio value cannot be zero")
        return redirect("/")
    weights = {t: w / total  for t, w in zip(normalize_tickers(raw_weights.keys()),raw_weights.values())
}
    logging.info(f"Normalized weights: {weights}")

    tickers = df[ticker_col].dropna().unique().tolist()
    logging.info(f"Tickers extracted: {tickers}")

    try:
        prices = fetch_price_data(tickers)
    except Exception as e:
        flash(str(e))
        return redirect("/")
    if "price" in df.columns or "ltp" in df.columns:
        price_col = "price" if "price" in df.columns else "ltp"
        current_value = float((df[weight_col] * df[price_col]).sum())
    else:
        latest_prices = prices.iloc[-1]

        current_value = 0

        for ticker in tickers:
            yf_ticker = ticker.upper().strip()
            if "." not in yf_ticker:
                yf_ticker = yf_ticker + ".NS"

            qty = df.loc[
                df[ticker_col] == ticker,
                weight_col
            ].values[0]

            # SAFE access
            if yf_ticker in latest_prices:
                price = latest_prices[yf_ticker]
            else:
                continue  # skip missing ticker safely

            current_value += qty * price
    returns = compute_returns(prices)
    portfolio_returns = compute_portfolio_returns(returns, weights)
    volatility = compute_volatility(portfolio_returns)
    sharpe = compute_sharpe(portfolio_returns)
    try:
        market = fetch_price_data(["^NSEI"])
        market_returns = compute_returns(market).iloc[:, 0]
        beta = compute_beta(portfolio_returns, market_returns)
    except:
        beta = 0
    var_95 = compute_var(portfolio_returns)
    cvar_95 = compute_cvar(portfolio_returns)
    max_dd = compute_max_drawdown(portfolio_returns)
    preview = df.head().to_html(classes="table")
    var=var_95
    cvar=cvar_95
    max_drawdown=max_dd
    simulations = run_monte_carlo(portfolio_returns,    initial_value=100000,
    num_simulations=5000)
    print(simulations.head())
    print(simulations.shape)
    plt.figure(figsize=(10,6))
    plt.plot(simulations.iloc[:, :100])   # first 100 paths only
    plt.title("Monte Carlo Portfolio Simulation")
    plt.xlabel("Days")
    plt.ylabel("Portfolio Value")
    mc_path = os.path.join("static", "monte_carlo.png")
    os.makedirs(os.path.dirname(mc_path), exist_ok=True)

    plt.savefig(mc_path, bbox_inches="tight", dpi=120)
    plt.close()
    value_2008 = market_crash(current_value)
    value_covid = covid_crash(current_value)
    value_custom = custom_shock(current_value, -15)
    risk_flag = concentration_risk(weights)
    logging.info(simulations.head())
    logging.info(f"MC shape: {simulations.shape}")
    session["report_metrics"] = {
    "volatility": float(volatility),
    "sharpe": float(sharpe),
    "beta": float(beta),
    "var": float(var),
    "cvar": float(cvar),
    "max_drawdown": float(max_drawdown),
    "value_2008": float(value_2008),
    "value_covid": float(value_covid),
    "value_custom": float(value_custom),
    "current_value": float(current_value),
    "risk_flag": risk_flag,
    "schema": str(schema),
    "tickers": tickers,
    "mc_start": float(current_value),
    "mc_return": round(returns.mean().mean() * 252 * 100, 1),
    "mc_volatility": round(volatility * 100, 0),
    "mc_years": 10,
}
    


    return render_template(
    "validate.html",
    schema=schema,
    issues=issues,
    preview=preview,
    volatility=round(volatility, 4),
    sharpe=round(sharpe, 4),
    beta=round(beta, 4),
    var=round(var, 4),
    cvar=round(cvar, 4),
    max_drawdown=round(max_drawdown, 4),
    value_2008=value_2008,
    value_covid=value_covid,
    value_custom=value_custom,
    current_value=current_value,
    risk_flag=risk_flag,
    mc_start=current_value,
    mc_return=round(sharpe * 10, 0),
    mc_vol=round(volatility * 100, 0)
    )
@app.route("/download-report")
def download_report():

    metrics = session.get("report_metrics")
    if not metrics:
        flash("No report found. Upload a portfolio first.")
        return redirect("/")

    pdf_path = generate_pdf_report(metrics)

    return send_file(
        pdf_path,
        as_attachment=True
    )
@app.errorhandler(413)
def too_large(e):
    flash("File too large. Max allowed is 2MB.")
    return redirect("/")
@app.errorhandler(500)
def internal_error(e):
    logging.exception(e)
    return "Ticker data unavailable. Please try again.", 500


if __name__ == "__main__":
    app.run(debug=True,port=5001)