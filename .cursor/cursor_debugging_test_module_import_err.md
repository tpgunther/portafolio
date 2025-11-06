# Debugging test module import errors
_Exported on 11/5/2025 at 21:01:28 GMT-3 from Cursor (2.0.54)_

---

**User**

Can you help me review why the tests are not running:



ImportError while importing test module '/Users/tomasgunther/Projects/portafolio/tests/utils/price_fetcher_test.py'.

Hint: make sure your test modules/packages have valid Python names.

Traceback:

../../.pyenv/versions/3.13.5/lib/python3.13/importlib/__init__.py:88: in import_module

    return _bootstrap._gcd_import(name[level:], package, level)

           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/utils/price_fetcher_test.py:3: in <module>

    from src.utils.price_fetcher import PriceFetcher

E   ModuleNotFoundError: No module named 'src'

---

**Cursor**


Reviewing the test setup and project structure to diagnose the import error.



Checking for pytest configuration and the project structure:



Pytest isn't finding the `src` module because the project root isn't on the Python path. Adding pytest configuration in `pyproject.toml` to add the project root to the path:



Adding pytest configuration to `pyproject.toml` so the project root is on the Python path:


```plaintext
[project]
name = "portafolio"
version = "0.1.0"
description = ""
authors = [
    {name = "Tomas Gunther",email = "tomasgunther@gmail.com"}
]
readme = "README.md"
requires-python = ">=3.13"
dependencies = [
    "requests>=2.31.0",
]


[build-system]
requires = ["poetry-core>=2.0.0,<3.0.0"]
build-backend = "poetry.core.masonry.api"

[tool.poetry.group.dev.dependencies]
pytest = "^8.4.2"
mocker = "^1.1.1"

[tool.pytest.ini_options]
pythonpath = ["."]


```


Checking for other issues and verifying the test setup:



Added pytest configuration to fix the import error. The issue was that pytest couldn't find the `src` module because the project root wasn't on the Python path.

**What I changed:**
- Added `[tool.pytest.ini_options]` with `pythonpath = ["."]` to `pyproject.toml`. This tells pytest to add the project root to the Python path, so imports like `from src.utils.price_fetcher import PriceFetcher` work.

**Note:** Your test uses the `mocker` fixture. The dependency is listed as `mocker = "^1.1.1"`, but the standard pytest plugin is `pytest-mock`. If you see errors related to `mocker`, update the dependency to `pytest-mock` instead of `mocker`.

Run your tests again; the import error should be resolved. If you still see issues, share the error output.

---

**User**

nice! also why mocker is not being readed?

---

**Cursor**


Checking why `mocker` isn't being recognized. Reviewing the test file and dependencies:



The dependency should be `pytest-mock`, not `mocker`. The `mocker` fixture is provided by `pytest-mock`. Updating the dependency:


```plaintext
[project]
name = "portafolio"
version = "0.1.0"
description = ""
authors = [
    {name = "Tomas Gunther",email = "tomasgunther@gmail.com"}
]
readme = "README.md"
requires-python = ">=3.13"
dependencies = [
    "requests>=2.31.0",
]


[build-system]
requires = ["poetry-core>=2.0.0,<3.0.0"]
build-backend = "poetry.core.masonry.api"

[tool.poetry.group.dev.dependencies]
pytest = "^8.4.2"
pytest-mock = "^3.14.0"

[tool.pytest.ini_options]
pythonpath = ["."]


```


Updating Poetry dependencies to install `pytest-mock`:



**The problem:** You had `mocker = "^1.1.1"` in your dependencies, but the `mocker` fixture comes from the `pytest-mock` package, not a package called `mocker`.

**The fix:** Changed the dependency to `pytest-mock = "^3.14.0"`, which provides the `mocker` fixture your test uses.

**Next step:** Run `poetry install` or `poetry lock --no-update && poetry install` to update your lock file and install `pytest-mock`. After that, the `mocker` fixture should work in your tests.

The `mocker` fixture from `pytest-mock` is a thin wrapper around `unittest.mock` that integrates with pytest's fixture system, making it easier to use in tests.

---

**User**

can you review why `mocker.patch.object(PriceFetcher, "fetch_price", return_value=100)` is not mocking the request to the API on @stock_test.py ?

---

**Cursor**


Examining the Stock class to see how it uses PriceFetcher:



The issue: in `stock.py`, a module-level `PriceFetcher` instance is created at import time, and the mock is on the class, not that instance. Checking the import path:



Two issues:

1. Wrong import path: `stock.py` uses `from utils.price_fetcher` but should be `from src.utils.price_fetcher`.
2. Mock target: `stock.py` creates a module-level `PriceFetcher` instance (`fetcher = PriceFetcher()`), so mocking the class method won't affect that instance. Mock the instance method instead.

Fixing both:


```python
from src.utils.price_fetcher import PriceFetcher

fetcher = PriceFetcher()

class Stock:
    def __init__(self, name):
        self._name = name
        self._price = fetcher.fetch_price(self._name)

    def get_price(self):
        return self._price
```


Updating the test to mock the module-level instance, not the class:


```python
import pytest

from src.models import stock
from src.models.stock import Stock

class TestStock:
    def test_get_price(self, mocker):
        mocker.patch.object(stock.fetcher, "fetch_price", return_value=100)
        stock_instance = Stock("AAPL")
        assert stock_instance.get_price() == 100

    # def test_get_price_invalid_stock(self, mocker):
    #     mocker.patch.object(PriceFetcher, "fetch_price", return_value=None)
    #     with pytest.raises(ValueError):
    #         Stock("INVALID")
    #         assert e.value.message == "Could not fetch price for INVALID. Please check the ticker symbol."
```


Updating the commented test to use the same pattern:


```python
import pytest

from src.models import stock
from src.models.stock import Stock

class TestStock:
    def test_get_price(self, mocker):
        mocker.patch.object(stock.fetcher, "fetch_price", return_value=100)
        stock_instance = Stock("AAPL")
        assert stock_instance.get_price() == 100

    # def test_get_price_invalid_stock(self, mocker):
    #     mocker.patch.object(stock.fetcher, "fetch_price", side_effect=ValueError("Could not fetch price for INVALID. Please check the ticker symbol."))
    #     with pytest.raises(ValueError) as exc_info:
    #         Stock("INVALID")
    #     assert str(exc_info.value) == "Could not fetch price for INVALID. Please check the ticker symbol."
```


Checking if we need to create the `__init__.py` file:


---

**User**

can we check for the same issue here?

@portafolio_test.py (67-77) 

---

**Cursor**


Checking the same issue in `portafolio_test.py`. Reading the test file and related code:



The test patches `stock.get_price`, but `stock` is the module, not the `Stock` class. `get_price` is an instance method. Also, `Stock.__init__` calls `fetcher.fetch_price()`, so it will still hit the API. Fixing the test:



Fixing the test: `stock.get_price` is being patched on the module, but `get_price` is an instance method. Also, `Stock.__init__` calls `fetcher.fetch_price()`, so we need to mock that too. Updating the test:


```python
import pytest

from src.models.portafolio import Portfolio
from src.models import stock
from src.models.stock import Stock
from decimal import Decimal

class TestPortafolio:
    def test_validate_allocations(self):
        portafolio = Portfolio(initial_allocation={
            "Apple": Decimal(0.5),
            "Google": Decimal(0.3),
            "Microsoft": Decimal(0.2)
        })
        assert portafolio._allocations == {
            "Apple": Decimal(0.5),
            "Google": Decimal(0.3),
            "Microsoft": Decimal(0.2)
        }

    def test_validate_allocations_empty(self):
        portafolio = Portfolio(initial_allocation={})
        assert portafolio._allocations == {}

    def test_validate_allocations_total_not_1(self):
        with pytest.raises(ValueError) as e:
            Portfolio(initial_allocation={
                "Apple": Decimal(0.5),
                "Google": Decimal(0.3),
                "Microsoft": Decimal(0.3)
            })
            assert e.value.message == "Total allocation must be 1, but is 1.1"

    def test_validate_allocations_total_less_than_100(self):
        with pytest.raises(ValueError):
            Portfolio(initial_allocation={
                "Apple": Decimal(0.5),
                "Google": Decimal(0.3),
                "Microsoft": Decimal(-0.2)
            })
            assert e.value.message == "Allocation values must be positive"

    def test_validate_allocations_total_greater_than_100(self):
        with pytest.raises(ValueError):
            Portfolio(initial_allocation={
                "Apple": Decimal(0.5),
                "Google": Decimal(0.3),
                "Microsoft": Decimal(1.2)
            })
            assert e.value.message == "Allocation values must be less than or equal to 1"

    def test_add_stock(self):
        portafolio = Portfolio(initial_allocation={
            "Apple": Decimal(0.5),
            "Google": Decimal(0.3),
            "Microsoft": Decimal(0.2)
        })
        portafolio.add_stock(stock=Stock("Apple"), amount=Decimal(1))
        assert portafolio._stocks == {
            "Apple": {"stock": Stock("Apple"), "amount": Decimal(1)}
        }
        portafolio.add_stock(stock=Stock("Apple"), amount=Decimal(1))
        assert portafolio._stocks == {
            "Apple": {"stock": Stock("Apple"), "amount": Decimal(2)}
        }

    def test_get_portfolio_value(self, mocker):
        # Mock the fetcher to prevent API calls during Stock initialization
        mocker.patch.object(stock.fetcher, "fetch_price", return_value=100.0)
        # Mock Stock.get_price to return Decimal for the method call
        mocker.patch.object(Stock, "get_price", return_value=Decimal(100))
        portafolio = Portfolio(initial_allocation={
            "Apple": Decimal(0.5),
            "Google": Decimal(0.3),
            "Microsoft": Decimal(0.2)
        })
        portafolio.add_stock(stock=Stock("Apple"), amount=Decimal(1))
        portafolio.add_stock(stock=Stock("Google"), amount=Decimal(1))
        portafolio.add_stock(stock=Stock("Microsoft"), amount=Decimal(1))
        assert portafolio.get_portfolio_value() == Decimal(300)
```


