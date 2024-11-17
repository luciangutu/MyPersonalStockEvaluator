import streamlit as st


def dcf(free_cash_flow: list[int], shares_outstanding: int) -> float:
    """
    Calculate the fair value of a stock using Discounted Cash Flow (DCF) analysis.

    :param free_cash_flow: List of historical free cash flows (most recent last).
    :param shares_outstanding: Total number of shares outstanding.
    :return: Estimated fair value per share.
    """
    if not free_cash_flow or shares_outstanding <= 0:
        raise ValueError("Invalid input: free_cash_flow must be a non-empty list, and shares_outstanding must be positive.")

    required_rate = st.session_state.get('required_rate', 7) / 100
    perpetual_rate = st.session_state.get('perpetual_rate', 2) / 100
    cash_flow_growth_rate = st.session_state.get('cash_flow_growth_rate', 3) / 100

    # Years for projection
    years = [1, 2, 3, 4]

    # Future Free Cash Flows
    future_free_cash_flow = [
        free_cash_flow[-1] * (1 + cash_flow_growth_rate) ** year for year in years
    ]

    # Terminal Value
    terminal_value = free_cash_flow[-1] * (1 + perpetual_rate) / (required_rate - perpetual_rate)

    # Discount Factor and Present Value
    discount_factor = [(1 + required_rate) ** year for year in years]
    discounted_future_free_cash_flow = [
        fcf / df for fcf, df in zip(future_free_cash_flow, discount_factor)
    ]

    # Discounted Terminal Value
    discounted_terminal_value = terminal_value / (1 + required_rate) ** len(years)

    # Calculate Total Present Value
    total_present_value = sum(discounted_future_free_cash_flow) + discounted_terminal_value

    # Fair Value Per Share
    fair_value = round(total_present_value / shares_outstanding, 2)

    return fair_value
