from dcf import dcf
import streamlit as st
import yfinance as yf
import logging
import math


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


st.set_page_config(layout="wide")
st.title("Ticker data")
st.sidebar.title("DCF Config")


def format_table_row(metric, value, is_positive):
    color = "green" if is_positive else "red" if is_positive is not None else "black"
    return f"<tr><td>{metric}</td><td style='color:{color}; font-weight:bold;'>{value}</td></tr>"


# Helper function to handle NaN values
def safe_round(value):
    return round(value) if value and not math.isnan(value) else None


# Required Rate slider
required_rate = st.sidebar.slider(
    "Required Rate (%)",
    min_value=5,
    max_value=12,
    value=st.session_state.get("required_rate", 6),
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


if "ticker" not in st.session_state:
    st.session_state.ticker = ""

def update_ticker():
    st.session_state.ticker = st.session_state.input_ticker

ticker = st.text_input(
    "Enter stock ticker", 
    placeholder="e.g., MSFT", 
    value=st.session_state.ticker, 
    key="input_ticker",
    on_change=update_ticker,
)

if ticker:
    st.session_state.ticker = ticker

    stock = yf.Ticker(ticker)

    info = stock.info
    balance_sheet = stock.balance_sheet
    financials = stock.financials
    cashflow = stock.cashflow

    st.subheader(f":coffee: {info.get('longName', ticker)}")

    # logging.info(dir(stock))

# INFO #######################################################################
    st.subheader(":sparkles: Info Metrics")

    # Create Info table structure
    table_header = """
    <table style="width:100%; border-collapse:collapse;">
    <thead>
    <tr style="border-bottom:2px solid black;">
    <th style="text-align:left;">Metric</th>
    <th style="text-align:left;">Value</th>
    </tr>
    </thead>
    <tbody>
    """

    table_rows = []
    info_dict = info

    # DCF
    free_cash_flow_data = cashflow.loc['Free Cash Flow'].tail(4)
    free_cash_flow = [
        safe_round(item) for item in free_cash_flow_data if item is not None
    ]
    free_cash_flow.reverse()  
    info_dict['dcf'] = dcf(free_cash_flow, info['sharesOutstanding'])

    # Iterate over metrics and populate the table
    for metric in list(info_dict.keys()):
        value = info_dict.get(metric, 0)
        if value is None:
            value = 0

        # Add positivity/negativity logic for specific metrics
        if metric == "trailingPE" and (10 <= value <= 20):
            table_rows.append(format_table_row(metric, value, True))
        elif metric == "trailingPE" and (value < 5 or value > 30):
            table_rows.append(format_table_row(metric, value, False))
        elif metric == "trailingPegRatio" and value < 1:
            table_rows.append(format_table_row(metric, f"{value:.2f}", True))
        elif metric == "trailingPegRatio" and value > 2:
            table_rows.append(format_table_row(metric, f"{value:.2f}", False))
        elif metric == "priceToSalesTrailing12Months" and value < 1:
            table_rows.append(format_table_row(metric, f"{value:.2f}", True))
        elif metric == "priceToSalesTrailing12Months" and value > 2:
            table_rows.append(format_table_row(metric, f"{value:.2f}", False))
        elif metric == "operatingMargins" and value > 0.20:
            table_rows.append(format_table_row(metric, f"{value * 100:.2f}%", True))
        elif metric == "operatingMargins" and value < 0.10:
            table_rows.append(format_table_row(metric, f"{value * 100:.2f}%", False))
        elif metric == "dcf" and value > info['currentPrice']:
            table_rows.append(format_table_row(metric, value, True))
        elif metric == "dcf" and value < info['currentPrice']:
            # percentage_diff = ((value - info['currentPrice']) / info['currentPrice']) * 100
            table_rows.append(format_table_row(metric, value, False))
        elif metric == "earningsQuarterlyGrowth" and value > 0:
            table_rows.append(format_table_row(metric, value, True))
        else:
            # Default handling for metrics without specific thresholds
            value_formatted = f"${value:,}" if isinstance(value, (int, float)) and value > 1e3 else str(value)
            table_rows.append(format_table_row(metric, value_formatted, is_positive=None))

    # Close table structure
    table_footer = "</tbody></table>"

    # Display the table
    st.markdown(table_header + "".join(table_rows) + table_footer, unsafe_allow_html=True)

    st.divider()


# Balance Sheet #######################################################################
    st.subheader(":sparkles: Balance Sheet Metrics")

    # Create Info table structure
    table_header = """
    <table style="width:100%; border-collapse:collapse;">
    <thead>
    <tr style="border-bottom:2px solid black;">
    <th style="text-align:left;">Metric</th>
    <th style="text-align:left;">Value</th>
    </tr>
    </thead>
    <tbody>
    """

    table_rows = []

    # Iterate over metrics and populate the table
    for metric in balance_sheet.index.tolist():
        try:
            value = balance_sheet.loc[metric].iloc[0]
            if value is None:
                value = 0
        except KeyError:
            value = 0

        # Add positivity/negativity logic for specific metrics
        if metric == "trailingPE" and (10 <= value <= 20):
            table_rows.append(format_table_row(metric, value, True))
        elif metric == "trailingPE" and (value < 5 or value > 30):
            table_rows.append(format_table_row(metric, value, False))
        else:
            # Default handling for metrics without specific thresholds
            value_formatted = f"${value:,}" if isinstance(value, (int, float)) and value > 1e3 else str(value)
            table_rows.append(format_table_row(metric, value_formatted, is_positive=None))

    # Close table structure
    table_footer = "</tbody></table>"

    # Display the table
    st.markdown(table_header + "".join(table_rows) + table_footer, unsafe_allow_html=True)

    st.divider()

# Financials #######################################################################
    st.subheader(":sparkles: Financials Metrics")

    # Create Info table structure
    table_header = """
    <table style="width:100%; border-collapse:collapse;">
    <thead>
    <tr style="border-bottom:2px solid black;">
    <th style="text-align:left;">Metric</th>
    <th style="text-align:left;">Value</th>
    </tr>
    </thead>
    <tbody>
    """
    table_rows = []
    try:
        sales_growth_1y = (financials.loc['Total Revenue'].iloc[0] / financials.loc['Total Revenue'].iloc[1] - 1) * 100
        sales_growth_3y = (financials.loc['Total Revenue'].iloc[0] / financials.loc['Total Revenue'].iloc[3] - 1) * 100
    except KeyError:
        sales_growth_1y = sales_growth_3y = 0

    try:
        operating_margin = (financials.loc['Operating Income'].iloc[0] / financials.loc['Total Revenue'].iloc[0]) * 100
    except KeyError:
        operating_margin = 0

    calculated_metrics = {
        'Sales Growth 1Y': f'{sales_growth_1y:.2f}%',
        'Sales Growth 3Y': f'{sales_growth_3y:.2f}%',
        'Operating Margin': f'{operating_margin:.2f}%',
    }

    # Iterate over metrics and populate the table
    for metric in financials.index.tolist():
        try:
            value = financials.loc[metric].iloc[0]
            if value is None:
                value = 0
        except KeyError:
            value = 0

        # Add positivity/negativity logic for specific metrics
        if metric == "trailingPE" and (10 <= value <= 20):
            table_rows.append(format_table_row(metric, value, True))
        elif metric == "trailingPE" and (value < 5 or value > 30):
            table_rows.append(format_table_row(metric, value, False))
        elif metric == "Gross Profit" and value > 0:
            table_rows.append(format_table_row(metric, value, True))
        else:
            # Default handling for metrics without specific thresholds
            value_formatted = f"${value:,}" if isinstance(value, (int, float)) and value > 1e3 else str(value)
            table_rows.append(format_table_row(metric, value_formatted, is_positive=None))

    # Add the calculated metrics to the table rows
    for metric, value in calculated_metrics.items():
        table_rows.append(format_table_row(metric, value, is_positive=None))

    # Close table structure
    table_footer = "</tbody></table>"

    # Display the table
    st.markdown(table_header + "".join(table_rows) + table_footer, unsafe_allow_html=True)

    st.divider()

# CashFlow
    st.subheader(":sparkles: CashFlow Metrics")

    # Create Info table structure
    table_header = """
    <table style="width:100%; border-collapse:collapse;">
    <thead>
    <tr style="border-bottom:2px solid black;">
    <th style="text-align:left;">Metric</th>
    <th style="text-align:left;">Value</th>
    </tr>
    </thead>
    <tbody>
    """

    table_rows = []

    # Iterate over metrics and populate the table
    for metric in cashflow.index.tolist():
        try:
            value = cashflow.loc[metric].iloc[0]
            if value is None:
                value = 0
        except KeyError:
            value = 0

        # Add positivity/negativity logic for specific metrics
        if metric == "trailingPE" and (10 <= value <= 20):
            table_rows.append(format_table_row(metric, value, True))
        elif metric == "trailingPE" and (value < 5 or value > 30):
            table_rows.append(format_table_row(metric, value, False))
        else:
            # Default handling for metrics without specific thresholds
            value_formatted = f"${value:,}" if isinstance(value, (int, float)) and value > 1e3 else str(value)
            table_rows.append(format_table_row(metric, value_formatted, is_positive=None))

    # Close table structure
    table_footer = "</tbody></table>"

    # Display the table
    st.markdown(table_header + "".join(table_rows) + table_footer, unsafe_allow_html=True)

    st.divider()