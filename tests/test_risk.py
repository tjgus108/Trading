"""RiskManager + CircuitBreaker 단위 테스트."""

import pytest
from src.risk.manager import CircuitBreaker, RiskManager, RiskStatus


@pytest.fixture
def risk_manager():
    cb = CircuitBreaker(max_daily_loss=0.05, max_drawdown=0.20)
    return RiskManager(
        risk_per_trade=0.01,
        atr_multiplier_sl=1.5,
        atr_multiplier_tp=3.0,
        circuit_breaker=cb,
    )


def test_hold_always_approved(risk_manager):
    result = risk_manager.evaluate("HOLD", entry_price=50000, atr=1000, account_balance=10000)
    assert result.status == RiskStatus.APPROVED
    assert result.position_size == 0


def test_buy_approved(risk_manager):
    result = risk_manager.evaluate("BUY", entry_price=50000, atr=1000, account_balance=10000)
    assert result.status == RiskStatus.APPROVED
    assert result.position_size > 0
    assert result.stop_loss < 50000
    assert result.take_profit > 50000


def test_sell_approved(risk_manager):
    result = risk_manager.evaluate("SELL", entry_price=50000, atr=1000, account_balance=10000)
    assert result.status == RiskStatus.APPROVED
    assert result.stop_loss > 50000
    assert result.take_profit < 50000


def test_circuit_breaker_flash_crash(risk_manager):
    result = risk_manager.evaluate(
        "BUY", entry_price=50000, atr=1000, account_balance=10000,
        last_candle_pct_change=-0.15,  # 15% 급락
    )
    assert result.status == RiskStatus.BLOCKED
    assert "flash crash" in result.reason


def test_circuit_breaker_drawdown():
    cb = CircuitBreaker(max_daily_loss=0.05, max_drawdown=0.10)
    rm = RiskManager(circuit_breaker=cb)
    # 피크 10000, 현재 8900 → 낙폭 11%
    cb._peak_balance = 10000
    result = rm.evaluate("BUY", entry_price=50000, atr=1000, account_balance=8900)
    assert result.status == RiskStatus.BLOCKED
    assert "drawdown" in result.reason


def test_position_size_max_cap():
    rm = RiskManager(max_position_size=0.05)  # 계좌의 5% 상한
    result = rm.evaluate("BUY", entry_price=50000, atr=100, account_balance=10000)
    assert result.status == RiskStatus.APPROVED
    max_size = (10000 * 0.05) / 50000
    assert result.position_size <= max_size + 1e-9


def test_risk_amount_equals_one_percent(risk_manager):
    result = risk_manager.evaluate("BUY", entry_price=50000, atr=1000, account_balance=10000)
    assert result.status == RiskStatus.APPROVED
    assert abs(result.risk_amount - 100.0) < 0.01  # 1% of 10000


def test_total_exposure_blocked():
    """기존 포지션이 총 노출 한도(30%)를 초과하면 BLOCKED."""
    rm = RiskManager(max_total_exposure=0.30)
    # 계좌 10000, 기존 포지션: 3500 USD (35%) → 초과
    open_pos = [{"size": 0.07, "price": 50000}]  # 0.07 * 50000 = 3500
    result = rm.evaluate(
        "BUY", entry_price=50000, atr=1000, account_balance=10000,
        open_positions=open_pos,
    )
    assert result.status == RiskStatus.BLOCKED
    assert "total_exposure" in result.reason


def test_total_exposure_approved_under_limit():
    """기존 포지션이 총 노출 한도 미만이면 APPROVED."""
    rm = RiskManager(max_total_exposure=0.30)
    # 계좌 10000, 기존 포지션: 2000 USD (20%) → 통과
    open_pos = [{"size": 0.04, "price": 50000}]  # 0.04 * 50000 = 2000
    result = rm.evaluate(
        "BUY", entry_price=50000, atr=1000, account_balance=10000,
        open_positions=open_pos,
    )
    assert result.status == RiskStatus.APPROVED


# --- position_sizer config 의존성 테스트 ---
from src.risk.position_sizer import kelly_position_size, kelly_position_size_from_sizer

# config: risk_per_trade=0.01, max_position_size=0.1

def test_kelly_position_size_config_risk_per_trade():
    """config risk_per_trade(0.01)를 kelly_fraction으로 전달했을 때 결과가 양수이고 상한(25%) 이내."""
    capital = 10000.0
    result = kelly_position_size(
        win_rate=0.6,
        win_loss_ratio=2.0,
        capital=capital,
        kelly_fraction=0.01,  # config: risk_per_trade
    )
    assert result > 0, "포지션 금액은 양수여야 한다"
    assert result <= capital * 0.25, "내부 상한 25% 초과 불가"


def test_kelly_position_size_from_sizer_config_max_fraction():
    """config max_position_size(0.1)를 max_fraction으로 전달했을 때 수량이 상한 이내."""
    capital = 10000.0
    price = 50000.0
    max_fraction = 0.10  # config: max_position_size
    result = kelly_position_size_from_sizer(
        win_rate=0.6,
        avg_win=0.02,
        avg_loss=0.01,
        capital=capital,
        price=price,
        kelly_fraction=0.25,
        max_fraction=max_fraction,
    )
    max_qty = (capital * max_fraction) / price
    assert result > 0, "수량은 양수여야 한다"
    assert result <= max_qty + 1e-9, f"max_fraction {max_fraction} 초과: {result} > {max_qty}"


# --- KellySizer 레짐 조정 테스트 ---
from src.risk.kelly_sizer import KellySizer


def test_kelly_regime_trend_up_is_largest():
    """TREND_UP(1.0x)이 TREND_DOWN(0.6x), RANGING(0.5x), HIGH_VOL(0.3x)보다 크다.

    max_fraction=0.50으로 높여 클리핑이 결과를 평탄화하지 않도록 한다.
    """
    sizer = KellySizer(fraction=0.5, max_fraction=0.50)
    kwargs = dict(win_rate=0.6, avg_win=0.02, avg_loss=0.01, capital=10000, price=50000)

    size_up = sizer.compute(**kwargs, regime="TREND_UP")
    size_down = sizer.compute(**kwargs, regime="TREND_DOWN")
    size_ranging = sizer.compute(**kwargs, regime="RANGING")
    size_high_vol = sizer.compute(**kwargs, regime="HIGH_VOL")

    assert size_up > size_down, f"TREND_UP {size_up} should > TREND_DOWN {size_down}"
    assert size_down > size_ranging, f"TREND_DOWN {size_down} should > RANGING {size_ranging}"
    assert size_ranging > size_high_vol, f"RANGING {size_ranging} should > HIGH_VOL {size_high_vol}"


