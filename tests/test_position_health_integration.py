"""
Position Health Monitor 통합 테스트.
시나리오: 손실 확대(HEALTHY → WARNING → CRITICAL) + 강제 청산 트리거
"""

import pytest
from src.monitoring.position_health import PositionHealthMonitor, PositionHealth


@pytest.fixture
def monitor():
    return PositionHealthMonitor()


class TestLossEscalationScenario:
    """손실 확대 시나리오: 연속 캔들 하락 → 상태 전이 → CRITICAL 강제 청산."""

    def test_loss_escalation_long(self, monitor):
        """LONG 포지션: 가격 하락에 따른 HEALTHY → WARNING → CRITICAL 전이."""
        entry = 50000.0
        stop_loss = 46000.0   # 8% 아래
        take_profit = 56000.0

        # T0: 소폭 하락 (−1.5%) → HEALTHY
        h0 = monitor.evaluate(entry, 49250, stop_loss, take_profit, side="long")
        assert h0.status == "HEALTHY"
        assert h0.unrealized_pnl_pct == pytest.approx(-0.015, abs=1e-4)

        # T1: 3.5% 손실 → WARNING
        h1 = monitor.evaluate(entry, 48250, stop_loss, take_profit, side="long")
        assert h1.status == "WARNING"
        assert h1.unrealized_pnl_pct < -0.03

        # T2: 7% 손실 → CRITICAL + 강제 청산 플래그
        h2 = monitor.evaluate(entry, 46500, stop_loss, take_profit, side="long")
        assert h2.status == "CRITICAL"
        assert h2.is_critical()
        assert h2.unrealized_pnl_pct <= -0.06

        # 강제 청산 시뮬레이션: is_critical() True 이면 실행 중단
        liquidated = False
        if h2.is_critical():
            liquidated = True  # 실제로는 exchange.close_position() 호출
        assert liquidated, "CRITICAL 시 강제 청산이 트리거되어야 한다"


class TestStopProximityForcedLiquidation:
    """손절가 근접(< 0.5%) → CRITICAL → 강제 청산."""

    def test_stop_proximity_triggers_critical(self, monitor):
        entry = 50000.0
        stop_loss = 49800.0   # 0.4% 아래 → MIN_STOP_DISTANCE 미만
        take_profit = 52000.0
        current = 49825.0     # stop_loss와 0.05% 차이

        health = monitor.evaluate(entry, current, stop_loss, take_profit, side="long")
        assert health.status == "CRITICAL"
        assert health.stop_distance_pct < PositionHealthMonitor.MIN_STOP_DISTANCE
        assert "손절 근접" in health.reason

        # 강제 청산 트리거 확인
        assert health.is_critical()