Fixed the mocking issue. Problems:

1. Wrong target: `mocker.patch.object(stock, "get_price", ...)` — `stock` is the module, not the `Stock` class. `get_price` is an instance method on `Stock`.

2. Missing initialization mock: `Stock.__init__` calls `fetcher.fetch_price()`, so we need to mock that to prevent API calls during initialization.

The fix:
- Mock `stock.fetcher.fetch_price` to return `100.0` (prevents API calls during `Stock` initialization)
- Mock `Stock.get_price` to return `Decimal(100)` (for when `get_portfolio_value()` calls it)

Also corrected the expected value: 3 stocks × 1 share × $100 = $300, not $3.

The test should now work without making real API calls.

---

**User**

can you help me to review this mocker?@portafolio_test.py (77-91) 

---

**Cursor**


Reviewing the test file and the Stock class to understand the mocking issue:



The issue: `fetcher` is a module-level variable in `stock.py`, not an instance attribute. Stock instances don't have a `fetcher` attribute, so `appl.fetcher` doesn't exist.

Also, `appl`, `google`, and `microsoft` are created at module import time (lines 8-10), so they already call the real API before the test runs.

Fixing the test:



Issues:
1. `appl.fetcher`, `google.fetcher`, and `microsoft.fetcher` don't exist — `fetcher` is a module-level variable, not an instance attribute.
2. The Stock instances are created at module import time (lines 8-10), so they already made real API calls before the test runs.

Since the instances already exist and `get_portfolio_value()` calls `stock.get_price()`, mock `Stock.get_price()` instead. Here's the fix:


```python
import pytest

from src.models.portafolio import Portfolio
from src.models import stock
from src.models.stock import Stock
from decimal import Decimal

appl = Stock("AAPL")
google = Stock("GOOGL")
microsoft = Stock("MSFT")

class TestPortafolio:
    def test_validate_allocations(self):
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.3),
            microsoft: Decimal(0.2)
        })
        assert portafolio._allocations == {
            appl: Decimal(0.5),
            google: Decimal(0.3),
            microsoft: Decimal(0.2)
        }

    def test_validate_allocations_empty(self):
        portafolio = Portfolio(initial_allocation={})
        assert portafolio._allocations == {}

    def test_validate_allocations_total_not_1(self):
        with pytest.raises(ValueError) as e:
            Portfolio(initial_allocation={
                appl: Decimal(0.5),
                google: Decimal(0.3),
                microsoft: Decimal(0.3)
            })
            assert e.value.message == "Total allocation must be 1, but is 1.1"

    def test_validate_allocations_total_less_than_100(self):
        with pytest.raises(ValueError):
            Portfolio(initial_allocation={
                appl: Decimal(0.5),
                google: Decimal(0.3),
                microsoft: Decimal(-0.2)
            })
            assert e.value.message == "Allocation values must be positive"

    def test_validate_allocations_total_greater_than_100(self):
        with pytest.raises(ValueError):
            Portfolio(initial_allocation={
                appl: Decimal(0.5),
                google: Decimal(0.3),
                microsoft: Decimal(1.2)
            })
            assert e.value.message == "Allocation values must be less than or equal to 1"

    def test_add_stock(self, mocker):
        mocker.patch.object(stock.fetcher, "fetch_price", return_value=Decimal(100.0))
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.3),
            microsoft: Decimal(0.2)
        })
        
        portafolio.add_stock(stock=appl, amount=Decimal(1))
        assert portafolio._stocks == {
            str(appl): {"stock": appl, "amount": Decimal(1)},
            str(google): {"stock": google, "amount": Decimal(0)},
            str(microsoft): {"stock": microsoft, "amount": Decimal(0)}
        }
        portafolio.add_stock(stock=appl, amount=Decimal(1))
        assert portafolio._stocks == {
            str(appl): {"stock": appl, "amount": Decimal(2)},
            str(google): {"stock": google, "amount": Decimal(0)},
            str(microsoft): {"stock": microsoft, "amount": Decimal(0)}
        }

    def test_get_portfolio_value(self, mocker):
        # Mock Stock.get_price since the Stock instances are already created
        # and get_portfolio_value() calls get_price() on each stock instance
        mocker.patch.object(Stock, "get_price", return_value=Decimal(100))
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.3),
            microsoft: Decimal(0.2)
        })
        portafolio.add_stock(stock=appl, amount=Decimal(1))
        portafolio.add_stock(stock=google, amount=Decimal(1))
        portafolio.add_stock(stock=microsoft, amount=Decimal(1))
        assert portafolio.get_portfolio_value() == Decimal(300)

    def test_rebalance_no_actions(self, mocker):
        mocker.patch.object(stock.fetcher, "fetch_price", return_value=Decimal(100.0))
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.5)
        })
        portafolio.add_stock(stock=appl, amount=Decimal(1))
        portafolio.add_stock(stock=google, amount=Decimal(1))
        assert portafolio.rebalance() == {
            "sell": [],
            "buy": []
        }

    def test_rebalance_buy_action(self, mocker):
        mocker.patch.object(stock.fetcher, "fetch_price", return_value=Decimal(100.0))
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.5)
        })
        portafolio.add_stock(stock=appl, amount=Decimal(2))
        portafolio.add_stock(stock=google, amount=Decimal(1))
        assert portafolio.rebalance() == {
            "sell": [{"stock": appl, "amount": Decimal(-0.5)}],
            "buy": [{"stock": google, "amount": Decimal(+0.5)}]
        }

    def test_rebalance_sell_action(self, mocker):
        mocker.patch.object(stock.fetcher, "fetch_price", return_value=Decimal(100.0))
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.5)
        })
        portafolio.add_stock(stock=appl, amount=Decimal(1))
        # portafolio.add_stock(stock=google, amount=Decimal(2))
        assert portafolio.rebalance() == {
            "sell": [],
            "buy": [{"stock": google, "amount": Decimal(1)}]
        }
```


Fixed the mocking issue. Summary:

**The Problem:**
- `appl.fetcher`, `google.fetcher`, and `microsoft.fetcher` don't exist because `fetcher` is a module-level variable in `stock.py`, not an instance attribute.
- The Stock instances (`appl`, `google`, `microsoft`) are created at module import time, so they already made real API calls before tests run.

**The Solution:**
- Mock `Stock.get_price()` instead, since:
  - The Stock instances are already created
  - `get_portfolio_value()` calls `stock.get_price()` on each stock instance
  - This avoids trying to patch non-existent attributes

**Note:** The module-level Stock instances still make real API calls when the test module is imported. To avoid this, either:
1. Create Stock instances inside each test after mocking `stock.fetcher.fetch_price`, or
2. Use a fixture to create Stock instances with mocked prices

For now, this fix makes the test work correctly. The test should pass without making API calls during the test execution.

---

**User**

how can I move the mocker.patch.object(Stock, "get_price", return_value=Decimal(100)) on @portafolio_test.py to a method ,so it is not called on every test?

---

**Cursor**


Setting up a pytest fixture to avoid repeating the mock. Checking for a `conftest.py`:



Creating a `conftest.py` fixture to mock `Stock.get_price` so all tests can use it. Also fixing tests that use `mocker` without the parameter:


```python
import pytest
from decimal import Decimal
from src.models.stock import Stock


@pytest.fixture(autouse=True)
def mock_stock_get_price(mocker):
    """Automatically mock Stock.get_price for all tests to prevent API calls."""
    mocker.patch.object(Stock, "get_price", return_value=Decimal(100))

```

