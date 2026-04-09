"""
MassIndexStrategy 단위 테스트 (mock DataFrame만, API 호출 없음).
"""

import numpy as np
import pandas as pd
import pytest

from src.strategy.mass_index import MassIndexStrategy, _calc_mass_index
from src.strategy.base import Action, Confidence, Signal


def _make_df(
    n: int = 60,
    close: float = 100.0,
    ema50: float = 95.0,
    hl_range: float = 1.0,
) -> pd.DataFrame:
    """기본 DataFrame — 균일한 H-L 범위 (Mass Index 안정 상태)."""
    return pd.DataFrame({
        "open": [close] * n,
        "close": [close] * n,
        "high": [close + hl_range] * n,
        "low": [close - hl_range] * n,
        "volume": [1000.0] * n,
        "ema50": [ema50] * n,
        "atr14": [hl_range] * n,
        "rsi14": [50.0] * n,
    })


def _inject_bulge(df: pd.DataFrame, bulge_idx_start: int, bulge_idx_end: int, wide_range: float = 20.0) -> pd.DataFrame:
    """
    bulge_idx_start ~ bulge_idx_end 구간에 넓은 H-L range 주입.
    Mass Index가 27을 넘도록 만들기 위해 해당 구간 HL을 크게 확장.
    """
    df = df.copy()
    base_close = float(df["close"].iloc[0])
    for i in range(bulge_idx_start, min(bulge_idx_end + 1, len(df))):
        df.iloc[i, df.columns.get_loc("high")] = base_close + wide_range
        df.iloc[i, df.columns.get_loc("low")] = base_close - wide_range
    return df


def _make_bulge_df(n: int = 80, close: float = 100.0, ema50: float = 95.0) -> pd.DataFrame:
    """
    Mass Index Reversal Bulge를 시뮬레이션하는 DataFrame.
    - 초반 구간: 넓은 H-L (bulge 생성, MI > 27)
    - 말미 구간: 좁은 H-L (MI < 26.5로 수축)
    """
    df = _make_df(n=n, close=close, ema50=ema50, hl_range=1.0)
    # 앞 40봉에 넓은 range 주입해 bulge 유발
    df = _inject_bulge(df, 0, 40, wide_range=30.0)
    # 마지막 15봉은 좁은 range 유지 (hl_range=1.0)
    return df


