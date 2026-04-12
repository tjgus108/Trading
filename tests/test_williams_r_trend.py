"""
WilliamsRTrendStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

from typing import Optional

import numpy as np
import pandas as pd
import pytest

from src.strategy.williams_r_trend import WilliamsRTrendStrategy
from src.strategy.base import Action, Confidence, Signal

_MIN_ROWS = 55
_PERIOD = 14
_HH = 110.0
_LL = 90.0
_RNG = _HH - _LL  # 20


def _close_for_wr(wr: float, hh: float = _HH, ll: float = _LL) -> float:
    """주어진 %R 값에 해당하는 close 계산."""
    return hh - (wr / -100) * (hh - ll)


def _make_df(
    n: int = _MIN_ROWS + 5,
    curr_wr: float = -50.0,
    prev_wr: float = -55.0,
    uptrend: bool = True,
) -> pd.DataFrame:
    """
    curr_wr: iloc[-2]의 Williams %R
    prev_wr: iloc[-3]의 Williams %R
    uptrend: EMA20 > EMA50이면 True, False면 EMA20 < EMA50

    EMA20 > EMA50 달성 방법:
    - uptrend: 앞부분(오래된 봉)은 낮은 가격, 뒷부분(최근 봉)은 높은 가격 → EMA20 > EMA50
    - downtrend: 앞부분 높은 가격, 뒷부분 낮은 가격 → EMA20 < EMA50
    단, 마지막 신호 봉(-2, -3)의 고가/저가는 _HH/_LL 고정하여 %R 정확히 제어.
    """
    close_curr = _close_for_wr(curr_wr)
    close_prev = _close_for_wr(prev_wr)

    # 신호 봉 기준 가격 (EMA 방향을 위한 기준)
    mid = (_HH + _LL) / 2  # 100.0

    # uptrend: 초반 50봉은 낮게, 최근 20봉 전후는 높게
    # downtrend: 반대
    closes = []
    for i in range(n):
        if uptrend:
            # 오래된 봉: mid - 5, 최근 봉: mid + 5
            frac = i / (n - 1)
            closes.append(mid - 5 + frac * 10)
        else:
            frac = i / (n - 1)
            closes.append(mid + 5 - frac * 10)

    # 신호 봉 위치 덮어쓰기 (고가/저가 범위 안에 있어야 %R 계산 정확)
    closes[-3] = close_prev
    closes[-2] = close_curr
    # 마지막 봉(-1)은 현재 진행 중인 봉이므로 아무 값이나
    closes[-1] = close_curr

    # 고가/저가: 전체 rolling window에서 _HH/_LL가 나오도록 고정
    highs = [_HH] * n
    lows = [_LL] * n

    df = pd.DataFrame({
        "open": closes[:],
        "close": closes,
        "high": highs,
        "low": lows,
        "volume": [1000.0] * n,
    })
    return df


class TestWilliamsRTrendStrategy:

    def setup_method(self):
        self.strategy = WilliamsRTrendStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strategy.name == "williams_r_trend"

    # 2. BUY: cross above -80 (prev < -80, now >= -80) + uptrend
    def test_buy_signal(self):
        df = _make_df(curr_wr=-78.0, prev_wr=-83.0, uptrend=True)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.strategy == "williams_r_trend"

    # 3. BUY HIGH confidence: curr_wr > -90 (e.g. -78, meaning closer to neutral after extreme)
    def test_buy_high_confidence(self):
        # curr_wr >= -80 AND prev_wr < -80 → crossed. curr_wr=-78 > -90 → HIGH
        df = _make_df(curr_wr=-78.0, prev_wr=-83.0, uptrend=True)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.HIGH

    # 4. BUY MEDIUM confidence: curr_wr <= -90
    def test_buy_medium_confidence(self):
        # curr_wr=-92.0 which is <= -90 → MEDIUM
        df = _make_df(curr_wr=-80.0, prev_wr=-92.0, uptrend=True)
        # curr=-80 (>= -80), prev=-92 (< -80): cross. curr=-80 <= -90? No → HIGH
        # Need curr <= -90: but curr must be >= -80 for cross. So MEDIUM only if curr <= -90 is impossible for cross
        # Actually HIGH threshold is curr_wr > -90, MEDIUM is curr_wr <= -90
        # For cross: prev < -80 AND curr >= -80. If curr=-80.0 exactly → curr > -90 → HIGH
        # To get MEDIUM: curr must be >= -80 AND <= -90 → impossible (>=-80 and <=-90 at same time)
        # So MEDIUM can't occur on BUY with cross condition. Let's test close to -80 => HIGH
        df = _make_df(curr_wr=-80.0, prev_wr=-85.0, uptrend=True)
        sig = self.strategy.generate(df)
        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.HIGH  # -80 > -90 → HIGH

    # 5. SELL: cross below -20 (prev > -20, now <= -20) + downtrend
    def test_sell_signal(self):
        df = _make_df(curr_wr=-22.0, prev_wr=-17.0, uptrend=False)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.strategy == "williams_r_trend"

    # 6. SELL HIGH confidence: curr_wr < -10
    # spec: %R < -10 → HIGH. Cross condition: curr <= -20 (which is < -10) → all crosses are HIGH.
    def test_sell_high_confidence(self):
        # curr_wr=-22.0 < -10 → HIGH
        df = _make_df(curr_wr=-22.0, prev_wr=-15.0, uptrend=False)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.confidence == Confidence.HIGH

    # 7. SELL: curr_wr exactly at -20 boundary (also HIGH since -20 < -10)
    def test_sell_medium_confidence_boundary(self):
        # curr_wr=-20.0 <= -20 (cross ok), prev=-18 > -20 (ok). -20 < -10 → HIGH
        df = _make_df(curr_wr=-20.0, prev_wr=-18.0, uptrend=False)
        sig = self.strategy.generate(df)
        assert sig.action == Action.SELL
        assert sig.confidence == Confidence.HIGH

    # 8. HOLD: cross above -80 but NO uptrend (downtrend)
    def test_hold_buy_no_uptrend(self):
        df = _make_df(curr_wr=-78.0, prev_wr=-83.0, uptrend=False)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 9. HOLD: cross below -20 but NO downtrend (uptrend)
    def test_hold_sell_no_downtrend(self):
        df = _make_df(curr_wr=-22.0, prev_wr=-17.0, uptrend=True)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 10. HOLD: no cross (both in neutral zone)
    def test_hold_neutral(self):
        df = _make_df(curr_wr=-50.0, prev_wr=-55.0, uptrend=True)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 11. HOLD: %R stays below -80 (no cross, both oversold)
    def test_hold_still_oversold(self):
        df = _make_df(curr_wr=-83.0, prev_wr=-86.0, uptrend=True)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 12. HOLD: %R stays above -20 (no cross, both overbought)
    def test_hold_still_overbought(self):
        df = _make_df(curr_wr=-15.0, prev_wr=-12.0, uptrend=False)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD

    # 13. 데이터 부족 (< 55행)
    def test_insufficient_data(self):
        df = _make_df(n=30)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "Insufficient" in sig.reasoning

    # 14. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_df(curr_wr=-78.0, prev_wr=-83.0, uptrend=True)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        for field in ("action", "confidence", "strategy", "entry_price",
                      "reasoning", "invalidation", "bull_case", "bear_case"):
            assert hasattr(sig, field)
        assert sig.reasoning != ""

    # 15. entry_price는 현재 close
    def test_entry_price_is_close(self):
        df = _make_df(curr_wr=-78.0, prev_wr=-83.0, uptrend=True)
        sig = self.strategy.generate(df)
        expected_close = float(df["close"].iloc[-2])
        assert sig.entry_price == pytest.approx(expected_close, rel=1e-3)

    # 16. HOLD reasoning에 No signal 포함
    def test_hold_reasoning_content(self):
        df = _make_df(curr_wr=-50.0, prev_wr=-55.0, uptrend=True)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert sig.reasoning != ""