```python
import pytest

from src.models.portafolio import Portfolio

from src.models.stock import Stock
from decimal import Decimal

appl = Stock("AAPL")
google = Stock("GOOGL")
microsoft = Stock("MSFT")

class TestPortafolio:
    def test_validate_allocations(self):
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.3),
            microsoft: Decimal(0.2)
        })
        assert portafolio._allocations == {
            appl: Decimal(0.5),
            google: Decimal(0.3),
            microsoft: Decimal(0.2)
        }

    def test_validate_allocations_empty(self):
        mocker.patch.object(Stock, "get_price", return_value=Decimal(100))
        portafolio = Portfolio(initial_allocation={})
        assert portafolio._allocations == {}

    def test_validate_allocations_total_not_1(self):
        mocker.patch.object(Stock, "get_price", return_value=Decimal(100))
        with pytest.raises(ValueError) as e:
            Portfolio(initial_allocation={
                appl: Decimal(0.5),
                google: Decimal(0.3),
                microsoft: Decimal(0.3)
            })
            assert e.value.message == "Total allocation must be 1, but is 1.1"

    def test_validate_allocations_total_less_than_100(self):
        with pytest.raises(ValueError):
            Portfolio(initial_allocation={
                appl: Decimal(0.5),
                google: Decimal(0.3),
                microsoft: Decimal(-0.2)
            })
            assert e.value.message == "Allocation values must be positive"

    def test_validate_allocations_total_greater_than_100(self):
        with pytest.raises(ValueError):
            Portfolio(initial_allocation={
                appl: Decimal(0.5),
                google: Decimal(0.3),
                microsoft: Decimal(1.2)
            })
            assert e.value.message == "Allocation values must be less than or equal to 1"

    def test_add_stock(self, mocker):
        mocker.patch.object(Stock, "get_price", return_value=Decimal(100.0))
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.3),
            microsoft: Decimal(0.2)
        })
        
        portafolio.add_stock(stock=appl, amount=Decimal(1))
        assert portafolio._stocks == {
            str(appl): {"stock": appl, "amount": Decimal(1)},
            str(google): {"stock": google, "amount": Decimal(0)},
            str(microsoft): {"stock": microsoft, "amount": Decimal(0)}
        }
        portafolio.add_stock(stock=appl, amount=Decimal(1))
        assert portafolio._stocks == {
            str(appl): {"stock": appl, "amount": Decimal(2)},
            str(google): {"stock": google, "amount": Decimal(0)},
            str(microsoft): {"stock": microsoft, "amount": Decimal(0)}
        }

    def test_get_portfolio_value(self, mocker):
        mocker.patch.object(Stock, "get_price", return_value=Decimal(100))
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.3),
            microsoft: Decimal(0.2)
        })
        portafolio.add_stock(stock=appl, amount=Decimal(1))
        portafolio.add_stock(stock=google, amount=Decimal(1))
        portafolio.add_stock(stock=microsoft, amount=Decimal(1))
        assert portafolio.get_portfolio_value() == Decimal(300)

    def test_rebalance_no_actions(self, mocker):
        mocker.patch.object(Stock, "get_price", return_value=Decimal(100.0))
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.5)
        })
        portafolio.add_stock(stock=appl, amount=Decimal(1))
        portafolio.add_stock(stock=google, amount=Decimal(1))
        assert portafolio.rebalance() == {
            "sell": [],
            "buy": []
        }

    def test_rebalance_actions(self, mocker):
        mocker.patch.object(Stock, "get_price", return_value=Decimal(100.0))
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.5)
        })
        portafolio.add_stock(stock=appl, amount=Decimal(2))
        portafolio.add_stock(stock=google, amount=Decimal(1))
        assert portafolio.rebalance() == {
            "sell": [{"stock": appl, "amount": Decimal(-0.5)}],
            "buy": [{"stock": google, "amount": Decimal(+0.5)}]
        }

```

```python
import pytest

from src.models.portafolio import Portfolio

from src.models.stock import Stock
from decimal import Decimal

appl = Stock("AAPL")
google = Stock("GOOGL")
microsoft = Stock("MSFT")

class TestPortafolio:
    def test_validate_allocations(self):
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.3),
            microsoft: Decimal(0.2)
        })
        assert portafolio._allocations == {
            appl: Decimal(0.5),
            google: Decimal(0.3),
            microsoft: Decimal(0.2)
        }

    def test_validate_allocations_empty(self):
        portafolio = Portfolio(initial_allocation={})
        assert portafolio._allocations == {}

    def test_validate_allocations_total_not_1(self):
        mocker.patch.object(Stock, "get_price", return_value=Decimal(100))
        with pytest.raises(ValueError) as e:
            Portfolio(initial_allocation={
                appl: Decimal(0.5),
                google: Decimal(0.3),
                microsoft: Decimal(0.3)
            })
            assert e.value.message == "Total allocation must be 1, but is 1.1"

    def test_validate_allocations_total_less_than_100(self):
        with pytest.raises(ValueError):
            Portfolio(initial_allocation={
                appl: Decimal(0.5),
                google: Decimal(0.3),
                microsoft: Decimal(-0.2)
            })
            assert e.value.message == "Allocation values must be positive"

    def test_validate_allocations_total_greater_than_100(self):
        with pytest.raises(ValueError):
            Portfolio(initial_allocation={
                appl: Decimal(0.5),
                google: Decimal(0.3),
                microsoft: Decimal(1.2)
            })
            assert e.value.message == "Allocation values must be less than or equal to 1"

    def test_add_stock(self, mocker):
        mocker.patch.object(Stock, "get_price", return_value=Decimal(100.0))
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.3),
            microsoft: Decimal(0.2)
        })
        
        portafolio.add_stock(stock=appl, amount=Decimal(1))
        assert portafolio._stocks == {
            str(appl): {"stock": appl, "amount": Decimal(1)},
            str(google): {"stock": google, "amount": Decimal(0)},
            str(microsoft): {"stock": microsoft, "amount": Decimal(0)}
        }
        portafolio.add_stock(stock=appl, amount=Decimal(1))
        assert portafolio._stocks == {
            str(appl): {"stock": appl, "amount": Decimal(2)},
            str(google): {"stock": google, "amount": Decimal(0)},
            str(microsoft): {"stock": microsoft, "amount": Decimal(0)}
        }

    def test_get_portfolio_value(self, mocker):
        mocker.patch.object(Stock, "get_price", return_value=Decimal(100))
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.3),
            microsoft: Decimal(0.2)
        })
        portafolio.add_stock(stock=appl, amount=Decimal(1))
        portafolio.add_stock(stock=google, amount=Decimal(1))
        portafolio.add_stock(stock=microsoft, amount=Decimal(1))
        assert portafolio.get_portfolio_value() == Decimal(300)

    def test_rebalance_no_actions(self, mocker):
        mocker.patch.object(Stock, "get_price", return_value=Decimal(100.0))
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.5)
        })
        portafolio.add_stock(stock=appl, amount=Decimal(1))
        portafolio.add_stock(stock=google, amount=Decimal(1))
        assert portafolio.rebalance() == {
            "sell": [],
            "buy": []
        }

    def test_rebalance_actions(self, mocker):
        mocker.patch.object(Stock, "get_price", return_value=Decimal(100.0))
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.5)
        })
        portafolio.add_stock(stock=appl, amount=Decimal(2))
        portafolio.add_stock(stock=google, amount=Decimal(1))
        assert portafolio.rebalance() == {
            "sell": [{"stock": appl, "amount": Decimal(-0.5)}],
            "buy": [{"stock": google, "amount": Decimal(+0.5)}]
        }

```

```python
import pytest

from src.models.portafolio import Portfolio

from src.models.stock import Stock
from decimal import Decimal

appl = Stock("AAPL")
google = Stock("GOOGL")
microsoft = Stock("MSFT")

class TestPortafolio:
    def test_validate_allocations(self):
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.3),
            microsoft: Decimal(0.2)
        })
        assert portafolio._allocations == {
            appl: Decimal(0.5),
            google: Decimal(0.3),
            microsoft: Decimal(0.2)
        }

    def test_validate_allocations_empty(self):
        portafolio = Portfolio(initial_allocation={})
        assert portafolio._allocations == {}

    def test_validate_allocations_total_not_1(self):
        with pytest.raises(ValueError) as e:
            Portfolio(initial_allocation={
                appl: Decimal(0.5),
                google: Decimal(0.3),
                microsoft: Decimal(0.3)
            })
            assert e.value.message == "Total allocation must be 1, but is 1.1"

    def test_validate_allocations_total_less_than_100(self):
        with pytest.raises(ValueError):
            Portfolio(initial_allocation={
                appl: Decimal(0.5),
                google: Decimal(0.3),
                microsoft: Decimal(-0.2)
            })
            assert e.value.message == "Allocation values must be positive"

    def test_validate_allocations_total_greater_than_100(self):
        with pytest.raises(ValueError):
            Portfolio(initial_allocation={
                appl: Decimal(0.5),
                google: Decimal(0.3),
                microsoft: Decimal(1.2)
            })
            assert e.value.message == "Allocation values must be less than or equal to 1"

    def test_add_stock(self, mocker):
        mocker.patch.object(Stock, "get_price", return_value=Decimal(100.0))
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.3),
            microsoft: Decimal(0.2)
        })
        
        portafolio.add_stock(stock=appl, amount=Decimal(1))
        assert portafolio._stocks == {
            str(appl): {"stock": appl, "amount": Decimal(1)},
            str(google): {"stock": google, "amount": Decimal(0)},
            str(microsoft): {"stock": microsoft, "amount": Decimal(0)}
        }
        portafolio.add_stock(stock=appl, amount=Decimal(1))
        assert portafolio._stocks == {
            str(appl): {"stock": appl, "amount": Decimal(2)},
            str(google): {"stock": google, "amount": Decimal(0)},
            str(microsoft): {"stock": microsoft, "amount": Decimal(0)}
        }

    def test_get_portfolio_value(self, mocker):
        mocker.patch.object(Stock, "get_price", return_value=Decimal(100))
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.3),
            microsoft: Decimal(0.2)
        })
        portafolio.add_stock(stock=appl, amount=Decimal(1))
        portafolio.add_stock(stock=google, amount=Decimal(1))
        portafolio.add_stock(stock=microsoft, amount=Decimal(1))
        assert portafolio.get_portfolio_value() == Decimal(300)

    def test_rebalance_no_actions(self, mocker):
        mocker.patch.object(Stock, "get_price", return_value=Decimal(100.0))
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.5)
        })
        portafolio.add_stock(stock=appl, amount=Decimal(1))
        portafolio.add_stock(stock=google, amount=Decimal(1))
        assert portafolio.rebalance() == {
            "sell": [],
            "buy": []
        }

    def test_rebalance_actions(self, mocker):
        mocker.patch.object(Stock, "get_price", return_value=Decimal(100.0))
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.5)
        })
        portafolio.add_stock(stock=appl, amount=Decimal(2))
        portafolio.add_stock(stock=google, amount=Decimal(1))
        assert portafolio.rebalance() == {
            "sell": [{"stock": appl, "amount": Decimal(-0.5)}],
            "buy": [{"stock": google, "amount": Decimal(+0.5)}]
        }

```

