import yfinance as yf
import streamlit as st
import plotly.graph_objects as go


st.set_page_config(layout="wide")

stock_ticker = st.session_state.get("ticker", "MSFT")

ticker = st.text_input("Enter stock ticker", placeholder="e.g., MSFT", value=stock_ticker)
if ticker:
    st.session_state.ticker = ticker
    stock_ticker = ticker

try:
    stock = yf.Ticker(stock_ticker)
    df = stock.history(interval='1d',period='1y')
except Exception as e:
    st.write(f"Error fetching stock data: {e}")

fig = go.Figure(data=[go.Candlestick(
    x=df.index,
    open=df['Open'],
    high=df['High'],
    low=df['Low'],
    close=df['Close'],
    name=stock_ticker
)])

# Set layout options
fig.update_layout(
    title=f"{stock_ticker} Stock Price",
    xaxis_title="Date",
    yaxis_title="Price (USD)",
    xaxis_rangeslider_visible=False
)

st.plotly_chart(fig)