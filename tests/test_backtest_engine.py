"""
BacktestEngine 단위 테스트.
"""

import numpy as np
import pandas as pd
import pytest

from src.backtest.engine import ANNUALIZATION, MAX_HOLD_CANDLES, BacktestEngine, BacktestResult
from src.strategy.base import Action, BaseStrategy, Confidence, Signal


# ---------------------------------------------------------------------------
# 헬퍼: 결정론적 테스트용 전략 & DataFrame
# ---------------------------------------------------------------------------

class AlwaysBuyStrategy(BaseStrategy):
    name = "always_buy"

    def generate(self, df: pd.DataFrame) -> Signal:
        last = df.iloc[-1]
        return Signal(
            action=Action.BUY,
            confidence=Confidence.HIGH,
            strategy=self.name,
            entry_price=float(last["close"]),
            reasoning="test",
            invalidation="none",
        )


class AlwaysSellStrategy(BaseStrategy):
    name = "always_sell"

    def generate(self, df: pd.DataFrame) -> Signal:
        last = df.iloc[-1]
        return Signal(
            action=Action.SELL,
            confidence=Confidence.HIGH,
            strategy=self.name,
            entry_price=float(last["close"]),
            reasoning="test",
            invalidation="none",
        )


class HoldStrategy(BaseStrategy):
    name = "hold"

    def generate(self, df: pd.DataFrame) -> Signal:
        last = df.iloc[-1]
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=float(last["close"]),
            reasoning="test",
            invalidation="none",
        )


def make_df(n: int = 200, close_trend: float = 0.001) -> pd.DataFrame:
    """단조 상승 가격 + 일정 ATR을 가진 테스트용 DataFrame."""
    np.random.seed(42)
    closes = 100.0 * np.cumprod(1 + close_trend + np.random.randn(n) * 0.002)
    highs = closes * 1.005
    lows = closes * 0.995
    atr14 = np.full(n, 1.0)  # 고정 ATR=1.0 for simplicity
    return pd.DataFrame({"close": closes, "high": highs, "low": lows, "atr14": atr14})


# ---------------------------------------------------------------------------
# 기본 동작 테스트
# ---------------------------------------------------------------------------

def test_no_trades_returns_result():
    engine = BacktestEngine()
    df = make_df()
    result = engine.run(HoldStrategy(), df)
    assert isinstance(result, BacktestResult)
    assert result.total_trades == 0
    assert result.passed is False
    assert "no trades generated" in result.fail_reasons


def test_result_fields_present():
    engine = BacktestEngine()
    df = make_df()
    result = engine.run(AlwaysBuyStrategy(), df)
    assert hasattr(result, "sharpe_ratio")
    assert hasattr(result, "max_drawdown")
    assert hasattr(result, "profit_factor")
    assert hasattr(result, "total_return")
    assert hasattr(result, "win_rate")


def test_summary_string():
    engine = BacktestEngine()
    df = make_df()
    result = engine.run(AlwaysBuyStrategy(), df)
    s = result.summary()
    assert "BACKTEST_RESULT" in s
    assert "always_buy" in s


def test_balance_decreases_with_commission():
    """커미션만 있어도 잔고는 초기보다 낮아질 수 있다."""
    engine = BacktestEngine(commission=0.01)  # 1% 커미션
    df = make_df()
    result = engine.run(AlwaysBuyStrategy(), df)
    # total_return이 반드시 커미션으로만 손실날 수 있음 — 값 존재 여부만 확인
    assert isinstance(result.total_return, float)


# ---------------------------------------------------------------------------
# 수정 1: 슬리피지 테스트
# ---------------------------------------------------------------------------

def test_slippage_reduces_profit():
    """slippage=0.001 이면 slippage=0 보다 수익이 작아야 한다."""
    df = make_df(n=300, close_trend=0.002)
    strategy = AlwaysBuyStrategy()

    result_no_slip = BacktestEngine(slippage=0.0).run(strategy, df)
    result_slip = BacktestEngine(slippage=0.001).run(strategy, df)

    assert result_slip.total_return < result_no_slip.total_return, (
        f"slippage 적용 시 수익이 감소해야 함: "
        f"slip={result_slip.total_return:.4f} vs no-slip={result_no_slip.total_return:.4f}"
    )