```python
import pytest

from src.models.portafolio import Portfolio

from src.models.stock import Stock
from decimal import Decimal

appl = Stock("AAPL")
google = Stock("GOOGL")
microsoft = Stock("MSFT")

class TestPortafolio:
    def test_validate_allocations(self):
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.3),
            microsoft: Decimal(0.2)
        })
        assert portafolio._allocations == {
            appl: Decimal(0.5),
            google: Decimal(0.3),
            microsoft: Decimal(0.2)
        }

    def test_validate_allocations_empty(self):
        portafolio = Portfolio(initial_allocation={})
        assert portafolio._allocations == {}

    def test_validate_allocations_total_not_1(self):
        with pytest.raises(ValueError) as e:
            Portfolio(initial_allocation={
                appl: Decimal(0.5),
                google: Decimal(0.3),
                microsoft: Decimal(0.3)
            })
            assert e.value.message == "Total allocation must be 1, but is 1.1"

    def test_validate_allocations_total_less_than_100(self):
        with pytest.raises(ValueError):
            Portfolio(initial_allocation={
                appl: Decimal(0.5),
                google: Decimal(0.3),
                microsoft: Decimal(-0.2)
            })
            assert e.value.message == "Allocation values must be positive"

    def test_validate_allocations_total_greater_than_100(self):
        with pytest.raises(ValueError):
            Portfolio(initial_allocation={
                appl: Decimal(0.5),
                google: Decimal(0.3),
                microsoft: Decimal(1.2)
            })
            assert e.value.message == "Allocation values must be less than or equal to 1"

    def test_add_stock(self):
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.3),
            microsoft: Decimal(0.2)
        })
        
        portafolio.add_stock(stock=appl, amount=Decimal(1))
        assert portafolio._stocks == {
            str(appl): {"stock": appl, "amount": Decimal(1)},
            str(google): {"stock": google, "amount": Decimal(0)},
            str(microsoft): {"stock": microsoft, "amount": Decimal(0)}
        }
        portafolio.add_stock(stock=appl, amount=Decimal(1))
        assert portafolio._stocks == {
            str(appl): {"stock": appl, "amount": Decimal(2)},
            str(google): {"stock": google, "amount": Decimal(0)},
            str(microsoft): {"stock": microsoft, "amount": Decimal(0)}
        }

    def test_get_portfolio_value(self, mocker):
        mocker.patch.object(Stock, "get_price", return_value=Decimal(100))
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.3),
            microsoft: Decimal(0.2)
        })
        portafolio.add_stock(stock=appl, amount=Decimal(1))
        portafolio.add_stock(stock=google, amount=Decimal(1))
        portafolio.add_stock(stock=microsoft, amount=Decimal(1))
        assert portafolio.get_portfolio_value() == Decimal(300)

    def test_rebalance_no_actions(self, mocker):
        mocker.patch.object(Stock, "get_price", return_value=Decimal(100.0))
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.5)
        })
        portafolio.add_stock(stock=appl, amount=Decimal(1))
        portafolio.add_stock(stock=google, amount=Decimal(1))
        assert portafolio.rebalance() == {
            "sell": [],
            "buy": []
        }

    def test_rebalance_actions(self, mocker):
        mocker.patch.object(Stock, "get_price", return_value=Decimal(100.0))
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.5)
        })
        portafolio.add_stock(stock=appl, amount=Decimal(2))
        portafolio.add_stock(stock=google, amount=Decimal(1))
        assert portafolio.rebalance() == {
            "sell": [{"stock": appl, "amount": Decimal(-0.5)}],
            "buy": [{"stock": google, "amount": Decimal(+0.5)}]
        }

```

```python
import pytest

from src.models.portafolio import Portfolio

from src.models.stock import Stock
from decimal import Decimal

appl = Stock("AAPL")
google = Stock("GOOGL")
microsoft = Stock("MSFT")

class TestPortafolio:
    def test_validate_allocations(self):
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.3),
            microsoft: Decimal(0.2)
        })
        assert portafolio._allocations == {
            appl: Decimal(0.5),
            google: Decimal(0.3),
            microsoft: Decimal(0.2)
        }

    def test_validate_allocations_empty(self):
        portafolio = Portfolio(initial_allocation={})
        assert portafolio._allocations == {}

    def test_validate_allocations_total_not_1(self):
        with pytest.raises(ValueError) as e:
            Portfolio(initial_allocation={
                appl: Decimal(0.5),
                google: Decimal(0.3),
                microsoft: Decimal(0.3)
            })
            assert e.value.message == "Total allocation must be 1, but is 1.1"

    def test_validate_allocations_total_less_than_100(self):
        with pytest.raises(ValueError):
            Portfolio(initial_allocation={
                appl: Decimal(0.5),
                google: Decimal(0.3),
                microsoft: Decimal(-0.2)
            })
            assert e.value.message == "Allocation values must be positive"

    def test_validate_allocations_total_greater_than_100(self):
        with pytest.raises(ValueError):
            Portfolio(initial_allocation={
                appl: Decimal(0.5),
                google: Decimal(0.3),
                microsoft: Decimal(1.2)
            })
            assert e.value.message == "Allocation values must be less than or equal to 1"

    def test_add_stock(self):
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.3),
            microsoft: Decimal(0.2)
        })
        
        portafolio.add_stock(stock=appl, amount=Decimal(1))
        assert portafolio._stocks == {
            str(appl): {"stock": appl, "amount": Decimal(1)},
            str(google): {"stock": google, "amount": Decimal(0)},
            str(microsoft): {"stock": microsoft, "amount": Decimal(0)}
        }
        portafolio.add_stock(stock=appl, amount=Decimal(1))
        assert portafolio._stocks == {
            str(appl): {"stock": appl, "amount": Decimal(2)},
            str(google): {"stock": google, "amount": Decimal(0)},
            str(microsoft): {"stock": microsoft, "amount": Decimal(0)}
        }

    def test_get_portfolio_value(self):
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.3),
            microsoft: Decimal(0.2)
        })
        portafolio.add_stock(stock=appl, amount=Decimal(1))
        portafolio.add_stock(stock=google, amount=Decimal(1))
        portafolio.add_stock(stock=microsoft, amount=Decimal(1))
        assert portafolio.get_portfolio_value() == Decimal(300)

    def test_rebalance_no_actions(self, mocker):
        mocker.patch.object(Stock, "get_price", return_value=Decimal(100.0))
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.5)
        })
        portafolio.add_stock(stock=appl, amount=Decimal(1))
        portafolio.add_stock(stock=google, amount=Decimal(1))
        assert portafolio.rebalance() == {
            "sell": [],
            "buy": []
        }

    def test_rebalance_actions(self, mocker):
        mocker.patch.object(Stock, "get_price", return_value=Decimal(100.0))
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.5)
        })
        portafolio.add_stock(stock=appl, amount=Decimal(2))
        portafolio.add_stock(stock=google, amount=Decimal(1))
        assert portafolio.rebalance() == {
            "sell": [{"stock": appl, "amount": Decimal(-0.5)}],
            "buy": [{"stock": google, "amount": Decimal(+0.5)}]
        }

```

