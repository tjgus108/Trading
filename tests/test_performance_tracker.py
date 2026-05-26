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


# --- timestamp 테스트 ---

def test_record_trade_has_timestamp_auto():
    """timestamp 미지정 시 자동으로 현재 시각 기록."""
    import time
    before = time.time()
    t = make_tracker()
    t.record_trade("strat", 10.0, 100.0, 110.0)
    after = time.time()
    ts = t._trades["strat"][0]["timestamp"]
    assert before <= ts <= after, "auto timestamp should be current time"


def test_record_trade_has_timestamp_explicit():
    """명시적 timestamp가 그대로 저장되는지 확인."""
    t = make_tracker()
    t.record_trade("strat", 10.0, 100.0, 110.0, timestamp=1234567890.0)
    ts = t._trades["strat"][0]["timestamp"]
    assert ts == 1234567890.0


# --- get_hourly_pnl 테스트 ---

def test_get_hourly_pnl_returns_list_of_correct_length():
    """get_hourly_pnl이 hours 길이의 리스트를 반환."""
    t = make_tracker()
    result = t.get_hourly_pnl("strat", hours=24)
    assert isinstance(result, list)
    assert len(result) == 24


def test_get_hourly_pnl_empty_strategy():
    """거래 없으면 모두 0.0."""
    t = make_tracker()
    result = t.get_hourly_pnl("no_strat", hours=12)
    assert result == [0.0] * 12


def test_get_hourly_pnl_recent_trade_in_last_bucket():
    """방금 기록한 거래는 마지막 버킷(index -1)에 합산."""
    import time
    t = make_tracker()
    t.record_trade("strat", 50.0, 100.0, 150.0, timestamp=time.time())
    result = t.get_hourly_pnl("strat", hours=24)
    assert result[-1] == pytest.approx(50.0), "recent trade pnl must be in last bucket"


def test_get_hourly_pnl_old_trade_excluded():
    """cutoff 이전 거래는 집계에서 제외."""
    import time
    t = make_tracker()
    old_ts = time.time() - 25 * 3600  # 25시간 전
    t.record_trade("strat", 999.0, 100.0, 1099.0, timestamp=old_ts)
    result = t.get_hourly_pnl("strat", hours=24)
    assert sum(result) == pytest.approx(0.0), "trade older than cutoff must be excluded"


# --- get_daily_pnl 테스트 ---

def test_get_daily_pnl_returns_correct_length():
    """get_daily_pnl이 days 길이의 리스트를 반환."""
    t = make_tracker()
    result = t.get_daily_pnl("strat", days=7)
    assert isinstance(result, list)
    assert len(result) == 7


def test_get_daily_pnl_empty_strategy():
    """거래 없으면 모두 0.0."""
    t = make_tracker()
    result = t.get_daily_pnl("no_strat", days=5)
    assert result == [0.0] * 5


def test_get_daily_pnl_recent_trade_in_last_bucket():
    """방금 기록한 거래는 마지막 버킷(index -1)에 합산."""
    import time
    t = make_tracker()
    t.record_trade("strat", 100.0, 100.0, 200.0, timestamp=time.time())
    result = t.get_daily_pnl("strat", days=7)
    assert result[-1] == pytest.approx(100.0)
    assert sum(result[:-1]) == pytest.approx(0.0)


def test_get_daily_pnl_old_trade_excluded():
    """cutoff 이전 거래는 집계에서 제외."""
    import time
    t = make_tracker()
    old_ts = time.time() - 8 * 86400  # 8일 전
    t.record_trade("strat", 999.0, 100.0, 1099.0, timestamp=old_ts)
    result = t.get_daily_pnl("strat", days=7)
    assert sum(result) == pytest.approx(0.0)


def test_get_daily_pnl_multiple_trades_same_day():
    """같은 날 여러 거래는 합산."""
    import time
    t = make_tracker()
    now = time.time()
    t.record_trade("strat", 50.0, 100.0, 150.0, timestamp=now)
    t.record_trade("strat", -20.0, 150.0, 130.0, timestamp=now - 100)
    t.record_trade("strat", 30.0, 130.0, 160.0, timestamp=now - 200)
    result = t.get_daily_pnl("strat", days=7)
    assert result[-1] == pytest.approx(60.0)  # 50 + (-20) + 30


def test_get_daily_pnl_trades_across_days():
    """여러 날에 걸친 거래가 올바른 버킷에 분류."""
    import time
    t = make_tracker()
    now = time.time()
    t.record_trade("strat", 100.0, 100.0, 200.0, timestamp=now)  # 오늘
    t.record_trade("strat", -50.0, 200.0, 150.0, timestamp=now - 86400)  # 어제
    t.record_trade("strat", 75.0, 150.0, 225.0, timestamp=now - 2 * 86400)  # 그제
    result = t.get_daily_pnl("strat", days=7)
    assert result[-1] == pytest.approx(100.0)   # 오늘
    assert result[-2] == pytest.approx(-50.0)    # 어제
    assert result[-3] == pytest.approx(75.0)     # 그제


