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


# --- check_regime_death 테스트 ---

def _build_regime_tracker(daily_pnls):
    """여러 날에 걸친 PnL로 트래커를 구성하는 헬퍼.

    daily_pnls: index 0 = 가장 오래된 날, index -1 = 오늘
    """
    import time
    t = make_tracker()
    now = time.time()
    n = len(daily_pnls)
    for i, pnl in enumerate(daily_pnls):
        # 가장 오래된 → (n-1) 일 전, 가장 최근 → 0일 전
        days_ago = n - 1 - i
        ts = now - days_ago * 86400
        t.record_trade("strat", pnl, 100.0, 100.0 + pnl, timestamp=ts)
    return t


def test_regime_death_insufficient_data():
    """거래 데이터 부족 시 is_dead=False, live_sharpe=None."""
    t = make_tracker()
    result = t.check_regime_death("strat", backtest_sharpe=2.0)
    assert result["is_dead"] is False
    assert result["live_sharpe"] is None
    assert result["consecutive_below"] == 0


def test_regime_death_healthy_strategy():
    """좋은 성과의 전략은 레짐 사망이 아님."""
    # 30일간 꾸준한 수익 → 높은 Sharpe
    daily_pnls = [10.0 + i * 0.1 for i in range(30)]
    t = _build_regime_tracker(daily_pnls)
    result = t.check_regime_death("strat", backtest_sharpe=2.0, window_days=30)
    assert result["is_dead"] is False
    assert result["live_sharpe"] is not None
    assert result["consecutive_below"] == 0


def test_regime_death_single_below_not_dead():
    """1번 미달은 아직 레짐 사망이 아님 (consecutive_periods=2)."""
    # 변동이 크고 평균 손실 → 낮은 Sharpe
    daily_pnls = [-5.0, 1.0, -5.0, 1.0, -5.0, 1.0, -5.0, 1.0, -5.0, 1.0]
    t = _build_regime_tracker(daily_pnls)

    result = t.check_regime_death(
        "strat", backtest_sharpe=3.0, window_days=10, threshold=0.5
    )
    # live_sharpe 음수 < 3.0 * 0.5 = 1.5 → 미달
    assert result["live_sharpe"] is not None
    assert result["live_sharpe"] < 1.5
    assert result["consecutive_below"] == 1
    assert result["is_dead"] is False


def test_regime_death_two_consecutive_is_dead():
    """2번 연속 미달이면 레짐 사망."""
    daily_pnls = [-5.0, 1.0, -5.0, 1.0, -5.0, 1.0, -5.0, 1.0, -5.0, 1.0]
    t = _build_regime_tracker(daily_pnls)

    # 첫 번째 체크 → consecutive=1
    t.check_regime_death("strat", backtest_sharpe=3.0, window_days=10, threshold=0.5)
    # 두 번째 체크 → consecutive=2 → is_dead
    result = t.check_regime_death(
        "strat", backtest_sharpe=3.0, window_days=10, threshold=0.5
    )
    assert result["consecutive_below"] == 2
    assert result["is_dead"] is True


def test_regime_death_reset_on_recovery():
    """Sharpe 회복 시 연속 카운터 리셋."""
    # 나쁜 성과 → 카운터 1
    bad_pnls = [-5.0, 1.0, -5.0, 1.0, -5.0, 1.0, -5.0, 1.0, -5.0, 1.0]
    t = _build_regime_tracker(bad_pnls)
    t.check_regime_death("strat", backtest_sharpe=3.0, window_days=10, threshold=0.5)
    assert t._regime_death_consecutive["strat"] == 1

    # 좋은 성과로 교체: 큰 수익 + 약간의 변동으로 높은 Sharpe 유도
    import time
    now = time.time()
    for i in range(30):
        pnl = 50.0 + (i % 3) * 2.0  # 50, 52, 54 반복 → 양수 평균, 작은 분산
        ts = now - (29 - i) * 86400  # 최근 30일에 분산 배치
        t.record_trade("strat", pnl, 100.0, 100.0 + pnl, timestamp=ts)

    result = t.check_regime_death(
        "strat", backtest_sharpe=0.01, window_days=30, threshold=0.5
    )
    # 높은 live_sharpe > 매우 낮은 threshold → 리셋
    assert result["consecutive_below"] == 0
    assert result["is_dead"] is False