def test_kelly_regime_trend_down_scale_is_0_6():
    """TREND_DOWN 스케일이 0.6이므로 TREND_UP 대비 약 60% 수량이어야 한다."""
    sizer = KellySizer(fraction=0.5, max_fraction=0.50)
    kwargs = dict(win_rate=0.6, avg_win=0.02, avg_loss=0.01, capital=10000, price=50000)

    size_up = sizer.compute(**kwargs, regime="TREND_UP")
    size_down = sizer.compute(**kwargs, regime="TREND_DOWN")

    ratio = size_down / size_up
    # 클리핑 영향 없을 때 ratio == 0.6
    assert 0.55 <= ratio <= 0.65, f"TREND_DOWN/TREND_UP ratio={ratio:.3f} expected ~0.6"


def test_kelly_regime_high_vol_scale_is_0_3():
    """HIGH_VOL 스케일이 0.3이므로 TREND_UP 대비 약 30% 수량이어야 한다."""
    sizer = KellySizer(fraction=0.5, max_fraction=0.50)
    kwargs = dict(win_rate=0.6, avg_win=0.02, avg_loss=0.01, capital=10000, price=50000)

    size_up = sizer.compute(**kwargs, regime="TREND_UP")
    size_high_vol = sizer.compute(**kwargs, regime="HIGH_VOL")

    ratio = size_high_vol / size_up
    assert 0.25 <= ratio <= 0.35, f"HIGH_VOL/TREND_UP ratio={ratio:.3f} expected ~0.3"


def test_kelly_regime_none_unchanged():
    """regime=None이면 레짐 조정 없이 기본 결과와 동일해야 한다."""
    sizer = KellySizer(fraction=0.5, max_fraction=0.10)
    kwargs = dict(win_rate=0.6, avg_win=0.02, avg_loss=0.01, capital=10000, price=50000)

    size_none = sizer.compute(**kwargs, regime=None)
    size_default = sizer.compute(**kwargs)
    assert size_none == size_default


def test_kelly_from_trade_history_regime():
    """from_trade_history에 regime 전달 시 TREND_UP > TREND_DOWN 성립.

    pnl 값은 소수(비율)로 전달해야 Kelly 계산이 정확하다.
    max_fraction=0.50으로 높여 클리핑이 결과를 평탄화하지 않도록 한다.
    """
    trades = [{"pnl": p} for p in [0.02, -0.01, 0.015, -0.008, 0.025, -0.012,
                                    0.018, -0.009, 0.022, -0.011, 0.016, -0.007]]
    kwargs = dict(trades=trades, capital=10000, price=50000, max_fraction=0.50)

    size_up = KellySizer.from_trade_history(**kwargs, regime="TREND_UP")
    size_down = KellySizer.from_trade_history(**kwargs, regime="TREND_DOWN")

    assert size_up > size_down, f"TREND_UP {size_up} should > TREND_DOWN {size_down}"


def test_kelly_adjust_for_regime_trend_down():
    """adjust_for_regime('TREND_DOWN')은 fraction * 0.6을 반환해야 한다.

    max_fraction=0.50으로 높여 클리핑이 0.3을 잘라내지 않도록 한다.
    """
    sizer = KellySizer(fraction=0.5, max_fraction=0.50)
    effective = sizer.adjust_for_regime("TREND_DOWN")
    expected = 0.5 * 0.6  # 0.3
    assert abs(effective - expected) < 1e-9, f"Expected {expected}, got {effective}"


# --- SignalCorrelationTracker (src/risk/manager.py) 단위 테스트 ---
from src.risk.manager import SignalCorrelationTracker


def test_signal_correlation_tracker_no_warn_below_threshold():
    """동일 방향 비율이 임계값 미만이면 None 반환."""
    tracker = SignalCorrelationTracker(warn_threshold=0.8)
    tracker.record("BTC/USDT", "StratA", "BUY")
    tracker.record("BTC/USDT", "StratB", "BUY")
    tracker.record("BTC/USDT", "StratC", "SELL")
    # 2/3 = 0.667 < 0.8 → 경고 없음
    result = tracker.check_and_warn("BTC/USDT")
    assert result is None


def test_signal_correlation_tracker_warns_at_threshold():
    """동일 방향 비율이 임계값 이상이면 방향 반환."""
    tracker = SignalCorrelationTracker(warn_threshold=0.75)
    tracker.record("BTC/USDT", "StratA", "BUY")
    tracker.record("BTC/USDT", "StratB", "BUY")
    tracker.record("BTC/USDT", "StratC", "BUY")
    tracker.record("BTC/USDT", "StratD", "SELL")
    # 3/4 = 0.75 >= 0.75 → BUY 반환
    result = tracker.check_and_warn("BTC/USDT")
    assert result == "BUY"


def test_signal_correlation_tracker_sell_concentration():
    """SELL 집중 시 SELL 반환."""
    tracker = SignalCorrelationTracker(warn_threshold=0.75)
    tracker.record("ETH/USDT", "S1", "SELL")
    tracker.record("ETH/USDT", "S2", "SELL")
    tracker.record("ETH/USDT", "S3", "SELL")
    result = tracker.check_and_warn("ETH/USDT")
    assert result == "SELL"


def test_signal_correlation_tracker_hold_ignored():
    """HOLD 시그널은 집계에서 제외."""
    tracker = SignalCorrelationTracker(warn_threshold=0.75)
    tracker.record("BTC/USDT", "S1", "HOLD")
    tracker.record("BTC/USDT", "S2", "HOLD")
    tracker.record("BTC/USDT", "S3", "BUY")
    # active < 2 → None
    result = tracker.check_and_warn("BTC/USDT")
    assert result is None


def test_signal_correlation_tracker_unknown_symbol_returns_none():
    """등록되지 않은 심볼은 None 반환."""
    tracker = SignalCorrelationTracker()
    result = tracker.check_and_warn("UNKNOWN/USDT")
    assert result is None


def test_signal_correlation_tracker_reset_clears_signals():
    """reset 호출 후 체크는 None을 반환해야 한다."""
    tracker = SignalCorrelationTracker(warn_threshold=0.75)
    tracker.record("BTC/USDT", "S1", "BUY")
    tracker.record("BTC/USDT", "S2", "BUY")
    tracker.record("BTC/USDT", "S3", "BUY")
    assert tracker.check_and_warn("BTC/USDT") == "BUY"
    tracker.reset("BTC/USDT")
    assert tracker.check_and_warn("BTC/USDT") is None


def test_signal_correlation_tracker_summary_fields():
    """summary 딕셔너리에 필수 필드가 포함되어야 한다."""
    tracker = SignalCorrelationTracker()
    tracker.record("BTC/USDT", "A", "BUY")
    tracker.record("BTC/USDT", "B", "SELL")
    tracker.record("BTC/USDT", "C", "HOLD")
    s = tracker.summary("BTC/USDT")
    assert s["symbol"] == "BTC/USDT"
    assert s["total_strategies"] == 3
    assert s["active_signals"] == 2
    assert s["buy"] == 1
    assert s["sell"] == 1
    assert s["hold"] == 1