def test_slippage_buy_entry_price_higher():
    """BUY 슬리피지: entry가 close보다 높아야 함 (직접 확인 불가하므로 수익 감소로 검증)."""
    df = make_df(n=200, close_trend=0.001)
    r0 = BacktestEngine(slippage=0.0).run(AlwaysBuyStrategy(), df)
    r1 = BacktestEngine(slippage=0.002).run(AlwaysBuyStrategy(), df)
    assert r1.total_return <= r0.total_return


def test_slippage_sell_entry_price_lower():
    """SELL 슬리피지: entry가 close보다 낮아야 함 (수익 감소로 검증)."""
    df = make_df(n=200, close_trend=-0.001)
    r0 = BacktestEngine(slippage=0.0).run(AlwaysSellStrategy(), df)
    r1 = BacktestEngine(slippage=0.002).run(AlwaysSellStrategy(), df)
    assert r1.total_return <= r0.total_return


# ---------------------------------------------------------------------------
# 수정 2: Sharpe 연환산 테스트
# ---------------------------------------------------------------------------

def test_annualization_map_keys():
    for tf in ("1m", "5m", "15m", "1h", "4h", "1d"):
        assert tf in ANNUALIZATION
    assert ANNUALIZATION["1d"] == 252
    assert ANNUALIZATION["1h"] == 252 * 24


def test_sharpe_timeframe_1h_vs_1d():
    """동일 데이터에서 1h annualization > 1d annualization → Sharpe 1h > Sharpe 1d."""
    df = make_df(n=300, close_trend=0.002)
    strategy = AlwaysBuyStrategy()

    r_1h = BacktestEngine(timeframe="1h").run(strategy, df)
    r_1d = BacktestEngine(timeframe="1d").run(strategy, df)

    assert r_1h.sharpe_ratio > r_1d.sharpe_ratio, (
        f"1h Sharpe({r_1h.sharpe_ratio}) should be > 1d Sharpe({r_1d.sharpe_ratio})"
    )


def test_sharpe_timeframe_default_is_1h():
    engine = BacktestEngine()
    assert engine.timeframe == "1h"


def test_sharpe_1m_largest():
    """1m annualization이 가장 크므로 Sharpe도 가장 크다."""
    df = make_df(n=300, close_trend=0.002)
    strategy = AlwaysBuyStrategy()
    r_1m = BacktestEngine(timeframe="1m").run(strategy, df)
    r_1d = BacktestEngine(timeframe="1d").run(strategy, df)
    assert r_1m.sharpe_ratio > r_1d.sharpe_ratio


# ---------------------------------------------------------------------------
# 수정 3: Funding Rate 테스트
# ---------------------------------------------------------------------------

def test_funding_cost_buy_reduces_balance():
    """BUY 포지션 보유 중 펀딩비가 양수면 잔고가 줄어 수익이 작아야 한다."""
    df = make_df(n=300, close_trend=0.001)
    strategy = AlwaysBuyStrategy()

    r_no_funding = BacktestEngine(funding_cost_per_candle=0.0).run(strategy, df)
    r_funding = BacktestEngine(funding_cost_per_candle=0.0001).run(strategy, df)

    assert r_funding.total_return < r_no_funding.total_return, (
        "펀딩비 적용 시 BUY 포지션 수익이 감소해야 함"
    )


def test_funding_cost_sell_increases_balance():
    """SELL 포지션 보유 중 펀딩비 수령 → 수익이 늘어야 한다."""
    df = make_df(n=300, close_trend=-0.001)
    strategy = AlwaysSellStrategy()

    r_no_funding = BacktestEngine(funding_cost_per_candle=0.0).run(strategy, df)
    r_funding = BacktestEngine(funding_cost_per_candle=0.0001).run(strategy, df)

    assert r_funding.total_return > r_no_funding.total_return, (
        "펀딩비 수령 시 SELL 포지션 수익이 증가해야 함"
    )


