try:
    from enum import StrEnum          # Py3.11+
except ImportError:
    from strenum import StrEnum       # backport for Py3.7+

try:
    from typing import Self          # 3.11+
except ImportError:
    from typing_extensions import Self



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


class BaseEndpoint(StrEnum):
    """Base endpoints."""

    @classmethod
    def from_string(cls, endpoint: str) -> Self:
        """Get the BaseEndpoint enum from a string."""
        try:
            return cls(endpoint)
        except ValueError as e:
            members = ", ".join([member.value for member in cls])
            raise ValueError(f"Unknown endpoint: {endpoint}. " + f"Supported values are: {members}.") from e


class Endpoint(BaseEndpoint):
    """Supporting endpoints."""

    EXCHANGES = "exchanges"
    FUTURE_MARKETS = "future-markets"
    SPOT_MARKETS = "spot-markets"


class CurrentEndpoint(BaseEndpoint):
    """Current endpoints."""

    OI = "open-interest"
    FUNDING_RATE = "funding-rate"
    PREDICTED_FUNDING_RATE = "predicted-funding-rate"


class HistoryEndpoint(BaseEndpoint):
    """History endpoints."""

    OI = "open-interest"
    FUNDING_RATE = "funding-rate"
    PREDICTED_FUNDING_RATE = "predicted-funding-rate"
    LIQUIDATION = "liquidation"
    LSRATIO = "long-short-ratio"
    OHLCV = "ohlcv"

    def __str__(self) -> str:
        return self.value + "-history"