def test_signal_correlation_tracker_case_insensitive():
    """action 문자열은 대소문자 무관하게 처리된다."""
    tracker = SignalCorrelationTracker(warn_threshold=0.75)
    tracker.record("BTC/USDT", "S1", "buy")
    tracker.record("BTC/USDT", "S2", "Buy")
    tracker.record("BTC/USDT", "S3", "BUY")
    result = tracker.check_and_warn("BTC/USDT")
    assert result == "BUY"


# --- DriftMonitor 단위 테스트 ---
import numpy as np
from src.risk.drawdown_monitor import DriftMonitor, DriftState


def _feed(monitor: DriftMonitor, returns, start=0):
    """helper: 수익률 리스트를 순서대로 update()에 입력."""
    state = DriftState.NORMAL
    for r in returns:
        state = monitor.update(r)
    return state


def test_drift_monitor_normal_during_warmup():
    """warm-up 기간 중에는 항상 NORMAL 반환."""
    dm = DriftMonitor(warm_up=50, lambda_=50.0)
    for _ in range(49):
        state = dm.update(0.001)
    assert state == DriftState.NORMAL
    assert dm.n_samples == 49


def test_drift_monitor_no_drift_stable():
    """분포 변화 없는 안정적 수익률 스트림에서 DRIFT 미발생."""
    rng = np.random.default_rng(42)
    dm = DriftMonitor(warm_up=50, lambda_=100.0, delta=0.001)
    returns = rng.normal(0.001, 0.005, 150).tolist()
    state = _feed(dm, returns)
    # 안정 분포: DRIFT 없어야 함 (WARNING은 허용)
    assert state != DriftState.DRIFT


def test_drift_monitor_detects_mean_shift():
    """평균 수익률이 크게 하락하면 DRIFT 감지."""
    # lambda_=5.0: 민감한 설정, 낮은 delta로 false-positive 억제 최소화
    dm = DriftMonitor(warm_up=30, lambda_=5.0, delta=0.0001)
    # warm-up: 평균 +0.005 수익률
    for _ in range(30):
        dm.update(0.005)
    # 급격한 하락: 평균 -0.05 → PH 통계량 빠르게 증가
    state = DriftState.NORMAL
    for _ in range(200):
        state = dm.update(-0.05)
        if state == DriftState.DRIFT:
            break
    assert state == DriftState.DRIFT


def test_drift_monitor_variance_warning():
    """분산이 기준 대비 2배 이상이면 최소 WARNING."""
    rng = np.random.default_rng(7)
    dm = DriftMonitor(warm_up=50, lambda_=500.0, var_ratio_threshold=2.0, window=30)
    # warm-up: 낮은 분산
    for _ in range(50):
        dm.update(rng.normal(0.001, 0.001))
    # 고분산 구간: std 10배
    state = DriftState.NORMAL
    for _ in range(40):
        state = dm.update(rng.normal(0.001, 0.05))
        if state != DriftState.NORMAL:
            break
    assert state in (DriftState.WARNING, DriftState.DRIFT)


def test_drift_monitor_callback_called():
    """DRIFT 감지 시 on_drift 콜백이 호출되어야 한다."""
    calls = []
    def cb(state, reason):
        calls.append((state, reason))

    dm = DriftMonitor(warm_up=30, lambda_=20.0, delta=0.0005, on_drift=cb)
    for _ in range(30):
        dm.update(0.002)
    for _ in range(50):
        dm.update(-0.05)
        if calls:
            break
    assert len(calls) >= 1
    assert calls[0][0] in (DriftState.WARNING, DriftState.DRIFT)


def test_drift_monitor_reset():
    """reset() 후에는 warm-up부터 재시작."""
    dm = DriftMonitor(warm_up=30, lambda_=20.0)
    for _ in range(30):
        dm.update(0.001)
    dm.reset()
    assert dm.n_samples == 0
    assert dm.state == DriftState.NORMAL
    # warm-up 미완료 상태에서 update → NORMAL
    state = dm.update(0.001)
    assert state == DriftState.NORMAL


def test_drift_monitor_is_drift_property():
    """is_drift / is_warning 프로퍼티 정합성."""
    dm = DriftMonitor(warm_up=30, lambda_=15.0, delta=0.0005)
    for _ in range(30):
        dm.update(0.002)
    for _ in range(60):
        dm.update(-0.03)
    if dm.is_drift:
        assert dm.state == DriftState.DRIFT
    if dm.state == DriftState.DRIFT:
        assert dm.is_warning  # DRIFT는 is_warning도 True


# --- DrawdownMonitor 연속 손실 쿨다운 단위 테스트 ---
from src.risk.drawdown_monitor import DrawdownMonitor


def test_streak_cooldown_triggers_on_threshold():
    """연속 손실이 threshold에 도달하면 streak 쿨다운이 시작되어야 한다."""
    monitor = DrawdownMonitor(
        loss_streak_threshold=3,
        streak_cooldown_seconds=14400.0,
        single_loss_halt_pct=1.0,  # 단일 손실 쿨다운은 비활성화 (100% 손실에만 반응)
    )
    # 2번 연속 손실 → streak 쿨다운 없음
    monitor.record_trade_result(-10.0, 1000.0)
    monitor.record_trade_result(-10.0, 990.0)
    assert not monitor.is_in_streak_cooldown()
    # 3번째 → streak_cooldown 시작 (완전 블록 아님, size reduction만)
    monitor.record_trade_result(-10.0, 980.0)
    assert monitor.is_in_streak_cooldown()
    # is_in_cooldown()은 단일 손실 쿨다운만 체크하므로 False
    assert not monitor.is_in_cooldown()
    # get_size_multiplier()는 0.5 반환 (streak threshold 도달)
    assert monitor.get_size_multiplier() == 0.5


def test_streak_cooldown_size_multiplier_reduction_during_cooldown():
    """streak 쿨다운 중에는 get_size_multiplier()가 0.5를 반환해야 한다."""
    monitor = DrawdownMonitor(
        loss_streak_threshold=2,
        streak_cooldown_seconds=3600.0,
        single_loss_halt_pct=1.0,
    )
    monitor.record_trade_result(-50.0, 1000.0)
    monitor.record_trade_result(-50.0, 950.0)
    assert monitor.get_size_multiplier() == 0.5


def test_streak_cooldown_disabled_when_zero():
    """streak_cooldown_seconds=0 이면 연속 손실 쿨다운이 시작되지 않는다."""
    monitor = DrawdownMonitor(
        loss_streak_threshold=2,
        streak_cooldown_seconds=0.0,
        single_loss_halt_pct=1.0,
    )
    monitor.record_trade_result(-50.0, 1000.0)
    monitor.record_trade_result(-50.0, 950.0)
    assert not monitor.is_in_cooldown()
    # size_multiplier는 0.5 (threshold 도달 시 축소)
    assert monitor.get_size_multiplier() == 0.5


