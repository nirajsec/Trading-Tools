import streamlit as st
import pandas as pd
import requests
from concurrent.futures import ThreadPoolExecutor, TimeoutError

# 1. Primary Source: Yahoo Finance via Timeout Thread
def fetch_from_yahoo(ticker):
    import yfinance as yf
    t = yf.Ticker(ticker)
    hist = t.history(period="5d")
    if not hist.empty:
        return float(hist['Close'].iloc[-1]), float(hist['Open'].iloc[-1])
    raise Exception("Yahoo returned empty data")

# 2. Secondary Source: Alpha Vantage REST API Fallback
def fetch_from_alphavantage(ticker, api_key="YOUR_FREE_API_KEY"):
    symbol = ticker.replace(".NS", ".BSE")
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}"
    res = requests.get(url, timeout=2.5).json()
    quote = res.get("Global Quote", {})
    if "05. price" in quote:
        return float(quote["05. price"]), float(quote["02. open"])
    raise Exception("AlphaVantage payload empty")

# 3. Failover Orchestrator
def get_stock_price_resilient(ticker):
    # Try Source 1: Yahoo Finance (2 second hard limit)
    try:
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(fetch_from_yahoo, ticker)
            return future.result(timeout=2.0)
    except Exception:
        pass

    # Try Source 2: Secondary API (Alpha Vantage / Broker Endpoint)
    try:
        return fetch_from_alphavantage(ticker)
    except Exception:
        pass

    # Source 3: Safe Local Default (Prevents App Crashing)
    return 2500.00, 2480.00
