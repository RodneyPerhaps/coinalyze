import httpx
import pytest

from coinalyze.client import CoinalyzeClient as Client
from coinalyze.constants import MAX_SYMBOLS_PER_REQUEST
from coinalyze.enums import CurrentEndpoint, Endpoint, HistoryEndpoint, Interval


@pytest.fixture
def client() -> Client:
    return Client(api_key="api_key")


@pytest.mark.parametrize(
    "method,endpoint,kwargs",
    [
        ("get", Endpoint.EXCHANGES, {}),
        ("get", Endpoint.FUTURE_MARKETS, {}),
        ("get", Endpoint.SPOT_MARKETS, {}),
        ("get_current", CurrentEndpoint.OI, {"symbols": "BTCUSDT_PERP.A"}),
        ("get_current", CurrentEndpoint.FUNDING_RATE, {"symbols": "BTCUSDT_PERP.A"}),
        ("get_current", CurrentEndpoint.PREDICTED_FUNDING_RATE, {"symbols": "BTCUSDT_PERP.A"}),
        ("get_history", HistoryEndpoint.OI, {"symbols": "BTCUSDT_PERP.A"}),
        ("get_history", HistoryEndpoint.FUNDING_RATE, {"symbols": "BTCUSDT_PERP.A"}),
        ("get_history", HistoryEndpoint.PREDICTED_FUNDING_RATE, {"symbols": "BTCUSDT_PERP.A", "interval": "daily"}),
        (
            "get_history",
            HistoryEndpoint.LIQUIDATION,
            {"symbols": "BTCUSDT_PERP.A", "start": "2024-01-01", "end": "2024-01-31"},
        ),
        ("get_history", HistoryEndpoint.LSRATIO, {"symbols": "BTCUSDT_PERP.A", "interval": "daily"}),
        ("get_history", HistoryEndpoint.OHLCV, {"symbols": "BTCUSDT_PERP.A", "interval": Interval.H4}),
    ],
)
def test_endpoints(mocked_api, client: Client, method: str, endpoint: str, kwargs: dict):
    response = getattr(client, method)(endpoint, **kwargs)
    # Assert that response is a list of dictionaries.
    assert isinstance(response, list)
    assert len(response) > 0
    assert all(isinstance(item, dict) for item in response)


def test_invalid_symbol(mocked_api, client: Client):
    """Test that invalid symbol returns empty data with 200 status code."""
    response = client.get_history("open-interest", symbols="invalid_symbol")
    assert isinstance(response, list)
    assert response == []


@pytest.mark.parametrize(
    "method,endpoint,kwargs",
    [
        ("get_history", "price", {"symbols": "BTCUSDT_PERP.A"}),
        ("get_current", "price", {"symbols": "BTCUSDT_PERP.A"}),
        ("get", "price", {}),
    ],
)
def test_invalid_endpoints(client: Client, method: str, endpoint: str, kwargs: dict):
    with pytest.raises(ValueError) as e:
        getattr(client, method)(endpoint, **kwargs)
    assert "Unknown endpoint" in str(e.value)


def test_too_many_symbols(client: Client):
    with pytest.raises(ValueError) as e:
        client.get_history("open-interest", symbols=["symbol"] * (MAX_SYMBOLS_PER_REQUEST + 1))
    assert "A single request can not have more than" in str(e.value)


def test_invalid_api_key(mocked_api):
    with pytest.raises(httpx.HTTPStatusError) as e:
        Client(api_key="invalid_api_key").get_exchanges()
    assert "Unauthorized" in str(e.value)


def test_no_api_key(monkeypatch):
    monkeypatch.delenv("COINALYZE_API_KEY", raising=False)
    with pytest.raises(ValueError) as e:
        Client()
    assert "COINALYZE_API_KEY must be set in the environment" in str(e.value)
