import pytest
from src.risk.performance_tracker import LivePerformanceTracker


def make_tracker():
    return LivePerformanceTracker()


# --- record_trade / get_summary ---

def test_record_trade_increments_total():
    t = make_tracker()
    t.record_trade("strat_a", 100.0, 1000.0, 1100.0)
    t.record_trade("strat_a", -50.0, 1100.0, 1050.0)
    summary = t.get_summary("strat_a")
    assert summary["total_trades"] == 2


def test_get_summary_empty_strategy():
    t = make_tracker()
    summary = t.get_summary("nonexistent")
    assert summary["total_trades"] == 0
    assert summary["win_rate"] == 0.0
    assert summary["live_sharpe"] is None
    assert summary["consecutive_losses"] == 0


def test_win_rate_all_wins():
    t = make_tracker()
    for _ in range(4):
        t.record_trade("strat", 10.0, 100.0, 110.0)
    summary = t.get_summary("strat")
    assert summary["win_rate"] == 1.0


def test_win_rate_mixed():
    t = make_tracker()
    t.record_trade("strat", 10.0, 100.0, 110.0)
    t.record_trade("strat", -5.0, 110.0, 105.0)
    t.record_trade("strat", 10.0, 105.0, 115.0)
    t.record_trade("strat", -5.0, 115.0, 110.0)
    summary = t.get_summary("strat")
    assert summary["win_rate"] == pytest.approx(0.5)


def test_win_rate_all_losses():
    t = make_tracker()
    for _ in range(3):
        t.record_trade("strat", -10.0, 100.0, 90.0)
    summary = t.get_summary("strat")
    assert summary["win_rate"] == 0.0


# --- get_live_sharpe ---

def test_live_sharpe_returns_none_below_5_trades():
    t = make_tracker()
    for _ in range(4):
        t.record_trade("strat", 10.0, 100.0, 110.0)
    assert t.get_live_sharpe("strat") is None


def test_live_sharpe_returns_float_with_5_trades():
    t = make_tracker()
    pnls = [10.0, -5.0, 8.0, -3.0, 12.0]
    for p in pnls:
        t.record_trade("strat", p, 100.0, 100.0 + p)
    result = t.get_live_sharpe("strat")
    assert result is not None
    assert isinstance(result, float)


def test_live_sharpe_uses_window():
    t = make_tracker()
    # 먼저 큰 손실 10개
    for _ in range(10):
        t.record_trade("strat", -100.0, 1000.0, 900.0)
    # 최근 5개는 수익
    for _ in range(5):
        t.record_trade("strat", 50.0, 900.0, 950.0)
    sharpe_w5 = t.get_live_sharpe("strat", window=5)
    # window=5로 보면 std=0 (모두 동일), None 반환
    assert sharpe_w5 is None


def test_live_sharpe_empty_strategy():
    t = make_tracker()
    assert t.get_live_sharpe("no_strat") is None


# --- check_degradation ---

def test_check_degradation_consecutive_losses():
    t = make_tracker()
    for _ in range(5):
        t.record_trade("strat", -10.0, 100.0, 90.0)
    result = t.check_degradation("strat", backtest_sharpe=1.5)
    assert result == "연속 손실 5회"


def test_check_degradation_low_sharpe():
    t = make_tracker()
    # 낮은 sharpe 유발: 작은 양수 수익 + 큰 변동
    pnls = [1.0, -10.0, 1.0, -10.0, 1.0, -10.0, 1.0, -10.0, 1.0, -10.0]
    for p in pnls:
        t.record_trade("strat", p, 100.0, 100.0 + p)
    live_sharpe = t.get_live_sharpe("strat")
    assert live_sharpe is not None
    backtest_sharpe = abs(live_sharpe) / 0.5 + 1.0  # live < 60% of backtest
    result = t.check_degradation("strat", backtest_sharpe=backtest_sharpe)
    assert result is not None
    assert "live Sharpe" in result
    assert "60% of backtest" in result


def test_check_degradation_no_issue():
    t = make_tracker()
    for _ in range(10):
        t.record_trade("strat", 20.0, 100.0, 120.0)
    # std=0 → sharpe=None → degradation check skips sharpe, no consecutive losses
    result = t.check_degradation("strat", backtest_sharpe=0.5)
    assert result is None


def test_check_degradation_returns_none_insufficient_trades():
    t = make_tracker()
    t.record_trade("strat", -5.0, 100.0, 95.0)
    # 1회만 기록 → consecutive_losses=1(<5), sharpe=None
    result = t.check_degradation("strat", backtest_sharpe=2.0)
    assert result is None


# --- 전략별 독립 추적 ---

def test_strategies_are_independent():
    t = make_tracker()
    for _ in range(5):
        t.record_trade("strat_a", -10.0, 100.0, 90.0)
    for _ in range(3):
        t.record_trade("strat_b", 20.0, 100.0, 120.0)

    summary_a = t.get_summary("strat_a")
    summary_b = t.get_summary("strat_b")

    assert summary_a["total_trades"] == 5
    assert summary_b["total_trades"] == 3
    assert summary_a["win_rate"] == 0.0
    assert summary_b["win_rate"] == 1.0
    assert summary_a["consecutive_losses"] == 5
    assert summary_b["consecutive_losses"] == 0


def test_consecutive_losses_resets_on_win():
    t = make_tracker()
    for _ in range(4):
        t.record_trade("strat", -10.0, 100.0, 90.0)
    t.record_trade("strat", 20.0, 90.0, 110.0)  # 수익으로 리셋
    summary = t.get_summary("strat")
    assert summary["consecutive_losses"] == 0
    result = t.check_degradation("strat", backtest_sharpe=2.0)
    assert result != "연속 손실 5회"
