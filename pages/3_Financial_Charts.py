import fmp_client as yf
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

if not stock_ticker:
    st.warning("Please enter a stock ticker")
    st.stop()

try:
    stock = yf.Ticker(stock_ticker)
    balance_sheet = stock.balance_sheet
    financials = stock.financials
    cashflow = stock.cashflow

except Exception as e:
    st.error(f"Error fetching stock data: {e}")
    st.stop()

# Show data availability status
st.info(f"**Data availability for {stock_ticker}:**")
col1, col2, col3 = st.columns(3)
with col1:
    if balance_sheet.empty:
        st.error("❌ Balance Sheet: Not available")
    else:
        st.success(f"✅ Balance Sheet: {balance_sheet.shape[1]} periods")
with col2:
    if financials.empty:
        st.error("❌ Income Statement: Not available")
    else:
        st.success(f"✅ Income Statement: {financials.shape[1]} periods")
with col3:
    if cashflow.empty:
        st.error("❌ Cash Flow: Not available")
    else:
        st.success(f"✅ Cash Flow: {cashflow.shape[1]} periods")

# Check if all dataframes are empty
if balance_sheet.empty and financials.empty and cashflow.empty:
    st.error(f"No financial data available for {stock_ticker}. Free tier may not support this stock.")
    st.stop()

st.divider()

# Convert DataFrame to plot-friendly format (only if not empty)
if not balance_sheet.empty:
    balance_sheet = balance_sheet.T
    if len(balance_sheet.index) > 0:
        balance_sheet.index = pd.to_datetime(balance_sheet.index)
        balance_sheet.index = balance_sheet.index.strftime('%Y-%m-%d')

if not financials.empty:
    financials = financials.T
    if len(financials.index) > 0:
        financials.index = pd.to_datetime(financials.index)
        financials.index = financials.index.strftime('%Y-%m-%d')

if not cashflow.empty:
    cashflow = cashflow.T
    if len(cashflow.index) > 0:
        cashflow.index = pd.to_datetime(cashflow.index)
        cashflow.index = cashflow.index.strftime('%Y-%m-%d')

# logging.info(dir(cashflow))
# logging.info(cashflow.columns)


financials_metrics = st.multiselect(
    "Financials Metrics",
    financials.columns if not financials.empty else [],
)

balance_sheet_metrics = st.multiselect(
    "Balance Sheet Metrics",
    balance_sheet.columns if not balance_sheet.empty else [],
)

cashflow_metrics = st.multiselect(
    "CashFlow Metrics",
    cashflow.columns if not cashflow.empty else [],
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