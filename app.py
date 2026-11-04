import time
import pandas as pd
import requests
import streamlit as st
from streamlit_autorefresh import st_autorefresh
import yfinance as yf

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Indian Stock & IPO Tracker",
    page_icon="📈",
    layout="wide"
)

# -----------------------------------------------------------------------------
# 2. AUTO-REFRESH CONFIGURATION (Every 2 Seconds)
# -----------------------------------------------------------------------------
# Auto-refresh interval set to 2000 ms (2 seconds)
refresh_count = st_autorefresh(interval=2000, limit=2000, key="live_feed_refresh")

# Custom CSS for UI layout and custom HTML Tooltips
st.markdown("""
    <style>
    .metric-card {
        background-color: #0e1117;
        border: 1px solid #262730;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 10px;
    }
    .custom-tooltip {
        position: relative;
        display: inline-block;
        cursor: pointer;
        color: #58a6ff;
        font-weight: 600;
        text-decoration: underline;
        text-decoration-style: dotted;
    }
    .custom-tooltip .tooltip-content {
        visibility: hidden;
        width: 280px;
        background-color: #161b22;
        color: #c9d1d9;
        text-align: left;
        border-radius: 8px;
        padding: 10px;
        position: absolute;
        z-index: 100;
        bottom: 125%;
        left: 50%;
        margin-left: -140px;
        opacity: 0;
        transition: opacity 0.2s ease-in-out;
        box-shadow: 0px 8px 16px rgba(0,0,0,0.5);
        border: 1px solid #30363d;
        font-size: 13px;
        font-weight: normal;
    }
    .custom-tooltip:hover .tooltip-content {
        visibility: visible;
        opacity: 1;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. MASTER TICKER LOADER & DATA FETCHING
# -----------------------------------------------------------------------------
@st.cache_data(ttl=3600)
def load_complete_ticker_master():
    """
    Downloads and caches the official full equity list from NSE.
    Appends '.NS' for yahoo finance compatibility.
    """
    try:
        url = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
        headers = {'User-Agent': 'Mozilla/5.0'}
        df = pd.read_csv(url)
        tickers = [f"{symbol}.NS" for symbol in df['SYMBOL'].tolist()]
        return tickers
    except Exception:
        # Fallback list if external fetch fails
        return ["BSE.NS", "RELIANCE.NS", "TCS.NS", "INFY.NS", "TATAMOTORS.NS", "ZOMATO.NS", "JIOFIN.NS"]

def fetch_live_stock_metrics(ticker_symbols):
    """
    Fetches real-time price, calculates total trades in Lakhs,
    and maps quarterly result summaries.
    """
    # Sample mock storage/database for earnings summaries
    results_database = {
        "BSE.NS": {
            "status": "Q2 Out",
            "summary": "Net Profit: ₹807.52 Cr (+45% YoY)<br>Revenue: ₹1,432.66 Cr (+34% YoY)<br>EBITDA Margin: 68.7%"
        },
        "RELIANCE.NS": {
            "status": "Q2 Out",
            "summary": "Net Profit: ₹16,563 Cr (+11% YoY)<br>Retail Revenue: Up 18%<br>Jio ARPU: ₹195.1"
        },
        "TCS.NS": {
            "status": "Q2 Out",
            "summary": "Net Profit: ₹11,909 Cr (+5% YoY)<br>Attritions: Down to 12.3%<br>Dividend: ₹10/share"
        }
    }

    results = []
    
    for symbol in ticker_symbols:
        try:
            ticker = yf.Ticker(symbol)
            fast_info = ticker.fast_info
            
            clean_symbol = symbol.replace(".NS", "")
            last_price = fast_info.get("last_price", 0.0)
            prev_close = fast_info.get("previous_close", last_price)
            volume = fast_info.get("last_volume", 0)
            
            # Convert raw volume to Lakhs (1 Lakh = 100,000)
            trades_in_lakhs = round(volume / 100000, 2)
            
            # Calculate price change percentage
            pct_change = 0.0
            if prev_close and prev_close > 0:
                pct_change = round(((last_price - prev_close) / prev_close) * 100, 2)
                
            # Get result summary and hover details if available
            earnings_info = results_database.get(
                symbol, 
                {"status": "Pending", "summary": "Quarterly results not declared yet for this period."}
            )

            results.append({
                "Symbol": clean_symbol,
                "Full Ticker": symbol,
                "Price (₹)": round(last_price, 2),
                "Change (%)": pct_change,
                "Trades (in Lakhs)": trades_in_lakhs,
                "Result Status": earnings_info["status"],
                "Result Summary": earnings_info["summary"]
            })
        except Exception:
            continue
            
    return pd.DataFrame(results)

# -----------------------------------------------------------------------------
# 4. DASHBOARD HEADER & CONTROLS
# -----------------------------------------------------------------------------
st.title("📈 Real-Time Indian Market & IPO Analytics")

col_a, col_b = st.columns([3, 1])
with col_a:
    st.caption(f"🔄 Auto-refreshing active: Updated **{refresh_count}** times (Every 2 Seconds)")
with col_b:
    st.markdown(f"**Server Time:** `{time.strftime('%H:%M:%S')}`")

# Sidebar for Master Ticker Search & Additions
st.sidebar.header("Stock Coverage Settings")
master_tickers = load_complete_ticker_master()
st.sidebar.success(f"Loaded **{len(master_tickers)}** tickers from Master List")

# Selected stocks display (defaults to high-volume active stocks)
default_watchlist = ["BSE.NS", "RELIANCE.NS", "TCS.NS", "INFY.NS", "TATAMOTORS.NS"]
selected_tickers = st.sidebar.multiselect(
    "Select or Add Stocks to Monitor:",
    options=master_tickers,
    default=default_watchlist
)

# -----------------------------------------------------------------------------
# 5. DATA PROCESSING & DISPLAY
# -----------------------------------------------------------------------------
if selected_tickers:
    data_df = fetch_live_stock_metrics(selected_tickers)

    st.subheader("Live Market Overview")

    # Native Data Table with Tooltip Note
    st.dataframe(
        data_df[["Symbol", "Price (₹)", "Change (%)", "Trades (in Lakhs)", "Result Status"]],
        use_container_width=True
    )

    st.markdown("---")
    st.subheader("Interactive Stock Cards (Hover for Quarterly Results)")

    # Render grid cards with HTML tooltips
    cols = st.columns(3)
    for index, row in data_df.iterrows():
        col = cols[index % 3]
        change_color = "#00c853" if row["Change (%)"] >= 0 else "#ff5252"
        
        card_html = f"""
        <div class="metric-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 18px; font-weight: bold; color: #ffffff;">{row['Symbol']}</span>
                <span class="custom-tooltip">
                    [{row['Result Status']}]
                    <div class="tooltip-content">
                        <strong>{row['Symbol']} Result Summary</strong><hr style="margin:4px 0; border-color:#30363d;">
                        {row['Result Summary']}
                    </div>
                </span>
            </div>
            <div style="margin-top: 8px;">
                <span style="font-size: 22px; font-weight: bold;">₹{row['Price (₹)']:,.2f}</span>
                <span style="color: {change_color}; font-size: 14px; margin-left: 8px;">
                    {'▲' if row['Change (%)'] >= 0 else '▼'} {row['Change (%)']}%
                </span>
            </div>
            <div style="margin-top: 6px; font-size: 12px; color: #8b949e;">
                Volume: <strong>{row['Trades (in Lakhs)']} Lakh trades</strong>
            </div>
        </div>
        """
        col.markdown(card_html, unsafe_allow_html=True)

else:
    st.warning("Please select at least one stock ticker from the sidebar to view metrics.")
