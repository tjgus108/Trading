"""Phase K: AnomalyDetector, PositionHealthMonitor 테스트."""

import sys
import os
import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.monitoring.anomaly_detector import AnomalyDetector
from src.monitoring.position_health import PositionHealthMonitor


# ── Helpers ──────────────────────────────────────────────────────────────────

def _make_normal_df(n: int = 100, seed: int = 0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    closes = 50000 + rng.normal(0, 100, n).cumsum()
    volumes = rng.uniform(100, 200, n)
    return pd.DataFrame({"close": closes, "volume": volumes})


def _inject_spike(df: pd.DataFrame, idx: int = -5, multiplier: float = 10.0) -> pd.DataFrame:
    df = df.copy()
    df.iloc[idx, df.columns.get_loc("close")] *= multiplier
    return df


# ═══════════════════════════════════════════════════════════════════════════
# K1. AnomalyDetector
# ═══════════════════════════════════════════════════════════════════════════

class TestAnomalyDetector:

    def test_no_anomaly_normal_data(self):
        """정상 데이터에서 이상치 없음."""
        det = AnomalyDetector(z_threshold=4.0, iqr_k=4.0, return_spike_threshold=0.20)
        df = _make_normal_df(100)
        events = det.detect(df)
        # 이상치 이벤트가 거의 없어야 함 (정상 분포에서 4σ 이상 극히 드묾)
        assert len(events) < 5

    def test_spike_detected(self):
        """가격 스파이크 감지."""
        det = AnomalyDetector(z_threshold=3.0, return_spike_threshold=0.05)
        df = _make_normal_df(100)
        df = _inject_spike(df, idx=50, multiplier=2.0)
        events = det.detect(df)
        assert len(events) > 0

    def test_return_spike_detected(self):
        """단일 캔들 수익률 스파이크."""
        det = AnomalyDetector(return_spike_threshold=0.05)
        df = _make_normal_df(50)
        # 마지막 캔들에 10% 급등 주입
        df = df.copy()
        df.iloc[-1, df.columns.get_loc("close")] = df.iloc[-2]["close"] * 1.15
        events = det.detect(df)
        spikes = [e for e in events if e.method == "return_spike"]
        assert len(spikes) > 0

    def test_event_fields(self):
        det = AnomalyDetector(z_threshold=3.0)
        df = _make_normal_df(100)
        df = _inject_spike(df, idx=50, multiplier=5.0)
        events = det.detect(df)
        if events:
            e = events[0]
            assert hasattr(e, "column")
            assert hasattr(e, "method")
            assert hasattr(e, "severity")
            assert e.severity in ("LOW", "MEDIUM", "HIGH")

    def test_severity_high_for_extreme(self):
        """극단적 스파이크 → HIGH severity."""
        det = AnomalyDetector(z_threshold=3.0)
        df = _make_normal_df(200)
        df = _inject_spike(df, idx=100, multiplier=50.0)
        events = det.detect(df)
        high_events = [e for e in events if e.severity == "HIGH"]
        assert len(high_events) > 0

    def test_detect_latest(self):
        """detect_latest는 최신 캔들만 반환."""
        det = AnomalyDetector(return_spike_threshold=0.01)
        df = _make_normal_df(100)
        # 최신 캔들에만 스파이크
        df.iloc[-2, df.columns.get_loc("close")] = df.iloc[-3]["close"] * 1.20
        events = det.detect_latest(df)
        # detect_latest는 idx >= len(df)-2 인 것만
        for e in events:
            assert e.index >= len(df) - 2

    def test_insufficient_data_no_crash(self):
        """데이터 5행 이하에서 에러 없음."""
        det = AnomalyDetector()
        df = pd.DataFrame({"close": [50000, 50100, 49900, 50200, 50050]})
        events = det.detect(df)
        assert isinstance(events, list)

    def test_summary_string(self):
        det = AnomalyDetector(z_threshold=3.0)
        df = _make_normal_df(100)
        df = _inject_spike(df, idx=50, multiplier=5.0)
        events = det.detect(df)
        if events:
            s = events[0].summary()
            assert isinstance(s, str)
            assert "Anomaly" in s


# ═══════════════════════════════════════════════════════════════════════════
# K2. PositionHealthMonitor
# ═══════════════════════════════════════════════════════════════════════════

class TestPositionHealthMonitor:

    def test_healthy_long(self):
        monitor = PositionHealthMonitor()
        health = monitor.evaluate(
            entry_price=50000, current_price=51000,
            stop_loss=49000, take_profit=54000, side="long",
        )
        assert health.status == "HEALTHY"
        assert health.unrealized_pnl_pct > 0

    def test_warning_loss(self):
        """3~6% 손실 → WARNING."""
        monitor = PositionHealthMonitor()
        health = monitor.evaluate(
            entry_price=50000, current_price=48500,  # -3% 손실
            stop_loss=47000, take_profit=55000, side="long",
        )
        assert health.status == "WARNING"

    def test_critical_loss(self):
        """6% 이상 손실 → CRITICAL."""
        monitor = PositionHealthMonitor()
        health = monitor.evaluate(
            entry_price=50000, current_price=46500,  # -7% 손실
            stop_loss=46000, take_profit=55000, side="long",
        )
        assert health.status == "CRITICAL"
        assert health.is_critical()

    def test_critical_near_stop(self):
        """손절까지 0.2% 미만 → CRITICAL."""
        monitor = PositionHealthMonitor()
        health = monitor.evaluate(
            entry_price=50000, current_price=49100,
            stop_loss=49000,  # 현재가와 100 차이 = 0.2%
            take_profit=55000, side="long",
        )
        assert health.status == "CRITICAL"

    def test_short_position_profit(self):
        """숏 포지션: 가격 하락 → 이익."""
        monitor = PositionHealthMonitor()
        health = monitor.evaluate(
            entry_price=50000, current_price=48000,
            stop_loss=52000, take_profit=44000, side="short",
        )
        assert health.unrealized_pnl_pct > 0

    def test_short_position_loss(self):
        """숏 포지션: 가격 상승 → 손실 → WARNING."""
        monitor = PositionHealthMonitor()
        health = monitor.evaluate(
            entry_price=50000, current_price=51800,  # -3.6% 숏 손실
            stop_loss=53000, take_profit=45000, side="short",
        )
        assert health.status in ("WARNING", "CRITICAL")

    def test_rr_ratio_calculated(self):
        monitor = PositionHealthMonitor()
        health = monitor.evaluate(
            entry_price=50000, current_price=50000,
            stop_loss=49000, take_profit=53000, side="long",
        )
        # TP거리 = 3000, SL거리 = 1000 → R/R ≈ 3.0
        assert health.risk_reward_ratio > 2.0

    def test_invalid_entry_price(self):
        monitor = PositionHealthMonitor()
        health = monitor.evaluate(
            entry_price=0, current_price=50000,
            stop_loss=49000, take_profit=53000,
        )
        assert health.status == "CRITICAL"
