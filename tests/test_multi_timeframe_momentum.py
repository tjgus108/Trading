"""MultiTimeframeMomentumStrategy 단위 테스트 (14개)."""

import numpy as np
import pandas as pd
import pytest

from src.strategy.multi_timeframe_momentum import MultiTimeframeMomentumStrategy
from src.strategy.base import Action, Confidence, Signal


def _make_df(n: int = 50, close_values=None, volume_values=None) -> pd.DataFrame:
    if close_values is not None:
        closes = list(close_values)
        n = len(closes)
    else:
        closes = [100.0 + i * 0.1 for i in range(n)]
    if volume_values is not None:
        volumes = list(volume_values)
    else:
        volumes = [1000.0] * n
    return pd.DataFrame({
        "open": closes,
        "high": [c + 1.0 for c in closes],
        "low": [c - 1.0 for c in closes],
        "close": closes,
        "volume": volumes,
    })


def _make_bull_df(n: int = 50) -> pd.DataFrame:
    """강한 상승 + 마지막 봉 거래량 높음 -> BUY 유도.

    vol_confirm = volume.iloc[idx] > volume.rolling(10).mean().iloc[idx]
    idx = n-2 = 48. rolling(10).mean() at idx 48 covers idx 39..48.
    따라서 idx 48의 볼륨이 idx 39..48 평균보다 높아야 함.
    -> idx 39..47은 낮게, idx 48만 높게 설정.
    """
    closes = [100.0 + i * 1.0 for i in range(n)]
    volumes = [500.0] * (n - 1) + [50000.0]  # 마지막(idx 49)만 높음 - but idx is n-2=48
    # idx 48이 높아야 하므로: idx 39..47 낮게, idx 48 높게
    volumes = [500.0] * n
    volumes[n - 2] = 50000.0  # idx 48
    return _make_df(close_values=closes, volume_values=volumes)


def _make_bear_df(n: int = 50) -> pd.DataFrame:
    """강한 하락 + 마지막 봉 거래량 높음 -> SELL 유도."""
    closes = [200.0 - i * 1.0 for i in range(n)]
    volumes = [500.0] * n
    volumes[n - 2] = 50000.0  # idx 48
    return _make_df(close_values=closes, volume_values=volumes)


# ── 테스트 ────────────────────────────────────────────────────────────────────

def test_strategy_name():
    """1. 전략 이름 확인."""
    assert MultiTimeframeMomentumStrategy.name == "multi_timeframe_momentum"
    assert MultiTimeframeMomentumStrategy().name == "multi_timeframe_momentum"


def test_instance_creation():
    """2. 인스턴스 생성."""
    strat = MultiTimeframeMomentumStrategy()
    assert strat is not None


def test_insufficient_data_hold():
    """3. 데이터 부족(< 30행) -> HOLD."""
    df = _make_df(n=10)
    sig = MultiTimeframeMomentumStrategy().generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


def test_insufficient_data_reasoning():
    """4. 데이터 부족 시 reasoning에 'Insufficient' 포함."""
    df = _make_df(n=10)
    sig = MultiTimeframeMomentumStrategy().generate(df)
    assert "Insufficient" in sig.reasoning or "insufficient" in sig.reasoning.lower()


def test_normal_data_returns_signal():
    """5. 정상 데이터 -> Signal 반환."""
    df = _make_df(n=50)
    sig = MultiTimeframeMomentumStrategy().generate(df)
    assert isinstance(sig, Signal)


def test_signal_fields_complete():
    """6. Signal 필드 완성."""
    df = _make_df(n=50)
    sig = MultiTimeframeMomentumStrategy().generate(df)
    assert isinstance(sig.action, Action)
    assert isinstance(sig.confidence, Confidence)
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)
    assert isinstance(sig.bull_case, str)
    assert isinstance(sig.bear_case, str)


def test_buy_signal_bull_trend():
    """7. 강한 상승 추세 + 높은 거래량 -> BUY."""
    df = _make_bull_df(n=50)
    sig = MultiTimeframeMomentumStrategy().generate(df)
    assert sig.action == Action.BUY


def test_sell_signal_bear_trend():
    """8. 강한 하락 추세 + 높은 거래량 -> SELL."""
    df = _make_bear_df(n=50)
    sig = MultiTimeframeMomentumStrategy().generate(df)
    assert sig.action == Action.SELL


def test_buy_strategy_field():
    """9. BUY 신호의 strategy 필드 값."""
    df = _make_bull_df(n=50)
    sig = MultiTimeframeMomentumStrategy().generate(df)
    assert sig.strategy == "multi_timeframe_momentum"


def test_entry_price_positive():
    """10. entry_price > 0."""
    df = _make_df(n=50)
    sig = MultiTimeframeMomentumStrategy().generate(df)
    assert sig.entry_price > 0


def test_vol_confirm_suppresses_signal():
    """11. 낮은 거래량 -> BUY/SELL 억제 (HOLD)."""
    # 상승 추세지만 낮은 볼륨 (평균보다 낮게)
    closes = [100.0 + i * 1.0 for i in range(50)]
    # 볼륨을 먼저 높게 설정 후 마지막 봉들만 낮게 -> 최근이 평균보다 낮음
    volumes = [5000.0] * 40 + [100.0] * 10
    df = _make_df(close_values=closes, volume_values=volumes)
    sig = MultiTimeframeMomentumStrategy().generate(df)
    # vol_confirm = False이므로 HOLD 또는 신호 없음
    assert sig.action == Action.HOLD


def test_minimum_rows_boundary():
    """12. 정확히 최소 행(30)에서 동작."""
    df = _make_df(n=30)
    sig = MultiTimeframeMomentumStrategy().generate(df)
    assert isinstance(sig, Signal)
    assert sig.strategy == "multi_timeframe_momentum"


def test_confidence_enum_values():
    """13. confidence는 HIGH/MEDIUM/LOW 중 하나."""
    df = _make_bull_df(n=50)
    sig = MultiTimeframeMomentumStrategy().generate(df)
    assert sig.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)


def test_hold_signal_has_strategy():
    """14. HOLD 신호도 strategy 필드 정상."""
    df = _make_df(n=50)
    sig = MultiTimeframeMomentumStrategy().generate(df)
    assert sig.strategy == "multi_timeframe_momentum"