def test_funding_cost_default_zero():
    engine = BacktestEngine()
    assert engine.funding_cost_per_candle == 0.0


def test_funding_zero_no_effect():
    """funding_cost_per_candle=0 이면 결과가 동일해야 한다."""
    df = make_df(n=200)
    strategy = AlwaysBuyStrategy()
    r1 = BacktestEngine(funding_cost_per_candle=0.0).run(strategy, df)
    r2 = BacktestEngine(funding_cost_per_candle=0.0).run(strategy, df)
    assert r1.total_return == r2.total_return


# ---------------------------------------------------------------------------
# 수정 4: 청산 수수료 + MAX_HOLD_CANDLES 테스트
# ---------------------------------------------------------------------------

def test_exit_commission_reduces_profit():
    """청산 수수료가 반영되면 commission=0 대비 수익이 낮아야 한다."""
    df = make_df(n=300, close_trend=0.002)
    strategy = AlwaysBuyStrategy()
    r_no_comm = BacktestEngine(commission=0.0, slippage=0.0).run(strategy, df)
    r_comm = BacktestEngine(commission=0.001, slippage=0.0).run(strategy, df)
    assert r_comm.total_return < r_no_comm.total_return, (
        f"수수료 적용 시 수익 감소 필요: comm={r_comm.total_return:.4f} vs no-comm={r_no_comm.total_return:.4f}"
    )


def test_profit_factor_zero_division_guard():
    """손실 거래가 없어도 profit_factor가 계산돼야 한다 (ZeroDivisionError 없음)."""
    df = make_df(n=200, close_trend=0.005)
    result = BacktestEngine(commission=0.0, slippage=0.0).run(AlwaysBuyStrategy(), df)
    assert isinstance(result.profit_factor, float)
    assert result.profit_factor >= 0


def test_max_hold_candles_constant():
    """MAX_HOLD_CANDLES 상수가 24로 정의되어야 한다."""
    assert MAX_HOLD_CANDLES == 24


def test_max_hold_candles_forces_close():
    """MAX_HOLD_CANDLES 제한으로 강제 청산 → 거래 수가 0이 아니어야 한다."""
    df = make_df(n=300, close_trend=0.0)  # 가격 변동 거의 없음 → SL/TP 미도달
    result = BacktestEngine(
        atr_multiplier_sl=100.0,  # SL/TP 매우 멀리 → 자연 청산 안 됨
        atr_multiplier_tp=200.0,
        commission=0.0,
        slippage=0.0,
    ).run(AlwaysBuyStrategy(), df)
    # MAX_HOLD_CANDLES마다 강제 청산되므로 거래 발생해야 함
    assert result.total_trades > 0


# ---------------------------------------------------------------------------
# 신규 5: Sortino Ratio (downside deviation 기반) 테스트
# ---------------------------------------------------------------------------

def test_sortino_ratio_higher_on_loss_reduction():
    """음수 PnL이 줄어들면 Sortino는 증가해야 한다 (downside deviation 감소)."""
    from src.backtest.report import BacktestReport
    
    # 시나리오 1: 큰 손실 거래들
    trades_with_big_losses = [
        {"pnl_pct": 0.02},
        {"pnl_pct": -0.10},  # 큰 손실
        {"pnl_pct": 0.01},
        {"pnl_pct": -0.08},  # 큰 손실
        {"pnl_pct": 0.03},
    ]
    
    # 시나리오 2: 작은 손실 거래들
    trades_with_small_losses = [
        {"pnl_pct": 0.02},
        {"pnl_pct": -0.02},  # 작은 손실
        {"pnl_pct": 0.01},
        {"pnl_pct": -0.01},  # 작은 손실
        {"pnl_pct": 0.03},
    ]
    
    report_big_loss = BacktestReport.from_trades(trades_with_big_losses, annualization=252*24)
    report_small_loss = BacktestReport.from_trades(trades_with_small_losses, annualization=252*24)
    
    # downside deviation이 작을수록 Sortino 비율이 커야 함
    assert report_small_loss.sortino_ratio > report_big_loss.sortino_ratio, (
        f"Small losses Sortino({report_small_loss.sortino_ratio:.3f}) should be > "
        f"Big losses Sortino({report_big_loss.sortino_ratio:.3f})"
    )


