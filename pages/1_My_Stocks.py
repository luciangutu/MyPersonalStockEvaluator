from db import create_db, add_stock, remove_stock, get_all_stocks_from_db
from Ticker_data import safe_round
from dcf import dcf
import streamlit as st
import pandas as pd
import yfinance as yf


create_db()

# Add stock function
def add_stock_to_db():
    ticker = st.text_input("Enter stock ticker to add:")
    if ticker:
        try:
            add_stock(ticker.upper())
            st.success(f"Added {ticker.upper()} to your list.")
        except Exception as e:
            st.error(f"Error adding stock info for {ticker}: {e}")

# Remove stock function
def remove_stock_from_db():
    ticker = st.text_input("Enter stock ticker to remove:")
    if ticker:
        remove_stock(ticker)
        st.success(f"Removed {ticker} from your list.")

# Display stock table with color coding for undervalued/overvalued
def display_stocks_table():
    stocks = get_all_stocks_from_db()

    if stocks:
        data = []
        for stock in stocks:
            ticker = stock[0]

            ystock = yf.Ticker(ticker)
            info = ystock.info
            cashflow = ystock.cashflow


            current_price = info.get("currentPrice", 0)
            free_cash_flow_data = cashflow.loc['Free Cash Flow'].tail(4)
            free_cash_flow = [
                safe_round(item) for item in free_cash_flow_data if item is not None
            ]
            free_cash_flow.reverse()  
            dcf_value = dcf(free_cash_flow, info['sharesOutstanding'])

            row = {
                "Stock Ticker": ticker,
                "Current Price": f"${current_price:,.2f}",
                "DCF Price": f"${dcf_value:,.2f}",
            }
            data.append(row)
        
        # Create the dataframe
        df = pd.DataFrame(data)

        df.index = df.index + 1

        # Apply color based on the price
        def color_row(row):
            styles = [''] * len(row)
            current_price = float(row["Current Price"].strip('$').replace(',', ''))
            dcf_value = float(row["DCF Price"].strip('$').replace(',', ''))
            
            if current_price < dcf_value:
                styles[1] = 'background-color: lime'
            else:
                styles[1] = 'background-color: lightcoral'
            
            return styles

        # Add hyperlinks for tickers
        df["Stock Ticker"] = df["Stock Ticker"].apply(
            lambda x: f'<a href="Charts?ticker={x}">{x}</a>'
        )

        # Style the DataFrame
        styled_df = (
            df.style.apply(color_row, axis=1)
            .set_properties(subset=["Stock Ticker"], **{"text-decoration": "none"})  # Prevent hyperlink formatting issues
        )

        # Render with HTML
        st.write(
            styled_df.to_html(escape=False),
            unsafe_allow_html=True,
        )

    else:
        st.write("No stocks in the list.")

# Page layout
st.title("Stock Portfolio")

# Add or Remove Stock
st.header("Add or Remove Stocks")
add_stock_to_db()
remove_stock_from_db()

# Display Stocks
st.header("Your Stock List")
display_stocks_table()