```python
import pytest

from src.models.portafolio import Portfolio

from src.models.stock import Stock
from decimal import Decimal

appl = Stock("AAPL")
google = Stock("GOOGL")
microsoft = Stock("MSFT")

class TestPortafolio:
    def test_validate_allocations(self):
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.3),
            microsoft: Decimal(0.2)
        })
        assert portafolio._allocations == {
            appl: Decimal(0.5),
            google: Decimal(0.3),
            microsoft: Decimal(0.2)
        }

    def test_validate_allocations_empty(self):
        portafolio = Portfolio(initial_allocation={})
        assert portafolio._allocations == {}

    def test_validate_allocations_total_not_1(self):
        with pytest.raises(ValueError) as e:
            Portfolio(initial_allocation={
                appl: Decimal(0.5),
                google: Decimal(0.3),
                microsoft: Decimal(0.3)
            })
            assert e.value.message == "Total allocation must be 1, but is 1.1"

    def test_validate_allocations_total_less_than_100(self):
        with pytest.raises(ValueError):
            Portfolio(initial_allocation={
                appl: Decimal(0.5),
                google: Decimal(0.3),
                microsoft: Decimal(-0.2)
            })
            assert e.value.message == "Allocation values must be positive"

    def test_validate_allocations_total_greater_than_100(self):
        with pytest.raises(ValueError):
            Portfolio(initial_allocation={
                appl: Decimal(0.5),
                google: Decimal(0.3),
                microsoft: Decimal(1.2)
            })
            assert e.value.message == "Allocation values must be less than or equal to 1"

    def test_add_stock(self):
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.3),
            microsoft: Decimal(0.2)
        })
        
        portafolio.add_stock(stock=appl, amount=Decimal(1))
        assert portafolio._stocks == {
            str(appl): {"stock": appl, "amount": Decimal(1)},
            str(google): {"stock": google, "amount": Decimal(0)},
            str(microsoft): {"stock": microsoft, "amount": Decimal(0)}
        }
        portafolio.add_stock(stock=appl, amount=Decimal(1))
        assert portafolio._stocks == {
            str(appl): {"stock": appl, "amount": Decimal(2)},
            str(google): {"stock": google, "amount": Decimal(0)},
            str(microsoft): {"stock": microsoft, "amount": Decimal(0)}
        }

    def test_get_portfolio_value(self):
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.3),
            microsoft: Decimal(0.2)
        })
        portafolio.add_stock(stock=appl, amount=Decimal(1))
        portafolio.add_stock(stock=google, amount=Decimal(1))
        portafolio.add_stock(stock=microsoft, amount=Decimal(1))
        assert portafolio.get_portfolio_value() == Decimal(300)

    def test_rebalance_no_actions(self):
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.5)
        })
        portafolio.add_stock(stock=appl, amount=Decimal(1))
        portafolio.add_stock(stock=google, amount=Decimal(1))
        assert portafolio.rebalance() == {
            "sell": [],
            "buy": []
        }

    def test_rebalance_actions(self, mocker):
        mocker.patch.object(Stock, "get_price", return_value=Decimal(100.0))
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.5)
        })
        portafolio.add_stock(stock=appl, amount=Decimal(2))
        portafolio.add_stock(stock=google, amount=Decimal(1))
        assert portafolio.rebalance() == {
            "sell": [{"stock": appl, "amount": Decimal(-0.5)}],
            "buy": [{"stock": google, "amount": Decimal(+0.5)}]
        }

```

```python
import pytest

from src.models.portafolio import Portfolio

from src.models.stock import Stock
from decimal import Decimal

appl = Stock("AAPL")
google = Stock("GOOGL")
microsoft = Stock("MSFT")

class TestPortafolio:
    def test_validate_allocations(self):
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.3),
            microsoft: Decimal(0.2)
        })
        assert portafolio._allocations == {
            appl: Decimal(0.5),
            google: Decimal(0.3),
            microsoft: Decimal(0.2)
        }

    def test_validate_allocations_empty(self):
        portafolio = Portfolio(initial_allocation={})
        assert portafolio._allocations == {}

    def test_validate_allocations_total_not_1(self):
        with pytest.raises(ValueError) as e:
            Portfolio(initial_allocation={
                appl: Decimal(0.5),
                google: Decimal(0.3),
                microsoft: Decimal(0.3)
            })
            assert e.value.message == "Total allocation must be 1, but is 1.1"

    def test_validate_allocations_total_less_than_100(self):
        with pytest.raises(ValueError):
            Portfolio(initial_allocation={
                appl: Decimal(0.5),
                google: Decimal(0.3),
                microsoft: Decimal(-0.2)
            })
            assert e.value.message == "Allocation values must be positive"

    def test_validate_allocations_total_greater_than_100(self):
        with pytest.raises(ValueError):
            Portfolio(initial_allocation={
                appl: Decimal(0.5),
                google: Decimal(0.3),
                microsoft: Decimal(1.2)
            })
            assert e.value.message == "Allocation values must be less than or equal to 1"

    def test_add_stock(self):
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.3),
            microsoft: Decimal(0.2)
        })
        
        portafolio.add_stock(stock=appl, amount=Decimal(1))
        assert portafolio._stocks == {
            str(appl): {"stock": appl, "amount": Decimal(1)},
            str(google): {"stock": google, "amount": Decimal(0)},
            str(microsoft): {"stock": microsoft, "amount": Decimal(0)}
        }
        portafolio.add_stock(stock=appl, amount=Decimal(1))
        assert portafolio._stocks == {
            str(appl): {"stock": appl, "amount": Decimal(2)},
            str(google): {"stock": google, "amount": Decimal(0)},
            str(microsoft): {"stock": microsoft, "amount": Decimal(0)}
        }

    def test_get_portfolio_value(self):
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.3),
            microsoft: Decimal(0.2)
        })
        portafolio.add_stock(stock=appl, amount=Decimal(1))
        portafolio.add_stock(stock=google, amount=Decimal(1))
        portafolio.add_stock(stock=microsoft, amount=Decimal(1))
        assert portafolio.get_portfolio_value() == Decimal(300)

    def test_rebalance_no_actions(self):
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.5)
        })
        portafolio.add_stock(stock=appl, amount=Decimal(1))
        portafolio.add_stock(stock=google, amount=Decimal(1))
        assert portafolio.rebalance() == {
            "sell": [],
            "buy": []
        }

    def test_rebalance_actions(self):
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.5)
        })
        portafolio.add_stock(stock=appl, amount=Decimal(2))
        portafolio.add_stock(stock=google, amount=Decimal(1))
        assert portafolio.rebalance() == {
            "sell": [{"stock": appl, "amount": Decimal(-0.5)}],
            "buy": [{"stock": google, "amount": Decimal(+0.5)}]
        }

```


Verifying the changes and checking for issues:



Created a `conftest.py` fixture that automatically mocks `Stock.get_price` for all tests.

**What I did:**

1. Created `/Users/tomasgunther/Projects/portafolio/tests/conftest.py` with a fixture that:
   - Uses `@pytest.fixture(autouse=True)` to automatically apply to all tests
   - Mocks `Stock.get_price` to return `Decimal(100)` to prevent API calls during tests

2. Removed all the repetitive `mocker.patch.object(Stock, "get_price", ...)` calls from your test methods

3. Removed the `mocker` parameter from test methods since it's no longer needed

**How it works:**
- The `autouse=True` parameter makes the fixture run automatically for every test in the `tests` directory
- The fixture receives `mocker` from pytest-mock automatically
- All tests now have `Stock.get_price` mocked without needing to set it up manually

**Note:** The Stock instances (`appl`, `google`, `microsoft`) are still created at module import time (lines 8-10), so they will make real API calls when the test module is imported. The fixture will mock `get_price()` calls during test execution, but if you want to prevent the initial API calls during import, you'd need to create the Stock instances inside the tests after the fixture runs, or mock the fetcher at import time.

---

**User**

can you make that update, to move the stocks inside the test to prevent the actual calls?

---

**Cursor**


Moving the Stock instances into the tests so they're created after the fixture mocks are in place. Updating the test file:



Updating the fixture to also mock the fetcher during Stock initialization, then moving all Stock instances into the tests:


```python
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


```

```python
import pytest

from src.models.portafolio import Portfolio

from src.models.stock import Stock
from decimal import Decimal

class TestPortafolio:
    def test_validate_allocations(self):
        appl = Stock("AAPL")
        google = Stock("GOOGL")
        microsoft = Stock("MSFT")
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.3),
            microsoft: Decimal(0.2)
        })
        assert portafolio._allocations == {
            appl: Decimal(0.5),
            google: Decimal(0.3),
            microsoft: Decimal(0.2)
        }

    def test_validate_allocations_empty(self):
        portafolio = Portfolio(initial_allocation={})
        assert portafolio._allocations == {}

    def test_validate_allocations_total_not_1(self):
        with pytest.raises(ValueError) as e:
            Portfolio(initial_allocation={
                appl: Decimal(0.5),
                google: Decimal(0.3),
                microsoft: Decimal(0.3)
            })
            assert e.value.message == "Total allocation must be 1, but is 1.1"

    def test_validate_allocations_total_less_than_100(self):
        with pytest.raises(ValueError):
            Portfolio(initial_allocation={
                appl: Decimal(0.5),
                google: Decimal(0.3),
                microsoft: Decimal(-0.2)
            })
            assert e.value.message == "Allocation values must be positive"

    def test_validate_allocations_total_greater_than_100(self):
        with pytest.raises(ValueError):
            Portfolio(initial_allocation={
                appl: Decimal(0.5),
                google: Decimal(0.3),
                microsoft: Decimal(1.2)
            })
            assert e.value.message == "Allocation values must be less than or equal to 1"

    def test_add_stock(self):
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.3),
            microsoft: Decimal(0.2)
        })
        
        portafolio.add_stock(stock=appl, amount=Decimal(1))
        assert portafolio._stocks == {
            str(appl): {"stock": appl, "amount": Decimal(1)},
            str(google): {"stock": google, "amount": Decimal(0)},
            str(microsoft): {"stock": microsoft, "amount": Decimal(0)}
        }
        portafolio.add_stock(stock=appl, amount=Decimal(1))
        assert portafolio._stocks == {
            str(appl): {"stock": appl, "amount": Decimal(2)},
            str(google): {"stock": google, "amount": Decimal(0)},
            str(microsoft): {"stock": microsoft, "amount": Decimal(0)}
        }

    def test_get_portfolio_value(self):
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.3),
            microsoft: Decimal(0.2)
        })
        portafolio.add_stock(stock=appl, amount=Decimal(1))
        portafolio.add_stock(stock=google, amount=Decimal(1))
        portafolio.add_stock(stock=microsoft, amount=Decimal(1))
        assert portafolio.get_portfolio_value() == Decimal(300)

    def test_rebalance_no_actions(self):
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.5)
        })
        portafolio.add_stock(stock=appl, amount=Decimal(1))
        portafolio.add_stock(stock=google, amount=Decimal(1))
        assert portafolio.rebalance() == {
            "sell": [],
            "buy": []
        }

    def test_rebalance_actions(self):
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.5)
        })
        portafolio.add_stock(stock=appl, amount=Decimal(2))
        portafolio.add_stock(stock=google, amount=Decimal(1))
        assert portafolio.rebalance() == {
            "sell": [{"stock": appl, "amount": Decimal(-0.5)}],
            "buy": [{"stock": google, "amount": Decimal(+0.5)}]
        }

```

