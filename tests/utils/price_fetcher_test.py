import pytest

from src.utils.price_fetcher import PriceFetcher


def test_fetch_price_from_alpha_vantage(mocker):
    mocker.patch.object(PriceFetcher, "_fetch_from_alpha_vantage", return_value=100)
    fetcher = PriceFetcher()
    price = fetcher.fetch_price("AAPL")
    assert price == 100
    assert fetcher._prices == {"AAPL": 100}


def test_fetch_price_from_finnhub_public(mocker):
    mocker.patch.object(PriceFetcher, "_fetch_from_alpha_vantage", return_value=None)
    mocker.patch.object(PriceFetcher, "_fetch_from_finnhub_public", return_value=100)
    fetcher = PriceFetcher()
    price = fetcher.fetch_price("AAPL")
    assert price == 100
    assert fetcher._prices == {"AAPL": 100}


def test_fetch_price_cache_hit(mocker):
    mock = mocker.patch.object(
        PriceFetcher, "_fetch_from_alpha_vantage", return_value=100
    )
    fetcher = PriceFetcher()
    price = fetcher.fetch_price("AAPL")
    assert price == 100

    price = fetcher.fetch_price("AAPL")
    assert price == 100
    assert mock.call_count == 1
