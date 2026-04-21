"""
RegimeDetector (src/ml/regime_detector.py) 단위 테스트.

시나리오:
  1. TREND→RANGE 전환
  2. RANGE→CRISIS 전환
  3. 2봉 미만 거짓 전환 무시
  4. CRISIS 포지션 스케일 = 0.5
"""

import numpy as np
import pandas as pd
import pytest

from src.ml.regime_detector import RegimeDetector


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_ohlcv(n: int, base_price: float = 100.0,
                high_mult: float = 1.01, low_mult: float = 0.99,
                atr_scale: float = 1.0, trend: bool = False) -> pd.DataFrame:
    """단순 OHLCV 생성. atr_scale로 변동폭 조정."""
    np.random.seed(42)
    close = np.full(n, base_price) + np.random.randn(n) * 0.01
    if trend:
        close = np.linspace(base_price, base_price * 1.30, n)

    high = close * high_mult * atr_scale + close * (1 - atr_scale)
    low = close * low_mult / atr_scale + close * (1 - 1 / atr_scale) if atr_scale != 1.0 else close * low_mult
    # simpler: high/low spread scaled
    spread = (close * 0.01) * atr_scale
    high = close + spread
    low = close - spread

    return pd.DataFrame({
        "open": close * 0.999,
        "high": high,
        "low": low,
        "close": close,
        "volume": np.ones(n) * 1000,
    })


def _inject_crisis(df: pd.DataFrame, start: int, multiplier: float = 5.0) -> pd.DataFrame:
    """start 인덱스부터 ATR을 크게 키워 CRISIS 조건 유발."""
    df = df.copy()
    base_spread = (df["close"].iloc[:start] * 0.01).mean()
    df.loc[df.index[start:], "high"] = df["close"].iloc[start:] + base_spread * multiplier
    df.loc[df.index[start:], "low"] = df["close"].iloc[start:] - base_spread * multiplier
    return df


# ── tests ─────────────────────────────────────────────────────────────────────

class TestRegimeDetectorBasic:

    def test_detect_returns_valid_regime(self):
        """detect()가 유효한 레짐 문자열을 반환해야 함."""
        df = _make_ohlcv(100)
        rd = RegimeDetector()
        result = rd.detect(df)
        assert result in ("TREND", "RANGE", "CRISIS")

    def test_insufficient_data_returns_default(self):
        """데이터 부족 시 디폴트 레짐(RANGE) 반환."""
        df = _make_ohlcv(10)
        rd = RegimeDetector()
        result = rd.detect(df)
        assert result == "RANGE"

    def test_none_df_returns_default(self):
        """None 입력 시 디폴트 레짐 반환."""
        rd = RegimeDetector()
        assert rd.detect(None) == "RANGE"

    def test_get_history_empty_at_start(self):
        """초기 상태에서 히스토리는 비어있어야 함."""
        rd = RegimeDetector()
        assert rd.get_history() == []


class TestPositionScale:

    def test_crisis_scale_is_half(self):
        """CRISIS 레짐의 포지션 스케일은 0.5."""
        assert RegimeDetector.get_position_scale("CRISIS") == 0.5

    def test_trend_scale_is_one(self):
        assert RegimeDetector.get_position_scale("TREND") == 1.0

    def test_range_scale_is_one(self):
        assert RegimeDetector.get_position_scale("RANGE") == 1.0

    def test_unknown_regime_defaults_to_one(self):
        assert RegimeDetector.get_position_scale("UNKNOWN") == 1.0


class TestStateMachineConfirmBars:

    def test_false_transition_ignored_with_single_bar(self):
        """confirm_bars=2: 1봉만 조건 충족 시 상태 유지 (거짓 전환 무시)."""
        rd = RegimeDetector(confirm_bars=2)
        rd._current_regime = "RANGE"

        # 첫 번째 봉 — CRISIS 후보 등록, pending_count=1
        rd._update_state("CRISIS", index=0)
        assert rd._current_regime == "RANGE"   # 아직 전환 안 됨
        assert rd._pending_count == 1
        assert rd._pending_regime == "CRISIS"

    def test_transition_after_confirm_bars(self):
        """confirm_bars=2: 2봉 연속 조건 충족 시 상태 전환."""
        rd = RegimeDetector(confirm_bars=2)
        rd._current_regime = "RANGE"
        rd._pending_regime = "CRISIS"
        rd._pending_count = 1

        # 두 번째 봉 — 전환 발생해야 함
        rd._update_state("CRISIS", index=99)
        assert rd._current_regime == "CRISIS"

    def test_pending_reset_on_different_candidate(self):
        """후보 레짐이 바뀌면 pending_count 리셋."""
        rd = RegimeDetector(confirm_bars=2)
        rd._current_regime = "RANGE"
        rd._pending_regime = "CRISIS"
        rd._pending_count = 1

        rd._update_state("TREND")  # 다른 후보
        assert rd._pending_count == 1
        assert rd._pending_regime == "TREND"

    def test_pending_reset_on_same_as_current(self):
        """후보가 현재 레짐과 같으면 pending 클리어."""
        rd = RegimeDetector(confirm_bars=2)
        rd._current_regime = "TREND"
        rd._pending_regime = "RANGE"
        rd._pending_count = 1

        rd._update_state("TREND")
        assert rd._pending_count == 0
        assert rd._pending_regime is None


class TestTrendToRangeTransition:

    def test_trend_to_range_history_recorded(self):
        """TREND→RANGE 전환 시 히스토리에 기록."""
        rd = RegimeDetector(confirm_bars=2)
        rd._current_regime = "TREND"

        # 강제로 2번 연속 RANGE 후보 투입
        rd._update_state("RANGE", index=10)
        rd._update_state("RANGE", index=11)

        history = rd.get_history()
        assert len(history) == 1
        assert history[0]["from"] == "TREND"
        assert history[0]["to"] == "RANGE"

    def test_history_immutable_copy(self):
        """get_history()는 내부 리스트의 복사본 반환."""
        rd = RegimeDetector(confirm_bars=2)
        h1 = rd.get_history()
        h1.append({"dummy": True})
        assert len(rd.get_history()) == 0


class TestRangeToCrisisTransition:

    def test_range_to_crisis_transition(self):
        """RANGE→CRISIS 전환 시나리오."""
        rd = RegimeDetector(confirm_bars=2)
        rd._current_regime = "RANGE"

        rd._update_state("CRISIS", index=20)
        rd._update_state("CRISIS", index=21)

        assert rd._current_regime == "CRISIS"
        history = rd.get_history()
        assert history[-1]["from"] == "RANGE"
        assert history[-1]["to"] == "CRISIS"


class TestCrisisModePositionScale:

    def test_crisis_detect_and_scale(self):
        """CRISIS 레짐 감지 후 포지션 스케일 0.5 확인."""
        # CRISIS로 강제 전환
        rd = RegimeDetector(confirm_bars=2)
        rd._current_regime = "RANGE"
        rd._update_state("CRISIS", index=0)
        rd._update_state("CRISIS", index=1)

        regime = rd._current_regime
        scale = RegimeDetector.get_position_scale(regime)
        assert regime == "CRISIS"
        assert scale == 0.5
