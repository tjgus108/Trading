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
    "OFICalculator",
    "VPINCalculator",
    "OrderFlowFetcher",
    "OrderFlowData",
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
    elif name == "OFICalculator":
        from .order_flow import OFICalculator
        return OFICalculator
    elif name == "VPINCalculator":
        from .order_flow import VPINCalculator
        return VPINCalculator
    elif name == "OrderFlowFetcher":
        from .order_flow import OrderFlowFetcher
        return OrderFlowFetcher
    elif name == "OrderFlowData":
        from .order_flow import OrderFlowData
        return OrderFlowData
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
