import streamlit as st
import yfinance as yf
import pandas as pd
import streamlit.components.v1 as components
from datetime import datetime, date

# Page Configuration
st.set_page_config(
    page_title="Nifty 100 Pro Terminal",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Styling for Market Indices Bar
st.markdown("""
<style>
    .index-card {
        background-color: #131c31;
        border: 1px solid #1e293b;
        padding: 10px 14px;
        border-radius: 8px;
        text-align: center;
        font-family: monospace;
    }
    .index-name {
        color: #94a3b8;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
    }
    .index-val {
        color: #f1f5f9;
        font-size: 15px;
        font-weight: 700;
        margin-top: 2px;
    }
    .pos { color: #22c55e; font-size: 12px; font-weight: 600; }
    .neg { color: #ef4444; font-size: 12px; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# Nifty 100 Master Watchlist
NIFTY_100_TICKERS = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
    "BHARTIARTL.NS", "SBIN.NS", "ITC.NS", "LTIM.NS", "HINDUNILVR.NS",
    "LT.NS", "BAJFINANCE.NS", "MARUTI.NS", "SUNPHARMA.NS", "TATASTEEL.NS",
    "M&M.NS", "KOTAKBANK.NS", "TITAN.NS", "NTPC.NS", "AXISBANK.NS",
    "ADANIENT.NS", "ADANIPORTS.NS", "ULTRACEMCO.NS", "POWERGRID.NS", "TATAMOTORS.NS",
    "BAJAJFINSV.NS", "COALINDIA.NS", "ASIANPAINT.NS", "ONGC.NS", "HCLTECH.NS",
    "GRASIM.NS", "BAJAJ-AUTO.NS", "TECHM.NS", "WIPRO.NS", "BRITANNIA.NS",
    "CIPLA.NS", "DRREDDY.NS", "EICHERMOT.NS", "BPCL.NS", "HEROMOTOCO.NS",
    "DIVISLAB.NS", "TATACONSUM.NS", "APOLLOHOSP.NS", "HINDALCO.NS", "INDUSINDBK.NS",
    "JSWSTEEL.NS", "SBILIFE.NS", "HDFCLIFE.NS", "BEL.NS", "TRENT.NS",
    "ABB.NS", "ADANIGREEN.NS", "ADANIPOWER.NS", "AMBUJACEM.NS", "ATGL.NS",
    "BANKBARODA.NS", "BHEL.NS", "CANBK.NS", "CHOLAFIN.NS", "DABUR.NS",
    "DLF.NS", "GAIL.NS", "GODREJCP.NS", "HAVELLS.NS", "ICICIGI.NS",
    "ICICIPRULI.NS", "IOC.NS", "IRCTC.NS", "JINDALSTEL.NS", "LICI.NS",
    "MARICO.NS", "MOTHERSON.NS", "NAUKRI.NS", "NESTLEIND.NS", "PFC.NS",
    "PIDILITIND.NS", "PNB.NS", "RECLTD.NS", "SBICARD.NS", "SHREECEM.NS",
    "SIEMENS.NS", "SRF.NS", "TATAPOWER.NS", "TVSMOTOR.NS", "UPL.NS",
    "VEDL.NS", "ZOMATO.NS", "ZYDUSLIFE.NS"
]

st.title("⚡ Nifty 100 Pro Market Terminal")
st.caption("Live professional stock screener with 30D/60D sparklines, earnings calendar alerts, technical recommendations, and analyst news links.")

# Fetch Global & Domestic Indices
@st.cache_data(ttl=300)
def fetch_indices():
    index_tickers = {
        "Nifty 50": "^NSEI",
        "Bank Nifty": "^NSEBANK",
        "India VIX": "^INDIAVIX",
        "Nasdaq": "^IXIC",
        "Dow Jones": "^DJI"
    }
    data = {}
    for name, ticker in index_tickers.items():
        try:
            hist = yf.Ticker(ticker).history(period="2d")
            if len(hist) >= 2:
                curr = float(hist['Close'].iloc[-1])
                prev = float(hist['Close'].iloc[-2])
                chg = ((curr - prev) / prev) * 100
                data[name] = {"val": curr, "chg": chg}
        except Exception:
            continue
    return data

indices_data = fetch_indices()
if indices_data:
    cols = st.columns(5)
    for i, (name, info) in enumerate(indices_data.items()):
        with cols[i]:
            chg_class = "pos" if info["chg"] >= 0 else "neg"
            sign = "+" if info["chg"] >= 0 else ""
            st.markdown(f"""
                <div class="index-card">
                    <div class="index-name">{name}</div>
                    <div class="index-val">{info['val']:,.2f}</div>
                    <div class="{chg_class}">{sign}{info['chg']:.2f}%</div>
                </div>
            """, unsafe_allow_html=True)

st.divider()

col_btn1, col_btn2 = st.columns([1, 5])
with col_btn1:
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()

def generate_svg_sparkline(prices, label="30D"):
    if not prices or len(prices) < 2:
        return ""
    min_p, max_p = min(prices), max(prices)
    p_range = max_p - min_p if max_p != min_p else 1.0

    width, height = 120, 35
    points = []
    for i, p in enumerate(prices):
        x = (i / (len(prices) - 1)) * width
        y = height - 4 - ((p - min_p) / p_range) * (height - 8)
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
        <circle cx="{width}" cy="{points[-1].split(',')[1]}" r="2.5" fill="{color}" />
        <text x="2" y="8" fill="#64748b" font-size="7.5" font-family="monospace">₹{min_p:.0f}</text>
        <text x="{width-32}" y="8" fill="#64748b" font-size="7.5" font-family="monospace">₹{max_p:.0f}</text>
    </svg>
    """
    return svg

@st.cache_data(ttl=1800)
def fetch_terminal_data():
    df_raw = yf.download(NIFTY_100_TICKERS, period="70d", interval="1d", group_by="ticker", progress=False)
    
    today = date.today()
    rows = []
    for ticker in NIFTY_100_TICKERS:
        try:
            t_obj = yf.Ticker(ticker)
            data = df_raw[ticker].dropna()
            if len(data) < 60:
                continue
            
            closes = data['Close'].values
            curr_price = float(closes[-1])
            prev_price = float(closes[-2])
            change_pct = ((curr_price - prev_price) / prev_price) * 100
            
            p30 = closes[-30:]
            p60 = closes[-60:]
            
            # Earnings Date Check
            earnings_date_str = "Not Available"
            is_released = False
            try:
                calendar = t_obj.calendar
                if calendar is not None and "Earnings Date" in calendar:
                    ed_list = calendar["Earnings Date"]
                    if len(ed_list) > 0:
                        ed = pd.to_datetime(ed_list[0]).date()
                        earnings_date_str = ed.strftime("%d %b %Y")
                        # If earnings date is today or in the past 2 days, mark as released/live alert
                        if (today - ed).days >= 0 and (today - ed).days <= 3:
                            is_released = True
            except Exception:
                pass
            
            delta = data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            rsi_series = 100 - (100 / (1 + rs))
            rsi = float(rsi_series.iloc[-1]) if not rsi_series.isna().iloc[-1] else 50.0
            
            sma50 = float(data['Close'].rolling(50).mean().iloc[-1])
            p30_ret = ((curr_price - p30[0]) / p30[0]) * 100
            
            if rsi < 35 and curr_price > sma50:
                signal = "STRONG BUY"
            elif rsi < 45 and p30_ret > 0:
                signal = "BUY"
            elif rsi > 70:
                signal = "SELL"
            else:
                signal = "HOLD"
                
            clean_sym = ticker.replace(".NS", "")
            
            rows.append({
                "Symbol": clean_sym,
                "Price": curr_price,
                "Change": change_pct,
                "30D": [float(x) for x in p30],
                "60D": [float(x) for x in p60],
                "Signal": signal,
                "EarningsDate": earnings_date_str,
                "IsReleased": is_released
            })
        except Exception:
            continue
            
    return pd.DataFrame(rows)

with st.spinner("Fetching live prices, earnings calendar & computing technical signals..."):
    df = fetch_terminal_data()

if df.empty:
    st.warning("Could not fetch market data. Please click Refresh.")
else:
    signals_list = ["ALL", "STRONG BUY", "BUY", "HOLD", "SELL"]
    selected_sig = st.selectbox("Filter Recommendation Signal:", signals_list)
    
    if selected_sig != "ALL":
        df_filtered = df[df["Signal"] == selected_sig]
    else:
        df_filtered = df

    st.markdown(f"Displaying **{len(df_filtered)}** stocks")

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
            padding: 11px 14px;
            font-weight: 600;
            border-bottom: 1px solid #1e293b;
            text-transform: uppercase;
            font-size: 10px;
            letter-spacing: 0.05em;
            cursor: pointer;
            user-select: none;
        }}
        .terminal-table th:hover {{
            background-color: #1e293b;
            color: #f8fafc;
        }}
        .terminal-table td {{
            padding: 10px 14px;
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
        .badge-strong-buy {{ color: #22c55e; background: rgba(34,197,94,0.1); padding: 4px 8px; border-radius: 4px; font-weight: 700; font-size: 11px; }}
        .badge-buy {{ color: #38bdf8; background: rgba(56,189,248,0.1); padding: 4px 8px; border-radius: 4px; font-weight: 700; font-size: 11px; }}
        .badge-hold {{ color: #eab308; background: rgba(234,179,8,0.1); padding: 4px 8px; border-radius: 4px; font-weight: 700; font-size: 11px; }}
        .badge-sell {{ color: #ef4444; background: rgba(239,68,68,0.1); padding: 4px 8px; border-radius: 4px; font-weight: 700; font-size: 11px; }}
        
        /* Blinking Animation for Released Results */
        @keyframes glowing-blink {{
            0% {{ color: #ef4444; text-shadow: 0 0 2px #ef4444; }}
            50% {{ color: #22c55e; text-shadow: 0 0 8px #22c55e; }}
            100% {{ color: #38bdf8; text-shadow: 0 0 2px #38bdf8; }}
        }}
        .blinking-result {{
            font-weight: 800;
            font-size: 12px;
            animation: glowing-blink 1.2s infinite;
            background: rgba(56, 189, 248, 0.15);
            padding: 4px 8px;
            border-radius: 4px;
            display: inline-block;
        }}
        .normal-result {{
            color: #94a3b8;
            font-family: monospace;
            font-size: 12px;
        }}
        
        /* Tooltip styling */
        .tooltip {{
            position: relative;
            display: inline-block;
            cursor: pointer;
        }}
        .tooltip .tooltiptext {{
            visibility: hidden;
            width: 210px;
            background-color: #1e293b;
            color: #f8fafc;
            text-align: left;
            border-radius: 6px;
            padding: 8px;
            position: absolute;
            z-index: 1;
            bottom: 125%;
            left: 50%;
            margin-left: -105px;
            opacity: 0;
            transition: opacity 0.3s;
            font-size: 11px;
            border: 1px solid #334155;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
        }}
        .tooltip:hover .tooltiptext {{
            visibility: visible;
            opacity: 1;
        }}

        .ext-link {{
            color: #94a3b8;
            text-decoration: none;
            background: #1e293b;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 11px;
            margin-right: 4px;
            transition: all 0.2s;
        }}
        .ext-link:hover {{
            background: #334155;
            color: #38bdf8;
        }}
    </style>
    <script>
        function sortTable(n) {{
            var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
            table = document.getElementById("stockTable");
            switching = true;
            dir = "asc";
            while (switching) {{
                switching = false;
                rows = table.rows;
                for (i = 1; i < (rows.length - 1); i++) {{
                    shouldSwitch = false;
                    x = rows[i].getElementsByTagName("TD")[n];
                    y = rows[i + 1].getElementsByTagName("TD")[n];
                    var xVal = x.textContent || x.innerText;
                    var yVal = y.textContent || y.innerText;
                    
                    var xNum = parseFloat(xVal.replace(/[^0-9.-]+/g,""));
                    var yNum = parseFloat(yVal.replace(/[^0-9.-]+/g,""));
                    
                    if (!isNaN(xNum) && !isNaN(yNum)) {{
                        if (dir == "asc") {{
                            if (xNum > yNum) {{ shouldSwitch = true; break; }}
                        }} else if (dir == "desc") {{
                            if (xNum < yNum) {{ shouldSwitch = true; break; }}
                        }}
                    }} else {{
                        if (dir == "asc") {{
                            if (xVal.toLowerCase() > yVal.toLowerCase()) {{ shouldSwitch = true; break; }}
                        }} else if (dir == "desc") {{
                            if (xVal.toLowerCase() < yVal.toLowerCase()) {{ shouldSwitch = true; break; }}
                        }}
                    }}
                }}
                if (shouldSwitch) {{
                    rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
                    switching = true;
                    switchcount++;
                }} else {{
                    if (switchcount == 0 && dir == "asc") {{
                        dir = "desc";
                        switching = true;
                    }}
                }}
            }}
        }}
    </script>
    </head>
    <body>
    <table id="stockTable" class="terminal-table">
        <thead>
            <tr>
                <th onclick="sortTable(0)">Ticker ↕</th>
                <th onclick="sortTable(1)">Current Price ↕</th>
                <th onclick="sortTable(2)">24H Change ↕</th>
                <th>30-Day Trend (₹)</th>
                <th>60-Day Trend (₹)</th>
                <th onclick="sortTable(5)">Recommendation ↕</th>
                <th onclick="sortTable(6)">Earnings Date / Status ↕</th>
                <th>Analyst & ZeeBiz News</th>
            </tr>
        </thead>
        <tbody>
    """
    
    for _, row in df_filtered.iterrows():
        change_class = "positive" if row["Change"] >= 0 else "negative"
        sign_str = "+" if row["Change"] >= 0 else ""
        
        svg_30 = generate_svg_sparkline(row["30D"], label="30D")
        svg_60 = generate_svg_sparkline(row["60D"], label="60D")
        
        sig = row["Signal"]
        badge_class = "badge-hold"
        if sig == "STRONG BUY": badge_class = "badge-strong-buy"
        elif sig == "BUY": badge_class = "badge-buy"
        elif sig == "SELL": badge_class = "badge-sell"
        
        sym = row["Symbol"]
        screener_url = f"https://www.screener.in/company/{sym}/consolidated/"
        zeebiz_url = f"https://www.zeebiz.com/search?q={sym}"
        
        is_rel = row["IsReleased"]
        ed_val = row["EarningsDate"]
        
        if is_rel:
            earnings_display = f"""<div class="tooltip"><span class="blinking-result">🚨 LIVE RESULT OUT!</span><span class="tooltiptext"><b>{sym} Earnings Released!</b><br>Date: {ed_val}<br>Check quarterly financial results on Screener & Moneycontrol.</span></div>"""
        else:
            earnings_display = f"""<div class="tooltip"><span class="normal-result">{ed_val}</span><span class="tooltiptext"><b>{sym} Earnings Calendar</b><br>Scheduled Date: {ed_val}<br>Status: Upcoming / Pending</span></div>"""
        
        html_content += f"""
            <tr>
                <td><span class="ticker-symbol">{sym}</span></td>
                <td><span class="price-val">₹{row['Price']:,.2f}</span></td>
                <td><span class="{change_class}">{sign_str}{row['Change']:.2f}%</span></td>
                <td>{svg_30}</td>
                <td>{svg_60}</td>
                <td><span class="{badge_class}">{sig}</span></td>
                <td>
                    {earnings_display}
                    <div style="margin-top: 4px;">
                        <a href="{screener_url}" target="_blank" class="ext-link">Results</a>
                    </div>
                </td>
                <td>
                    <a href="{zeebiz_url}" target="_blank" class="ext-link">ZeeBiz News</a>
                </td>
            </tr>
        """
        
    html_content += "</tbody></table></body></html>"
    
    components.html(html_content, height=850, scrolling=True)
