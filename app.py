import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import ta

st.set_page_config(page_title="Grok World-Class Scanner", layout="wide")
st.title("🚀 Grok World-Class Automation Scanner & Backtester")
st.markdown("**Professional • Multi-Symbol • Full Backtester • Live Charts**")

# Primary symbols
symbols = ["GC=F", "EURUSD=X", "CL=F", "^GDAXI", "^GSPC", "BTC-USD", "NQ=F"]

st.sidebar.header("Settings")
selected_symbols = st.sidebar.multiselect("Select Symbols", symbols, default=symbols)
timeframe = st.sidebar.selectbox("Timeframe", ["1h", "4h", "1d"], index=1)
capital = st.sidebar.number_input("Starting Capital ($)", value=100000, step=10000)
risk_pct = st.sidebar.slider("Risk per Trade (%)", 0.5, 5.0, 2.0)

# Scanner
def scan():
    results = []
    for sym in selected_symbols:
        data = yf.download(sym, period="6mo", interval=timeframe)
        if len(data) < 100:
            continue
            
        data['SMA50'] = ta.trend.sma_indicator(data['Close'], 50)
        data['SMA200'] = ta.trend.sma_indicator(data['Close'], 200)
        data['RSI'] = ta.momentum.rsi(data['Close'], 14)
        data['VolAvg'] = data['Volume'].rolling(20).mean()
        
        latest = data.iloc[-1]
        prev = data.iloc[-2]
        
        golden_cross = (latest['SMA50'] > latest['SMA200']) and (prev['SMA50'] <= prev['SMA200'])
        volume_surge = latest['Volume'] > 1.5 * latest['VolAvg']
        rsi_condition = latest['RSI'] < 35
        
        if golden_cross and volume_surge and rsi_condition:
            size = round((capital * risk_pct / 100) / latest['Close'], 2)
            results.append({
                "Symbol": sym,
                "Signal": "BUY",
                "Price": round(latest['Close'], 4),
                "Size": size,
                "Reason": "Golden Cross + Volume + RSI"
            })
    return pd.DataFrame(results)

# Backtester
def backtest(sym):
    data = yf.download(sym, period="6mo", interval=timeframe)
    data['SMA50'] = ta.trend.sma_indicator(data['Close'], 50)
    data['SMA200'] = ta.trend.sma_indicator(data['Close'], 200)
    data['Signal'] = (data['SMA50'] > data['SMA200']).astype(int).shift(1)
    data['Returns'] = data['Close'].pct_change()
    data['Strategy'] = data['Signal'] * data['Returns']
    equity = (1 + data['Strategy']).cumprod()
    
    total_return = (equity.iloc[-1] - 1) * 100
    max_dd = ((equity / equity.cummax()) - 1).min() * 100
    win_rate = (data['Strategy'] > 0).mean() * 100
    
    return {
        "Symbol": sym,
        "Total Return (%)": round(total_return, 2),
        "Max Drawdown (%)": round(max_dd, 2),
        "Win Rate (%)": round(win_rate, 2),
        "Equity": equity
    }

# UI Tabs
tab1, tab2, tab3 = st.tabs(["🔍 Scanner", "📈 Backtester", "📊 Live Charts"])

with tab1:
    if st.button("Run Full Market Scan"):
        with st.spinner("Scanning..."):
            df = scan()
            if not df.empty:
                st.success(f"Found {len(df)} buy signals!")
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No signals today.")

with tab2:
    st.subheader("Backtest Results")
    for sym in selected_symbols:
        result = backtest(sym)
        st.write(f"**{sym}**")
        st.write(result)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=result["Equity"].index, y=result["Equity"], name="Equity Curve"))
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("Live Charts")
    selected = st.selectbox("Choose Symbol", selected_symbols)
    data = yf.download(selected, period="3mo", interval="1h")
    fig = go.Figure(data=[go.Candlestick(x=data.index,
                                         open=data['Open'],
                                         high=data['High'],
                                         low=data['Low'],
                                         close=data['Close'])])
    fig.update_layout(title=f"{selected} Live Chart", xaxis_title="Date", yaxis_title="Price")
    st.plotly_chart(fig, use_container_width=True)

st.caption("World-Class Automation Dashboard • Built live for you • Zero cost")
