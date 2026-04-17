"""
TWAP + DrawdownMonitor 통합 테스트.

execute_with_drawdown_protection() 메서드 검증.
"""

import pytest
import numpy as np

from src.exchange.twap import TWAPExecutor
from src.risk.drawdown_monitor import DrawdownMonitor


class TestTWAPDrawdownIntegration:
    """TWAP execute_with_drawdown_protection() 테스트."""

    def _make_executor(self, n_slices=5, dry_run=True):
        return TWAPExecutor(n_slices=n_slices, interval_seconds=0, dry_run=dry_run)

    def test_twap_drawdown_normal_state(self):
        """DrawdownMonitor 정상 → 주문 실행."""
        monitor = DrawdownMonitor()
        monitor.update(current_equity=10_000)
        
        executor = self._make_executor(n_slices=3)
        result = executor.execute_with_drawdown_protection(
            connector=None,
            symbol="BTC/USDT",
            side="buy",
            total_qty=1.0,
            price_limit=50_000.0,
            drawdown_monitor=monitor,
        )
        
        assert result.slices_executed == 3
        assert result.total_qty == 1.0

    def test_twap_drawdown_cooldown_rejects_order(self):
        """쿨다운 활성 → 주문 완전 거부 (slices_executed=0)."""
        monitor = DrawdownMonitor(single_loss_halt_pct=0.02)
        
        # 쿨다운 시작
        monitor.record_trade_result(pnl=-300, equity=9_700)
        assert monitor.is_in_cooldown() is True
        
        executor = self._make_executor(n_slices=5)
        result = executor.execute_with_drawdown_protection(
            connector=None,
            symbol="BTC/USDT",
            side="buy",
            total_qty=2.0,
            price_limit=50_000.0,
            drawdown_monitor=monitor,
        )
        
        # 쿨다운으로 인해 주문 거부
        assert result.slices_executed == 0
        assert result.filled_qty == 0.0
        assert result.total_qty == 2.0  # 원청 수량 보존


    def test_twap_drawdown_size_multiplier_applied(self):
        """연속 손실 → size_multiplier=0.5 적용."""
        monitor = DrawdownMonitor(loss_streak_threshold=3)
        
        # 연속 손실 3회
        monitor.record_trade_result(pnl=-50, equity=9_950)
        monitor.record_trade_result(pnl=-50, equity=9_900)
        monitor.record_trade_result(pnl=-50, equity=9_850)
        
        assert monitor.get_size_multiplier() == 0.5
        
        executor = self._make_executor(n_slices=4)
        np.random.seed(42)
        result = executor.execute_with_drawdown_protection(
            connector=None,
            symbol="ETH/USDT",
            side="sell",
            total_qty=2.0,  # 원청
            price_limit=2000.0,
            drawdown_monitor=monitor,
        )
        
        # 실행된 총 수량은 2.0 * 0.5 = 1.0 (근처)
        # TWAP dry_run에서 부분 체결이 있을 수 있으므로 filled_qty <= 1.0
        assert result.slices_executed == 4
        assert result.total_qty == 1.0, "size_multiplier should adjust qty to 1.0"
        assert result.filled_qty <= 1.0 + 1e-8

    def test_twap_drawdown_none_monitor(self):
        """drawdown_monitor=None → 제약 없음."""
        executor = self._make_executor(n_slices=2)
        result = executor.execute_with_drawdown_protection(
            connector=None,
            symbol="BTC/USDT",
            side="buy",
            total_qty=0.5,
            price_limit=50_000.0,
            drawdown_monitor=None,  # 제약 없음
        )
        
        assert result.slices_executed == 2
        assert result.total_qty == 0.5

    def test_twap_drawdown_zero_qty_after_adjustment(self):
        """size_multiplier=0 → total_qty=0 → 빈 결과."""
        monitor = DrawdownMonitor(single_loss_halt_pct=0.01)
        monitor.record_trade_result(pnl=-200, equity=9_800)
        
        assert monitor.get_size_multiplier() == 0.0
        
        executor = self._make_executor(n_slices=5)
        result = executor.execute_with_drawdown_protection(
            connector=None,
            symbol="BTC/USDT",
            side="buy",
            total_qty=1.0,
            price_limit=50_000.0,
            drawdown_monitor=monitor,
        )
        
        assert result.slices_executed == 0
        assert result.filled_qty == 0.0
        assert result.errors == 1

    def test_twap_drawdown_integration_sequence(self):
        """워크플로우: 정상 → 손실 1회 → 손실 2회 → 손실 3회 (축소) → 손실 4회 (여전히 축소)."""
        monitor = DrawdownMonitor(loss_streak_threshold=3)
        executor = self._make_executor(n_slices=2, dry_run=True)
        
        # 정상 상태
        result1 = executor.execute_with_drawdown_protection(
            connector=None,
            symbol="BTC/USDT",
            side="buy",
            total_qty=1.0,
            price_limit=50_000.0,
            drawdown_monitor=monitor,
        )
        assert result1.total_qty == 1.0
        assert result1.slices_executed == 2
        
        # 손실 1회
        monitor.record_trade_result(pnl=-50, equity=9_950)
        result2 = executor.execute_with_drawdown_protection(
            connector=None,
            symbol="BTC/USDT",
            side="buy",
            total_qty=1.0,
            price_limit=50_000.0,
            drawdown_monitor=monitor,
        )
        assert result2.total_qty == 1.0  # 아직 조정 없음
        
        # 손실 2회
        monitor.record_trade_result(pnl=-50, equity=9_900)
        result3 = executor.execute_with_drawdown_protection(
            connector=None,
            symbol="BTC/USDT",
            side="buy",
            total_qty=1.0,
            price_limit=50_000.0,
            drawdown_monitor=monitor,
        )
        assert result3.total_qty == 1.0  # 아직 조정 없음
        
        # 손실 3회 → threshold 도달 → 50% 축소
        monitor.record_trade_result(pnl=-50, equity=9_850)
        result4 = executor.execute_with_drawdown_protection(
            connector=None,
            symbol="BTC/USDT",
            side="buy",
            total_qty=1.0,
            price_limit=50_000.0,
            drawdown_monitor=monitor,
        )
        assert result4.total_qty == 0.5, "consecutive_losses=3 → 50% reduction"
        assert result4.slices_executed == 2
        
        # 손실 4회 → 여전히 축소 상태
        monitor.record_trade_result(pnl=-25, equity=9_825)
        result5 = executor.execute_with_drawdown_protection(
            connector=None,
            symbol="BTC/USDT",
            side="buy",
            total_qty=1.0,
            price_limit=50_000.0,
            drawdown_monitor=monitor,
        )
        assert result5.total_qty == 0.5, "still under consecutive loss reduction"