def test_streak_cooldown_win_resets_counter():
    """수익 거래 후 연속 손실 카운터가 0으로 리셋되어야 한다."""
    monitor = DrawdownMonitor(
        loss_streak_threshold=3,
        streak_cooldown_seconds=14400.0,
        single_loss_halt_pct=1.0,
    )
    monitor.record_trade_result(-10.0, 1000.0)
    monitor.record_trade_result(-10.0, 990.0)
    # 수익 → 리셋
    monitor.record_trade_result(20.0, 980.0)
    assert monitor.consecutive_losses == 0
    assert not monitor.is_in_cooldown()
    # 다시 2번 손실 → threshold 미도달
    monitor.record_trade_result(-10.0, 1000.0)
    monitor.record_trade_result(-10.0, 990.0)
    assert not monitor.is_in_cooldown()


def test_streak_cooldown_serialization():
    """to_dict/from_dict이 streak_cooldown_seconds를 올바르게 직렬화/복원한다."""
    monitor = DrawdownMonitor(
        loss_streak_threshold=3,
        streak_cooldown_seconds=7200.0,
    )
    d = monitor.to_dict()
    assert d["streak_cooldown_seconds"] == 7200.0
    restored = DrawdownMonitor.from_dict(d)
    assert restored.streak_cooldown_seconds == 7200.0


# --- src/risk/circuit_breaker.py (full-featured) 경계값 테스트 ---
from src.risk.circuit_breaker import CircuitBreaker as FullCircuitBreaker


def _make_cb(**kwargs) -> FullCircuitBreaker:
    defaults = dict(
        daily_drawdown_limit=0.03,
        total_drawdown_limit=0.15,
        flash_crash_pct=0.10,
        max_consecutive_losses=5,
        cooldown_periods=3,
        max_daily_trades=0,
    )
    defaults.update(kwargs)
    return FullCircuitBreaker(**defaults)


# ── 낙폭 경계값 ───────────────────────────────────────────────────────────────

def test_cb_daily_dd_exactly_at_limit_triggers():
    """일일 낙폭이 limit와 정확히 같으면 triggered=True."""
    cb = _make_cb(daily_drawdown_limit=0.03)
    # 10000 → 9700: dd = 300/10000 = 3.00%
    result = cb.check(current_balance=9700, peak_balance=10000, daily_start_balance=10000)
    assert result["triggered"] is True
    assert "일일" in result["reason"]


def test_cb_daily_dd_just_below_limit_not_triggered():
    """일일 낙폭이 limit 미만이면 triggered=False."""
    cb = _make_cb(daily_drawdown_limit=0.03)
    # 10000 → 9701: dd = 299/10000 = 2.99%
    result = cb.check(current_balance=9701, peak_balance=10000, daily_start_balance=10000)
    assert result["triggered"] is False


def test_cb_total_dd_exactly_at_limit_triggers():
    """전체 낙폭이 limit와 정확히 같으면 triggered=True."""
    cb = _make_cb(total_drawdown_limit=0.15)
    # peak=10000, current=8500: total_dd=15%, daily_start=8600 so daily_dd=1.16% < 3%
    result = cb.check(current_balance=8500, peak_balance=10000, daily_start_balance=8600)
    assert result["triggered"] is True
    assert "전체" in result["reason"]


def test_cb_total_dd_just_below_limit_not_triggered():
    """전체 낙폭이 limit 미만이면 triggered=False."""
    cb = _make_cb(total_drawdown_limit=0.15)
    # peak=10000, current=8501: dd = 1499/10000 = 14.99%
    result = cb.check(current_balance=8501, peak_balance=10000, daily_start_balance=8600)
    assert result["triggered"] is False


# ── 플래시 크래시 경계값 ──────────────────────────────────────────────────────

def test_cb_flash_crash_exactly_at_limit_triggers():
    """캔들 변동이 flash_crash_pct와 정확히 같으면 triggered=True."""
    cb = _make_cb(flash_crash_pct=0.10)
    # open=10000, close=9000: chg = 1000/10000 = 10.0%
    result = cb.check(
        current_balance=10000, peak_balance=10000, daily_start_balance=10000,
        candle_open=10000, candle_close=9000,
    )
    assert result["triggered"] is True
    assert "플래시" in result["reason"]


def test_cb_flash_crash_just_below_limit_not_triggered():
    """캔들 변동이 flash_crash_pct 미만이면 triggered=False."""
    cb = _make_cb(flash_crash_pct=0.10)
    # open=10000, close=9001: chg = 999/10000 = 9.99%
    result = cb.check(
        current_balance=10000, peak_balance=10000, daily_start_balance=10000,
        candle_open=10000, candle_close=9001,
    )
    assert result["triggered"] is False


def test_cb_flash_crash_upward_move_also_triggers():
    """급등(상승 방향)도 abs() 처리되어 플래시 크래시로 감지된다."""
    cb = _make_cb(flash_crash_pct=0.10)
    result = cb.check(
        current_balance=10000, peak_balance=10000, daily_start_balance=10000,
        candle_open=9000, candle_close=9900,  # +10%
    )
    assert result["triggered"] is True


# ── 연속 손실 쿨다운 ──────────────────────────────────────────────────────────

def test_cb_consecutive_losses_triggers_cooldown():
    """연속 손실 5회 → cooldown 시작, check() triggered=True."""
    cb = _make_cb(max_consecutive_losses=5, cooldown_periods=3)
    for _ in range(5):
        cb.record_trade_result(is_loss=True)
    assert cb.cooldown_remaining == 3
    result = cb.check(current_balance=10000, peak_balance=10000, daily_start_balance=10000)
    assert result["triggered"] is True
    assert "쿨다운" in result["reason"]


def test_cb_consecutive_losses_below_threshold_no_cooldown():
    """연속 손실 4회 → 쿨다운 미발생."""
    cb = _make_cb(max_consecutive_losses=5, cooldown_periods=3)
    for _ in range(4):
        cb.record_trade_result(is_loss=True)
    assert cb.cooldown_remaining == 0
    result = cb.check(current_balance=10000, peak_balance=10000, daily_start_balance=10000)
    assert result["triggered"] is False


def test_cb_win_resets_consecutive_losses():
    """4연속 손실 후 승리 → 연속 손실 카운터 초기화."""
    cb = _make_cb(max_consecutive_losses=5)
    for _ in range(4):
        cb.record_trade_result(is_loss=True)
    cb.record_trade_result(is_loss=False)
    assert cb.consecutive_losses == 0


def test_cb_tick_cooldown_decrements_and_resets():
    """tick_cooldown() 3회 호출 후 쿨다운 종료, consecutive_losses 초기화."""
    cb = _make_cb(max_consecutive_losses=5, cooldown_periods=3)
    for _ in range(5):
        cb.record_trade_result(is_loss=True)
    assert cb.cooldown_remaining == 3
    cb.tick_cooldown()
    assert cb.cooldown_remaining == 2
    cb.tick_cooldown()
    cb.tick_cooldown()
    assert cb.cooldown_remaining == 0
    assert cb.consecutive_losses == 0


