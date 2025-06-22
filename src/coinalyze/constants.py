from coinalyze.enums import HistoryEndpoint

BASE_API_URL = "https://api.coinalyze.net/v1/"

ONE_SECOND_IN_MS = 1000

LOOKBACK = 30  # days to look back for history
MAX_SYMBOLS_PER_REQUEST = 20

OHLC = {"o": "open", "h": "high", "l": "low", "c": "close"}

COLS_MAPPING: dict[HistoryEndpoint, dict[str, str]] = {
    HistoryEndpoint.OI: OHLC,
    HistoryEndpoint.FUNDING_RATE: OHLC,
    HistoryEndpoint.PREDICTED_FUNDING_RATE: OHLC,
    HistoryEndpoint.OHLCV: {**OHLC, "v": "volume", "bv": "buyvolume", "tx": "trades", "btx": "buytrades"},
    HistoryEndpoint.LIQUIDATION: {"l": "longvolume", "s": "shortvolume"},
    HistoryEndpoint.LSRATIO: {"r": "ratio", "l": "longpct", "s": "shortpct"},
}