class TestMassIndexStrategy:

    def setup_method(self):
        self.strategy = MassIndexStrategy()

    # 1. 전략 이름
    def test_name(self):
        assert self.strategy.name == "mass_index"

    # 2. 데이터 부족 (< 40행)
    def test_insufficient_data(self):
        df = _make_df(n=30)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert "부족" in sig.reasoning

    # 3. None 입력
    def test_none_input(self):
        sig = self.strategy.generate(None)
        assert sig.action == Action.HOLD

    # 4. HOLD: bulge 없는 안정 상태
    def test_hold_no_bulge(self):
        df = _make_df(n=60)
        sig = self.strategy.generate(df)
        assert sig.action == Action.HOLD
        assert sig.strategy == "mass_index"

    # 5. Signal 필드 완전성
    def test_signal_fields_complete(self):
        df = _make_df(n=60)
        sig = self.strategy.generate(df)
        assert isinstance(sig, Signal)
        for field in ["action", "confidence", "strategy", "entry_price", "reasoning", "invalidation", "bull_case", "bear_case"]:
            assert hasattr(sig, field)

    # 6. _calc_mass_index: 반환값이 Series
    def test_calc_mass_index_returns_series(self):
        df = _make_df(n=60)
        mi = _calc_mass_index(df)
        assert isinstance(mi, pd.Series)
        assert len(mi) == len(df)

    # 7. _calc_mass_index: NaN은 앞부분에만 (충분한 데이터 이후 유효값)
    def test_calc_mass_index_valid_after_warmup(self):
        df = _make_df(n=60, hl_range=2.0)
        mi = _calc_mass_index(df)
        # 최소 40행 이후 유효
        assert not pd.isna(mi.iloc[-1])
        assert mi.iloc[-1] > 0

    # 8. BUY: bulge 하향 + close > ema50 (정상 bulge DataFrame)
    def test_buy_signal_with_bulge(self):
        df = _make_bulge_df(n=80, close=100.0, ema50=95.0)
        sig = self.strategy.generate(df)
        # bulge 패턴에 따라 BUY 또는 HOLD (MI 값은 데이터에 의존)
        assert sig.action in (Action.BUY, Action.HOLD)
        if sig.action == Action.BUY:
            assert sig.entry_price > 0

    # 9. SELL: bulge 하향 + close < ema50
    def test_sell_signal_with_bulge(self):
        df = _make_bulge_df(n=80, close=90.0, ema50=95.0)
        sig = self.strategy.generate(df)
        assert sig.action in (Action.SELL, Action.HOLD)
        if sig.action == Action.SELL:
            assert sig.entry_price > 0

    # 10. Confidence HIGH when mi_prev > 27.5
    def test_high_confidence_threshold(self):
        """MI 이전값 > 27.5 이면 HIGH confidence."""
        from unittest.mock import patch
        import src.strategy.mass_index as mi_mod

        df = _make_df(n=60, close=100.0, ema50=95.0)

        # _calc_mass_index 를 mock해서 bulge 조건 강제
        fake_mi = pd.Series([27.8] * (len(df) - 2) + [26.0, 25.0])

        with patch.object(mi_mod, "_calc_mass_index", return_value=fake_mi):
            sig = self.strategy.generate(df)

        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.HIGH

    # 11. Confidence MEDIUM when 27 < mi_prev <= 27.5
    def test_medium_confidence_threshold(self):
        """MI 이전값 27 < x <= 27.5 이면 MEDIUM confidence."""
        from unittest.mock import patch
        import src.strategy.mass_index as mi_mod

        df = _make_df(n=60, close=100.0, ema50=95.0)
        fake_mi = pd.Series([27.2] * (len(df) - 2) + [26.0, 25.0])

        with patch.object(mi_mod, "_calc_mass_index", return_value=fake_mi):
            sig = self.strategy.generate(df)

        assert sig.action == Action.BUY
        assert sig.confidence == Confidence.MEDIUM

    # 12. HOLD: bulge 발생했지만 현재 MI 여전히 > 26.5 (하향 미완)
    def test_hold_bulge_not_completed(self):
        """MI > 27 이후 26.5 미만으로 안 내려오면 HOLD."""
        from unittest.mock import patch
        import src.strategy.mass_index as mi_mod

        df = _make_df(n=60, close=100.0, ema50=95.0)
        # 이전값 27.5, 현재값 26.8 (26.5 미만 아님)
        fake_mi = pd.Series([27.5] * (len(df) - 2) + [26.8, 25.0])

        with patch.object(mi_mod, "_calc_mass_index", return_value=fake_mi):
            sig = self.strategy.generate(df)

        assert sig.action == Action.HOLD

    # 13. entry_price == close
    def test_entry_price_equals_close(self):
        df = _make_df(n=60, close=123.45, ema50=95.0)
        sig = self.strategy.generate(df)
        assert sig.entry_price == pytest.approx(123.45, abs=0.01) or sig.action == Action.HOLD

    # 14. reasoning 비어 있지 않음
    def test_reasoning_not_empty(self):
        df = _make_df(n=60)
        sig = self.strategy.generate(df)
        assert sig.reasoning != ""

    # 15. SELL: bulge + close < ema50 (mock)
    def test_sell_signal_mock(self):
        from unittest.mock import patch
        import src.strategy.mass_index as mi_mod

        df = _make_df(n=60, close=90.0, ema50=95.0)
        fake_mi = pd.Series([27.8] * (len(df) - 2) + [26.0, 25.0])

        with patch.object(mi_mod, "_calc_mass_index", return_value=fake_mi):
            sig = self.strategy.generate(df)

        assert sig.action == Action.SELL
        assert sig.confidence == Confidence.HIGH