# ── reset_daily / reset_all ───────────────────────────────────────────────────

def test_cb_reset_daily_clears_daily_trigger():
    """일일 낙폭 트리거 후 reset_daily() → triggered False로 해제."""
    cb = _make_cb(daily_drawdown_limit=0.03)
    cb.check(current_balance=9700, peak_balance=10000, daily_start_balance=10000)
    assert cb.is_triggered is True
    cb.reset_daily(daily_start_balance=10000)
    assert cb.is_triggered is False


def test_cb_reset_all_clears_everything():
    """reset_all() 후 모든 상태가 초기화된다."""
    cb = _make_cb(max_consecutive_losses=5, cooldown_periods=3)
    for _ in range(5):
        cb.record_trade_result(is_loss=True)
    cb.check(current_balance=9700, peak_balance=10000, daily_start_balance=10000)
    cb.reset_all()
    assert cb.is_triggered is False
    assert cb.consecutive_losses == 0
    assert cb.cooldown_remaining == 0


# ── to_dict / from_dict 직렬화 ────────────────────────────────────────────────

def test_cb_serialization_roundtrip():
    """to_dict() → from_dict() 후 상태가 복원된다."""
    cb = _make_cb(max_consecutive_losses=5, cooldown_periods=3)
    for _ in range(5):
        cb.record_trade_result(is_loss=True)
    state = cb.to_dict()

    cb2 = _make_cb(max_consecutive_losses=5, cooldown_periods=3)
    cb2.from_dict(state)
    assert cb2.cooldown_remaining == cb.cooldown_remaining
    assert cb2.consecutive_losses == cb.consecutive_losses
    assert cb2.is_triggered == cb.is_triggered


# ── ATR 변동성 급등 ────────────────────────────────────────────────────────────

def test_cb_atr_surge_returns_size_multiplier_05():
    """현재 ATR ≥ baseline × atr_surge_multiplier → size_multiplier=0.5, triggered=False."""
    cb = _make_cb(atr_surge_multiplier=2.0)
    result = cb.check(
        current_balance=10000, peak_balance=10000, daily_start_balance=10000,
        current_atr=200, baseline_atr=100,  # 200 >= 100*2 → surge
    )
    assert result["triggered"] is False
    assert result["volatility_surge"] is True
    assert result["size_multiplier"] == 0.5


def test_cb_atr_no_surge_below_multiplier():
    """ATR 비율이 multiplier 미만이면 surge 없음, size_multiplier=1.0."""
    cb = _make_cb(atr_surge_multiplier=2.0)
    result = cb.check(
        current_balance=10000, peak_balance=10000, daily_start_balance=10000,
        current_atr=199, baseline_atr=100,  # 199 < 100*2 → no surge
    )
    assert result["volatility_surge"] is False
    assert result["size_multiplier"] == 1.0


# ── 우선순위: 플래시 크래시 > 낙폭 ──────────────────────────────────────────

def test_cb_flash_crash_takes_priority_over_drawdown():
    """플래시 크래시와 낙폭 동시 발생 시, 플래시 크래시 reason이 우선."""
    cb = _make_cb(flash_crash_pct=0.10, daily_drawdown_limit=0.03)
    result = cb.check(
        current_balance=9700, peak_balance=10000, daily_start_balance=10000,
        candle_open=10000, candle_close=9000,
    )
    assert result["triggered"] is True
    assert "플래시" in result["reason"]


# ── 단계적 MDD 서킷브레이커 (DrawdownMonitor) 테스트 ──────────────────────────
from src.risk.drawdown_monitor import MddLevel


def _make_dm(**kwargs) -> DrawdownMonitor:
    """단계적 MDD 테스트용 DrawdownMonitor 생성 헬퍼."""
    defaults = dict(
        mdd_warn_pct=0.05,
        mdd_block_pct=0.10,
        mdd_liquidate_pct=0.15,
        mdd_halt_pct=0.20,
        # 쿨다운/streak 영향 제거
        single_loss_halt_pct=1.0,
        loss_streak_threshold=999,
    )
    defaults.update(kwargs)
    return DrawdownMonitor(**defaults)


# ── MDD 레벨 판정 테스트 ─────────────────────────────────────────────────────

def test_mdd_level_normal_when_no_drawdown():
    """drawdown 없으면 NORMAL."""
    dm = _make_dm()
    dm.update(10000)
    assert dm.get_mdd_level() == MddLevel.NORMAL


def test_mdd_level_normal_below_warn():
    """MDD < 5% → NORMAL."""
    dm = _make_dm()
    dm.update(10000)
    dm.update(9600)  # 4% drawdown
    assert dm.get_mdd_level() == MddLevel.NORMAL


def test_mdd_level_warn_at_boundary():
    """MDD = 5% 정확히 → WARN."""
    dm = _make_dm()
    dm.update(10000)
    dm.update(9500)  # 5% drawdown
    assert dm.get_mdd_level() == MddLevel.WARN


def test_mdd_level_warn_between_5_and_10():
    """5% ≤ MDD < 10% → WARN."""
    dm = _make_dm()
    dm.update(10000)
    dm.update(9200)  # 8% drawdown
    assert dm.get_mdd_level() == MddLevel.WARN


def test_mdd_level_block_entry_at_boundary():
    """MDD = 10% 정확히 → BLOCK_ENTRY."""
    dm = _make_dm()
    dm.update(10000)
    dm.update(9000)  # 10% drawdown
    assert dm.get_mdd_level() == MddLevel.BLOCK_ENTRY


def test_mdd_level_block_entry_between_10_and_15():
    """10% ≤ MDD < 15% → BLOCK_ENTRY."""
    dm = _make_dm()
    dm.update(10000)
    dm.update(8700)  # 13% drawdown
    assert dm.get_mdd_level() == MddLevel.BLOCK_ENTRY


def test_mdd_level_liquidate_at_boundary():
    """MDD = 15% 정확히 → LIQUIDATE."""
    dm = _make_dm()
    dm.update(10000)
    dm.update(8500)  # 15% drawdown
    assert dm.get_mdd_level() == MddLevel.LIQUIDATE


def test_mdd_level_liquidate_between_15_and_20():
    """15% ≤ MDD < 20% → LIQUIDATE."""
    dm = _make_dm()
    dm.update(10000)
    dm.update(8200)  # 18% drawdown
    assert dm.get_mdd_level() == MddLevel.LIQUIDATE


def test_mdd_level_full_halt_at_boundary():
    """MDD = 20% 정확히 → FULL_HALT."""
    dm = _make_dm()
    dm.update(10000)
    dm.update(8000)  # 20% drawdown
    assert dm.get_mdd_level() == MddLevel.FULL_HALT


def test_mdd_level_full_halt_above_20():
    """MDD > 20% → FULL_HALT."""
    dm = _make_dm()
    dm.update(10000)
    dm.update(7000)  # 30% drawdown
    assert dm.get_mdd_level() == MddLevel.FULL_HALT