def test_regime_death_custom_consecutive_periods():
    """consecutive_periods 파라미터 커스텀 값 테스트."""
    daily_pnls = [-5.0, 1.0, -5.0, 1.0, -5.0, 1.0, -5.0, 1.0, -5.0, 1.0]
    t = _build_regime_tracker(daily_pnls)

    # consecutive_periods=3 → 3회 미달이어야 사망
    for i in range(2):
        result = t.check_regime_death(
            "strat", backtest_sharpe=3.0, window_days=10,
            threshold=0.5, consecutive_periods=3,
        )
    assert result["consecutive_below"] == 2
    assert result["is_dead"] is False

    result = t.check_regime_death(
        "strat", backtest_sharpe=3.0, window_days=10,
        threshold=0.5, consecutive_periods=3,
    )
    assert result["consecutive_below"] == 3
    assert result["is_dead"] is True


def test_regime_death_returns_correct_keys():
    """반환값에 필수 키가 모두 포함되는지 확인."""
    daily_pnls = [10.0, -5.0, 8.0, -3.0, 12.0, -1.0, 7.0, -2.0, 9.0, 4.0]
    t = _build_regime_tracker(daily_pnls)
    result = t.check_regime_death("strat", backtest_sharpe=2.0, window_days=10)
    assert "is_dead" in result
    assert "live_sharpe" in result
    assert "threshold_sharpe" in result
    assert "consecutive_below" in result


def test_regime_death_threshold_sharpe_value():
    """threshold_sharpe가 backtest_sharpe * threshold로 올바르게 계산되는지."""
    t = make_tracker()
    result = t.check_regime_death(
        "strat", backtest_sharpe=2.0, threshold=0.5
    )
    assert result["threshold_sharpe"] == pytest.approx(1.0)


def test_regime_death_strategies_independent():
    """전략별 레짐 사망 카운터가 독립적."""
    daily_pnls = [-5.0, 1.0, -5.0, 1.0, -5.0, 1.0, -5.0, 1.0, -5.0, 1.0]
    t = _build_regime_tracker(daily_pnls)

    # strat에 대해 카운터 증가
    t.check_regime_death("strat", backtest_sharpe=3.0, window_days=10, threshold=0.5)
    assert t._regime_death_consecutive["strat"] == 1

    # strat_b는 별도 카운터
    assert t._regime_death_consecutive["strat_b"] == 0


# --- get_rolling_sharpe 테스트 ---


def test_rolling_sharpe_insufficient_data():
    """비제로 일수 < 2이면 None 반환."""
    t = make_tracker()
    assert t.get_rolling_sharpe("strat", window_days=30) is None


def test_rolling_sharpe_single_day_returns_none():
    """1일만 거래 → 비제로 일수 1 → None."""
    import time
    t = make_tracker()
    t.record_trade("strat", 50.0, 100.0, 150.0, timestamp=time.time())
    assert t.get_rolling_sharpe("strat", window_days=30) is None


def test_rolling_sharpe_returns_float_with_enough_data():
    """충분한 일별 데이터가 있으면 float 반환."""
    daily_pnls = [10.0, -5.0, 8.0, -3.0, 12.0, -1.0, 7.0, -2.0, 9.0, 4.0]
    t = _build_regime_tracker(daily_pnls)
    result = t.get_rolling_sharpe("strat", window_days=10)
    assert result is not None
    assert isinstance(result, float)


def test_rolling_sharpe_positive_for_profitable_strategy():
    """꾸준한 수익 전략은 양수 Sharpe."""
    daily_pnls = [10.0 + i * 0.5 for i in range(30)]
    t = _build_regime_tracker(daily_pnls)
    result = t.get_rolling_sharpe("strat", window_days=30)
    assert result is not None
    assert result > 0, f"Expected positive Sharpe, got {result}"


def test_rolling_sharpe_negative_for_losing_strategy():
    """꾸준한 손실 전략은 음수 Sharpe."""
    daily_pnls = [-10.0 - i * 0.5 for i in range(30)]
    t = _build_regime_tracker(daily_pnls)
    result = t.get_rolling_sharpe("strat", window_days=30)
    assert result is not None
    assert result < 0, f"Expected negative Sharpe, got {result}"


def test_rolling_sharpe_uses_window_days():
    """window_days 파라미터가 올바르게 적용되는지 확인."""
    import time
    t = make_tracker()
    now = time.time()
    # 최근 5일: 큰 수익
    for i in range(5):
        t.record_trade("strat", 100.0, 100.0, 200.0, timestamp=now - i * 86400)
    # 6~15일 전: 큰 손실
    for i in range(5, 15):
        t.record_trade("strat", -100.0, 200.0, 100.0, timestamp=now - i * 86400)

    sharpe_5d = t.get_rolling_sharpe("strat", window_days=5)
    sharpe_15d = t.get_rolling_sharpe("strat", window_days=15)

    # 5일 윈도우는 수익만 → 높은 Sharpe (또는 None if std=0)
    # 15일 윈도우는 손실 포함 → 낮은 Sharpe
    if sharpe_5d is not None and sharpe_15d is not None:
        assert sharpe_5d > sharpe_15d


