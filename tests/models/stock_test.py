import pytest

from src.models import stock
from src.models.stock import Stock


class TestStock:
    def test_get_price(self, mocker):
        mocker.patch.object(stock.fetcher, "fetch_price", return_value=100)
        stock_instance = Stock("AAPL")
        assert stock_instance.get_price() == 100

    def test_get_price_invalid_stock(self, mocker):
        mocker.patch.object(
            stock.fetcher,
            "fetch_price",
            side_effect=ValueError(
                "Could not fetch price for INVALID. Please check the stock symbol."
            ),
        )
        with pytest.raises(ValueError) as exc_info:
            Stock("INVALID")
        assert (
            str(exc_info.value)
            == "Could not fetch price for INVALID. Please check the stock symbol."
        )
