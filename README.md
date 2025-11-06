# Requisitos

Nota: la instalación es para dispositivos OSX

- Poetry (`brew install poetry`)
- Pyenv (`brew install pyenv`)
- Python 3.13 (`pyenv local 3.13` - `pyenv install 3.13`)
- Instalar dependencias de python (`poetry install`)
- Finalmente para ejecutar

```
poetry run python src/main.py
```

Output de ejemplo

```
1.- Get initial stocks prices:
Price from Finnhub: 270.14
Price from Finnhub: 284.31
Price from Alpha Vantage: 507.1600
Stock name: AAPL, current price: 270.14
Stock name: GOOGL, current price: 284.31
Stock name: MSFT, current price: 507.16
--------------------------------
2.Initial portfolio is unbalanced:
Stock name: AAPL
  Target value for AAPL is: 1608.975000
  Current value for AAPL is: 1350.700000
  Delta shares for AAPL is: 0.9560783298
Stock name: GOOGL
  Target value for GOOGL is: 321.7950000
  Current value for GOOGL is: 852.9300000
  Delta shares for GOOGL is: -1.868154479
Stock name: MSFT
  Target value for MSFT is: 1287.180000
  Current value for MSFT is: 1014.3200
  Delta shares for MSFT is: 0.5380156164
--------------------------------
3. Actions to balance the portfolio:
  Buy 0.9560783298 shares of AAPL
  Buy 0.5380156164 shares of MSFT
  Sell -1.868154479 shares of GOOGL
4. By adding the delta shares to the stocks, the portfolio is now balanced.
--------------------------------
5. Balanced portfolio:
Stock name: AAPL
  Target value for AAPL is: 1608.975000
  Current value for AAPL is: 1608.975000
  Delta shares for AAPL is: 0E+37
  No action needed for AAPL
Stock name: GOOGL
  Target value for GOOGL is: 321.7950000
  Current value for GOOGL is: 321.7950001
  Delta shares for GOOGL is: -3.517287468E-10
  No action needed for GOOGL
Stock name: MSFT
  Target value for MSFT is: 1287.180000
  Current value for MSFT is: 1287.180000
  Delta shares for MSFT is: 0.00
  No action needed for MSFT
  No actions needed.
```

# Introducción

Esta tarea siguió el siguiente procedimiento

1. Leer y entender el problema. Para tener más contexto sobre acciones y balanceos utilicé ChatGPT
2. Seteo base con poetry y crear las estructuras iniciales para la estructura base
3. Instalar pytest y pytest-mock para el seteo de tests básicos
4. Integrar API externa para leer el precio de las acciones. La IDE Cursor facilitó la integración de la API
5. Desarrollo de métodos para rebalancear un portafolio
6. Validación, tests y lint (con `black`)

# Desafíos

El mayor desafío fue entender el balanceo del portafolio. Luego de entender la lógica de cómo funciona, el siguiente desafío fue el manejo de decimales, ya que en especial con manejo de dinero, es necesario que sea lo más preciso posible.

Para el balanceo se dejó un margen de tolerancia para que se considere balanceado, dado el problema de precisión.

Para manejar esto, se utilizó la librería `Decimal`, la cual actúa de forma en base 10 al momento de realizar el cálculo, por lo que todos los métodos utilizan objetos de esta clase.

# Test y Lint

Para ejecutar los tests

```
poetry run pytest tests/
```

Para ejecutar el lint

```
poetry run black .
```
