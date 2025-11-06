from utils.price_fetcher import PriceFetcher
from decimal import Decimal, ROUND_HALF_UP


fetcher = PriceFetcher()


class Stock:
    def __init__(self, name):
        self._name = name
        self._price = fetcher.fetch_price(self._name)

    def __str__(self) -> str:
        return self._name

    def get_price(self) -> Decimal:
        return self._price

    def get_display_price(self) -> str:
        return self._price.quantize(Decimal("0.00"), rounding=ROUND_HALF_UP)
