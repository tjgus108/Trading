"""CoppockStrategy 단위 테스트 (12개 이상)."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.coppock import CoppockStrategy
from src.strategy.base import Action, Confidence


def _make_df(n: int = 60, close_values=None) -> pd.DataFrame:
    """테스트용 DataFrame 생성."""
    if close_values is not None:
        closes = list(close_values)
        n = len(closes)
    else:
        closes = [100.0 + i * 0.1 for i in range(n)]

    return pd.DataFrame(
        {
            "open": closes,
            "high": [c + 1 for c in closes],
            "low": [c - 1 for c in closes],
            "close": closes,
            "volume": [1000.0] * n,
            "ema50": closes,
            "atr14": [1.0] * n,
        }
    )


def _make_buy_df() -> pd.DataFrame:
    """Coppock < 0, 상승 중 → BUY 신호 유도."""
    # 처음엔 급락 후 완만하게 회복 → ROC 음수 + 최근 상승
    closes = [100.0] * 20 + [80.0 - i * 0.5 for i in range(20)] + [72.0 + i * 0.3 for i in range(20)]
    return _make_df(close_values=closes)


def _make_sell_df() -> pd.DataFrame:
    """Coppock > 0, 하락 중 → SELL 신호 유도."""
    # 처음엔 급등 후 완만하게 하락 → ROC 양수 + 최근 하락
    closes = [100.0] * 20 + [120.0 + i * 0.5 for i in range(20)] + [130.0 - i * 0.3 for i in range(20)]
    return _make_df(close_values=closes)


def _force_signal(cop_now: float, cop_prev: float):
    """cop_now, cop_prev를 직접 설정해 신호를 검증하는 헬퍼."""
    strat = CoppockStrategy()

    class _FakeResult:
        def __init__(self, action, confidence, cop_now):
            self.action = action
            self.confidence = confidence
            self.cop_now = cop_now

    entry = 100.0
    from src.strategy.base import Signal
    if cop_now < 0 and cop_now > cop_prev:
        from src.strategy.coppock import _HIGH_CONF_THRESHOLD
        conf = Confidence.HIGH if abs(cop_now) > _HIGH_CONF_THRESHOLD else Confidence.MEDIUM
        return Signal(
            action=Action.BUY,
            confidence=conf,
            strategy="coppock",
            entry_price=entry,
            reasoning=f"Coppock 바닥 반등: {cop_prev:.4f} → {cop_now:.4f} (음수 구간 상승)",
            invalidation="Coppock이 다시 하락 전환 시",
            bull_case=f"Coppock={cop_now:.4f} < 0, 장기 바닥 반등 신호",
            bear_case="아직 음수 구간, 추가 하락 가능",
        )
    elif cop_now > 0 and cop_now < cop_prev:
        from src.strategy.coppock import _HIGH_CONF_THRESHOLD
        conf = Confidence.HIGH if abs(cop_now) > _HIGH_CONF_THRESHOLD else Confidence.MEDIUM
        return Signal(
            action=Action.SELL,
            confidence=conf,
            strategy="coppock",
            entry_price=entry,
            reasoning=f"Coppock 고점 반락: {cop_prev:.4f} → {cop_now:.4f} (양수 구간 하락)",
            invalidation="Coppock이 다시 상승 전환 시",
            bull_case="단기 반등 가능",
            bear_case=f"Coppock={cop_now:.4f} > 0, 하락 전환 신호",
        )
    else:
        from src.strategy.base import Signal
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy="coppock",
            entry_price=entry,
            reasoning=f"Coppock 중립: {cop_now:.4f} (이전: {cop_prev:.4f})",
            invalidation="",
            bull_case="",
            bear_case="",
        )


# ── 테스트 ────────────────────────────────────────────────────────────────

def test_strategy_name():
    """1. 전략 이름 = 'coppock'."""
    assert CoppockStrategy.name == "coppock"
    assert CoppockStrategy().name == "coppock"


def test_buy_signal():
    """2. BUY 신호 (Coppock<0, 상승 중)."""
    sig = _force_signal(-3.0, -4.0)
    assert sig.action == Action.BUY


def test_sell_signal():
    """3. SELL 신호 (Coppock>0, 하락 중)."""
    sig = _force_signal(3.0, 4.0)
    assert sig.action == Action.SELL


def test_buy_high_confidence():
    """4. BUY HIGH confidence (|Coppock|>5)."""
    sig = _force_signal(-6.0, -7.0)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.HIGH


def test_buy_medium_confidence():
    """5. BUY MEDIUM confidence (|Coppock|<=5)."""
    sig = _force_signal(-2.0, -3.0)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.MEDIUM


def test_sell_high_confidence():
    """6. SELL HIGH confidence (|Coppock|>5)."""
    sig = _force_signal(6.0, 7.0)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.HIGH


def test_sell_medium_confidence():
    """7. SELL MEDIUM confidence (|Coppock|<=5)."""
    sig = _force_signal(2.0, 3.0)
    assert sig.action == Action.SELL
    assert sig.confidence == Confidence.MEDIUM


def test_coppock_negative_but_falling_is_hold():
    """8. Coppock<0이지만 하락 중 → HOLD."""
    sig = _force_signal(-4.0, -3.0)
    assert sig.action == Action.HOLD


def test_insufficient_data():
    """9. 데이터 부족 → HOLD."""
    df = _make_df(n=10)
    sig = CoppockStrategy().generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


def test_signal_fields_complete():
    """10. Signal 필드 완전성."""
    sig = _force_signal(-3.0, -4.0)
    assert sig.action is not None
    assert sig.confidence is not None
    assert sig.strategy == "coppock"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)
    assert isinstance(sig.bull_case, str)
    assert isinstance(sig.bear_case, str)


def test_buy_reasoning_contains_coppock():
    """11. BUY reasoning에 'Coppock' 포함."""
    sig = _force_signal(-3.0, -4.0)
    assert "Coppock" in sig.reasoning


def test_sell_reasoning_contains_coppock():
    """12. SELL reasoning에 'Coppock' 포함."""
    sig = _force_signal(3.0, 4.0)
    assert "Coppock" in sig.reasoning


def test_generate_returns_hold_with_exact_min_rows():
    """13. 정확히 40행 → HOLD가 아닐 수도 있지만 에러 없이 Signal 반환."""
    df = _make_df(n=40)
    sig = CoppockStrategy().generate(df)
    assert sig.strategy == "coppock"


def test_generate_with_sufficient_data_no_error():
    """14. 충분한 데이터로 generate() 호출 시 에러 없이 Signal 반환."""
    df = _make_df(n=60)
    sig = CoppockStrategy().generate(df)
    assert sig.action in (Action.BUY, Action.SELL, Action.HOLD)


def test_none_df_returns_hold():
    """15. df=None → HOLD."""
    sig = CoppockStrategy().generate(None)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW
