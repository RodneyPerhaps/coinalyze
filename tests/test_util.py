import datetime as dt

import pytest

from coinalyze.util.base import from_timestamp, set_start_and_end, to_timestamp

LOOKBACK = 30  # Should match the value in util.base


def test_set_start_and_end_defaults(monkeypatch):
    today = dt.datetime(2025, 1, 1, tzinfo=dt.UTC)
    # Patch _utc_today to control 'today' value
    monkeypatch.setattr("coinalyze.util.base._utc_today", lambda: today)
    start, end = set_start_and_end()
    assert end == today
    assert start == today - dt.timedelta(days=LOOKBACK)


def test_set_start_and_end_args():
    start = dt.datetime(2025, 1, 1, tzinfo=dt.UTC)
    end = dt.datetime(2025, 2, 1, tzinfo=dt.UTC)
    s, e = set_start_and_end(start, end)
    assert s == start
    assert e == end


@pytest.mark.parametrize("date", [dt.datetime(2025, 1, 1), dt.date(2025, 1, 1), "2025-01-01"])
def test_to_timestamp(date):
    ts = to_timestamp(date)
    assert ts == int(dt.datetime(2025, 1, 1).timestamp())


def test_from_timestamp_ms():
    timestamp = 1750625067892
    ts = from_timestamp(timestamp)
    assert ts == dt.datetime.fromtimestamp(int(timestamp / 1000), tz=dt.UTC)


def test_from_timestamp_s():
    timestamp = 1750550400
    ts = from_timestamp(timestamp)
    assert ts == dt.datetime.fromtimestamp(timestamp, tz=dt.UTC)
