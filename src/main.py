from models.portafolio import Portfolio
from models.stock import Stock
from decimal import Decimal, getcontext, ROUND_HALF_UP

from utils.constants import PRECISION

getcontext().prec = PRECISION
getcontext().rounding = ROUND_HALF_UP


def print_actions(actions: dict[str, list[dict[str, Decimal]]]):
    if len(actions["buy"]) == 0 and len(actions["sell"]) == 0:
        print("  No actions needed.")
        return
    for action in actions["buy"]:
        print(f"  Buy {action['amount']} shares of {action['stock']}")
    for action in actions["sell"]:
        print(f"  Sell {action['amount']} shares of {action['stock']}")


def main():
    print("1.- Get initial stocks prices:")
    appl = Stock("AAPL")
    google = Stock("GOOGL")
    microsoft = Stock("MSFT")
    print(f"Stock name: {appl}, current price: {appl.get_display_price()}")
    print(f"Stock name: {google}, current price: {google.get_display_price()}")
    print(f"Stock name: {microsoft}, current price: {microsoft.get_display_price()}")

    portfolio = Portfolio(
        initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.1),
            microsoft: Decimal(0.4),
        }
    )
    print("--------------------------------")
    print("2.Initial portfolio is unbalanced:")
    portfolio.add_stock(stock=appl, amount=Decimal(5))
    portfolio.add_stock(stock=google, amount=Decimal(3))
    portfolio.add_stock(stock=microsoft, amount=Decimal(2))
    delta_shares = portfolio.rebalance()

    print("--------------------------------")
    print("3. Actions to balance the portfolio:")
    print_actions(delta_shares)

    print("4. By adding the delta shares to the stocks, the portfolio is now balanced.")

    for action in delta_shares["buy"]:
        portfolio.add_stock(stock=action["stock"], amount=action["amount"])
    for action in delta_shares["sell"]:
        portfolio.add_stock(stock=action["stock"], amount=action["amount"])
    print("--------------------------------")
    print("5. Balanced portfolio:")
    delta_shares = portfolio.rebalance()
    print_actions(delta_shares)


if __name__ == "__main__":
    main()