```python
import pytest

from src.models.portafolio import Portfolio

from src.models.stock import Stock
from decimal import Decimal

class TestPortafolio:
    def test_validate_allocations(self):
        appl = Stock("AAPL")
        google = Stock("GOOGL")
        microsoft = Stock("MSFT")
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.3),
            microsoft: Decimal(0.2)
        })
        assert portafolio._allocations == {
            appl: Decimal(0.5),
            google: Decimal(0.3),
            microsoft: Decimal(0.2)
        }

    def test_validate_allocations_empty(self):
        portafolio = Portfolio(initial_allocation={})
        assert portafolio._allocations == {}

    def test_validate_allocations_total_not_1(self):
        appl = Stock("AAPL")
        google = Stock("GOOGL")
        microsoft = Stock("MSFT")
        with pytest.raises(ValueError) as e:
            Portfolio(initial_allocation={
                appl: Decimal(0.5),
                google: Decimal(0.3),
                microsoft: Decimal(0.3)
            })
            assert e.value.message == "Total allocation must be 1, but is 1.1"

    def test_validate_allocations_total_less_than_100(self):
        with pytest.raises(ValueError):
            Portfolio(initial_allocation={
                appl: Decimal(0.5),
                google: Decimal(0.3),
                microsoft: Decimal(-0.2)
            })
            assert e.value.message == "Allocation values must be positive"

    def test_validate_allocations_total_greater_than_100(self):
        with pytest.raises(ValueError):
            Portfolio(initial_allocation={
                appl: Decimal(0.5),
                google: Decimal(0.3),
                microsoft: Decimal(1.2)
            })
            assert e.value.message == "Allocation values must be less than or equal to 1"

    def test_add_stock(self):
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.3),
            microsoft: Decimal(0.2)
        })
        
        portafolio.add_stock(stock=appl, amount=Decimal(1))
        assert portafolio._stocks == {
            str(appl): {"stock": appl, "amount": Decimal(1)},
            str(google): {"stock": google, "amount": Decimal(0)},
            str(microsoft): {"stock": microsoft, "amount": Decimal(0)}
        }
        portafolio.add_stock(stock=appl, amount=Decimal(1))
        assert portafolio._stocks == {
            str(appl): {"stock": appl, "amount": Decimal(2)},
            str(google): {"stock": google, "amount": Decimal(0)},
            str(microsoft): {"stock": microsoft, "amount": Decimal(0)}
        }

    def test_get_portfolio_value(self):
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.3),
            microsoft: Decimal(0.2)
        })
        portafolio.add_stock(stock=appl, amount=Decimal(1))
        portafolio.add_stock(stock=google, amount=Decimal(1))
        portafolio.add_stock(stock=microsoft, amount=Decimal(1))
        assert portafolio.get_portfolio_value() == Decimal(300)

    def test_rebalance_no_actions(self):
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.5)
        })
        portafolio.add_stock(stock=appl, amount=Decimal(1))
        portafolio.add_stock(stock=google, amount=Decimal(1))
        assert portafolio.rebalance() == {
            "sell": [],
            "buy": []
        }

    def test_rebalance_actions(self):
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.5)
        })
        portafolio.add_stock(stock=appl, amount=Decimal(2))
        portafolio.add_stock(stock=google, amount=Decimal(1))
        assert portafolio.rebalance() == {
            "sell": [{"stock": appl, "amount": Decimal(-0.5)}],
            "buy": [{"stock": google, "amount": Decimal(+0.5)}]
        }

```

```python
import pytest

from src.models.portafolio import Portfolio

from src.models.stock import Stock
from decimal import Decimal

class TestPortafolio:
    def test_validate_allocations(self):
        appl = Stock("AAPL")
        google = Stock("GOOGL")
        microsoft = Stock("MSFT")
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.3),
            microsoft: Decimal(0.2)
        })
        assert portafolio._allocations == {
            appl: Decimal(0.5),
            google: Decimal(0.3),
            microsoft: Decimal(0.2)
        }

    def test_validate_allocations_empty(self):
        portafolio = Portfolio(initial_allocation={})
        assert portafolio._allocations == {}

    def test_validate_allocations_total_not_1(self):
        appl = Stock("AAPL")
        google = Stock("GOOGL")
        microsoft = Stock("MSFT")
        with pytest.raises(ValueError) as e:
            Portfolio(initial_allocation={
                appl: Decimal(0.5),
                google: Decimal(0.3),
                microsoft: Decimal(0.3)
            })
            assert e.value.message == "Total allocation must be 1, but is 1.1"

    def test_validate_allocations_total_less_than_100(self):
        appl = Stock("AAPL")
        google = Stock("GOOGL")
        microsoft = Stock("MSFT")
        with pytest.raises(ValueError):
            Portfolio(initial_allocation={
                appl: Decimal(0.5),
                google: Decimal(0.3),
                microsoft: Decimal(-0.2)
            })
            assert e.value.message == "Allocation values must be positive"

    def test_validate_allocations_total_greater_than_100(self):
        with pytest.raises(ValueError):
            Portfolio(initial_allocation={
                appl: Decimal(0.5),
                google: Decimal(0.3),
                microsoft: Decimal(1.2)
            })
            assert e.value.message == "Allocation values must be less than or equal to 1"

    def test_add_stock(self):
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.3),
            microsoft: Decimal(0.2)
        })
        
        portafolio.add_stock(stock=appl, amount=Decimal(1))
        assert portafolio._stocks == {
            str(appl): {"stock": appl, "amount": Decimal(1)},
            str(google): {"stock": google, "amount": Decimal(0)},
            str(microsoft): {"stock": microsoft, "amount": Decimal(0)}
        }
        portafolio.add_stock(stock=appl, amount=Decimal(1))
        assert portafolio._stocks == {
            str(appl): {"stock": appl, "amount": Decimal(2)},
            str(google): {"stock": google, "amount": Decimal(0)},
            str(microsoft): {"stock": microsoft, "amount": Decimal(0)}
        }

    def test_get_portfolio_value(self):
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.3),
            microsoft: Decimal(0.2)
        })
        portafolio.add_stock(stock=appl, amount=Decimal(1))
        portafolio.add_stock(stock=google, amount=Decimal(1))
        portafolio.add_stock(stock=microsoft, amount=Decimal(1))
        assert portafolio.get_portfolio_value() == Decimal(300)

    def test_rebalance_no_actions(self):
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.5)
        })
        portafolio.add_stock(stock=appl, amount=Decimal(1))
        portafolio.add_stock(stock=google, amount=Decimal(1))
        assert portafolio.rebalance() == {
            "sell": [],
            "buy": []
        }

    def test_rebalance_actions(self):
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.5)
        })
        portafolio.add_stock(stock=appl, amount=Decimal(2))
        portafolio.add_stock(stock=google, amount=Decimal(1))
        assert portafolio.rebalance() == {
            "sell": [{"stock": appl, "amount": Decimal(-0.5)}],
            "buy": [{"stock": google, "amount": Decimal(+0.5)}]
        }

```