# --- get_daily_summary 테스트 ---

def test_get_daily_summary_empty():
    """거래 없는 전략의 daily summary."""
    t = make_tracker()
    summary = t.get_daily_summary("no_strat", days=7)
    assert summary["days"] == 7
    assert summary["total_trades"] == 0
    assert summary["total_pnl"] == 0.0
    assert summary["win_rate"] == 0.0
    assert summary["profit_factor"] is None
    assert summary["sharpe"] is None


def test_get_daily_summary_with_trades():
    """거래가 있는 전략의 daily summary 기본 키 확인."""
    import time
    t = make_tracker()
    now = time.time()
    t.record_trade("strat", 50.0, 100.0, 150.0, timestamp=now)
    t.record_trade("strat", -20.0, 150.0, 130.0, timestamp=now - 100)
    t.record_trade("strat", 30.0, 130.0, 160.0, timestamp=now - 200)

    summary = t.get_daily_summary("strat", days=7)
    assert summary["total_trades"] == 3
    assert summary["total_pnl"] == pytest.approx(60.0)
    assert summary["win_rate"] == pytest.approx(2 / 3, abs=0.01)
    assert "daily_pnl" in summary
    assert len(summary["daily_pnl"]) == 7


def test_get_daily_summary_profit_factor():
    """PF 계산 정확성 검증."""
    import time
    t = make_tracker()
    now = time.time()
    # wins: 100, 50 (total=150), losses: -30, -20 (total=50)
    t.record_trade("strat", 100.0, 100.0, 200.0, timestamp=now)
    t.record_trade("strat", 50.0, 200.0, 250.0, timestamp=now - 100)
    t.record_trade("strat", -30.0, 250.0, 220.0, timestamp=now - 200)
    t.record_trade("strat", -20.0, 220.0, 200.0, timestamp=now - 300)

    summary = t.get_daily_summary("strat", days=7)
    assert summary["profit_factor"] == pytest.approx(150.0 / 50.0, abs=0.01)


def test_get_daily_summary_all_wins_pf_inf():
    """모두 수익이면 PF는 inf."""
    import time
    t = make_tracker()
    now = time.time()
    t.record_trade("strat", 10.0, 100.0, 110.0, timestamp=now)
    t.record_trade("strat", 20.0, 110.0, 130.0, timestamp=now - 100)

    summary = t.get_daily_summary("strat", days=7)
    assert summary["profit_factor"] == float("inf")


def test_get_daily_summary_sharpe_with_multiple_days():
    """여러 날에 걸친 거래에서 Sharpe 계산."""
    import time
    t = make_tracker()
    now = time.time()
    # 3일간 거래 → daily_pnl에 비제로 값이 최소 2개
    t.record_trade("strat", 100.0, 100.0, 200.0, timestamp=now)
    t.record_trade("strat", -30.0, 200.0, 170.0, timestamp=now - 86400)
    t.record_trade("strat", 50.0, 170.0, 220.0, timestamp=now - 2 * 86400)

    summary = t.get_daily_summary("strat", days=7)
    # 3일간 비제로 거래 → Sharpe 계산 가능
    assert summary["sharpe"] is not None
    assert isinstance(summary["sharpe"], float)


def test_get_daily_summary_excludes_old_trades():
    """window 밖의 거래는 summary에서 제외."""
    import time
    t = make_tracker()
    now = time.time()
    t.record_trade("strat", 999.0, 100.0, 1099.0, timestamp=now - 10 * 86400)  # 10일 전
    t.record_trade("strat", 50.0, 100.0, 150.0, timestamp=now)  # 오늘

    summary = t.get_daily_summary("strat", days=7)
    assert summary["total_trades"] == 1  # 10일 전 거래 제외
    assert summary["total_pnl"] == pytest.approx(50.0)


# --- get_weekly_pnl 테스트 ---

def test_get_weekly_pnl_returns_correct_length():
    """get_weekly_pnl이 weeks 길이의 리스트를 반환."""
    t = make_tracker()
    result = t.get_weekly_pnl("strat", weeks=4)
    assert isinstance(result, list)
    assert len(result) == 4


def test_get_weekly_pnl_empty_strategy():
    """거래 없으면 모두 0.0."""
    t = make_tracker()
    result = t.get_weekly_pnl("no_strat", weeks=4)
    assert result == [0.0] * 4


