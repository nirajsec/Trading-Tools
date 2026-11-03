import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as gg
import plotly.express as px

# Page Setup
st.set_page_config(page_title="Nifty 50 Tracker", layout="wide", initial_sidebar_state="expanded")

# Nifty 50 Stocks Map (Ticker -> Name)
NIFTY_50_TICKERS = {
    "RELIANCE.NS": "Reliance Industries",
    "TCS.NS": "Tata Consultancy Services",
    "HDFCBANK.NS": "HDFC Bank",
    "INFY.NS": "Infosys",
    "ICICIBANK.NS": "ICICI Bank",
    "BHARTIARTL.NS": "Bharti Airtel",
    "SBIN.NS": "State Bank of India",
    "LTIM.NS": "LTIMindtree",
    "ITC.NS": "ITC",
    "HINDUNILVR.NS": "Hindustan Unilever",
    "LT.NS": "Larsen & Toubro",
    "BAJFINANCE.NS": "Bajaj Finance",
    "MARUTI.NS": "Maruti Suzuki",
    "SUNPHARMA.NS": "Sun Pharma",
    "TATASTEEL.NS": "Tata Steel",
    "M&M.NS": "Mahindra & Mahindra",
    "KOTAKBANK.NS": "Kotak Mahindra Bank",
    "TITAN.NS": "Titan Company",
    "NTPC.NS": "NTPC",
    "AXISBANK.NS": "Axis Bank",
    "ADANIENT.NS": "Adani Enterprises",
    "ADANIPORTS.NS": "Adani Ports",
    "ULTRACEMCO.NS": "UltraTech Cement",
    "POWERGRID.NS": "Power Grid Corp",
    "TATAMOTORS.NS": "Tata Motors",
    "BAJAJFINSV.NS": "Bajaj Finserv",
    "COALINDIA.NS": "Coal India",
    "ASIANPAINT.NS": "Asian Paints",
    "ONGC.NS": "ONGC",
    "HCLTECH.NS": "HCL Technologies"
}

st.title("📈 Nifty 50 Live Stock Tracker & Signal Screener")
st.caption("Live Yahoo Finance feed with interactive 30D / 60D price trend lines, RSI technical analysis, and automated trading signals.")

# Refresh Controls
col1, col2 = st.columns([1, 4])
with col1:
    if st.button("🔄 Fetch Live Data"):
        st.cache_data.clear()

@st.cache_data(ttl=300)
def fetch_stock_analysis():
    tickers = list(NIFTY_50_TICKERS.keys())
    # Download 90 days to safely get 60 trading days data
    df_raw = yf.download(tickers, period="90d", interval="1d", group_by="ticker", progress=False)
    
    rows = []
    for ticker, name in NIFTY_50_TICKERS.items():
        try:
            data = df_raw[ticker].dropna()
            if len(data) < 60:
                continue
            
            closes = data['Close'].values
            curr_price = float(closes[-1])
            prev_price = float(closes[-2])
            change_pct = ((curr_price - prev_price) / prev_price) * 100
            
            # Extract historical 30D & 60D prices
            p30 = closes[-30:]
            p60 = closes[-60:]
            
            # Technical Indicators
            delta = data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            rsi_series = 100 - (100 / (1 + rs))
            rsi = float(rsi_series.iloc[-1]) if not rsi_series.isna().iloc[-1] else 50.0
            
            sma50 = float(data['Close'].rolling(50).mean().iloc[-1])
            
            # Recommendation Logic
            p30_ret = ((curr_price - p30[0]) / p30[0]) * 100
            p60_ret = ((curr_price - p60[0]) / p60[0]) * 100
            
            if rsi < 35 and curr_price > sma50:
                signal = "STRONG BUY"
                rationale = "Oversold RSI with strong trend support above 50-DMA."
            elif rsi < 45 and p30_ret > 0:
                signal = "BUY"
                rationale = "Positive 30-day momentum with bullish pullback."
            elif rsi > 70:
                signal = "SELL"
                rationale = "Overbought conditions reached (RSI > 70)."
            else:
                signal = "HOLD"
                rationale = "Consolidating within normal trading range."
                
            rows.append({
                "Symbol": ticker.replace(".NS", ""),
                "Name": name,
                "Price (₹)": round(curr_price, 2),
                "Change %": round(change_pct, 2),
                "30D Price (₹)": [round(x, 2) for x in p30.tolist()],
                "60D Price (₹)": [round(x, 2) for x in p60.tolist()],
                "30D Return %": round(p30_ret, 2),
                "60D Return %": round(p60_ret, 2),
                "RSI (14)": round(rsi, 1),
                "Signal": signal,
                "Rationale": rationale
            })
        except Exception:
            continue
            
    return pd.DataFrame(rows)

with st.spinner("Fetching data from NSE/Yahoo Finance..."):
    df = fetch_stock_analysis()

# Streamlit Dataframe View with Built-in Column Sorting
st.subheader("📋 Screener & Summary Table")
st.text("Tip: Click on any column header to sort the table by that metric.")

# Interactive Filter
signals_selected = st.multiselect("Filter by Signal:", ["STRONG BUY", "BUY", "HOLD", "SELL"], default=["STRONG BUY", "BUY", "HOLD", "SELL"])
df_filtered = df[df["Signal"].isin(signals_selected)]

st.dataframe(
    df_filtered[["Symbol", "Name", "Price (₹)", "Change %", "30D Return %", "60D Return %", "RSI (14)", "Signal", "Rationale"]],
    use_container_width=True,
    hide_index=True
)

st.divider()

# Interactive Price Graph Inspector
st.subheader("📊 Interactive 30-Day & 60-Day Price Trend Charts")
selected_symbol = st.selectbox("Select a Stock to inspect 30D & 60D Price Charts:", df["Symbol"].tolist())

stock_row = df[df["Symbol"] == selected_symbol].iloc[0]

g_col1, g_col2 = st.columns(2)

with g_col1:
    st.markdown(f"### 30-Day Price Trend (₹)")
    p30_vals = stock_row["30D Price (₹)"]
    fig30 = gg.Figure()
    fig30.add_trace(gg.Scatter(y=p30_vals, mode='lines+markers', name='Price (₹)', line=dict(color='#00F0FF', width=2)))
    fig30.update_layout(
        xaxis_title="Trading Days",
        yaxis_title="Price (₹)",
        template="plotly_dark",
        margin=dict(l=20, r=20, t=30, b=20)
    )
    st.plotly_chart(fig30, use_container_width=True)

with g_col2:
    st.markdown(f"### 60-Day Price Trend (₹)")
    p60_vals = stock_row["60D Price (₹)"]
    fig60 = gg.Figure()
    fig60.add_trace(gg.Scatter(y=p60_vals, mode='lines+markers', name='Price (₹)', line=dict(color='#7000FF', width=2)))
    fig60.update_layout(
        xaxis_title="Trading Days",
        yaxis_title="Price (₹)",
        template="plotly_dark",
        margin=dict(l=20, r=20, t=30, b=20)
    )
    st.plotly_chart(fig60, use_container_width=True)

# Technical Card
st.info(f"**{stock_row['Name']} ({stock_row['Symbol']})** | Current Price: **₹{stock_row['Price (₹)']}** | Signal: **{stock_row['Signal']}** | RSI: **{stock_row['RSI (14)']}**\n\n*Rationale:* {stock_row['Rationale']}")
