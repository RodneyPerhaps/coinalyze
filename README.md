# coinalyze

[![Ruff][ruff-badge]](https://github.com/astral-sh/ruff)
[![PyPI][pypi-badge]](https://pypi.org/project/coinalyze/)
[![Python versions][python-versions-badge]](https://github.com/ivarurdalen/coinalyze)
[![MIT License Badge][license-badge]][license]

This is an unofficial Python client for [coinalyze.net REST API](https://api.coinalyze.net/v1/doc/).

## Features

- Implementation of all endpoints.
- Uses [httpx](https://www.python-httpx.org/) for making HTTP requests
- Uses [pyrate-limiter](https://github.com/vutran1710/PyrateLimiter/tree/master) for maintaining [40 API calls per minute](https://api.coinalyze.net/v1/doc/).
- Uses [httpx-retries](https://github.com/will-ockmore/httpx-retries) for handling retries.
- Provides convenience functions to get results as pandas DataFrames

## Installation

```bash
pip install coinalyze
```

## Usage

1. Add your API key from [coinalyze.net](https://coinalyze.net/account/api-key/) to your environment variables as `COINALYZE_API_KEY`.
2. Then use the client as shown in the example below.

See more examples in the [coinalyze_client notebook](examples/coinalyze_client.ipynb).

```python
import os
from coinalyze import CoinalyzeClient, HistoryEndpoint, Interval, response_to_df, history_response_to_df

client = CoinalyzeClient(api_key=os.getenv("COINALYZE_API_KEY"))

# Get exchange information as a list of dictionaries
client.get_exchanges()

# Get the supported future markets as a DataFrame
future_markets_df = response_to_df(client.get_future_markets())

# Get the current predicted funding rate
response = client.get_current_predicted_funding_rate("BTCUSDT_PERP.A")

# Get the open interest history as a DataFrame for a symbol
oi_df = client.get_history_df(
        endpoint=HistoryEndpoint.OI,
        symbols="BTCUSDT_PERP.A",
        interval=Interval.H4,
        start="2025-06-01",
        end="2025-06-20",
    )
```

[ruff-badge]: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
[license]: ./LICENSE
[license-badge]: https://img.shields.io/badge/License-MIT-blue.svg
[python-versions-badge]: https://img.shields.io/pypi/pyversions/coinalyze.svg
[pypi-badge]: https://img.shields.io/pypi/coinalyze.svg
