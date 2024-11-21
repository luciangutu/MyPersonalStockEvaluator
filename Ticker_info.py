import streamlit as st
from get_data import get_stock_data

st.set_page_config(layout="wide")
st.title("Ticker info")
st.sidebar.title("DCF Config")

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

ticker = st.text_input("Enter stock ticker", placeholder="e.g., MSFT", value=st.session_state.get("ticker", ""))
if ticker:
    if "ticker" not in st.session_state:
        st.session_state.ticker = ticker
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

            # Income Statement
            if stock_data.get("earningsQuarterlyGrowth") is not None and stock_data["earningsQuarterlyGrowth"] > 0:
                positives.append(f"Earnings Quarterly Growth: {stock_data['earningsQuarterlyGrowth'] * 100:.2f}%")
            if stock_data.get("grossProfits") is not None and stock_data["grossProfits"] > 0:
                positives.append(f"Gross Profits: ${stock_data['grossProfits']:,}")
            if stock_data.get("netIncomeToCommon") is not None and stock_data["netIncomeToCommon"] > 0:
                positives.append(f"Net Income: ${stock_data['netIncomeToCommon']:,}")

            # Cash Flow Statement
            if stock_data.get("freeCashflow") is not None and stock_data["freeCashflow"] > 0:
                positives.append(f"Free Cash Flow: ${stock_data['freeCashflow']:,}")
            if stock_data.get("operatingCashflow") is not None and stock_data["operatingCashflow"] > 0:
                positives.append(f"Operating Cash Flow: ${stock_data['operatingCashflow']:,}")

            # Balance Sheet
            if stock_data.get("totalCash") is not None and stock_data["totalCash"] > 0:
                positives.append(f"Total Cash: ${stock_data['totalCash']:,}")
            if stock_data.get("currentRatio") is not None and stock_data["currentRatio"] >= 1.5:
                positives.append(f"Healthy Current Ratio: {stock_data['currentRatio']:.2f}")

            # Return on Equity (ROE)
            if stock_data.get("returnOnEquity") is not None and stock_data["returnOnEquity"] > 0.15:
                positives.append(f"Strong ROE: {stock_data['returnOnEquity'] * 100:.2f}%")

            # Return on Investment (ROI)
            if stock_data.get("returnOnInvestment") is not None and stock_data["returnOnInvestment"] > 0.10:
                positives.append(f"Good ROI: {stock_data['returnOnInvestment'] * 100:.2f}%")

            st.write("\n\n".join(positives) if positives else "No notable positives.")

            st.subheader(":heavy_exclamation_mark: Negatives")
            negatives = []

            # Income Statement
            if stock_data.get("trailingEps") is not None and float(stock_data["trailingEps"]) < 2:
                negatives.append(f"Low EPS: {stock_data['trailingEps']}")
            if stock_data.get("revenueGrowth") is not None and stock_data["revenueGrowth"] < 0:
                negatives.append(f"Declining Revenue Growth: {stock_data['revenueGrowth'] * 100:.2f}%")

            # Balance Sheet
            if stock_data.get("debtToEquity") is not None and float(stock_data["debtToEquity"]) > 100:
                negatives.append(f"High Debt-to-Equity: {stock_data['debtToEquity']}")

            # Cash Flow Statement
            if stock_data.get("freeCashflow") is not None and stock_data["freeCashflow"] < 0:
                negatives.append(f"Negative Free Cash Flow: ${stock_data['freeCashflow']:,}")

            # Return on Equity (ROE)
            if stock_data.get("returnOnEquity") is not None and stock_data["returnOnEquity"] < 0.05:
                negatives.append(f"Low ROE: {stock_data['returnOnEquity'] * 100:.2f}%")

            # Return on Investment (ROI)
            if stock_data.get("returnOnInvestment") is not None and stock_data["returnOnInvestment"] < 0.05:
                negatives.append(f"Poor ROI: {stock_data['returnOnInvestment'] * 100:.2f}%")

            st.write("\n\n".join(negatives) if negatives else "No notable negatives.")

        st.divider()
        # Key Financial Metrics
        st.subheader(":sparkles: Key Metrics")
        col1, col2 = st.columns(2)
        with col1:
            total_assets = stock_data.get('totalAssets', None)
            total_liabilities = stock_data.get('totalLiabilities', None)
            shares_outstanding = stock_data.get('sharesOutstanding', None)

            if total_assets is not None:
                st.metric("Total Assets", f"${total_assets:,.2f}")
            else:
                st.metric("Total Assets", "N/A")

            if total_liabilities is not None:
                st.metric("Total Liabilities", f"${total_liabilities:,.2f}")
            else:
                st.metric("Total Liabilities", "N/A")
            
            if shares_outstanding is not None:
                st.metric("Shares Outstanding", f"${shares_outstanding:,.2f}")
            else:
                st.metric("Shares Outstanding", "N/A")
            
        with col2:
            trailing_pe = stock_data.get('trailingPE', None)
            forward_pe = stock_data.get('forwardPE', None)
            book_value = stock_data.get('bookValue', None)
            
            if trailing_pe is not None:
                st.metric("Trailing PE", f"{trailing_pe:.2f}")
            else:
                st.metric("Trailing PE", "N/A")

            if forward_pe is not None:
                st.metric("Forward PE", f"{forward_pe:.2f}")
            else:
                st.metric("Forward PE", "N/A")

            if book_value is not None:
                st.metric("Book Value", f"{book_value:.2f}")
            else:
                st.metric("Book Value", "N/A")

