import streamlit as st
import yfinance as yf


st.set_page_config(layout="wide")

if "ticker" not in st.session_state:
    st.session_state.ticker = ""

ticker = st.text_input(
    "Enter stock ticker", 
    placeholder="e.g., MSFT", 
    value=st.session_state.ticker, 
    key="ticker"
)

if ticker:
    stock = yf.Ticker(ticker)

    info = stock.info
    balance_sheet = stock.balance_sheet
    financials = stock.financials
    cashflow = stock.cashflow

    # st.subheader(f":coffee: {info.get('longName', ticker)}")

    # table_header = """
    # <table style="width:100%; border-collapse:collapse;">
    # <thead>
    # <tr style="border-bottom:2px solid black;">
    # <th style="text-align:left;">Metric</th>
    # <th style="text-align:left;">Value</th>
    # </tr>
    # </thead>
    # <tbody>
    # """