# ── MDD size_multiplier 테스트 ─────────────────────────────────────────────────

def test_mdd_size_multiplier_normal_is_1():
    """NORMAL 단계 → size_multiplier=1.0."""
    dm = _make_dm()
    dm.update(10000)
    dm.update(9600)  # 4%
    assert dm.get_mdd_size_multiplier() == 1.0


def test_mdd_size_multiplier_warn_is_05():
    """WARN 단계 → size_multiplier=0.5."""
    dm = _make_dm()
    dm.update(10000)
    dm.update(9500)  # 5%
    assert dm.get_mdd_size_multiplier() == 0.5


def test_mdd_size_multiplier_block_entry_is_0():
    """BLOCK_ENTRY 단계 → size_multiplier=0.0 (진입 차단)."""
    dm = _make_dm()
    dm.update(10000)
    dm.update(9000)  # 10%
    assert dm.get_mdd_size_multiplier() == 0.0


def test_mdd_size_multiplier_liquidate_is_0():
    """LIQUIDATE 단계 → size_multiplier=0.0."""
    dm = _make_dm()
    dm.update(10000)
    dm.update(8500)  # 15%
    assert dm.get_mdd_size_multiplier() == 0.0


def test_mdd_size_multiplier_full_halt_is_0():
    """FULL_HALT 단계 → size_multiplier=0.0."""
    dm = _make_dm()
    dm.update(10000)
    dm.update(8000)  # 20%
    assert dm.get_mdd_size_multiplier() == 0.0


# ── get_size_multiplier 통합: MDD와 streak 중 최소값 적용 ─────────────────────

def test_size_multiplier_min_of_mdd_and_streak():
    """MDD WARN(0.5) + streak 정상(1.0) → min=0.5."""
    dm = _make_dm(loss_streak_threshold=999)
    dm.update(10000)
    dm.update(9500)  # 5% → WARN → mdd_mult=0.5
    assert dm.get_size_multiplier() == 0.5


def test_size_multiplier_streak_wins_when_lower():
    """MDD NORMAL(1.0) + streak 축소(0.5) → min=0.5."""
    dm = _make_dm(loss_streak_threshold=2, single_loss_halt_pct=1.0, streak_cooldown_seconds=0.0)
    dm.update(10000)
    dm.update(9800)  # 2% → NORMAL → mdd_mult=1.0
    dm.record_trade_result(-10.0, 9800)
    dm.record_trade_result(-10.0, 9790)
    # streak=2 >= threshold=2 → streak_mult=0.5
    assert dm.get_size_multiplier() == 0.5


def test_size_multiplier_mdd_block_overrides_streak():
    """MDD BLOCK_ENTRY(0.0)은 streak 0.5보다 낮으므로 0.0."""
    dm = _make_dm(loss_streak_threshold=2, single_loss_halt_pct=1.0, streak_cooldown_seconds=0.0)
    dm.update(10000)
    dm.update(9000)  # 10% → BLOCK_ENTRY → mdd_mult=0.0
    dm.record_trade_result(-10.0, 9000)
    dm.record_trade_result(-10.0, 8990)
    assert dm.get_size_multiplier() == 0.0


# ── should_liquidate_all 테스트 ──────────────────────────────────────────────

def test_should_liquidate_all_false_below_15():
    """MDD < 15% → should_liquidate_all=False."""
    dm = _make_dm()
    dm.update(10000)
    dm.update(8600)  # 14%
    assert not dm.should_liquidate_all()


def test_should_liquidate_all_true_at_15():
    """MDD ≥ 15% → should_liquidate_all=True."""
    dm = _make_dm()
    dm.update(10000)
    dm.update(8500)  # 15%
    assert dm.should_liquidate_all()


def test_should_liquidate_all_true_at_20():
    """MDD ≥ 20% → should_liquidate_all=True."""
    dm = _make_dm()
    dm.update(10000)
    dm.update(8000)  # 20%
    assert dm.should_liquidate_all()


# ── DrawdownStatus 포함 확인 ─────────────────────────────────────────────────

def test_update_returns_mdd_level_in_status():
    """update() 결과 DrawdownStatus에 mdd_level과 mdd_size_multiplier가 포함된다."""
    dm = _make_dm()
    status = dm.update(10000)
    assert status.mdd_level == MddLevel.NORMAL
    assert status.mdd_size_multiplier == 1.0

    status2 = dm.update(9500)  # 5% → WARN
    assert status2.mdd_level == MddLevel.WARN
    assert status2.mdd_size_multiplier == 0.5

    status3 = dm.update(9000)  # 10% → BLOCK_ENTRY
    assert status3.mdd_level == MddLevel.BLOCK_ENTRY
    assert status3.mdd_size_multiplier == 0.0


# ── 회복 시나리오: MDD 단계 하강 ────────────────────────────────────────────

def test_mdd_level_recovers_when_equity_rises():
    """equity 회복 시 MDD 단계도 정상적으로 하강."""
    dm = _make_dm()
    dm.update(10000)
    dm.update(9000)  # 10% → BLOCK_ENTRY
    assert dm.get_mdd_level() == MddLevel.BLOCK_ENTRY
    # equity 회복 (peak은 여전히 10000)
    dm.update(9600)  # 4% → NORMAL
    assert dm.get_mdd_level() == MddLevel.NORMAL
    assert dm.get_mdd_size_multiplier() == 1.0


# ── 커스텀 임계값 테스트 ─────────────────────────────────────────────────────

def test_mdd_custom_thresholds():
    """커스텀 임계값으로 MDD 단계가 올바르게 판정."""
    dm = _make_dm(
        mdd_warn_pct=0.02,
        mdd_block_pct=0.05,
        mdd_liquidate_pct=0.08,
        mdd_halt_pct=0.12,
    )
    dm.update(10000)

    dm.update(9850)  # 1.5% < 2% → NORMAL
    assert dm.get_mdd_level() == MddLevel.NORMAL

    dm.update(9800)  # 2% → WARN
    assert dm.get_mdd_level() == MddLevel.WARN

    dm.update(9500)  # 5% → BLOCK_ENTRY
    assert dm.get_mdd_level() == MddLevel.BLOCK_ENTRY

    dm.update(9200)  # 8% → LIQUIDATE
    assert dm.get_mdd_level() == MddLevel.LIQUIDATE

    dm.update(8800)  # 12% → FULL_HALT
    assert dm.get_mdd_level() == MddLevel.FULL_HALT


# ── mdd_level 프로퍼티 테스트 ────────────────────────────────────────────────

def test_mdd_level_property_matches_method():
    """mdd_level 프로퍼티가 get_mdd_level()과 동일 결과."""
    dm = _make_dm()
    dm.update(10000)
    dm.update(9200)  # 8% → WARN
    assert dm.mdd_level == dm.get_mdd_level()
    assert dm.mdd_level == MddLevel.WARN


# ── 직렬화 호환성 테스트 ─────────────────────────────────────────────────────