def test_get_weekly_pnl_recent_trade_in_last_bucket():
    """방금 기록한 거래는 마지막 버킷(index -1)에 합산."""
    import time
    t = make_tracker()
    t.record_trade("strat", 200.0, 100.0, 300.0, timestamp=time.time())
    result = t.get_weekly_pnl("strat", weeks=4)
    assert result[-1] == pytest.approx(200.0)
    assert sum(result[:-1]) == pytest.approx(0.0)


def test_get_weekly_pnl_old_trade_excluded():
    """cutoff 이전 거래는 집계에서 제외."""
    import time
    t = make_tracker()
    old_ts = time.time() - 5 * 7 * 86400  # 5주 전
    t.record_trade("strat", 999.0, 100.0, 1099.0, timestamp=old_ts)
    result = t.get_weekly_pnl("strat", weeks=4)
    assert sum(result) == pytest.approx(0.0)


def test_get_weekly_pnl_trades_across_weeks():
    """여러 주에 걸친 거래가 올바른 버킷에 분류."""
    import time
    t = make_tracker()
    now = time.time()
    t.record_trade("strat", 100.0, 100.0, 200.0, timestamp=now)  # 이번 주
    t.record_trade("strat", -50.0, 200.0, 150.0, timestamp=now - 7 * 86400)  # 저번 주
    t.record_trade("strat", 75.0, 150.0, 225.0, timestamp=now - 14 * 86400)  # 2주 전
    result = t.get_weekly_pnl("strat", weeks=4)
    assert result[-1] == pytest.approx(100.0)   # 이번 주
    assert result[-2] == pytest.approx(-50.0)    # 저번 주
    assert result[-3] == pytest.approx(75.0)     # 2주 전


# --- get_monthly_pnl 테스트 ---

def test_get_monthly_pnl_returns_correct_length():
    """get_monthly_pnl이 months 길이의 리스트를 반환."""
    t = make_tracker()
    result = t.get_monthly_pnl("strat", months=3)
    assert isinstance(result, list)
    assert len(result) == 3


def test_get_monthly_pnl_empty_strategy():
    """거래 없으면 모두 0.0."""
    t = make_tracker()
    result = t.get_monthly_pnl("no_strat", months=3)
    assert result == [0.0] * 3


def test_get_monthly_pnl_recent_trade_in_last_bucket():
    """방금 기록한 거래는 마지막 버킷에 합산."""
    import time
    t = make_tracker()
    t.record_trade("strat", 500.0, 100.0, 600.0, timestamp=time.time())
    result = t.get_monthly_pnl("strat", months=3)
    assert result[-1] == pytest.approx(500.0)
    assert sum(result[:-1]) == pytest.approx(0.0)


def test_get_monthly_pnl_old_trade_excluded():
    """cutoff 이전 거래는 집계에서 제외 (4개월 전 → 3개월 윈도우 밖)."""
    import time
    t = make_tracker()
    old_ts = time.time() - 4 * 30 * 86400  # 약 4개월 전
    t.record_trade("strat", 999.0, 100.0, 1099.0, timestamp=old_ts)
    result = t.get_monthly_pnl("strat", months=3)
    assert sum(result) == pytest.approx(0.0)


# --- get_weekly_summary 테스트 ---

def test_get_weekly_summary_empty():
    """거래 없는 전략의 weekly summary."""
    t = make_tracker()
    summary = t.get_weekly_summary("no_strat", weeks=4)
    assert summary["weeks"] == 4
    assert summary["total_trades"] == 0
    assert summary["total_pnl"] == 0.0
    assert summary["win_rate"] == 0.0
    assert summary["profit_factor"] is None
    assert summary["sharpe"] is None
    assert summary["mdd"] == 0.0


def test_get_weekly_summary_with_trades():
    """거래가 있는 전략의 weekly summary 기본 키 확인."""
    import time
    t = make_tracker()
    now = time.time()
    t.record_trade("strat", 100.0, 100.0, 200.0, timestamp=now)
    t.record_trade("strat", -30.0, 200.0, 170.0, timestamp=now - 7 * 86400)
    t.record_trade("strat", 50.0, 170.0, 220.0, timestamp=now - 14 * 86400)

    summary = t.get_weekly_summary("strat", weeks=4)
    assert summary["total_trades"] == 3
    assert summary["total_pnl"] == pytest.approx(120.0)
    assert "weekly_pnl" in summary
    assert len(summary["weekly_pnl"]) == 4
    assert summary["win_rate"] == pytest.approx(2 / 3, abs=0.01)


