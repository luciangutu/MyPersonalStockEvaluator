import streamlit as st
import pandas as pd
from dcf import dcf
from get_data import get_stock_data
from db import create_db, add_stock, remove_stock, get_all_stocks

create_db()
st.set_page_config(layout="wide")

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
    stocks = get_all_stocks()

    if stocks:
        data = []
        for stock in stocks:
            ticker = stock[0]
            stock_data = get_stock_data(ticker)
            current_price = stock_data.get("currentPrice", 0)
            dcf_value = stock_data.get("dcf", 0)

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

        # Display the table with styling
        st.dataframe(df.style.apply(color_row, axis=1), height=1000)
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