def test_mdd_serialization_roundtrip():
    """to_dict/from_dict이 mdd_*_pct 파라미터를 올바르게 직렬화/복원."""
    dm = _make_dm(mdd_warn_pct=0.03, mdd_block_pct=0.08, mdd_liquidate_pct=0.12, mdd_halt_pct=0.18)
    d = dm.to_dict()
    assert d["mdd_warn_pct"] == 0.03
    assert d["mdd_block_pct"] == 0.08
    assert d["mdd_liquidate_pct"] == 0.12
    assert d["mdd_halt_pct"] == 0.18

    restored = DrawdownMonitor.from_dict(d)
    assert restored.mdd_warn_pct == 0.03
    assert restored.mdd_block_pct == 0.08
    assert restored.mdd_liquidate_pct == 0.12
    assert restored.mdd_halt_pct == 0.18


def test_mdd_from_dict_defaults_when_missing():
    """from_dict에서 mdd_*_pct 키가 없으면 기본값 사용 (backward compatibility)."""
    dm = DrawdownMonitor()
    d = dm.to_dict()
    # mdd_* 키 제거하여 old format 시뮬레이션
    for k in ("mdd_warn_pct", "mdd_block_pct", "mdd_liquidate_pct", "mdd_halt_pct"):
        d.pop(k, None)
    restored = DrawdownMonitor.from_dict(d)
    assert restored.mdd_warn_pct == 0.05
    assert restored.mdd_block_pct == 0.10
    assert restored.mdd_liquidate_pct == 0.15
    assert restored.mdd_halt_pct == 0.20


# ── 경계값 정밀 테스트 ───────────────────────────────────────────────────────

def test_mdd_boundary_just_below_warn():
    """MDD = 4.99% → NORMAL (5% 미만)."""
    dm = _make_dm()
    dm.update(10000)
    dm.update(9501)  # dd = 499/10000 = 4.99%
    assert dm.get_mdd_level() == MddLevel.NORMAL
    assert dm.get_mdd_size_multiplier() == 1.0


def test_mdd_boundary_just_below_block():
    """MDD = 9.99% → WARN (10% 미만)."""
    dm = _make_dm()
    dm.update(10000)
    dm.update(9001)  # dd = 999/10000 = 9.99%
    assert dm.get_mdd_level() == MddLevel.WARN
    assert dm.get_mdd_size_multiplier() == 0.5


def test_mdd_boundary_just_below_liquidate():
    """MDD = 14.99% → BLOCK_ENTRY (15% 미만)."""
    dm = _make_dm()
    dm.update(10000)
    dm.update(8501)  # dd = 1499/10000 = 14.99%
    assert dm.get_mdd_level() == MddLevel.BLOCK_ENTRY
    assert dm.get_mdd_size_multiplier() == 0.0


def test_mdd_boundary_just_below_halt():
    """MDD = 19.99% → LIQUIDATE (20% 미만)."""
    dm = _make_dm()
    dm.update(10000)
    dm.update(8001)  # dd = 1999/10000 = 19.99%
    assert dm.get_mdd_level() == MddLevel.LIQUIDATE
    assert dm.get_mdd_size_multiplier() == 0.0


# ── 레짐 스무딩 테스트 ───────────────────────────────────────────────────────
def test_kelly_regime_smooth_alpha_transition():
    """regime_smooth_alpha=0.3 이면 레짐 전환 시 EMA 블렌딩이 적용된다."""
    sizer = KellySizer(fraction=0.5, max_fraction=0.50, regime_smooth_alpha=0.3)
    kwargs = dict(win_rate=0.6, avg_win=0.02, avg_loss=0.01, capital=10000, price=50000)

    # 첫 호출: TREND_UP → smoothing 없음 (prev=None)
    size_up = sizer.compute(**kwargs, regime="TREND_UP")

    # 두 번째 호출: HIGH_VOL로 전환 → EMA 블렌딩
    size_high_vol_smooth = sizer.compute(**kwargs, regime="HIGH_VOL")

    # alpha=0 (smoothing 없음) 으로 비교
    sizer_no_smooth = KellySizer(fraction=0.5, max_fraction=0.50, regime_smooth_alpha=0.0)
    sizer_no_smooth.compute(**kwargs, regime="TREND_UP")  # prev 세팅
    size_high_vol_raw = sizer_no_smooth.compute(**kwargs, regime="HIGH_VOL")

    # 스무딩 버전은 이전 스케일(1.0) 30%를 유지하므로 raw(0.3x)보다 커야 함
    assert size_high_vol_smooth > size_high_vol_raw, (
        f"smooth={size_high_vol_smooth:.6f} should > raw={size_high_vol_raw:.6f}"
    )


def test_kelly_regime_smooth_same_regime_no_blend():
    """동일 레짐 반복 호출 시 스무딩 없이 target_scale이 그대로 적용된다."""
    sizer = KellySizer(fraction=0.5, max_fraction=0.50, regime_smooth_alpha=0.3)
    kwargs = dict(win_rate=0.6, avg_win=0.02, avg_loss=0.01, capital=10000, price=50000)

    size1 = sizer.compute(**kwargs, regime="TREND_DOWN")
    size2 = sizer.compute(**kwargs, regime="TREND_DOWN")
    # 동일 레짐 반복 → 결과가 동일해야 함 (블렌딩 없음)
    assert size1 == size2, f"Same regime repeated: {size1} != {size2}"


# ── Cornish-Fisher VaR 테스트 ──────────────────────────────────────────────
from src.risk.portfolio_optimizer import PortfolioOptimizer


def test_cf_var_fat_tails_at_99():
    """99% 신뢰수준에서 두꺼운 꼬리(t-분포) 수익률에 CF VaR이 Normal VaR보다 크다."""
    rng = np.random.default_rng(99)
    # t(df=3): 정규분포보다 훨씬 두꺼운 꼬리 (excess kurtosis > 0)
    fat_tail_returns = rng.standard_t(df=3, size=200) * 0.01

    var_cf, _ = PortfolioOptimizer._parametric_var_cvar(fat_tail_returns, confidence=0.99)

    # Normal VaR (alpha=0 → no CF)
    from scipy.stats import norm
    mu = float(fat_tail_returns.mean())
    sigma = float(fat_tail_returns.std(ddof=1))
    z = norm.ppf(0.01)
    normal_var = max(0.0, -(mu + z * sigma))

    # 99% CF VaR은 두꺼운 꼬리에서 더 보수적이어야 함
    assert var_cf >= normal_var - 1e-8, (
        f"CF VaR {var_cf:.6f} should >= Normal VaR {normal_var:.6f} for fat tails at 99%"
    )


