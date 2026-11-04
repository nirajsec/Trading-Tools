import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# Page Setup
st.set_page_config(page_title="Nifty Mini Tracker", layout="wide")

# Reduced Watchlist for Fast Small-Scale Loading
NIFTY_MINI_TICKERS = {
    "RELIANCE.NS": "Reliance Industries",
    "TCS.NS": "Tata Consultancy Services",
    "HDFCBANK.NS": "HDFC Bank",
    "INFY.NS": "Infosys",
    "ICICIBANK.NS": "ICICI Bank",
    "SBIN.NS": "State Bank of India"
}

st.title("⚡ Nifty Mini Stock Tracker (Fast Mode)")
st.caption("Optimized small-scale tracker displaying live 30D and 60D actual price trends.")

# Refresh Controls
if st.button("🔄 Refresh Data"):
    st.cache_data.clear()

@st.cache_data(ttl=300)
def fetch_small_scale_data():
    tickers = list(NIFTY_MINI_TICKERS.keys())
    # Download exactly 70 days to ensure 60 trading days are captured safely
    df_raw = yf.download(tickers, period="70d", interval="1d", group_by="ticker", progress=False)
    
    rows = []
    for ticker, name in NIFTY_MINI_TICKERS.items():
        try:
            data = df_raw[ticker].dropna()
            if len(data) < 60:
                continue
            
            closes = data['Close'].values
            curr_price = float(closes[-1])
            prev_price = float(closes[-2])
            change_pct = ((curr_price - prev_price) / prev_price) * 100
            
            # Extract 30D & 60D actual price arrays
            p30 = closes[-30:]
            p60 = closes[-60:]
            
            # RSI Calculation
            delta = data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            rsi_series = 100 - (100 / (1 + rs))
            rsi = float(rsi_series.iloc[-1]) if not rsi_series.isna().iloc[-1] else 50.0
            
            # Recommendation Logic
            p30_ret = ((curr_price - p30[0]) / p30[0]) * 100
            if rsi < 35:
                signal = "STRONG BUY"
            elif rsi < 45 and p30_ret > 0:
                signal = "BUY"
            elif rsi > 70:
                signal = "SELL"
            else:
                signal = "HOLD"
                
            rows.append({
                "Symbol": ticker.replace(".NS", ""),
                "Name": name,
                "Price (₹)": round(curr_price, 2),
                "Change %": round(change_pct, 2),
                "30D Prices": [round(x, 2) for x in p30.tolist()],
                "60D Prices": [round(x, 2) for x in p60.tolist()],
                "RSI (14)": round(rsi, 1),
                "Signal": signal
            })
        except Exception:
            continue
            
    return pd.DataFrame(rows)

with st.spinner("Fetching live stock prices..."):
    df = fetch_small_scale_data()

# Display Table
st.subheader("📋 Watchlist Summary")
st.dataframe(
    df[["Symbol", "Name", "Price (₹)", "Change %", "RSI (14)", "Signal"]],
    use_container_width=True,
    hide_index=True
)

st.divider()

# Individual Chart Inspector
st.subheader("📈 30D & 60D Actual Price Trend Charts")
selected_symbol = st.selectbox("Select Stock:", df["Symbol"].tolist())
stock_row = df[df["Symbol"] == selected_symbol].iloc[0]

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 30-Day Price Trend (₹)")
    fig30 = go.Figure()
    fig30.add_trace(go.Scatter(y=stock_row["30D Prices"], mode='lines+markers', line=dict(color='#00F0FF', width=2)))
    fig30.update_layout(xaxis_title="Days", yaxis_title="Price (₹)", template="plotly_dark", margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig30, use_container_width=True)

with col2:
    st.markdown("### 60-Day Price Trend (₹)")
    fig60 = go.Figure()
    fig60.add_trace(go.Scatter(y=stock_row["60D Prices"], mode='lines+markers', line=dict(color='#7000FF', width=2)))
    fig60.update_layout(xaxis_title="Days", yaxis_title="Price (₹)", template="plotly_dark", margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig60, use_container_width=True)
