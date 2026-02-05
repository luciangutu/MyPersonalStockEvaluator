import requests
import requests_cache
import pandas as pd
import logging
from config import FMP_API_KEY

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configure cache with URL pattern matching
urls_expire_after = {
    '*/profile*': 86400,                      # 24h - company profile
    '*/quote*': 3600,                         # 1h - stock prices
    '*/balance-sheet-statement*': 86400 * 7,  # 7 days - financials
    '*/income-statement*': 86400 * 7,         # 7 days - financials
    '*/cash-flow-statement*': 86400 * 7,      # 7 days - financials
    '*/key-metrics*': 86400,                  # 24h - metrics
    '*/ratios*': 86400,                       # 24h - ratios
    '*/historical-price-eod*': 3600,          # 1h - historical prices
}

# Install cache globally
requests_cache.install_cache(
    'fmp_cache',
    backend='sqlite',
    urls_expire_after=urls_expire_after,
    allowable_codes=[200],
    match_headers=False,
    ignored_parameters=['apikey']
)

logging.info("FMP API cache initialized with SQLite backend")

BASE_URL = "https://financialmodelingprep.com/stable"


class FMPTicker:
    def __init__(self, ticker):
        self.ticker = ticker.upper()
        self._info = None
        self._balance_sheet = None
        self._financials = None
        self._cashflow = None

    def _make_request(self, endpoint, extra_params=None):
        """Make API request to FMP"""
        url = f"{BASE_URL}/{endpoint}"
        params = {"apikey": FMP_API_KEY}
        if extra_params:
            params.update(extra_params)

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            # Log cache status
            if hasattr(response, 'from_cache') and response.from_cache:
                logging.info(f"Cache HIT for {endpoint}")
            else:
                logging.info(f"Cache MISS for {endpoint} - API call made")

            # Check if response contains error message
            if isinstance(data, dict) and 'Error Message' in data:
                logging.error(f"FMP API Error: {data['Error Message']}")
                return None

            return data
        except requests.exceptions.HTTPError as e:
            logging.error(f"HTTP Error from FMP: {e}")
            logging.error(f"Response content: {response.text if response else 'No response'}")
            return None
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching data from FMP: {e}")
            return None

    @property
    def info(self):
        """Get company info similar to yfinance"""
        if self._info is not None:
            return self._info

        # Fetch profile data
        profile_data = self._make_request("profile", {"symbol": self.ticker})
        if not profile_data or len(profile_data) == 0:
            logging.warning(f"No profile data for {self.ticker}. Free tier may not support this stock.")
            self._info = {}
            return self._info

        profile = profile_data[0] if isinstance(profile_data, list) else profile_data

        # Fetch quote data
        quote_data = self._make_request("quote", {"symbol": self.ticker})
        quote = quote_data[0] if quote_data and len(quote_data) > 0 else {}

        # Fetch key metrics (may not be available in free tier)
        metrics_data = self._make_request("key-metrics", {"symbol": self.ticker})
        metrics = metrics_data[0] if metrics_data and len(metrics_data) > 0 else {}

        # Fetch ratios (may not be available in free tier)
        ratios_data = self._make_request("ratios", {"symbol": self.ticker})
        ratios = ratios_data[0] if ratios_data and len(ratios_data) > 0 else {}

        # Map to yfinance-like structure
        price = quote.get('price', profile.get('price', 0))
        market_cap = profile.get('marketCap', profile.get('mktCap', 0))

        # Calculate shares outstanding from market cap and price
        shares_outstanding = 0
        if price > 0 and market_cap > 0:
            shares_outstanding = market_cap / price
        elif metrics and 'numberOfShares' in metrics:
            shares_outstanding = metrics['numberOfShares']

        self._info = {
            'longName': profile.get('companyName', ''),
            'symbol': profile.get('symbol', ''),
            'currentPrice': price,
            'marketCap': market_cap,
            'sharesOutstanding': shares_outstanding,
            'trailingPE': quote.get('pe', profile.get('beta', 0)),
            'trailingPegRatio': ratios.get('pegRatio', 0),
            'priceToSalesTrailing12Months': ratios.get('priceToSalesRatio', 0),
            'operatingMargins': ratios.get('operatingProfitMargin', 0),
            'earningsQuarterlyGrowth': metrics.get('revenuePerShare', 0),
            'industry': profile.get('industry', ''),
            'sector': profile.get('sector', ''),
            'website': profile.get('website', ''),
            'description': profile.get('description', ''),
        }

        return self._info

    @property
    def balance_sheet(self):
        """Get balance sheet data"""
        if self._balance_sheet is not None:
            return self._balance_sheet

        data = self._make_request("balance-sheet-statement", {"symbol": self.ticker})
        if not data or len(data) == 0:
            logging.warning(f"No balance sheet data for {self.ticker}. This endpoint may require a paid FMP plan.")
            # Return empty DataFrame
            self._balance_sheet = pd.DataFrame()
            return self._balance_sheet

        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date')

        # Map FMP field names to yfinance names
        field_mapping = {
            'totalAssets': 'Total Assets',
            'totalLiabilities': 'Total Liabilities Net Minority Interest',
            'totalStockholdersEquity': 'Stockholders Equity',
            'cashAndCashEquivalents': 'Cash Cash Equivalents And Short Term Investments',
            'totalCurrentAssets': 'Current Assets',
            'totalCurrentLiabilities': 'Current Liabilities',
            'longTermDebt': 'Long Term Debt',
            'totalDebt': 'Total Debt',
            'retainedEarnings': 'Retained Earnings',
            'commonStock': 'Common Stock',
        }

        df = df.rename(columns=field_mapping)
        self._balance_sheet = df.T

        return self._balance_sheet

    @property
    def financials(self):
        """Get income statement data"""
        if self._financials is not None:
            return self._financials

        data = self._make_request("income-statement", {"symbol": self.ticker})
        if not data or len(data) == 0:
            logging.warning(f"No income statement data for {self.ticker}. This endpoint may require a paid FMP plan.")
            # Return empty DataFrame
            self._financials = pd.DataFrame()
            return self._financials

        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date')

        # Map FMP field names to yfinance names
        field_mapping = {
            'revenue': 'Total Revenue',
            'costOfRevenue': 'Cost Of Revenue',
            'grossProfit': 'Gross Profit',
            'operatingIncome': 'Operating Income',
            'netIncome': 'Net Income',
            'ebitda': 'EBITDA',
            'eps': 'Basic EPS',
            'operatingExpenses': 'Operating Expense',
        }

        df = df.rename(columns=field_mapping)
        self._financials = df.T

        return self._financials

    @property
    def cashflow(self):
        """Get cash flow statement data"""
        if self._cashflow is not None:
            return self._cashflow

        data = self._make_request("cash-flow-statement", {"symbol": self.ticker})
        if not data or len(data) == 0:
            logging.warning(f"No cashflow data for {self.ticker}. This endpoint may require a paid FMP plan.")
            # Return empty DataFrame with expected columns
            self._cashflow = pd.DataFrame(columns=['Free Cash Flow', 'Operating Cash Flow', 'Capital Expenditure', 'Cash Dividends Paid'])
            return self._cashflow

        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date')

        # Map FMP field names to yfinance names
        field_mapping = {
            'operatingCashFlow': 'Operating Cash Flow',
            'capitalExpenditure': 'Capital Expenditure',
            'freeCashFlow': 'Free Cash Flow',
            'dividendsPaid': 'Cash Dividends Paid',
            'commonDividendsPaid': 'Cash Dividends Paid',
        }

        df = df.rename(columns=field_mapping)
        self._cashflow = df.T

        return self._cashflow

    def history(self, period="1y", interval="1d"):
        """Get historical price data"""
        data = self._make_request("historical-price-eod/full", {"symbol": self.ticker})
        if not data or 'historical' not in data:
            logging.warning(f"No historical price data for {self.ticker}")
            return pd.DataFrame(columns=['Open', 'High', 'Low', 'Close', 'Volume'])

        df = pd.DataFrame(data['historical'])
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date')
        df = df.sort_index()

        # Map to yfinance column names
        df = df.rename(columns={
            'open': 'Open',
            'high': 'High',
            'low': 'Low',
            'close': 'Close',
            'volume': 'Volume'
        })

        # Filter by period
        if period == "1y":
            df = df.last('365D')
        elif period == "6mo":
            df = df.last('180D')

        return df[['Open', 'High', 'Low', 'Close', 'Volume']]


def download(ticker, period="6mo", interval="1d"):
    """Download historical data for a ticker (similar to yf.download)"""
    stock = FMPTicker(ticker)
    return stock.history(period=period, interval=interval)


def Ticker(ticker):
    """Factory function to create FMPTicker instance"""
    return FMPTicker(ticker)