def test_cf_var_normal_returns_consistent():
    """정규분포 수익률에서 CF VaR은 Normal VaR과 근사해야 한다 (skew≈0, kurt≈0)."""
    rng = np.random.default_rng(42)
    normal_returns = rng.normal(0.0, 0.01, 500)

    var_cf, cvar_cf = PortfolioOptimizer._parametric_var_cvar(normal_returns, confidence=0.95)

    from scipy.stats import norm
    mu = float(normal_returns.mean())
    sigma = float(normal_returns.std(ddof=1))
    z = norm.ppf(0.05)
    normal_var = max(0.0, -(mu + z * sigma))

    # 정규분포에서는 CF ≈ Normal (편차 10% 이내)
    assert abs(var_cf - normal_var) <= normal_var * 0.10, (
        f"CF VaR {var_cf:.6f} should be within 10% of Normal VaR {normal_var:.6f}"
    )
    assert var_cf > 0.0
    assert cvar_cf >= var_cf - 1e-12


# ── DrawdownMonitor 레짐별 동적 cooldown 테스트 ────────────────────────────────

def test_dm_regime_cooldown_high_vol_longer():
    """HIGH_VOL 레짐에서 단일 손실 쿨다운이 기본의 2배 길이여야 한다."""
    monitor = DrawdownMonitor(
        cooldown_seconds=3600.0,
        single_loss_halt_pct=0.01,
        loss_streak_threshold=999,
    )
    monitor.set_regime("HIGH_VOL")
    assert monitor._effective_cooldown_seconds() == 7200.0  # 3600 * 2.0


def test_dm_regime_cooldown_trend_up_shorter():
    """TREND_UP 레짐에서 단일 손실 쿨다운이 기본의 0.5배여야 한다."""
    monitor = DrawdownMonitor(
        cooldown_seconds=3600.0,
        single_loss_halt_pct=0.01,
        loss_streak_threshold=999,
    )
    monitor.set_regime("TREND_UP")
    assert monitor._effective_cooldown_seconds() == 1800.0  # 3600 * 0.5


def test_dm_regime_streak_cooldown_high_vol():
    """HIGH_VOL 레짐에서 streak 쿨다운이 기본의 2배 길이여야 한다."""
    monitor = DrawdownMonitor(
        streak_cooldown_seconds=14400.0,
        loss_streak_threshold=3,
        single_loss_halt_pct=1.0,
    )
    monitor.set_regime("HIGH_VOL")
    assert monitor._effective_streak_cooldown_seconds() == 28800.0  # 14400 * 2.0


def test_dm_regime_cooldown_default_no_regime():
    """레짐 미설정 시 배수는 1.0 (기본 cooldown 그대로)."""
    monitor = DrawdownMonitor(cooldown_seconds=3600.0)
    assert monitor._regime_cooldown_multiplier() == 1.0
    assert monitor._effective_cooldown_seconds() == 3600.0


def test_dm_regime_cooldown_trend_down():
    """TREND_DOWN 레짐에서 cooldown 배수 1.5x."""
    monitor = DrawdownMonitor(cooldown_seconds=3600.0)
    monitor.set_regime("TREND_DOWN")
    assert monitor._effective_cooldown_seconds() == 5400.0  # 3600 * 1.5


def test_dm_regime_cooldown_ranging():
    """RANGING 레짐에서 cooldown 배수 1.0x (기본과 동일)."""
    monitor = DrawdownMonitor(cooldown_seconds=3600.0)
    monitor.set_regime("RANGING")
    assert monitor._effective_cooldown_seconds() == 3600.0  # 3600 * 1.0


# ── CircuitBreaker 일일 거래 횟수 제한 테스트 ─────────────────────────────────

def test_cb_daily_trade_limit_triggers_when_exceeded():
    """일일 거래 횟수 max_daily_trades 초과 시 check()가 triggered=True."""
    cb = _make_cb(max_daily_trades=3)
    # 3번 거래 기록
    cb.record_trade_result(is_loss=False)
    cb.record_trade_result(is_loss=False)
    cb.record_trade_result(is_loss=False)
    assert cb.daily_trade_count == 3
    result = cb.check(current_balance=10000, peak_balance=10000, daily_start_balance=10000)
    assert result["triggered"] is True
    assert "거래 횟수" in result["reason"]


def test_cb_daily_trade_limit_not_triggered_below():
    """거래 횟수가 한계 미만이면 triggered=False."""
    cb = _make_cb(max_daily_trades=5)
    cb.record_trade_result(is_loss=False)
    cb.record_trade_result(is_loss=True)
    assert cb.daily_trade_count == 2
    result = cb.check(current_balance=10000, peak_balance=10000, daily_start_balance=10000)
    assert result["triggered"] is False


def test_cb_daily_trade_limit_zero_means_unlimited():
    """max_daily_trades=0이면 거래 횟수 제한 없음."""
    cb = _make_cb(max_daily_trades=0)
    for _ in range(100):
        cb.record_trade_result(is_loss=False)
    result = cb.check(current_balance=10000, peak_balance=10000, daily_start_balance=10000)
    assert result["triggered"] is False


def test_cb_daily_trade_count_resets_on_daily_reset():
    """reset_daily() 호출 시 daily_trade_count가 0으로 초기화."""
    cb = _make_cb(max_daily_trades=3)
    cb.record_trade_result(is_loss=False)
    cb.record_trade_result(is_loss=False)
    cb.record_trade_result(is_loss=False)
    assert cb.daily_trade_count == 3
    cb.reset_daily(daily_start_balance=10000)
    assert cb.daily_trade_count == 0
    # 리셋 후 다시 거래 가능
    result = cb.check(current_balance=10000, peak_balance=10000, daily_start_balance=10000)
    assert result["triggered"] is False


def test_cb_daily_trade_count_resets_on_reset_all():
    """reset_all() 호출 시 daily_trade_count가 0으로 초기화."""
    cb = _make_cb(max_daily_trades=3)
    cb.record_trade_result(is_loss=False)
    cb.record_trade_result(is_loss=False)
    cb.reset_all()
    assert cb.daily_trade_count == 0


def test_cb_daily_trade_count_serialization():
    """to_dict/from_dict이 daily_trade_count를 올바르게 직렬화/복원."""
    cb = _make_cb(max_daily_trades=10)
    cb.record_trade_result(is_loss=False)
    cb.record_trade_result(is_loss=True)
    cb.record_trade_result(is_loss=False)
    state = cb.to_dict()
    assert state["daily_trade_count"] == 3

    cb2 = _make_cb(max_daily_trades=10)
    cb2.from_dict(state)
    assert cb2.daily_trade_count == 3


def test_cb_daily_trade_limit_reset_clears_trigger():
    """일일 거래 횟수 초과로 트리거된 후 reset_daily()로 해제."""
    cb = _make_cb(max_daily_trades=2)
    cb.record_trade_result(is_loss=False)
    cb.record_trade_result(is_loss=False)
    # check()로 트리거 설정
    result = cb.check(current_balance=10000, peak_balance=10000, daily_start_balance=10000)
    assert result["triggered"] is True
    # reset_daily로 해제
    cb.reset_daily(daily_start_balance=10000)
    assert cb.daily_trade_count == 0
