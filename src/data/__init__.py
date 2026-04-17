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
    "HistoricalDataDownloader",
    "DataValidationReport",
    "download_multi_timeframe",
]


def __getattr__(name: str):
    """Lazy-load modules to avoid importing ccxt at collection time."""
    if name == "DataFeed":
        from .feed import DataFeed
        return DataFeed
    elif name == "HistoricalDataDownloader":
        from .data_utils import HistoricalDataDownloader
        return HistoricalDataDownloader
    elif name == "DataValidationReport":
        from .data_utils import DataValidationReport
        return DataValidationReport
    elif name == "download_multi_timeframe":
        from .data_utils import download_multi_timeframe
        return download_multi_timeframe
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
