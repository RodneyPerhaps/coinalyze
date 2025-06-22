import datetime as dt

from coinalyze.constants import LOOKBACK
from coinalyze.types import Time


def _utc_today() -> dt.datetime:
    """Get today's date in UTC timezone with time set to 00:00:00."""
    return dt.datetime.now(dt.UTC).replace(hour=0, minute=0, second=0, microsecond=0)


def set_start_and_end(start: Time | None = None, end: Time | None = None) -> tuple[Time, Time]:
    """Set default start and end dates with UTC timezone."""
    if start is None:
        start = _utc_today() - dt.timedelta(days=LOOKBACK)
    if end is None:
        end = _utc_today()
    return start, end


def to_timestamp(date: Time) -> int:
    """Convert a datetime or date to a POSIX timestamp."""
    if isinstance(date, dt.datetime):
        return int(date.timestamp())
    if isinstance(date, dt.date):
        return int(dt.datetime(date.year, date.month, date.day).timestamp())
    return int(dt.datetime.strptime(date, "%Y-%m-%d").timestamp())


def from_timestamp(timestamp: int) -> dt.datetime:
    """Convert a POSIX timestamp to a datetime."""
    if timestamp > 1e12:
        # Timestamp is in milliseconds -> convert to seconds
        timestamp = int(timestamp / 1000)
    return dt.datetime.fromtimestamp(timestamp, tz=dt.UTC)


def bool_to_string(b: bool) -> str:
    """Convert a boolean to a string equivalent."""
    return "true" if b else "false"
