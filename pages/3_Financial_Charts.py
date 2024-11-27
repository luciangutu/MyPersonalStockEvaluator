import yfinance as yf
import streamlit as st
import pandas as pd
import logging


st.set_page_config(layout="wide")

if "ticker" in st.session_state:
    stock_ticker = st.session_state.get("ticker", "MSFT")
elif "ticker" in st.query_params:
    stock_ticker = st.query_params.get("ticker", None)
else:
    stock_ticker = ""

try:
    stock = yf.Ticker(stock_ticker)
    balance_sheet = stock.balance_sheet
    financials = stock.financials
    cashflow = stock.cashflow
except Exception as e:
    st.write(f"Error fetching stock data: {e}")
    
# Convert DataFrame to plot-friendly format
balance_sheet = balance_sheet.T  # Transpose for better plotting
balance_sheet.index = pd.to_datetime(balance_sheet.index)  # Ensure proper datetime format
balance_sheet.index = balance_sheet.index.strftime('%Y-%m-%d')  # Format to include year

# Convert DataFrame to plot-friendly format
financials = financials.T  # Transpose for better plotting
financials.index = pd.to_datetime(financials.index)  # Ensure proper datetime format
financials.index = financials.index.strftime('%Y-%m-%d')  # Format to include year

# Convert DataFrame to plot-friendly format
cashflow = cashflow.T  # Transpose for better plotting
cashflow.index = pd.to_datetime(cashflow.index)  # Ensure proper datetime format
cashflow.index = cashflow.index.strftime('%Y-%m-%d')  # Format to include year

# logging.info(dir(cashflow))
# logging.info(cashflow.columns)


financials_metrics = st.multiselect(
    "Financials Metrics",
    financials.columns,
)

balance_sheet_metrics = st.multiselect(
    "Balance Sheet Metrics",
    balance_sheet.columns,
)

cashflow_metrics = st.multiselect(
    "CashFlow Metrics",
    cashflow.columns,
)

elements = sorted(balance_sheet_metrics + cashflow_metrics + financials_metrics)

if len(elements) > 0:
    for element in elements:
        st.subheader(element)
        try:
            st.line_chart(cashflow[element])
        except KeyError:
            try:
                st.line_chart(balance_sheet[element][-10:], use_container_width=True)
            except KeyError:
                st.line_chart(financials[element])
else:
    st.warning(f"Pick metrics to chart for {stock_ticker}!")