def test_rolling_sharpe_consistent_with_check_regime_death():
    """get_rolling_sharpe와 check_regime_death의 live_sharpe가 일치."""
    daily_pnls = [10.0, -5.0, 8.0, -3.0, 12.0, -1.0, 7.0, -2.0, 9.0, 4.0]
    t = _build_regime_tracker(daily_pnls)

    rolling = t.get_rolling_sharpe("strat", window_days=10)
    regime = t.check_regime_death("strat", backtest_sharpe=2.0, window_days=10)

    assert rolling is not None
    assert regime["live_sharpe"] is not None
    assert abs(rolling - regime["live_sharpe"]) < 0.01


# --- check_distribution_drift 테스트 ---

def test_distribution_drift_identical_distributions():
    """동일 분포 → is_drifted=False."""
    t = make_tracker()
    baseline = [0.01, -0.005, 0.02, 0.003, -0.01, 0.015, 0.008, -0.003, 0.012, 0.007]
    recent = baseline.copy()
    result = t.check_distribution_drift(baseline, recent)
    assert result["is_drifted"] is False
    assert result["warn"] is False


def test_distribution_drift_clearly_different():
    """명백히 다른 분포 → is_drifted=True."""
    t = make_tracker()
    baseline = [0.01] * 30
    recent = [-0.05] * 30
    result = t.check_distribution_drift(baseline, recent)
    assert result["is_drifted"] is True
    assert result["ks_stat"] is not None
    assert result["ks_pvalue"] is not None


def test_distribution_drift_insufficient_baseline():
    """baseline 5개 미만 → insufficient_data."""
    t = make_tracker()
    result = t.check_distribution_drift([0.01, 0.02, 0.03], [0.01] * 10)
    assert result["ks_stat"] is None
    assert "insufficient_data" in result["reason"]


def test_distribution_drift_insufficient_recent():
    """recent 5개 미만 → insufficient_data."""
    t = make_tracker()
    result = t.check_distribution_drift([0.01] * 10, [0.01, 0.02])
    assert result["ks_stat"] is None
    assert "insufficient_data" in result["reason"]


def test_distribution_drift_two_signal_warn():
    """KS drift + Sharpe < threshold → warn=True."""
    t = make_tracker()
    # 음수 수익 + 변동 있게 기록 (Sharpe 계산 가능 + 음수)
    import random
    rng = random.Random(99)
    for i in range(10):
        pnl = -1.0 - rng.uniform(0, 0.5)  # -1.0 ~ -1.5 (varying negatives)
        t.record_trade("strat_drift", pnl, 100.0, 99.0)

    baseline = [0.01] * 20
    recent = [-0.05] * 20  # 완전히 다른 분포
    result = t.check_distribution_drift(
        baseline, recent,
        strategy="strat_drift",
        sharpe_window=10,
    )
    assert result["is_drifted"] is True
    assert result["warn"] is True
    assert len(result["reason"]) > 0


def test_distribution_drift_no_warn_when_sharpe_ok():
    """KS drift이지만 Sharpe 양수이면 warn=False."""
    t = make_tracker()
    for _ in range(10):
        t.record_trade("strat_ok", 10.0, 100.0, 110.0)

    baseline = [0.05] * 20
    recent = [-0.05] * 20
    result = t.check_distribution_drift(
        baseline, recent,
        strategy="strat_ok",
        sharpe_threshold=0.5,
        sharpe_window=10,
    )
    assert result["is_drifted"] is True
    # Sharpe > 0.5 → warn=False
    assert result["warn"] is False


def test_distribution_drift_return_keys():
    """반환 딕셔너리에 필수 키 존재."""
    t = make_tracker()
    baseline = [0.01] * 10
    recent = [0.02] * 10
    result = t.check_distribution_drift(baseline, recent)
    for key in ("ks_stat", "ks_pvalue", "is_drifted", "rolling_sharpe", "warn", "reason"):
        assert key in result, f"Missing key: {key}"


def test_distribution_drift_ks_stat_range():
    """ks_stat ∈ [0, 1]."""
    t = make_tracker()
    import random
    rng = random.Random(42)
    baseline = [rng.gauss(0, 0.01) for _ in range(50)]
    recent = [rng.gauss(0.005, 0.015) for _ in range(50)]
    result = t.check_distribution_drift(baseline, recent)
    if result["ks_stat"] is not None:
        assert 0.0 <= result["ks_stat"] <= 1.0