```python
import pytest

from src.models.portafolio import Portfolio

from src.models.stock import Stock
from decimal import Decimal

class TestPortafolio:
    def test_validate_allocations(self):
        appl = Stock("AAPL")
        google = Stock("GOOGL")
        microsoft = Stock("MSFT")
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.3),
            microsoft: Decimal(0.2)
        })
        assert portafolio._allocations == {
            appl: Decimal(0.5),
            google: Decimal(0.3),
            microsoft: Decimal(0.2)
        }

    def test_validate_allocations_empty(self):
        portafolio = Portfolio(initial_allocation={})
        assert portafolio._allocations == {}

    def test_validate_allocations_total_not_1(self):
        appl = Stock("AAPL")
        google = Stock("GOOGL")
        microsoft = Stock("MSFT")
        with pytest.raises(ValueError) as e:
            Portfolio(initial_allocation={
                appl: Decimal(0.5),
                google: Decimal(0.3),
                microsoft: Decimal(0.3)
            })
            assert e.value.message == "Total allocation must be 1, but is 1.1"

    def test_validate_allocations_total_less_than_100(self):
        appl = Stock("AAPL")
        google = Stock("GOOGL")
        microsoft = Stock("MSFT")
        with pytest.raises(ValueError):
            Portfolio(initial_allocation={
                appl: Decimal(0.5),
                google: Decimal(0.3),
                microsoft: Decimal(-0.2)
            })
            assert e.value.message == "Allocation values must be positive"

    def test_validate_allocations_total_greater_than_100(self):
        appl = Stock("AAPL")
        google = Stock("GOOGL")
        microsoft = Stock("MSFT")
        with pytest.raises(ValueError):
            Portfolio(initial_allocation={
                appl: Decimal(0.5),
                google: Decimal(0.3),
                microsoft: Decimal(1.2)
            })
            assert e.value.message == "Allocation values must be less than or equal to 1"

    def test_add_stock(self):
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.3),
            microsoft: Decimal(0.2)
        })
        
        portafolio.add_stock(stock=appl, amount=Decimal(1))
        assert portafolio._stocks == {
            str(appl): {"stock": appl, "amount": Decimal(1)},
            str(google): {"stock": google, "amount": Decimal(0)},
            str(microsoft): {"stock": microsoft, "amount": Decimal(0)}
        }
        portafolio.add_stock(stock=appl, amount=Decimal(1))
        assert portafolio._stocks == {
            str(appl): {"stock": appl, "amount": Decimal(2)},
            str(google): {"stock": google, "amount": Decimal(0)},
            str(microsoft): {"stock": microsoft, "amount": Decimal(0)}
        }

    def test_get_portfolio_value(self):
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.3),
            microsoft: Decimal(0.2)
        })
        portafolio.add_stock(stock=appl, amount=Decimal(1))
        portafolio.add_stock(stock=google, amount=Decimal(1))
        portafolio.add_stock(stock=microsoft, amount=Decimal(1))
        assert portafolio.get_portfolio_value() == Decimal(300)

    def test_rebalance_no_actions(self):
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.5)
        })
        portafolio.add_stock(stock=appl, amount=Decimal(1))
        portafolio.add_stock(stock=google, amount=Decimal(1))
        assert portafolio.rebalance() == {
            "sell": [],
            "buy": []
        }

    def test_rebalance_actions(self):
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.5)
        })
        portafolio.add_stock(stock=appl, amount=Decimal(2))
        portafolio.add_stock(stock=google, amount=Decimal(1))
        assert portafolio.rebalance() == {
            "sell": [{"stock": appl, "amount": Decimal(-0.5)}],
            "buy": [{"stock": google, "amount": Decimal(+0.5)}]
        }

```

```python
import pytest

from src.models.portafolio import Portfolio

from src.models.stock import Stock
from decimal import Decimal

class TestPortafolio:
    def test_validate_allocations(self):
        appl = Stock("AAPL")
        google = Stock("GOOGL")
        microsoft = Stock("MSFT")
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.3),
            microsoft: Decimal(0.2)
        })
        assert portafolio._allocations == {
            appl: Decimal(0.5),
            google: Decimal(0.3),
            microsoft: Decimal(0.2)
        }

    def test_validate_allocations_empty(self):
        portafolio = Portfolio(initial_allocation={})
        assert portafolio._allocations == {}

    def test_validate_allocations_total_not_1(self):
        appl = Stock("AAPL")
        google = Stock("GOOGL")
        microsoft = Stock("MSFT")
        with pytest.raises(ValueError) as e:
            Portfolio(initial_allocation={
                appl: Decimal(0.5),
                google: Decimal(0.3),
                microsoft: Decimal(0.3)
            })
            assert e.value.message == "Total allocation must be 1, but is 1.1"

    def test_validate_allocations_total_less_than_100(self):
        appl = Stock("AAPL")
        google = Stock("GOOGL")
        microsoft = Stock("MSFT")
        with pytest.raises(ValueError):
            Portfolio(initial_allocation={
                appl: Decimal(0.5),
                google: Decimal(0.3),
                microsoft: Decimal(-0.2)
            })
            assert e.value.message == "Allocation values must be positive"

    def test_validate_allocations_total_greater_than_100(self):
        appl = Stock("AAPL")
        google = Stock("GOOGL")
        microsoft = Stock("MSFT")
        with pytest.raises(ValueError):
            Portfolio(initial_allocation={
                appl: Decimal(0.5),
                google: Decimal(0.3),
                microsoft: Decimal(1.2)
            })
            assert e.value.message == "Allocation values must be less than or equal to 1"

    def test_add_stock(self):
        appl = Stock("AAPL")
        google = Stock("GOOGL")
        microsoft = Stock("MSFT")
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.3),
            microsoft: Decimal(0.2)
        })
        
        portafolio.add_stock(stock=appl, amount=Decimal(1))
        assert portafolio._stocks == {
            str(appl): {"stock": appl, "amount": Decimal(1)},
            str(google): {"stock": google, "amount": Decimal(0)},
            str(microsoft): {"stock": microsoft, "amount": Decimal(0)}
        }
        portafolio.add_stock(stock=appl, amount=Decimal(1))
        assert portafolio._stocks == {
            str(appl): {"stock": appl, "amount": Decimal(2)},
            str(google): {"stock": google, "amount": Decimal(0)},
            str(microsoft): {"stock": microsoft, "amount": Decimal(0)}
        }

    def test_get_portfolio_value(self):
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.3),
            microsoft: Decimal(0.2)
        })
        portafolio.add_stock(stock=appl, amount=Decimal(1))
        portafolio.add_stock(stock=google, amount=Decimal(1))
        portafolio.add_stock(stock=microsoft, amount=Decimal(1))
        assert portafolio.get_portfolio_value() == Decimal(300)

    def test_rebalance_no_actions(self):
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.5)
        })
        portafolio.add_stock(stock=appl, amount=Decimal(1))
        portafolio.add_stock(stock=google, amount=Decimal(1))
        assert portafolio.rebalance() == {
            "sell": [],
            "buy": []
        }

    def test_rebalance_actions(self):
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.5)
        })
        portafolio.add_stock(stock=appl, amount=Decimal(2))
        portafolio.add_stock(stock=google, amount=Decimal(1))
        assert portafolio.rebalance() == {
            "sell": [{"stock": appl, "amount": Decimal(-0.5)}],
            "buy": [{"stock": google, "amount": Decimal(+0.5)}]
        }

```

```python
import pytest

from src.models.portafolio import Portfolio

from src.models.stock import Stock
from decimal import Decimal

class TestPortafolio:
    def test_validate_allocations(self):
        appl = Stock("AAPL")
        google = Stock("GOOGL")
        microsoft = Stock("MSFT")
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.3),
            microsoft: Decimal(0.2)
        })
        assert portafolio._allocations == {
            appl: Decimal(0.5),
            google: Decimal(0.3),
            microsoft: Decimal(0.2)
        }

    def test_validate_allocations_empty(self):
        portafolio = Portfolio(initial_allocation={})
        assert portafolio._allocations == {}

    def test_validate_allocations_total_not_1(self):
        appl = Stock("AAPL")
        google = Stock("GOOGL")
        microsoft = Stock("MSFT")
        with pytest.raises(ValueError) as e:
            Portfolio(initial_allocation={
                appl: Decimal(0.5),
                google: Decimal(0.3),
                microsoft: Decimal(0.3)
            })
            assert e.value.message == "Total allocation must be 1, but is 1.1"

    def test_validate_allocations_total_less_than_100(self):
        appl = Stock("AAPL")
        google = Stock("GOOGL")
        microsoft = Stock("MSFT")
        with pytest.raises(ValueError):
            Portfolio(initial_allocation={
                appl: Decimal(0.5),
                google: Decimal(0.3),
                microsoft: Decimal(-0.2)
            })
            assert e.value.message == "Allocation values must be positive"

    def test_validate_allocations_total_greater_than_100(self):
        appl = Stock("AAPL")
        google = Stock("GOOGL")
        microsoft = Stock("MSFT")
        with pytest.raises(ValueError):
            Portfolio(initial_allocation={
                appl: Decimal(0.5),
                google: Decimal(0.3),
                microsoft: Decimal(1.2)
            })
            assert e.value.message == "Allocation values must be less than or equal to 1"

    def test_add_stock(self):
        appl = Stock("AAPL")
        google = Stock("GOOGL")
        microsoft = Stock("MSFT")
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.3),
            microsoft: Decimal(0.2)
        })
        
        portafolio.add_stock(stock=appl, amount=Decimal(1))
        assert portafolio._stocks == {
            str(appl): {"stock": appl, "amount": Decimal(1)},
            str(google): {"stock": google, "amount": Decimal(0)},
            str(microsoft): {"stock": microsoft, "amount": Decimal(0)}
        }
        portafolio.add_stock(stock=appl, amount=Decimal(1))
        assert portafolio._stocks == {
            str(appl): {"stock": appl, "amount": Decimal(2)},
            str(google): {"stock": google, "amount": Decimal(0)},
            str(microsoft): {"stock": microsoft, "amount": Decimal(0)}
        }

    def test_get_portfolio_value(self):
        appl = Stock("AAPL")
        google = Stock("GOOGL")
        microsoft = Stock("MSFT")
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.3),
            microsoft: Decimal(0.2)
        })
        portafolio.add_stock(stock=appl, amount=Decimal(1))
        portafolio.add_stock(stock=google, amount=Decimal(1))
        portafolio.add_stock(stock=microsoft, amount=Decimal(1))
        assert portafolio.get_portfolio_value() == Decimal(300)

    def test_rebalance_no_actions(self):
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.5)
        })
        portafolio.add_stock(stock=appl, amount=Decimal(1))
        portafolio.add_stock(stock=google, amount=Decimal(1))
        assert portafolio.rebalance() == {
            "sell": [],
            "buy": []
        }

    def test_rebalance_actions(self):
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.5)
        })
        portafolio.add_stock(stock=appl, amount=Decimal(2))
        portafolio.add_stock(stock=google, amount=Decimal(1))
        assert portafolio.rebalance() == {
            "sell": [{"stock": appl, "amount": Decimal(-0.5)}],
            "buy": [{"stock": google, "amount": Decimal(+0.5)}]
        }

```

