import httpx
import pytest
import respx

from coinalyze.constants import BASE_API_URL

current_json = [{"symbol": "BTCUSDT_PERP.A", "update": 1735686000000, "value": 1}]
history_json = [{"symbol": "BTCUSDT_PERP.A", "history": [{"t": 1735686000000, "o": 1, "h": 2, "l": 3, "c": 4}]}]

endpoints_data: dict[str, list[dict]] = {
    "exchanges": [{"name": "Binance", "code": "A"}],
    "future-markets": [
        {
            "symbol": "BTCUSDT_PERP.A",
            "exchange": "A",
            "symbol_on_exchange": "BTCUSDT",
            "base_asset": "BTC",
            "quote_asset": "USDT",
        }
    ],
    "spot-markets": [
        {
            "symbol": "BTC/USDT",
            "exchange": "A",
            "symbol_on_exchange": "BTCUSDT",
            "base_asset": "BTC",
            "quote_asset": "USDT",
            "has_buy_sell_data": True,
        }
    ],
    "open-interest": current_json,
    "funding-rate": current_json,
    "predicted-funding-rate": current_json,
    "open-interest-history": history_json,
    "funding-rate-history": history_json,
    "predicted-funding-rate-history": history_json,
    "liquidation-history": [{"symbol": "BTCUSDT_PERP.A", "history": [{"t": 1735686000000, "l": 1, "s": 2}]}],
    "long-short-ratio-history": [
        {"symbol": "BTCUSDT_PERP.A", "history": [{"t": 1735686000000, "r": 1, "l": 2, "s": 3}]}
    ],
    "ohlcv-history": [
        {
            "symbol": "BTCUSDT_PERP.A",
            "history": [{"t": 1735686000000, "o": 1, "h": 2, "l": 3, "c": 4, "v": 5, "bv": 6, "tx": 7, "btx": 8}],
        }
    ],
}

valid_symbols = {"BTCUSDT_PERP.A"}


def side_effect(request: httpx.Request) -> httpx.Response:
    if request.headers.get("api_key") != "api_key":
        raise httpx.HTTPStatusError(message="Unauthorized", request=request, response=httpx.Response(401))
    endpoint = request.url.path.split("/")[-1]
    data = endpoints_data[endpoint]

    params = request.url.params
    if "symbols" in params:
        symbols_list = params["symbols"].split(",")
        symbols = set(symbols_list).intersection(valid_symbols)
        data = [item for item in data if item["symbol"] in symbols]

    return httpx.Response(200, json=data)


@pytest.fixture
def mocked_api():
    with respx.mock(base_url=BASE_API_URL, assert_all_called=False) as rm:
        for endpoint in endpoints_data:
            rm.get(endpoint, name=endpoint).mock(side_effect=side_effect)

        yield rm
