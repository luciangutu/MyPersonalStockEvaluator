import fmp_client as yf
import streamlit as st
import pandas as pd

# Define the stock symbols to check
symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']

# Manual RSI calculation
def calculate_rsi(series, period=14):
    """Calculate RSI manually using pandas"""
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Function to calculate indicators
def get_technical_indicators(stock):
    df = yf.download(stock, period="6mo", interval="1d")

    # Calculate moving averages
    df['50_MA'] = df['Close'].rolling(window=50).mean()
    df['200_MA'] = df['Close'].rolling(window=200).mean()

    # Calculate RSI manually
    df['RSI'] = calculate_rsi(df['Close'], period=14)

    # Calculate volume moving average
    df['50_Volume_MA'] = df['Volume'].rolling(window=50).mean()

    return df

# Function to check if the stock meets the rules
def check_stock(stock):
    df = get_technical_indicators(stock)

    # Check if we have enough data
    if df.empty or len(df) < 200:
        st.warning(f"⚠️ {stock}: Not enough data (need 200+ days)")
        return

    # Check if indicators are calculated (not NaN)
    if pd.isna(df['50_MA'].iloc[-1]) or pd.isna(df['200_MA'].iloc[-1]) or pd.isna(df['RSI'].iloc[-1]):
        st.warning(f"⚠️ {stock}: Indicators not calculated (insufficient data)")
        return

    # Check if in an uptrend (50-day MA above 200-day MA)
    if df['50_MA'].iloc[-1] > df['200_MA'].iloc[-1]:
        # Check if RSI is not overbought (below 70)
        if df['RSI'].iloc[-1] < 70:
            # Check for recent volume increase
            if df['Volume'].iloc[-1] > df['50_Volume_MA'].iloc[-1]:
                st.success(f"✅ {stock}: Meets criteria - potential buy")
            else:
                st.info(f"📊 {stock}: No volume confirmation")
        else:
            st.warning(f"🔴 {stock}: Overbought (RSI > 70)")
    else:
        st.info(f"📉 {stock}: Not in uptrend (50MA < 200MA)")

st.title("📈 Stock Screener")
st.write("Screening stocks for: Uptrend (50MA > 200MA), RSI < 70, Volume confirmation")

st.divider()

# Run the checks for all stocks
for symbol in symbols:
    check_stock(symbol)



