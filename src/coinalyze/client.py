from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

import httpx
from httpx_retries import Retry, RetryTransport
from pyrate_limiter import Duration, Limiter, Rate

from coinalyze.constants import BASE_API_URL, MAX_SYMBOLS_PER_REQUEST, ONE_SECOND_IN_MS
from coinalyze.enums import CurrentEndpoint, Endpoint, HistoryEndpoint, Interval
from coinalyze.types import Time
from coinalyze.util.base import bool_to_string, set_start_and_end, to_timestamp

if TYPE_CHECKING:
    try:
        import pandas as pd
    except ImportError:
        pass

logger = logging.getLogger(__name__)


class CoinalyzeClient:
    """
    Client for Coinalyze API.

    Docs: https://api.coinalyze.net/v1/doc/
    """

    def __init__(self, api_key: str | None = None, httpx_client: httpx.Client | None = None) -> None:
        """
        Coinalyze API client constructor.

        Args:
            api_key: API key for authentication.
            httpx_client: Optional httpx client to use for requests.
        """
        if api_key is None:
            try:
                api_key = os.environ["COINALYZE_API_KEY"]
            except KeyError as e:
                raise ValueError("If api_key is not provided, COINALYZE_API_KEY must be set in the environment") from e
        headers = {"api_key": api_key}
        # Retry has a default policy of retrying 429 codes and reading the Retry-After header
        # for calculating the delay.
        self._client = httpx_client or httpx.Client(headers=headers, transport=RetryTransport(retry=Retry(total=10)))
        self._limiter = Limiter(
            Rate(40, Duration.MINUTE), raise_when_fail=False, max_delay=Duration.MINUTE.value + ONE_SECOND_IN_MS
        )
        self._counter = 0

    def _get(self, endpoint: HistoryEndpoint | Endpoint | CurrentEndpoint, params: dict | None = None) -> list[dict]:
        """
        Make a GET request to the Coinalyze API using the httpx client.

        Args:
            endpoint: The endpoint to make the request to.
            params: Optional parameters to pass to the request.

        Raises:
            httpx.HTTPStatusError: If the request and the server respond with an error.
            Exception: If an unexpected error occurs.
        """
        if params is None:
            params = {}
        try:
            self._counter += 1
            # Since the API is rate limited per symbol, we need to weight the request
            # by the number of symbols.
            weight = 1
            if symbols := params.get("symbols"):
                params["symbols"] = ",".join(symbols)
                weight = len(symbols)

            self._limiter.try_acquire(str(self._counter), weight)

            response = self._client.get(url=f"{BASE_API_URL}{endpoint}", params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error("HTTP error: %s", e)
            raise
        except Exception as e:
            logger.error("Unexpected error: %s", e)
            raise

    def get_exchanges(self) -> list[dict]:
        """Get supported exchanges."""
        return self._get(Endpoint.EXCHANGES)

    def get_future_markets(self) -> list[dict]:
        """Get supported future markets."""
        return self._get(Endpoint.FUTURE_MARKETS)

    def get_spot_markets(self) -> list[dict]:
        """Get supported spot markets."""
        return self._get(Endpoint.SPOT_MARKETS)

    def get(self, endpoint: Endpoint | str) -> list[dict]:
        """
        Get exchanges, future markets or spot markets data.

        Args:
            endpoint: The endpoint to make the request to. Can be: exchanges, future-markets or spot-markets.
        """
        if isinstance(endpoint, str):
            endpoint = Endpoint.from_string(endpoint)
        return self._get(endpoint)

    def get_current_open_interest(self, symbols: str | list[str]) -> list[dict]:
        """Get current open interest."""
        return self.get_current(CurrentEndpoint.OI, symbols)

    def get_current_funding_rate(self, symbols: str | list[str]) -> list[dict]:
        """Get current funding rate."""
        return self.get_current(CurrentEndpoint.FUNDING_RATE, symbols)

    def get_current_predicted_funding_rate(self, symbols: str | list[str]) -> list[dict]:
        """Get current predicted funding rate."""
        return self.get_current(CurrentEndpoint.PREDICTED_FUNDING_RATE, symbols)

    def get_current(self, endpoint: CurrentEndpoint | str, symbols: str | list[str]) -> list[dict]:
        """Get current data for open interest, funding rate or predicted funding rate."""
        if isinstance(endpoint, str):
            endpoint = CurrentEndpoint.from_string(endpoint)
        return self._get_with_symbols(endpoint, symbols)

    def _get_with_symbols(
        self, endpoint: HistoryEndpoint | CurrentEndpoint, symbols: str | list[str], params: dict | None = None
    ) -> list[dict]:
        if isinstance(symbols, str):
            symbols = [symbols]
        if len(symbols) > MAX_SYMBOLS_PER_REQUEST:
            raise ValueError(f"A single request can not have more than {MAX_SYMBOLS_PER_REQUEST} symbols")
        params = params or {}
        params["symbols"] = symbols
        return self._get(endpoint, params)

    def get_history(
        self,
        endpoint: HistoryEndpoint | str,
        symbols: str | list[str],
        interval: Interval | str = Interval.D1,
        start: Time | None = None,
        end: Time | None = None,
        convert_to_usd: bool | None = None,
    ) -> list[dict]:
        """
        Get historical data for the specified endpoint.

        Args:
            endpoint: The history endpoint enum (e.g., OI, FUNDING_RATE, LIQUIDATION, LSRATIO, OHLCV).
            symbols: Symbol(s) to query.
            interval: Data interval.
            start: Start time.
            end: End time.
            convert_to_usd: Only used for endpoints that support it (e.g., OI, LIQUIDATION).

        Returns:
            list[dict]: Historical data from the API.
        """
        if isinstance(endpoint, str):
            endpoint = HistoryEndpoint.from_string(endpoint)
        if isinstance(interval, str):
            interval = Interval(interval)
        start, end = set_start_and_end(start, end)
        params = {"interval": str(interval), "from": to_timestamp(start), "to": to_timestamp(end)}
        if convert_to_usd is not None:
            params["convert_to_usd"] = bool_to_string(convert_to_usd)
        return self._get_with_symbols(endpoint, symbols, params)

    def get_history_df(
        self,
        endpoint: HistoryEndpoint | str,
        symbols: str | list[str],
        interval: Interval | str = Interval.D1,
        start: Time | None = None,
        end: Time | None = None,
        convert_to_usd: bool | None = None,
    ) -> pd.DataFrame:
        """Return historical data from the API as a pandas DataFrame. See `get_history` method for more details."""
        try:
            from coinalyze.util.pandas import history_response_to_df
        except ImportError:
            logger.error("pandas is required to use this method")
            raise

        if isinstance(endpoint, str):
            endpoint = HistoryEndpoint.from_string(endpoint)
        return history_response_to_df(
            self.get_history(endpoint, symbols, interval, start, end, convert_to_usd), endpoint
        )