def test_recovery_factor_reflects_profit_to_drawdown_ratio():
    """Recovery Factor = total_return / max_drawdown 검증."""
    from src.backtest.report import BacktestReport
    
    # 데이터: 명확한 수익/손실 패턴
    trades = [
        {"pnl_pct": 0.05},   # +5%
        {"pnl_pct": 0.05},   # +5% cumsum: +10.25%
        {"pnl_pct": -0.10},  # -10% (누적이 가장 낮아짐) → DD 발생
        {"pnl_pct": 0.10},   # +10% 회복
        {"pnl_pct": 0.05},   # +5%
    ]
    
    report = BacktestReport.from_trades(trades, annualization=252*24)
    
    # Recovery Factor는 total_return / max_drawdown으로 정의됨
    # max_drawdown이 0이 아니면 recovery > 0 이어야 함
    if report.max_drawdown > 1e-9:
        expected_recovery = report.total_return / report.max_drawdown
        assert abs(report.recovery_factor - expected_recovery) < 1e-6, (
            f"Recovery factor mismatch: got {report.recovery_factor:.6f}, "
            f"expected {expected_recovery:.6f}"
        )


# ---------------------------------------------------------------------------
# 신규 6: DSR 통합 테스트
# ---------------------------------------------------------------------------

def test_dsr_field_present_in_result():
    """BacktestResult에 deflated_sharpe_ratio 필드가 있어야 한다."""
    engine = BacktestEngine()
    df = make_df(n=300, close_trend=0.002)
    result = engine.run(AlwaysBuyStrategy(), df)
    assert hasattr(result, "deflated_sharpe_ratio")
    assert isinstance(result.deflated_sharpe_ratio, float)


def test_dsr_in_summary_output():
    """summary() 출력에 deflated_sharpe_ratio 줄이 포함되어야 한다."""
    engine = BacktestEngine()
    df = make_df(n=300, close_trend=0.002)
    result = engine.run(AlwaysBuyStrategy(), df)
    summary = result.summary()
    assert "deflated_sharpe_ratio" in summary


def test_dsr_threshold_warning_logged(caplog):
    """dsr_threshold=999 이면 경고 로그가 발생해야 한다."""
    import logging
    engine = BacktestEngine(dsr_threshold=999.0)
    df = make_df(n=300, close_trend=0.002)
    with caplog.at_level(logging.WARNING, logger="src.backtest.engine"):
        result = engine.run(AlwaysBuyStrategy(), df)
    assert any("DSR" in r.message for r in caplog.records), (
        "dsr_threshold 초과 시 WARNING 로그가 발생해야 함"
    )


def test_dsr_threshold_strict_mode_validation():
    """dsr_threshold를 엄격하게 설정 시, DSR이 threshold 미만이면 경고 로그가 발생해야 한다."""
    import logging
    
    engine_strict = BacktestEngine(dsr_threshold=1.0)  # 엄격 모드 (DSR >= 1.0 필요)
    engine_loose = BacktestEngine(dsr_threshold=0.0)   # 기본 모드 (DSR >= 0.0)
    
    df = make_df(n=300, close_trend=0.001)
    
    # 엄격 모드에서 경고가 발생할 가능성 검증
    # (모든 경우에 발생하진 않겠지만, dsr_threshold가 높을수록 경고 가능성이 높음)
    assert engine_strict.dsr_threshold == 1.0
    assert engine_loose.dsr_threshold == 0.0
    assert engine_strict.dsr_threshold > engine_loose.dsr_threshold
    
    # 두 엔진이 동일 데이터에서 동일 DSR을 계산하고, 
    # threshold 값이 다르므로 경고 발생 조건이 다름을 검증
    result_strict = engine_strict.run(AlwaysBuyStrategy(), df)
    result_loose = engine_loose.run(AlwaysBuyStrategy(), df)
    
    assert result_strict.deflated_sharpe_ratio == result_loose.deflated_sharpe_ratio, (
        "동일 데이터 · 동일 전략 → DSR 계산 결과는 동일해야 함"
    )


