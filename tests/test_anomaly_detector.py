"""AnomalyDetector 단위 테스트."""

import numpy as np
import pandas as pd
import pytest

from src.monitoring.anomaly_detector import AnomalyDetector, AnomalyEvent


def _make_df(n=100, base_vol=1000.0) -> pd.DataFrame:
    """기본 OHLCV DataFrame 생성."""
    rng = np.random.default_rng(42)
    closes = 30000 + np.cumsum(rng.normal(0, 50, n))
    volumes = rng.uniform(base_vol * 0.8, base_vol * 1.2, n)
    return pd.DataFrame({"close": closes, "volume": volumes})


# ── 거래량 급증 감지 ──────────────────────────────────────────────

class TestVolumeSurge:
    def test_surge_detected_when_3x(self):
        """평균 대비 3배 초과 거래량이 감지되어야 한다."""
        df = _make_df(n=60, base_vol=1000.0)
        # 마지막 캔들에 10배 거래량 주입
        df.loc[df.index[-1], "volume"] = 10_000.0

        detector = AnomalyDetector(window=20, volume_surge_multiplier=3.0)
        events = [e for e in detector.detect(df) if e.method == "volume_surge"]

        assert len(events) >= 1
        last_event = max(events, key=lambda e: e.index)
        assert last_event.index == len(df) - 1
        assert last_event.score >= 3.0

    def test_surge_severity_high_at_4_5x(self):
        """3.0 * 1.5 = 4.5배 이상이면 HIGH severity."""
        df = _make_df(n=60, base_vol=1000.0)
        df.loc[df.index[-1], "volume"] = 8_000.0  # rolling mean ~1200, ratio ~5.9x (>= 4.5)

        detector = AnomalyDetector(window=20, volume_surge_multiplier=3.0)
        events = [
            e for e in detector.detect(df)
            if e.method == "volume_surge" and e.index == len(df) - 1
        ]
        assert events, "volume_surge 이벤트 없음"
        assert events[0].severity == "HIGH"

    def test_normal_volume_not_flagged(self):
        """정상 거래량은 이벤트를 생성하지 않아야 한다."""
        df = _make_df(n=60, base_vol=1000.0)
        detector = AnomalyDetector(window=20, volume_surge_multiplier=3.0)
        events = [e for e in detector.detect(df) if e.method == "volume_surge"]
        assert len(events) == 0

    def test_no_volume_column_no_crash(self):
        """volume 컬럼 없어도 예외 없이 동작해야 한다."""
        df = pd.DataFrame({"close": [100.0] * 30})
        detector = AnomalyDetector(window=10)
        events = detector.detect(df)
        surge_events = [e for e in events if e.method == "volume_surge"]
        assert len(surge_events) == 0


# ── detect_latest 통합 확인 ────────────────────────────────────────

class TestDetectLatestWithSurge:
    def test_latest_includes_surge(self):
        """detect_latest가 마지막 캔들 거래량 급증을 반환해야 한다."""
        df = _make_df(n=60, base_vol=1000.0)
        df.loc[df.index[-1], "volume"] = 9_000.0

        detector = AnomalyDetector(window=20, volume_surge_multiplier=3.0)
        latest = detector.detect_latest(df)
        methods = [e.method for e in latest]
        assert "volume_surge" in methods
