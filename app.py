import streamlit as st
import yfinance as yf
import pandas as pd
import streamlit.components.v1 as components

# Page Configuration
st.set_page_config(
    page_title="Nifty 50 Terminal",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Complete Nifty 50 Watchlist with Sectors
NIFTY_50_METADATA = {
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
    "LT.NS": {"name": "Larsen & Toubro Ltd.", "sector": "Construction"},
    "BAJFINANCE.NS": {"name": "Bajaj Finance Ltd.", "sector": "Financial Services"},
    "MARUTI.NS": {"name": "Maruti Suzuki India Ltd.", "sector": "Automobile"},
    "SUNPHARMA.NS": {"name": "Sun Pharmaceutical Ind.", "sector": "Pharma"},
    "TATASTEEL.NS": {"name": "Tata Steel Ltd.", "sector": "Metals"},
    "M&M.NS": {"name": "Mahindra & Mahindra Ltd.", "sector": "Automobile"},
    "KOTAKBANK.NS": {"name": "Kotak Mahindra Bank Ltd.", "sector": "Banking"},
    "TITAN.NS": {"name": "Titan Company Ltd.", "sector": "Consumer Goods"},
    "NTPC.NS": {"name": "NTPC Limited", "sector": "Energy"},
    "AXISBANK.NS": {"name": "Axis Bank Ltd.", "sector": "Banking"},
    "ADANIENT.NS": {"name": "Adani Enterprises Ltd.", "sector": "Metals & Mining"},
    "ADANIPORTS.NS": {"name": "Adani Ports & SEZ Ltd.", "sector": "Services"},
    "ULTRACEMCO.NS": {"name": "UltraTech Cement Ltd.", "sector": "Cement"},
    "POWERGRID.NS": {"name": "Power Grid Corp of India", "sector": "Energy"},
    "TATAMOTORS.NS": {"name": "Tata Motors Ltd.", "sector": "Automobile"},
    "BAJAJFINSV.NS": {"name": "Bajaj Finserv Ltd.", "sector": "Financial Services"},
    "COALINDIA.NS": {"name": "Coal India Ltd.", "sector": "Metals & Mining"},
    "ASIANPAINT.NS": {"name": "Asian Paints Ltd.", "sector": "Consumer Goods"},
    "ONGC.NS": {"name": "Oil & Natural Gas Corp Ltd.", "sector": "Energy"},
    "HCLTECH.NS": {"name": "HCL Technologies Ltd.", "sector": "Information Tech"},
    "GRASIM.NS": {"name": "Grasim Industries Ltd.", "sector": "Cement"},
    "BAJAJ-AUTO.NS": {"name": "Bajaj Auto Ltd.", "sector": "Automobile"},
    "TECHM.NS": {"name": "Tech Mahindra Ltd.", "sector": "Information Tech"},
    "WIPRO.NS": {"name": "Wipro Ltd.", "sector": "Information Tech"},
    "BRITANNIA.NS": {"name": "Britannia Industries Ltd.", "sector": "Consumer Goods"},
    "CIPLA.NS": {"name": "Cipla Ltd.", "sector": "Pharma"},
    "DRREDDY.NS": {"name": "Dr. Reddy's Laboratories", "sector": "Pharma"},
    "EICHERMOT.NS": {"name": "Eicher Motors Ltd.", "sector": "Automobile"},
    "BPCL.NS": {"name": "Bharat Petroleum Corp Ltd.", "sector": "Energy"},
    "HEROMOTOCO.NS": {"name": "Hero MotoCorp Ltd.", "sector": "Automobile"},
    "DIVISLAB.NS": {"name": "Divi's Laboratories Ltd.", "sector": "Pharma"},
    "TATACONSUM.NS": {"name": "Tata Consumer Products Ltd.", "sector": "Consumer Goods"},
    "APOLLOHOSP.NS": {"name": "Apollo Hospitals Enterprise", "sector": "Healthcare"},
    "HINDALCO.NS": {"name": "Hindalco Industries Ltd.", "sector": "Metals"},
    "INDUSINDBK.NS": {"name": "IndusInd Bank Ltd.", "sector": "Banking"},
    "JSWSTEEL.NS": {"name": "JSW Steel Ltd.", "sector": "Metals"},
    "SBILIFE.NS": {"name": "SBI Life Insurance Co Ltd.", "sector": "Financial Services"},
    "HDFCLIFE.NS": {"name": "HDFC Life Insurance Co Ltd.", "sector": "Financial Services"},
    "BEL.NS": {"name": "Bharat Electronics Ltd.", "sector": "Capital Goods"},
    "TRENT.NS": {"name": "Trent Ltd.", "sector": "Consumer Goods"}
}

st.title("⚡ Nifty 50 Master Sector Terminal")
st.caption("Live multi-sector market overview tracking all 50 Nifty stocks with embedded 30D and 60D price trends.")

col_btn1, col_btn2 = st.columns([1, 5])
with col_btn1:
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()

def generate_svg_sparkline(prices, label="30D"):
    """Generates a responsive SVG sparkline with min/max bounds and gradient fill."""
    if not prices or len(prices) < 2:
        return ""
    min_p, max_p = min(prices), max(prices)
    p_range = max_p - min_p if max_p != min_p else 1.0

    width, height = 130, 38
    points = []
    for i, p in enumerate(prices):
        x = (i / (len(prices) - 1)) * width
        y = height - 4 - ((p - min_p) / p_range) * (height - 10)
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
        <polyline fill="none" stroke="{color}" stroke-width="1.8" points="{pts_str}" />
        <circle cx="{width}" cy="{points[-1].split(',')[1]}" r="3" fill="{color}" />
        <text x="2" y="8" fill="#64748b" font-size="8" font-family="monospace">₹{min_p:.0f}</text>
        <text x="{width-35}" y="8" fill="#64748b" font-size="8" font-family="monospace">₹{max_p:.0f}</text>
    </svg>
    """
    return svg

@st.cache_data(ttl=1800)
def fetch_nifty50_data():
    tickers = list(NIFTY_50_METADATA.keys())
    df_raw = yf.download(tickers, period="70d", interval="1d", group_by="ticker", progress=False)
    
    rows = []
    for ticker, meta in NIFTY_50_METADATA.items():
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

with st.spinner("Fetching live prices for all Nifty 50 stocks..."):
    df = fetch_nifty50_data()

if df.empty:
    st.warning("Could not fetch market data. Please click Refresh.")
else:
    # Sidebar or top filter controls
    sectors = ["All Sectors"] + sorted(df["Sector"].unique().tolist())
    selected_sector = st.selectbox("Filter by Sector:", sectors)
    
    if selected_sector != "All Sectors":
        df_filtered = df[df["Sector"] == selected_sector]
    else:
        df_filtered = df

    st.markdown(f"Showing **{len(df_filtered)}** stocks")

    # Build HTML Terminal Table
    html_content = f"""
    <html>
    <head>
    <style>
        body {{
            background-color: #0b0f19;
            color: #e2e8f0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            margin: 0;
            padding: 0;
        }}
        .terminal-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }}
        .terminal-table th {{
            background-color: #131c31;
            color: #94a3b8;
            text-align: left;
            padding: 10px 14px;
            font-weight: 600;
            border-bottom: 1px solid #1e293b;
            text-transform: uppercase;
            font-size: 10px;
            letter-spacing: 0.05em;
        }}
        .terminal-table td {{
            padding: 11px 14px;
            border-bottom: 1px solid #131c31;
            vertical-align: middle;
        }}
        .terminal-table tr:hover {{
            background-color: #111827;
        }}
        .ticker-symbol {{
            color: #38bdf8;
            font-weight: 700;
            font-family: monospace;
            font-size: 14px;
        }}
        .company-name {{
            color: #f8fafc;
            font-weight: 500;
        }}
        .sector-tag {{
            color: #94a3b8;
            font-size: 11px;
            background: #1e293b;
            padding: 3px 6px;
            border-radius: 4px;
            display: inline-block;
        }}
        .price-val {{
            font-family: monospace;
            font-weight: 600;
            color: #f1f5f9;
            font-size: 14px;
        }}
        .positive {{
            color: #22c55e;
            font-weight: 600;
            font-family: monospace;
        }}
        .negative {{
            color: #ef4444;
            font-weight: 600;
            font-family: monospace;
        }}
    </style>
    </head>
    <body>
    <table class="terminal-table">
        <thead>
            <tr>
                <th>Ticker</th>
                <th>Company Name</th>
                <th>Sector</th>
                <th>Current Price</th>
                <th>24H Change</th>
                <th>30-Day Trend (₹)</th>
                <th>60-Day Trend (₹)</th>
            </tr>
        </thead>
        <tbody>
    """
    
    for _, row in df_filtered.iterrows():
        change_class = "positive" if row["Change"] >= 0 else "negative"
        sign_str = "+" if row["Change"] >= 0 else ""
        
        svg_30 = generate_svg_sparkline(row["30D"], label="30D")
        svg_60 = generate_svg_sparkline(row["60D"], label="60D")
        
        html_content += f"""
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
        
    html_content += "</tbody></table></body></html>"
    
    # Render full height scrollable component
    components.html(html_content, height=750, scrolling=True)
