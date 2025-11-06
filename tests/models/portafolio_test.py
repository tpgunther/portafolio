import pytest

from src.models.portafolio import Portfolio

from src.models.stock import Stock
from decimal import Decimal


class TestPortafolio:
    def test_validate_allocations(self):
        appl = Stock("AAPL")
        google = Stock("GOOGL")
        microsoft = Stock("MSFT")
        portafolio = Portfolio(
            initial_allocation={
                appl: Decimal(0.5),
                google: Decimal(0.3),
                microsoft: Decimal(0.2),
            }
        )
        assert portafolio._allocations == {
            appl: Decimal(0.5),
            google: Decimal(0.3),
            microsoft: Decimal(0.2),
        }

    def test_validate_allocations_empty(self):
        portafolio = Portfolio(initial_allocation={})
        assert portafolio._allocations == {}

    def test_validate_allocations_total_not_1(self):
        appl = Stock("AAPL")
        google = Stock("GOOGL")
        microsoft = Stock("MSFT")
        with pytest.raises(ValueError) as e:
            Portfolio(
                initial_allocation={
                    appl: Decimal(0.5),
                    google: Decimal(0.3),
                    microsoft: Decimal(0.3),
                }
            )
            assert e.value.message == "Total allocation must be 1, but is 1.1"

    def test_validate_allocations_total_less_than_100(self):
        appl = Stock("AAPL")
        google = Stock("GOOGL")
        microsoft = Stock("MSFT")
        with pytest.raises(ValueError):
            Portfolio(
                initial_allocation={
                    appl: Decimal(0.5),
                    google: Decimal(0.3),
                    microsoft: Decimal(-0.2),
                }
            )
            assert e.value.message == "Allocation values must be positive"

    def test_validate_allocations_total_greater_than_100(self):
        appl = Stock("AAPL")
        google = Stock("GOOGL")
        microsoft = Stock("MSFT")
        with pytest.raises(ValueError):
            Portfolio(
                initial_allocation={
                    appl: Decimal(0.5),
                    google: Decimal(0.3),
                    microsoft: Decimal(1.2),
                }
            )
            assert (
                e.value.message == "Allocation values must be less than or equal to 1"
            )

    def test_add_stock(self):
        appl = Stock("AAPL")
        google = Stock("GOOGL")
        microsoft = Stock("MSFT")
        portafolio = Portfolio(
            initial_allocation={
                appl: Decimal(0.5),
                google: Decimal(0.3),
                microsoft: Decimal(0.2),
            }
        )

        portafolio.add_stock(stock=appl, amount=Decimal(1))
        assert portafolio._stocks == {
            str(appl): {"stock": appl, "amount": Decimal(1)},
            str(google): {"stock": google, "amount": Decimal(0)},
            str(microsoft): {"stock": microsoft, "amount": Decimal(0)},
        }
        portafolio.add_stock(stock=appl, amount=Decimal(1))
        assert portafolio._stocks == {
            str(appl): {"stock": appl, "amount": Decimal(2)},
            str(google): {"stock": google, "amount": Decimal(0)},
            str(microsoft): {"stock": microsoft, "amount": Decimal(0)},
        }

    def test_get_portfolio_value(self):
        appl = Stock("AAPL")
        google = Stock("GOOGL")
        microsoft = Stock("MSFT")
        portafolio = Portfolio(
            initial_allocation={
                appl: Decimal(0.5),
                google: Decimal(0.3),
                microsoft: Decimal(0.2),
            }
        )
        portafolio.add_stock(stock=appl, amount=Decimal(1))
        portafolio.add_stock(stock=google, amount=Decimal(1))
        portafolio.add_stock(stock=microsoft, amount=Decimal(1))
        assert portafolio.get_portfolio_value() == Decimal(300)

    def test_rebalance_no_actions(self):
        appl = Stock("AAPL")
        google = Stock("GOOGL")
        portafolio = Portfolio(
            initial_allocation={appl: Decimal(0.5), google: Decimal(0.5)}
        )
        portafolio.add_stock(stock=appl, amount=Decimal(1))
        portafolio.add_stock(stock=google, amount=Decimal(1))
        assert portafolio.rebalance() == {"sell": [], "buy": []}

    def test_rebalance_actions(self):
        appl = Stock("AAPL")
        google = Stock("GOOGL")
        portafolio = Portfolio(
            initial_allocation={appl: Decimal(0.5), google: Decimal(0.5)}
        )
        portafolio.add_stock(stock=appl, amount=Decimal(2))
        portafolio.add_stock(stock=google, amount=Decimal(1))
        assert portafolio.rebalance() == {
            "sell": [{"stock": appl, "amount": Decimal(-0.5)}],
            "buy": [{"stock": google, "amount": Decimal(+0.5)}],
        }
