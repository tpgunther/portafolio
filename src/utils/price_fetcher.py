import requests
from typing import Optional
from decimal import Decimal

"""
Fetch the current price of a stock using free APIs.

Keeps cache of prices to avoid duplicate requests.
"""


class PriceFetcher:
    def __init__(self):
        self._prices = {}

    def fetch_price(self, stock_name: str) -> Decimal:
        """
        Fetch the current price of a stock using free APIs.

        Args:
            stock_name: Stock symbol (e.g., 'AAPL', 'MSFT', 'GOOGL')

        Returns:
            float: Current stock price

        Raises:
            ValueError: If stock_name is invalid or cannot be fetched
        """
        # Check cache first
        if stock_name in self._prices:
            return self._prices[stock_name]

        # Try multiple free API sources
        price = self._fetch_from_alpha_vantage(stock_name)

        if price is None:
            price = self._fetch_from_finnhub_public(stock_name)

        if price is None:
            raise ValueError(
                f"Could not fetch price for {stock_name}. Please check the stock symbol."
            )

        # Cache the price
        self._prices[stock_name] = price
        return price

    def _fetch_from_alpha_vantage(self, stock_name: str) -> Optional[Decimal]:
        """
        Fetch price from Alpha Vantage API using demo key (free, no signup needed).
        Note: Demo key has strict rate limits (5 requests per minute, 500 per day).
        For better rate limits, get a free API key from https://www.alphavantage.co/support/#api-key
        """
        try:
            url = "https://www.alphavantage.co/query"
            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": stock_name,
                "apikey": "demo",  # Demo key works without signup, but has rate limits
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if "Global Quote" in data and data["Global Quote"]:
                quote = data["Global Quote"]
                price_str = quote.get("05. price")  # Current price field
                if price_str and price_str != "0.0000":
                    print(f"Price from Alpha Vantage: {price_str}")
                    return Decimal(price_str)
        except Exception:
            pass  # Try next API

        return None

    def _fetch_from_finnhub_public(self, stock_name: str) -> Optional[Decimal]:
        """
        Fetch price using a simple web scraping approach from Yahoo Finance.
        This is a fallback method that doesn't require any API key.
        """
        try:
            # Using Yahoo Finance's quote endpoint (public, no key needed)
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{stock_name}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }

            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()

            if "chart" in data and "result" in data["chart"]:
                result = data["chart"]["result"]
                if result and len(result) > 0:
                    meta = result[0].get("meta", {})
                    # Try to get current price
                    price = meta.get("regularMarketPrice") or meta.get("previousClose")
                    if price:
                        print(f"Price from Finnhub: {price}")
                        return Decimal(price)
        except Exception:
            pass  # Try next method

        return None
