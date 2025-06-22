from enum import StrEnum


class Interval(StrEnum):
    """Interval for history endpoints."""

    M1 = "1min"
    M5 = "5min"
    M15 = "15min"
    M30 = "30min"
    H1 = "1hour"
    H2 = "2hour"
    H4 = "4hour"
    H6 = "6hour"
    H12 = "12hour"
    D1 = "daily"


class Endpoint(StrEnum):
    """Supporting endpoints."""

    EXCHANGES = "exchanges"
    FUTURE_MARKETS = "future-markets"
    SPOT_MARKETS = "spot-markets"


class CurrentEndpoint(StrEnum):
    """Current endpoints."""

    OI = "open-interest"
    FUNDING_RATE = "funding-rate"
    PREDICTED_FUNDING_RATE = "predicted-funding-rate"


class HistoryEndpoint(StrEnum):
    """History endpoints."""

    OI = "open-interest-history"
    FUNDING_RATE = "funding-rate-history"
    PREDICTED_FUNDING_RATE = "predicted-funding-rate-history"
    LIQUIDATION = "liquidation-history"
    LSRATIO = "long-short-ratio-history"
    OHLCV = "ohlcv-history"