```python
import pytest

from src.models.portafolio import Portfolio

from src.models.stock import Stock
from decimal import Decimal

class TestPortafolio:
    def test_validate_allocations(self):
        appl = Stock("AAPL")
        google = Stock("GOOGL")
        microsoft = Stock("MSFT")
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.3),
            microsoft: Decimal(0.2)
        })
        assert portafolio._allocations == {
            appl: Decimal(0.5),
            google: Decimal(0.3),
            microsoft: Decimal(0.2)
        }

    def test_validate_allocations_empty(self):
        portafolio = Portfolio(initial_allocation={})
        assert portafolio._allocations == {}

    def test_validate_allocations_total_not_1(self):
        appl = Stock("AAPL")
        google = Stock("GOOGL")
        microsoft = Stock("MSFT")
        with pytest.raises(ValueError) as e:
            Portfolio(initial_allocation={
                appl: Decimal(0.5),
                google: Decimal(0.3),
                microsoft: Decimal(0.3)
            })
            assert e.value.message == "Total allocation must be 1, but is 1.1"

    def test_validate_allocations_total_less_than_100(self):
        appl = Stock("AAPL")
        google = Stock("GOOGL")
        microsoft = Stock("MSFT")
        with pytest.raises(ValueError):
            Portfolio(initial_allocation={
                appl: Decimal(0.5),
                google: Decimal(0.3),
                microsoft: Decimal(-0.2)
            })
            assert e.value.message == "Allocation values must be positive"

    def test_validate_allocations_total_greater_than_100(self):
        appl = Stock("AAPL")
        google = Stock("GOOGL")
        microsoft = Stock("MSFT")
        with pytest.raises(ValueError):
            Portfolio(initial_allocation={
                appl: Decimal(0.5),
                google: Decimal(0.3),
                microsoft: Decimal(1.2)
            })
            assert e.value.message == "Allocation values must be less than or equal to 1"

    def test_add_stock(self):
        appl = Stock("AAPL")
        google = Stock("GOOGL")
        microsoft = Stock("MSFT")
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.3),
            microsoft: Decimal(0.2)
        })
        
        portafolio.add_stock(stock=appl, amount=Decimal(1))
        assert portafolio._stocks == {
            str(appl): {"stock": appl, "amount": Decimal(1)},
            str(google): {"stock": google, "amount": Decimal(0)},
            str(microsoft): {"stock": microsoft, "amount": Decimal(0)}
        }
        portafolio.add_stock(stock=appl, amount=Decimal(1))
        assert portafolio._stocks == {
            str(appl): {"stock": appl, "amount": Decimal(2)},
            str(google): {"stock": google, "amount": Decimal(0)},
            str(microsoft): {"stock": microsoft, "amount": Decimal(0)}
        }

    def test_get_portfolio_value(self):
        appl = Stock("AAPL")
        google = Stock("GOOGL")
        microsoft = Stock("MSFT")
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.3),
            microsoft: Decimal(0.2)
        })
        portafolio.add_stock(stock=appl, amount=Decimal(1))
        portafolio.add_stock(stock=google, amount=Decimal(1))
        portafolio.add_stock(stock=microsoft, amount=Decimal(1))
        assert portafolio.get_portfolio_value() == Decimal(300)

    def test_rebalance_no_actions(self):
        appl = Stock("AAPL")
        google = Stock("GOOGL")
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.5)
        })
        portafolio.add_stock(stock=appl, amount=Decimal(1))
        portafolio.add_stock(stock=google, amount=Decimal(1))
        assert portafolio.rebalance() == {
            "sell": [],
            "buy": []
        }

    def test_rebalance_actions(self):
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.5)
        })
        portafolio.add_stock(stock=appl, amount=Decimal(2))
        portafolio.add_stock(stock=google, amount=Decimal(1))
        assert portafolio.rebalance() == {
            "sell": [{"stock": appl, "amount": Decimal(-0.5)}],
            "buy": [{"stock": google, "amount": Decimal(+0.5)}]
        }

```

```python
import pytest

from src.models.portafolio import Portfolio

from src.models.stock import Stock
from decimal import Decimal

class TestPortafolio:
    def test_validate_allocations(self):
        appl = Stock("AAPL")
        google = Stock("GOOGL")
        microsoft = Stock("MSFT")
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.3),
            microsoft: Decimal(0.2)
        })
        assert portafolio._allocations == {
            appl: Decimal(0.5),
            google: Decimal(0.3),
            microsoft: Decimal(0.2)
        }

    def test_validate_allocations_empty(self):
        portafolio = Portfolio(initial_allocation={})
        assert portafolio._allocations == {}

    def test_validate_allocations_total_not_1(self):
        appl = Stock("AAPL")
        google = Stock("GOOGL")
        microsoft = Stock("MSFT")
        with pytest.raises(ValueError) as e:
            Portfolio(initial_allocation={
                appl: Decimal(0.5),
                google: Decimal(0.3),
                microsoft: Decimal(0.3)
            })
            assert e.value.message == "Total allocation must be 1, but is 1.1"

    def test_validate_allocations_total_less_than_100(self):
        appl = Stock("AAPL")
        google = Stock("GOOGL")
        microsoft = Stock("MSFT")
        with pytest.raises(ValueError):
            Portfolio(initial_allocation={
                appl: Decimal(0.5),
                google: Decimal(0.3),
                microsoft: Decimal(-0.2)
            })
            assert e.value.message == "Allocation values must be positive"

    def test_validate_allocations_total_greater_than_100(self):
        appl = Stock("AAPL")
        google = Stock("GOOGL")
        microsoft = Stock("MSFT")
        with pytest.raises(ValueError):
            Portfolio(initial_allocation={
                appl: Decimal(0.5),
                google: Decimal(0.3),
                microsoft: Decimal(1.2)
            })
            assert e.value.message == "Allocation values must be less than or equal to 1"

    def test_add_stock(self):
        appl = Stock("AAPL")
        google = Stock("GOOGL")
        microsoft = Stock("MSFT")
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.3),
            microsoft: Decimal(0.2)
        })
        
        portafolio.add_stock(stock=appl, amount=Decimal(1))
        assert portafolio._stocks == {
            str(appl): {"stock": appl, "amount": Decimal(1)},
            str(google): {"stock": google, "amount": Decimal(0)},
            str(microsoft): {"stock": microsoft, "amount": Decimal(0)}
        }
        portafolio.add_stock(stock=appl, amount=Decimal(1))
        assert portafolio._stocks == {
            str(appl): {"stock": appl, "amount": Decimal(2)},
            str(google): {"stock": google, "amount": Decimal(0)},
            str(microsoft): {"stock": microsoft, "amount": Decimal(0)}
        }

    def test_get_portfolio_value(self):
        appl = Stock("AAPL")
        google = Stock("GOOGL")
        microsoft = Stock("MSFT")
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.3),
            microsoft: Decimal(0.2)
        })
        portafolio.add_stock(stock=appl, amount=Decimal(1))
        portafolio.add_stock(stock=google, amount=Decimal(1))
        portafolio.add_stock(stock=microsoft, amount=Decimal(1))
        assert portafolio.get_portfolio_value() == Decimal(300)

    def test_rebalance_no_actions(self):
        appl = Stock("AAPL")
        google = Stock("GOOGL")
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.5)
        })
        portafolio.add_stock(stock=appl, amount=Decimal(1))
        portafolio.add_stock(stock=google, amount=Decimal(1))
        assert portafolio.rebalance() == {
            "sell": [],
            "buy": []
        }

    def test_rebalance_actions(self):
        appl = Stock("AAPL")
        google = Stock("GOOGL")
        portafolio = Portfolio(initial_allocation={
            appl: Decimal(0.5),
            google: Decimal(0.5)
        })
        portafolio.add_stock(stock=appl, amount=Decimal(2))
        portafolio.add_stock(stock=google, amount=Decimal(1))
        assert portafolio.rebalance() == {
            "sell": [{"stock": appl, "amount": Decimal(-0.5)}],
            "buy": [{"stock": google, "amount": Decimal(+0.5)}]
        }

```


Verifying the file is correct and checking for issues:



## Changes Made:

1. **Updated `conftest.py`**:
   - Added mock for `stock.fetcher.fetch_price` to prevent API calls during `Stock.__init__`
   - Kept the mock for `Stock.get_price` for method calls

2. **Moved Stock instances into tests**:
   - Removed module-level `appl`, `google`, and `microsoft` instances (lines 8-10)
   - Each test now creates its Stock instances inside the test method
   - Stock instances are created after the fixture sets up the mocks

## Benefits:

- No API calls during module import: Stock instances are created only when tests run, after mocks are in place
- Tests are isolated: each test creates its own Stock instances
- Cleaner code: no module-level test data

The fixture automatically mocks both:
- `stock.fetcher.fetch_price` — prevents API calls during `Stock.__init__`
- `Stock.get_price` — ensures consistent return values for method calls

All tests should now run without making real API calls.

