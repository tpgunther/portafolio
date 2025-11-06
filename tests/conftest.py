import pytest
from decimal import Decimal
from src.models import stock
from src.models.stock import Stock


@pytest.fixture(autouse=True)
def mock_stock_get_price(mocker):
    """Automatically mock Stock initialization and get_price for all tests to prevent API calls."""
    # Mock the fetcher to prevent API calls during Stock.__init__
    mocker.patch.object(stock.fetcher, "fetch_price", return_value=100.0)
    # Mock Stock.get_price to return Decimal for method calls
    mocker.patch.object(Stock, "get_price", return_value=Decimal(100))
