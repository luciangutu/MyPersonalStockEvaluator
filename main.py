import streamlit as st
from get_data import get_stock_data

st.set_page_config(layout="wide")
st.title("main")
st.sidebar.title("Config")

# Required Rate slider
required_rate = st.sidebar.slider(
    "Required Rate (%)",
    min_value=5,
    max_value=12,
    value=st.session_state.get("required_rate", 7),
    step=1,
    help="The required rate of return (discount rate) typically reflects the Weighted Average Cost of Capital (WACC) or the investor's hurdle rate.",
    key="required_rate"
)

# Perpetual Growth Rate slider
perpetual_rate = st.sidebar.slider(
    "Perpetual Growth Rate (%)",
    min_value=1,
    max_value=3,
    value=st.session_state.get("perpetual_rate", 2),
    step=1,
    help="Reflects long-term growth after the projection period, generally tied to GDP growth or inflation.",
    key="perpetual_rate"
)

# Cash Flow Growth Rate slider
cash_flow_growth_rate = st.sidebar.slider(
    "Cash Flow Growth Rate (%)",
    min_value=2,
    max_value=10,
    value=st.session_state.get("cash_flow_growth_rate", 3),
    step=1,
    help="Reflects expected annual growth in free cash flow during the projection period.",
    key="cash_flow_growth_rate"
)

ticker = st.text_input("Enter stock ticker", placeholder="e.g., MSFT")
if ticker:
    stock_data = get_stock_data(ticker)
    if "error" in stock_data:
        st.error(stock_data["error"])
    else:
        c1, c2 = st.columns(2, gap='large')
        with c1:
            st.subheader(f":coffee: {stock_data.get('longName', ticker)}")
            st.markdown(f"### Current Price: **${stock_data.get('currentPrice', 'N/A')}**")

            st.subheader(":umbrella_with_rain_drops: Discounted Cash Flow")
            try:
                dcf_value = stock_data.get("dcf")
                st.metric("Fair Value per Share (DCF)", f"${dcf_value}")

                current_price = float(stock_data.get("currentPrice", 0))

                if current_price == 0:
                    st.warning("Current price information is missing.")
                else:
                    percentage_diff = ((dcf_value - current_price) / current_price) * 100

                    if dcf_value > current_price:
                        st.success(f"The stock is undervalued based on DCF! ({percentage_diff:.2f}%)")
                    else:
                        st.warning(f"The stock is overvalued based on DCF. ({percentage_diff:.2f}%)")
            except Exception as e:
                st.error(f"Error in DCF analysis: {e}")
        with c2:
            # Positives and Negatives
            st.subheader(":white_check_mark: Positives")
            positives = []
            if stock_data.get("earningsQuarterlyGrowth") is not None and stock_data["earningsQuarterlyGrowth"] > 0:
                positives.append(f"Earnings Quarterly Growth: {stock_data['earningsQuarterlyGrowth'] * 100:.2f}%")
            if stock_data.get("grossProfits") is not None and stock_data["grossProfits"] > 0:
                positives.append(f"Gross Profits: ${stock_data['grossProfits']:,}")
            if stock_data.get("freeCashflow") is not None and stock_data["freeCashflow"] > 0:
                positives.append(f"Free Cash Flow: ${stock_data['freeCashflow']:,}")
            st.write("\n\n".join(positives) if positives else "No notable positives.")

            st.subheader(":heavy_exclamation_mark: Negatives")
            negatives = []
            if stock_data.get("debtToEquity") is not None and float(stock_data["debtToEquity"]) > 100:
                negatives.append(f"High Debt-to-Equity: {stock_data['debtToEquity']}")
            if stock_data.get("priceToBook") is not None and float(stock_data["priceToBook"]) > 1.5:
                negatives.append(f"Price-to-Book is high: {stock_data['priceToBook']:.2f}")
            st.write("\n\n".join(negatives) if negatives else "No notable negatives.")

        st.divider()
        # Key Financial Metrics
        st.subheader(":sparkles: Key Metrics")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Assets", f"${stock_data.get('totalAssets', 'N/A'):,}")
            st.metric("Total Liabilities", f"${stock_data.get('totalLiabilities', 'N/A'):,}")
            st.metric("Shares Outstanding", f"{stock_data.get('sharesOutstanding', 'N/A'):,}")
        with col2:
            st.metric("Trailing PE", f"{stock_data.get('trailingPE', 'N/A'):.2f}")
            st.metric("Forward PE", f"{stock_data.get('forwardPE', 'N/A'):.2f}")
            st.metric("Book Value", f"${stock_data.get('bookValue', 'N/A'):.2f}")


