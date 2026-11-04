import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# Page Configuration
st.set_page_config(
    page_title="Nifty Sector Terminal",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Dark Theme Styling matching Financial Terminals
st.markdown("""
<style>
    .stApp {
        background-color: #0b0f19;
        color: #e2e8f0;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    .terminal-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 10px;
        font-size: 14px;
    }
    .terminal-table th {
        background-color: #131c31;
        color: #94a3b8;
        text-align: left;
        padding: 12px 16px;
        font-weight: 600;
        border-bottom: 1px solid #1e293b;
        text-transform: uppercase;
        font-size: 11px;
        letter-spacing: 0.05em;
    }
    .terminal-table td {
        padding: 14px 16px;
        border-bottom: 1px solid #131c31;
        vertical-align: middle;
    }
    .terminal-table tr:hover {
        background-color: #111827;
    }
    .ticker-symbol {
        color: #38bdf8;
        font-weight: 700;
        font-family: monospace;
        font-size: 15px;
    }
    .company-name {
        color: #f8fafc;
        font-weight: 500;
    }
    .sector-tag {
        color: #94a3b8;
        font-size: 12px;
        background: #1e293b;
        padding: 4px 8px;
        border-radius: 4px;
        display: inline-block;
    }
    .price-val {
        font-family: monospace;
        font-weight: 600;
        color: #f1f5f9;
        font-size: 15px;
    }
    .positive {
        color: #22c55e;
        font-weight: 600;
        font-family: monospace;
    }
    .negative {
        color: #ef4444;
        font-weight: 600;
        font-family: monospace;
    }
</style>
""", unsafe_allow_html=True)

# Define Watchlist grouped with Sectors
STOCKS_METADATA = {
    "RELIANCE.NS": {"name": "Reliance Industries Ltd.", "sector": "Energy"},
    "TCS.NS": {"name": "Tata Consultancy Services", "sector": "Information Tech"},
    "HDFCBANK.NS": {"name": "HDFC Bank Ltd.", "sector": "Banking"},
    "INFY.NS": {"name": "Infosys Ltd.", "sector": "Information Tech"},
    "ICICIBANK.NS": {"name": "ICICI Bank Ltd.", "sector": "Banking"},
    "BHARTIARTL.NS": {"name": "Bharti Airtel Ltd.", "sector": "Telecom"},
    "SBIN.NS": {"name": "State Bank of India", "sector": "Banking"},
    "ITC.NS": {"name": "ITC Limited", "sector": "Consumer Goods"},
    "LTIM.NS": {"name": "LTIMindtree Ltd.", "sector": "Information Tech"},
    "HINDUNILVR.NS": {"name": "Hindustan Unilever Ltd.", "sector": "Consumer Goods"},
    "BAJFINANCE.NS": {"name": "Bajaj Finance Ltd.", "sector": "Financial Services"},
    "MARUTI.NS": {"name": "Maruti Suzuki India Ltd.", "sector": "Automobile"},
    "SUNPHARMA.NS": {"name": "Sun Pharmaceutical Ind.", "sector": "Pharma"},
    "TATASTEEL.NS": {"name": "Tata Steel Ltd.", "sector": "Metals"},
    "ASIANPAINT.NS": {"name": "Asian Paints Ltd.", "sector": "Consumer Goods"}
}

st.title("⚡ Nifty Sector Terminal & Price Trends")
st.caption("Live multi-sector market overview with embedded 30-day and 60-day price trend sparklines.")

if st.button("🔄 Refresh Market Data"):
    st.cache_data.clear()
    st.rerun()

def generate_svg_sparkline(prices, label="30D"):
    """Generates a responsive SVG sparkline with min/max bounds and gradient fill."""
    if not prices or len(prices) < 2:
        return ""
    min_p, max_p = min(prices), max(prices)
    p_range = max_p - min_p if max_p != min_p else 1.0

    width, height = 150, 45
    points = []
    for i, p in enumerate(prices):
        x = (i / (len(prices) - 1)) * width
        y = height - 5 - ((p - min_p) / p_range) * (height - 15)
        points.append(f"{x:.1f},{y:.1f}")

    pts_str = " ".join(points)
    is_bullish = prices[-1] >= prices[0]
    color = "#22c55e" if is_bullish else "#ef4444"
    
    area_pts = f"0,{height} " + pts_str + f" {width},{height}"

    svg = f"""
    <svg width="{width}" height="{height}" style="background:transparent; overflow:visible;">
        <defs>
            <linearGradient id="grad_{label}_{abs(hash(tuple(prices)))}" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stop-color="{color}" stop-opacity="0.25"/>
                <stop offset="100%" stop-color="{color}" stop-opacity="0.0"/>
            </linearGradient>
        </defs>
        <polygon points="{area_pts}" fill="url(#grad_{label}_{abs(hash(tuple(prices)))})" />
        <polyline fill="none" stroke="{color}" stroke-width="2" points="{pts_str}" />
        <circle cx="{width}" cy="{points[-1].split(',')[1]}" r="3.5" fill="{color}" />
        <text x="2" y="10" fill="#64748b" font-size="9" font-family="monospace">₹{min_p:.0f}</text>
        <text x="{width-38}" y="10" fill="#64748b" font-size="9" font-family="monospace">₹{max_p:.0f}</text>
    </svg>
    """
    return svg

@st.cache_data(ttl=300)
def fetch_terminal_data():
    tickers = list(STOCKS_METADATA.keys())
    df_raw = yf.download(tickers, period="70d", interval="1d", group_by="ticker", progress=False)
    
    rows = []
    for ticker, meta in STOCKS_METADATA.items():
        try:
            data = df_raw[ticker].dropna()
            if len(data) < 60:
                continue
            
            closes = data['Close'].values
            curr_price = float(closes[-1])
            prev_price = float(closes[-2])
            change_pct = ((curr_price - prev_price) / prev_price) * 100
            
            p30 = closes[-30:]
            p60 = closes[-60:]
            
            rows.append({
                "Symbol": ticker.replace(".NS", ""),
                "Name": meta["name"],
                "Sector": meta["sector"],
                "Price": curr_price,
                "Change": change_pct,
                "30D": [float(x) for x in p30],
                "60D": [float(x) for x in p60]
            })
        except Exception:
            continue
            
    return pd.DataFrame(rows)

with st.spinner("Fetching live prices and building sparklines..."):
    df = fetch_terminal_data()

if df.empty:
    st.warning("Could not fetch data. Please try again.")
else:
    # Sector Filter
    sectors = ["All"] + sorted(df["Sector"].unique().tolist())
    selected_sector = st.selectbox("Filter by Sector:", sectors)
    
    if selected_sector != "All":
        df_filtered = df[df["Sector"] == selected_sector]
    else:
        df_filtered = df

    # Render Terminal Table via HTML
    html_table = """
    <table class="terminal-table">
        <thead>
            <tr>
                <th>Ticker</th>
                <th>Company Name</th>
                <th>Sector</th>
                <th>Current Price (₹)</th>
                <th>24H Change</th>
                <th>30-Day Price Trend (₹)</th>
                <th>60-Day Price Trend (₹)</th>
            </tr>
        </thead>
        <tbody>
    """
    
    for _, row in df_filtered.iterrows():
        change_class = "positive" if row["Change"] >= 0 else "negative"
        sign_str = "+" if row["Change"] >= 0 else ""
        
        svg_30 = generate_svg_sparkline(row["30D"], label="30D")
        svg_60 = generate_svg_sparkline(row["60D"], label="60D")
        
        html_table += f"""
            <tr>
                <td><span class="ticker-symbol">{row['Symbol']}</span></td>
                <td><span class="company-name">{row['Name']}</span></td>
                <td><span class="sector-tag">{row['Sector']}</span></td>
                <td><span class="price-val">₹{row['Price']:,.2f}</span></td>
                <td><span class="{change_class}">{sign_str}{row['Change']:.2f}%</span></td>
                <td>{svg_30}</td>
                <td>{svg_60}</td>
            </tr>
        """
        
    html_table += "</tbody></table>"
    
    st.markdown(html_table, unsafe_allow_html=True)
