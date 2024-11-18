import yfinance as yf
import streamlit as st
import pandas as pd


st.set_page_config(layout="wide")


def display_charts(_elements, group):
    mid = len(_elements) // 2

    with col1:
        for element in _elements[:mid]:
            st.subheader(element)
            st.line_chart(group[element])

    with col2:
        for element in _elements[mid:]:
            st.subheader(element)
            st.line_chart(group[element])



stock_ticker = st.query_params.get("ticker", None)

if not stock_ticker:
    stock_ticker = st.session_state.get("ticker", "MSFT")

st.markdown(f"""
1. [Balance Sheet for {stock_ticker}](#balance-sheet-for-{stock_ticker.lower()})
2. [Cash Flow for {stock_ticker}](#cash-flow-for-{stock_ticker.lower()})
""")

try:
    stock = yf.Ticker(stock_ticker)
    balance_sheet = stock.get_balance_sheet()
    cash_flow = stock.cashflow
except Exception as e:
    st.write(f"Error fetching stock data: {e}")
    
# Convert DataFrame to plot-friendly format
balance_sheet = balance_sheet.T  # Transpose for better plotting
balance_sheet.index = pd.to_datetime(balance_sheet.index)  # Ensure proper datetime format
balance_sheet.index = balance_sheet.index.strftime('%Y-%m-%d')  # Format to include year


# Convert DataFrame to plot-friendly format
cash_flow = cash_flow.T  # Transpose for better plotting
cash_flow.index = pd.to_datetime(cash_flow.index)  # Ensure proper datetime format
cash_flow.index = cash_flow.index.strftime('%Y-%m-%d')  # Format to include year

# Create charts for Balance Sheet
st.title(f"Balance Sheet for {stock_ticker}")

col1, col2 = st.columns(2, gap='large')

elements = sorted(list(balance_sheet.columns))

if len(elements) > 0:
    display_charts(elements, balance_sheet)
else:
    st.warning(f"Balance sheet is empty for {stock_ticker}!")

st.divider()
st.title(f"Cash Flow for {stock_ticker}")
col1, col2 = st.columns(2, gap='large')


elements = sorted(list(cash_flow.columns))

if len(elements) > 0:
    display_charts(elements, cash_flow)
else:
    st.warning(f"Cash Flow is empty for {stock_ticker}!")