class TestTWAPDrawdownLogging:
    """로깅 및 경고 메시지 검증."""

    def test_twap_drawdown_cooldown_warning_logged(self, caplog):
        """쿨다운 상태에서 경고 로그."""
        import logging
        caplog.set_level(logging.WARNING)
        
        monitor = DrawdownMonitor(single_loss_halt_pct=0.02)
        monitor.record_trade_result(pnl=-300, equity=9_700)
        
        executor = TWAPExecutor(n_slices=2, dry_run=True)
        executor.execute_with_drawdown_protection(
            connector=None,
            symbol="BTC/USDT",
            side="buy",
            total_qty=1.0,
            price_limit=50_000.0,
            drawdown_monitor=monitor,
        )
        
        # "cooldown_active" 또는 유사 메시지 확인
        assert any("cooldown" in msg.lower() for msg in caplog.text.lower().split('\n'))

    def test_twap_drawdown_size_adjustment_logged(self, caplog):
        """size_multiplier 적용 시 정보 로그."""
        import logging
        caplog.set_level(logging.INFO)
        
        monitor = DrawdownMonitor(loss_streak_threshold=3)
        monitor.record_trade_result(pnl=-50, equity=9_950)
        monitor.record_trade_result(pnl=-50, equity=9_900)
        monitor.record_trade_result(pnl=-50, equity=9_850)
        
        executor = TWAPExecutor(n_slices=2, dry_run=True)
        executor.execute_with_drawdown_protection(
            connector=None,
            symbol="BTC/USDT",
            side="buy",
            total_qty=1.0,
            price_limit=50_000.0,
            drawdown_monitor=monitor,
        )
        
        # "size_multiplier" 관련 로그 확인
        assert any("size_multiplier" in msg.lower() for msg in caplog.text.lower().split('\n'))
