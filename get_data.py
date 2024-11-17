import yfinance as yf
from dcf import dcf
import math
import logging


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def get_stock_data(stock_ticker: str) -> dict:
    stock_info = {}

    try:
        stock = yf.Ticker(stock_ticker)
        
        # Helper function to handle NaN values
        def safe_round(value):
            return round(value) if value and not math.isnan(value) else None
        
        # Balance Sheet Information
        balance_sheet = stock.get_balance_sheet()
        if balance_sheet is not None and not balance_sheet.empty:
            logging.info(f'{balance_sheet=}')
            total_assets = safe_round(balance_sheet.loc['TotalAssets', :].iloc[0])
            
            total_liabilities_short = safe_round(balance_sheet.loc['TotalLiabilitiesNetMinorityInterest', :].iloc[0]) if 'TotalLiabilitiesNetMinorityInterest' in balance_sheet.index else None
            total_liabilities_long = safe_round(balance_sheet.loc['TotalNonCurrentLiabilitiesNetMinorityInterest', :].iloc[0]) if 'TotalNonCurrentLiabilitiesNetMinorityInterest' in balance_sheet.index else None
            
            stock_info['totalAssets'] = total_assets if total_assets is not None else None

            stock_info['totalLiabilities'] = (
                total_liabilities_short + total_liabilities_long
                if total_liabilities_short is not None and total_liabilities_long is not None
                else None
            )
        else:
            stock_info['totalAssets'] = stock_info['totalLiabilities'] = None

        # General Information
        info_fields = [
            'longName', 'website', 'currentPrice', 'regularMarketDayLow', 'regularMarketDayHigh',
            'regularMarketPreviousClose', 'sharesOutstanding', 'trailingPE', 'forwardPE',
            'priceToSalesTrailing12Months', 'bookValue', 'priceToBook', 'earningsQuarterlyGrowth',
            'trailingEps', 'forwardEps', 'pegRatio', 'totalRevenue', 'totalDebt', 'debtToEquity',
            'revenuePerShare'
        ]
        for field in info_fields:
            stock_info[field] = stock.info.get(field, None)
            logging.info(f'{field}={stock_info[field]}')

        # Additional Financials with Default Handling
        stock_info['grossProfits'] = safe_round(stock.info.get('grossProfits', 0))
        stock_info['freeCashflow'] = safe_round(stock.info.get('freeCashflow', 0))
        stock_info['operatingCashflow'] = safe_round(stock.info.get('operatingCashflow', 0))

        # Cash Flow Data for DCF Calculation
        if stock.cashflow is not None:
            free_cash_flow_data = stock.cashflow.loc['Free Cash Flow'].tail(4)
            free_cash_flow = [
                safe_round(item) for item in free_cash_flow_data if item is not None
            ]
            free_cash_flow.reverse()
            stock_info['dcf'] = (
                dcf(free_cash_flow, stock_info['sharesOutstanding']) 
                if stock_info['sharesOutstanding'] else None
            )
        else:
            stock_info['dcf'] = None

    except Exception as e:
        stock_info['error'] = f"Error fetching stock information: {e}"

    return stock_info
