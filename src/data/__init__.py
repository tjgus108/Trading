from .health_check import (
    DataFeedsHealthCheck,
    DataHealthCheck,
    FeedHealthReport,
    FeedStatus,
)

__all__ = [
    "DataFeed",
    "DataFeedsHealthCheck",
    "DataHealthCheck",
    "FeedHealthReport",
    "FeedStatus",
]


def __getattr__(name: str):
    """Lazy-load DataFeed to avoid importing ccxt at collection time."""
    if name == "DataFeed":
        from .feed import DataFeed
        return DataFeed
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
