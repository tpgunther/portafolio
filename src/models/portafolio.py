from decimal import Decimal
from models.stock import Stock
from utils.constants import TOLERANCE


class Portfolio:
    def __init__(self, initial_allocation: dict[Stock, Decimal]):
        self._stocks = {}
        self._allocations = self._validate_allocations(initial_allocation)
        for stock, amount in initial_allocation.items():
            self._stocks[str(stock)] = {"stock": stock, "amount": 0}

    def _validate_allocations(
        self, initial_allocation: dict[str, Decimal]
    ) -> dict[str, Decimal]:
        """
        Validate the allocations of a portafolio.
        Args:
            initial_allocation: A dictionary of stock names and their allocations.
        Returns:
            A dictionary of stock names and their allocations.
        Raises:
            ValueError: If the total allocation is not 1, or if any allocation value is negative or greater than 1.
        """
        # a portafolio can be empty
        if len(initial_allocation) == 0:
            return initial_allocation

        total_allocation = sum(initial_allocation.values())
        if total_allocation != 1:
            raise ValueError(f"Total allocation must be 1, but is {total_allocation}")
        if any(value < 0 for value in initial_allocation.values()):
            raise ValueError("Allocation values must be positive")
        if any(value > 1 for value in initial_allocation.values()):
            raise ValueError("Allocation values must be less than or equal to 1")

        return initial_allocation

    def add_stock(self, stock: Stock, amount: Decimal):
        """
        Add a stock to the portfolio. If the stock already exists, add the amount to the existing stock.

        Args:
            stock: A Stock object.
            amount: The amount of the stock to add.
        """
        name = str(stock)
        if name in self._stocks:
            self._stocks[name]["amount"] += amount
            return
        self._stocks[name] = {"stock": stock, "amount": amount}

    def get_portfolio_value(self) -> Decimal:
        """
        Get the value of the portfolio.
        Returns:
            The value of the portfolio.
        """
        total_value = Decimal(0)
        for stock_name, stock_data in self._stocks.items():
            stock = stock_data["stock"]
            amount = stock_data["amount"]
            total_value += Decimal(amount) * Decimal(stock.get_price())
        return total_value

    def rebalance(self) -> dict[str, list[dict[str, Decimal]]]:
        """
        Calculate the actions that needs to be sold and bought to rebalance the portfolio.
        Returns:
            A dictionary with the actions to sell and buy.
        """
        total_value = self.get_portfolio_value()
        buy_actions = []
        sell_actions = []
        for stock, amount in self._allocations.items():
            print(f"Stock name: {stock}")
            name = str(stock)
            price = stock.get_price()
            target_value = amount * total_value
            current_value = Decimal(self._stocks[name]["amount"]) * price
            delta_shares = (target_value - current_value) / price
            print(f"  Target value for {name} is: {target_value}")
            print(f"  Current value for {name} is: {current_value}")
            print(f"  Delta shares for {name} is: {delta_shares}")

            if abs(target_value - current_value) <= TOLERANCE:
                print(f"  No action needed for {name}")
                continue

            if delta_shares > 0:
                buy_actions.append({"stock": stock, "amount": delta_shares})
            else:
                sell_actions.append({"stock": stock, "amount": delta_shares})

        return {"sell": sell_actions, "buy": buy_actions}