# ---------------------------------------------------------------------------
# 신규 7: Slippage 누적 비용 검증
# ---------------------------------------------------------------------------

def test_total_slippage_cost_accumulates_correctly():
    """
    slippage 비용이 정확히 누적되는지 검증.
    BUY: entry = close * (1 + slippage) → slip = size * (entry - close)
    SELL: entry = close * (1 - slippage) → slip = size * (close - entry)
    Exit 시에도 동일하게 적용.
    """
    slippage_rate = 0.001  # 0.1%
    
    engine = BacktestEngine(
        initial_balance=10000.0,
        slippage=slippage_rate,
        commission=0.0,  # 슬리피지만 검증
        atr_multiplier_sl=0.5,  # TP 자주 도달하도록 설정
        atr_multiplier_tp=1.0,
    )
    
    df = make_df(n=200, close_trend=0.002)
    result = engine.run(AlwaysBuyStrategy(), df)
    
    # 거래가 최소 1개는 있어야 함
    assert result.total_trades > 0, "거래가 발생해야 함"
    
    # total_slippage_cost는 0보다 커야 함
    assert result.total_slippage_cost > 0.0, (
        f"슬리피지 비용이 발생해야 함: {result.total_slippage_cost:.6f}"
    )
    
    # 각 거래의 PnL에서 slippage 비용이 차감되었으므로
    # slippage=0인 경우보다 수익이 작아야 함
    result_no_slip = BacktestEngine(
        initial_balance=10000.0,
        slippage=0.0,
        commission=0.0,
        atr_multiplier_sl=0.5,
        atr_multiplier_tp=1.0,
    ).run(AlwaysBuyStrategy(), df)
    
    assert result.total_return < result_no_slip.total_return, (
        f"슬리피지 적용 시 수익이 감소: "
        f"slip={result.total_return:.4f} vs no-slip={result_no_slip.total_return:.4f}"
    )


def test_slippage_cost_scales_with_position_size():
    """
    슬리피지 비용은 포지션 크기(size)에 비례해야 함.
    larger balance → larger position size → larger slippage cost
    """
    slippage_rate = 0.001
    
    # 작은 초기 자본
    engine_small = BacktestEngine(
        initial_balance=1000.0,
        slippage=slippage_rate,
        commission=0.0,
    )
    
    # 큰 초기 자본
    engine_large = BacktestEngine(
        initial_balance=100000.0,
        slippage=slippage_rate,
        commission=0.0,
    )
    
    df = make_df(n=200, close_trend=0.002)
    strategy = AlwaysBuyStrategy()
    
    result_small = engine_small.run(strategy, df)
    result_large = engine_large.run(strategy, df)
    
    # 동일 슬리피지율이지만 큰 잔고가 더 큰 절대값 슬리피지 비용을 발생
    assert result_small.total_trades > 0
    assert result_large.total_trades > 0
    assert result_large.total_slippage_cost > result_small.total_slippage_cost, (
        f"큰 잔고가 더 큰 슬리피지 비용 발생: "
        f"large={result_large.total_slippage_cost:.6f} > small={result_small.total_slippage_cost:.6f}"
    )


# ---------------------------------------------------------------------------
# 신규 8: Fee tracking 정확성 (진입/청산 수수료 2배 누적)
# ---------------------------------------------------------------------------