def test_get_weekly_summary_profit_factor():
    """주간 PF 계산 정확성 검증."""
    import time
    t = make_tracker()
    now = time.time()
    # wins: 100, 50 (total=150), losses: -30, -20 (total=50)
    t.record_trade("strat", 100.0, 100.0, 200.0, timestamp=now)
    t.record_trade("strat", 50.0, 200.0, 250.0, timestamp=now - 100)
    t.record_trade("strat", -30.0, 250.0, 220.0, timestamp=now - 200)
    t.record_trade("strat", -20.0, 220.0, 200.0, timestamp=now - 300)

    summary = t.get_weekly_summary("strat", weeks=4)
    assert summary["profit_factor"] == pytest.approx(150.0 / 50.0, abs=0.01)


def test_get_weekly_summary_mdd():
    """MDD 계산: 연속 손실 후 드로다운 반영."""
    import time
    t = make_tracker()
    now = time.time()
    t.record_trade("strat", 100.0, 100.0, 200.0, timestamp=now - 300)
    t.record_trade("strat", -60.0, 200.0, 140.0, timestamp=now - 200)
    t.record_trade("strat", -20.0, 140.0, 120.0, timestamp=now - 100)

    summary = t.get_weekly_summary("strat", weeks=4)
    # peak=100, equity after losses=100-60-20=20, dd=(100-20)/100=0.8
    assert summary["mdd"] == pytest.approx(0.8, abs=0.01)


def test_get_weekly_summary_excludes_old_trades():
    """window 밖의 거래는 summary에서 제외."""
    import time
    t = make_tracker()
    now = time.time()
    t.record_trade("strat", 999.0, 100.0, 1099.0, timestamp=now - 35 * 86400)  # 5주 전
    t.record_trade("strat", 50.0, 100.0, 150.0, timestamp=now)  # 오늘

    summary = t.get_weekly_summary("strat", weeks=4)
    assert summary["total_trades"] == 1
    assert summary["total_pnl"] == pytest.approx(50.0)


# --- get_monthly_summary 테스트 ---

def test_get_monthly_summary_empty():
    """거래 없는 전략의 monthly summary."""
    t = make_tracker()
    summary = t.get_monthly_summary("no_strat", months=3)
    assert summary["months"] == 3
    assert summary["total_trades"] == 0
    assert summary["total_pnl"] == 0.0
    assert summary["win_rate"] == 0.0
    assert summary["profit_factor"] is None
    assert summary["sharpe"] is None
    assert summary["mdd"] == 0.0


def test_get_monthly_summary_with_trades():
    """거래가 있는 전략의 monthly summary 기본 키 확인."""
    import time
    t = make_tracker()
    now = time.time()
    t.record_trade("strat", 200.0, 100.0, 300.0, timestamp=now)
    t.record_trade("strat", -80.0, 300.0, 220.0, timestamp=now - 30 * 86400)

    summary = t.get_monthly_summary("strat", months=3)
    assert summary["total_trades"] == 2
    assert summary["total_pnl"] == pytest.approx(120.0)
    assert "monthly_pnl" in summary
    assert len(summary["monthly_pnl"]) == 3


def test_get_monthly_summary_profit_factor():
    """월간 PF 계산 정확성 검증."""
    import time
    t = make_tracker()
    now = time.time()
    t.record_trade("strat", 300.0, 100.0, 400.0, timestamp=now)
    t.record_trade("strat", -100.0, 400.0, 300.0, timestamp=now - 100)

    summary = t.get_monthly_summary("strat", months=3)
    assert summary["profit_factor"] == pytest.approx(300.0 / 100.0, abs=0.01)


def test_get_monthly_summary_excludes_old_trades():
    """window 밖의 거래는 summary에서 제외."""
    import time
    t = make_tracker()
    now = time.time()
    t.record_trade("strat", 999.0, 100.0, 1099.0, timestamp=now - 4 * 30 * 86400)  # 4개월 전
    t.record_trade("strat", 50.0, 100.0, 150.0, timestamp=now)

    summary = t.get_monthly_summary("strat", months=3)
    assert summary["total_trades"] == 1
    assert summary["total_pnl"] == pytest.approx(50.0)


def test_get_monthly_summary_sharpe_with_multiple_months():
    """여러 달에 걸친 거래에서 Sharpe 계산."""
    import time
    t = make_tracker()
    now = time.time()
    t.record_trade("strat", 200.0, 100.0, 300.0, timestamp=now)
    t.record_trade("strat", -50.0, 300.0, 250.0, timestamp=now - 30 * 86400)
    t.record_trade("strat", 100.0, 250.0, 350.0, timestamp=now - 60 * 86400)

    summary = t.get_monthly_summary("strat", months=3)
    # 3개월간 비제로 거래 → Sharpe 계산 가능
    assert summary["sharpe"] is not None
    assert isinstance(summary["sharpe"], float)
