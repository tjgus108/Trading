"""
BbSqueezeStrategy 단위 테스트
- volume confirmation (HIGH / MEDIUM confidence)
- RSI 필터 (HOLD on overbought/oversold)
- 기존 squeeze release 로직
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.bb_squeeze import BbSqueezeStrategy
from src.strategy.base import Action, Confidence, Signal

_BB_PERIOD = 20
_PERCENTILE_WINDOW = 50
_MIN_ROWS = _BB_PERIOD + _PERCENTILE_WINDOW + 2  # 72


def _make_df(n: int, closes=None, volumes=None, rsi_values=None) -> pd.DataFrame:
    """
    BbSqueezeStrategy가 요구하는 컬럼이 포함된 DataFrame 생성.
    rsi14는 명시 없으면 중립값(50) 시리즈로 채움.
    """
    if closes is None:
        closes = [100.0 + i * 0.01 for i in range(n)]
    closes = list(closes)
    assert len(closes) == n

    if volumes is None:
        volumes = [1000.0] * n
    if rsi_values is None:
        rsi_values = [50.0] * n

    return pd.DataFrame({
        "open": closes,
        "high": [c + 0.5 for c in closes],
        "low":  [c - 0.5 for c in closes],
        "close": closes,
        "volume": volumes,
        "rsi14": rsi_values,
    })


def _make_squeeze_release_buy_df(vol_spike=True, rsi_at_last=50.0) -> pd.DataFrame:
    """
    BB squeeze + release + close > upper BB 조건.

    총 200봉을 사용하여 squeeze / release 조건을 확실하게 구성.
    - 앞 100봉: 큰 진동 (100 ↔ 120) → BB 폭 크게
    - 중간 80봉: flat 110 → BB 폭 매우 작음 (squeeze)
    - index n-3 (last_idx-1=prev_idx): flat 110 → squeeze 상태
    - index n-2 (last_idx): 급등 150 → squeeze release + close > upper
    - index n-1: 마지막 (현재 진행 중, 무시)
    """
    n = 200
    front = [100.0 + (i % 2) * 20.0 for i in range(100)]
    mid   = [110.0] * 97
    # index n-3 = 197: flat → squeeze
    # index n-2 = 198: 급등 150 → release (last_idx)
    # index n-1 = 199: dummy
    tail  = [110.0, 150.0, 150.0]
    closes = front + mid + tail
    assert len(closes) == n

    volumes = [1000.0] * n
    if vol_spike:
        volumes[n - 2] = 2500.0   # last_idx에 vol spike (> 1000*1.5=1500)
    else:
        volumes[n - 2] = 1000.0   # 평범한 volume (< 1500)

    rsi_values = [50.0] * n
    rsi_values[n - 2] = rsi_at_last

    return _make_df(n, closes=closes, volumes=volumes, rsi_values=rsi_values)


def _make_squeeze_release_sell_df(vol_spike=True, rsi_at_last=50.0) -> pd.DataFrame:
    """
    BB squeeze + release + close < lower BB 조건 (하락 버전).
    """
    n = 200
    front = [100.0 + (i % 2) * 20.0 for i in range(100)]
    mid   = [110.0] * 97
    tail  = [110.0, 70.0, 70.0]
    closes = front + mid + tail
    assert len(closes) == n

    volumes = [1000.0] * n
    if vol_spike:
        volumes[n - 2] = 2500.0
    else:
        volumes[n - 2] = 1000.0

    rsi_values = [50.0] * n
    rsi_values[n - 2] = rsi_at_last

    return _make_df(n, closes=closes, volumes=volumes, rsi_values=rsi_values)


class TestBbSqueezeStrategy:

    def setup_method(self):
        self.strategy = BbSqueezeStrategy()

    # ── 기본 ──────────────────────────────────────────────────────────────

    def test_name(self):
        assert self.strategy.name == "bb_squeeze"

    def test_insufficient_data_hold(self):
        df = _make_df(10)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    def test_signal_fields_complete(self):
        df = _make_df(_MIN_ROWS)
        sig = self.strategy.generate(df)
        for attr in ("action", "confidence", "strategy", "entry_price", "reasoning", "invalidation"):
            assert hasattr(sig, attr)
        assert sig.reasoning != ""

    def test_strategy_field(self):
        df = _make_df(_MIN_ROWS)
        sig = self.strategy.generate(df)
        assert sig.strategy == "bb_squeeze"

    def test_entry_price_is_float(self):
        df = _make_df(_MIN_ROWS)
        sig = self.strategy.generate(df)
        assert isinstance(sig.entry_price, float)

    def test_large_dataframe(self):
        df = _make_df(200)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)

    # ── Volume confirmation: HIGH confidence ──────────────────────────────

    def test_buy_high_confidence_with_vol_spike_and_low_rsi(self):
        """vol_spike=True, rsi=50 (< 60) → HIGH confidence BUY"""
        df = _make_squeeze_release_buy_df(vol_spike=True, rsi_at_last=50.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.HIGH

    def test_sell_high_confidence_with_vol_spike_and_mid_rsi(self):
        """vol_spike=True, rsi=50 (> 40) → HIGH confidence SELL"""
        df = _make_squeeze_release_sell_df(vol_spike=True, rsi_at_last=50.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.confidence == Confidence.HIGH

    # ── Volume confirmation: MEDIUM confidence ────────────────────────────

    def test_buy_medium_confidence_without_vol_spike(self):
        """vol_spike=False → MEDIUM confidence BUY"""
        df = _make_squeeze_release_buy_df(vol_spike=False, rsi_at_last=50.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.MEDIUM

    def test_sell_medium_confidence_without_vol_spike(self):
        """vol_spike=False → MEDIUM confidence SELL"""
        df = _make_squeeze_release_sell_df(vol_spike=False, rsi_at_last=50.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.confidence == Confidence.MEDIUM

    def test_buy_medium_confidence_high_rsi_but_vol_spike(self):
        """vol_spike=True, rsi=65 (>= 60) → MEDIUM (not HIGH)"""
        df = _make_squeeze_release_buy_df(vol_spike=True, rsi_at_last=65.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.MEDIUM

    def test_sell_medium_confidence_low_rsi_but_vol_spike(self):
        """vol_spike=True, rsi=35 (<= 40) → MEDIUM (not HIGH)"""
        df = _make_squeeze_release_sell_df(vol_spike=True, rsi_at_last=35.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.confidence == Confidence.MEDIUM

    # ── RSI 필터: HOLD ────────────────────────────────────────────────────

    def test_buy_blocked_by_rsi_overbought(self):
        """BUY 시그널이지만 rsi=76 (>= 75) → HOLD"""
        df = _make_squeeze_release_buy_df(vol_spike=True, rsi_at_last=76.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "blocked" in sig.reasoning.lower()

    def test_buy_blocked_at_rsi_boundary(self):
        """rsi=75 → HOLD (경계값)"""
        df = _make_squeeze_release_buy_df(vol_spike=True, rsi_at_last=75.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    def test_buy_not_blocked_just_below_boundary(self):
        """rsi=74.9 → BUY 허용"""
        df = _make_squeeze_release_buy_df(vol_spike=True, rsi_at_last=74.9)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY

    def test_sell_blocked_by_rsi_oversold(self):
        """SELL 시그널이지만 rsi=24 (<= 25) → HOLD"""
        df = _make_squeeze_release_sell_df(vol_spike=True, rsi_at_last=24.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "blocked" in sig.reasoning.lower()

    def test_sell_blocked_at_rsi_boundary(self):
        """rsi=25 → HOLD (경계값)"""
        df = _make_squeeze_release_sell_df(vol_spike=True, rsi_at_last=25.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    def test_sell_not_blocked_just_above_boundary(self):
        """rsi=25.1 → SELL 허용"""
        df = _make_squeeze_release_sell_df(vol_spike=True, rsi_at_last=25.1)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL

    # ── entry_price ───────────────────────────────────────────────────────

    def test_buy_entry_price_equals_last_close(self):
        df = _make_squeeze_release_buy_df(vol_spike=True, rsi_at_last=50.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.entry_price == float(df["close"].iloc[-2])

    def test_sell_entry_price_equals_last_close(self):
        df = _make_squeeze_release_sell_df(vol_spike=True, rsi_at_last=50.0)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.entry_price == float(df["close"].iloc[-2])

    # ── no squeeze → HOLD ─────────────────────────────────────────────────

    def test_hold_no_squeeze_flat_data(self):
        """완전 flat → squeeze release 없음 → HOLD"""
        closes = [100.0] * _MIN_ROWS
        df = _make_df(_MIN_ROWS, closes=closes)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