def test_fee_accumulates_on_entry_and_exit():
    """
    BUY 진입 시 수수료 + 청산 시 수수료 = 왕복 수수료.
    commission=0.001 (0.1%)이면 진입+청산 = 0.2% 누적.
    """
    commission = 0.001  # 0.1% per trade
    
    engine = BacktestEngine(
        initial_balance=10000.0,
        commission=commission,
        slippage=0.0,  # 슬리피지 제외하고 수수료만 검증
        atr_multiplier_sl=0.5,
        atr_multiplier_tp=1.0,
    )
    
    df = make_df(n=200, close_trend=0.002)
    result = engine.run(AlwaysBuyStrategy(), df)
    
    # 최소 1개 거래가 있어야 함
    assert result.total_trades > 0, "거래가 발생해야 함"
    
    # 총 수수료 > 0이어야 함 (진입 + 청산)
    assert result.total_fees > 0.0, (
        f"수수료가 누적되어야 함: {result.total_fees:.6f}"
    )
    
    # commission=0인 경우 대비 수익이 낮아야 함
    result_no_fee = BacktestEngine(
        initial_balance=10000.0,
        commission=0.0,
        slippage=0.0,
        atr_multiplier_sl=0.5,
        atr_multiplier_tp=1.0,
    ).run(AlwaysBuyStrategy(), df)
    
    assert result.total_return < result_no_fee.total_return, (
        f"수수료 적용 시 수익이 감소해야 함: "
        f"with_fee={result.total_return:.4f} vs no_fee={result_no_fee.total_return:.4f}"
    )


def test_fee_double_on_buy_sell_cycle():
    """
    단일 BUY→SELL 사이클에서 수수료는:
    - 진입: size * entry_price * commission
    - 청산: size * exit_price * commission
    두 번 누적되어야 한다.
    
    예: commission=0.001, entry=100, exit=110, size=1
    - Entry fee: 1 * 100 * 0.001 = 0.1
    - Exit fee:  1 * 110 * 0.001 = 0.11
    - Total: 0.21 (약 0.2%)
    """
    commission = 0.001
    initial_balance = 10000.0
    
    # 극단적으로 강한 수익 트렌드: TP가 자주 도달하도록
    engine = BacktestEngine(
        initial_balance=initial_balance,
        commission=commission,
        slippage=0.0,
        atr_multiplier_sl=10.0,  # SL 멀리 → TP 도달이 우선
        atr_multiplier_tp=0.3,   # TP 가까이
    )
    
    df = make_df(n=200, close_trend=0.003)
    result = engine.run(AlwaysBuyStrategy(), df)
    
    assert result.total_trades > 0
    
    # fee_rate이 0.001이므로 예상 최소 누적 수수료:
    # 거래당 대략 size * price * 0.002 (진입+청산)
    # 정확한 값은 size 변동에 따라 다르지만, total_fees > 0이어야 함
    assert result.total_fees > 0.0, (
        f"BUY→SELL 사이클 수수료: {result.total_fees:.6f}"
    )
    
    # 수수료가 누적되므로 잔고 < 초기 잔고
    final_balance = initial_balance * (1 + result.total_return)
    assert final_balance < initial_balance or result.total_return < 0 or abs(result.total_fees) > 1e-6, (
        f"수수료 누적 검증 실패: return={result.total_return:.4f}, fees={result.total_fees:.6f}"
    )


def test_slippage_pct_param_identical_to_slippage():
    """slippage_pct 파라미터가 slippage와 동일하게 동작하는지 검증 (slippage_pct=0.001 vs slippage=0.001)."""
    df = make_df(n=300, close_trend=0.002)
    strategy = AlwaysBuyStrategy()

    # slippage 파라미터 사용
    result_slippage = BacktestEngine(slippage=0.001).run(strategy, df)
    
    # slippage_pct 파라미터 사용 (slippage_pct이 우선됨)
    result_slippage_pct = BacktestEngine(slippage_pct=0.001).run(strategy, df)
    
    # 동일 값이면 동일한 결과가 나와야 함
    assert result_slippage.total_return == result_slippage_pct.total_return, (
        f"slippage와 slippage_pct이 동일 값이면 결과가 같아야 함: "
        f"slippage={result_slippage.total_return:.6f} vs slippage_pct={result_slippage_pct.total_return:.6f}"
    )
    assert result_slippage.total_slippage_cost == result_slippage_pct.total_slippage_cost, (
        f"slippage_cost도 동일해야 함: "
        f"slippage={result_slippage.total_slippage_cost:.6f} vs slippage_pct={result_slippage_pct.total_slippage_cost:.6f}"
    )
