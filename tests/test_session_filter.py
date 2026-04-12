"""Tests for is_active_session() session filter helper."""
from datetime import datetime, timezone

import pytest

from src.strategy import SessionType, is_active_session


# -- EU-US overlap: Mon-Fri 12:00-15:59 UTC → ACTIVE ----------------------

def test_eu_us_overlap_is_active():
    # Wednesday 14:00 UTC
    ts = datetime(2026, 4, 8, 14, 0, tzinfo=timezone.utc)
    assert is_active_session(ts) == SessionType.ACTIVE


def test_overlap_boundary_start_is_active():
    # Friday 12:00 UTC (inclusive)
    ts = datetime(2026, 4, 10, 12, 0, tzinfo=timezone.utc)
    assert is_active_session(ts) == SessionType.ACTIVE


def test_overlap_boundary_end_is_reduced():
    # Friday 16:00 UTC (exclusive upper bound)
    ts = datetime(2026, 4, 10, 16, 0, tzinfo=timezone.utc)
    assert is_active_session(ts) == SessionType.REDUCED


# -- Outside overlap on weekday → REDUCED ----------------------------------

def test_asian_session_is_reduced():
    # Tuesday 03:00 UTC (Asian session)
    ts = datetime(2026, 4, 7, 3, 0, tzinfo=timezone.utc)
    assert is_active_session(ts) == SessionType.REDUCED


def test_late_us_session_is_reduced():
    # Monday 20:00 UTC
    ts = datetime(2026, 4, 6, 20, 0, tzinfo=timezone.utc)
    assert is_active_session(ts) == SessionType.REDUCED


# -- Weekend → REDUCED regardless of hour ---------------------------------

def test_saturday_is_reduced():
    ts = datetime(2026, 4, 11, 14, 0, tzinfo=timezone.utc)  # Saturday
    assert is_active_session(ts) == SessionType.REDUCED


def test_sunday_is_reduced():
    ts = datetime(2026, 4, 12, 14, 0, tzinfo=timezone.utc)  # Sunday
    assert is_active_session(ts) == SessionType.REDUCED


# -- Naive datetime treated as UTC ----------------------------------------

def test_naive_datetime_treated_as_utc():
    naive = datetime(2026, 4, 8, 13, 30)  # Wednesday, no tzinfo
    assert is_active_session(naive) == SessionType.ACTIVE


# -- pandas.Timestamp input -----------------------------------------------

def test_pandas_timestamp():
    import pandas as pd
    ts = pd.Timestamp("2026-04-08 15:00", tz="UTC")
    assert is_active_session(ts) == SessionType.ACTIVE


# -- Default (no arg) returns a valid SessionType -------------------------

def test_default_returns_session_type():
    result = is_active_session()
    assert isinstance(result, SessionType)
