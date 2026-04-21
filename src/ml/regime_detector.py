"""
RegimeDetector: ADX(14) + ATR(20) 기반 상태머신으로 시장 레짐 감지.

레짐:
  TREND  — ADX > 25
  RANGE  — ATR < MA(ATR,20) AND ADX < 20
  CRISIS — ATR > 2 * MA(ATR,20)
  default — 이전 상태 유지 (위 조건 모두 불충족)

상태 전환 조건: 최소 2봉 연속 동일 조건 충족 (거짓 전환 방지).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from typing import List, Optional


REGIMES = ("TREND", "RANGE", "CRISIS")
DEFAULT_REGIME = "RANGE"


class RegimeDetector:
    """ADX/ATR 기반 상태머신 레짐 감지기."""

    # ── position scale per regime ─────────────────────────────────────────────
    _SCALE = {"TREND": 1.0, "RANGE": 1.0, "CRISIS": 0.5}

    def __init__(
        self,
        adx_period: int = 14,
        atr_period: int = 20,
        atr_ma_period: int = 20,
        confirm_bars: int = 2,
    ) -> None:
        self.adx_period = adx_period
        self.atr_period = atr_period
        self.atr_ma_period = atr_ma_period
        self.confirm_bars = confirm_bars

        self._current_regime: str = DEFAULT_REGIME
        self._pending_regime: Optional[str] = None
        self._pending_count: int = 0
        self._history: List[dict] = []

    # ── public interface ──────────────────────────────────────────────────────

    def detect(self, df: pd.DataFrame) -> str:
        """OHLCV DataFrame을 받아 현재 레짐 문자열 반환."""
        if df is None or len(df) < max(self.adx_period + 1, self.atr_period + self.atr_ma_period):
            return self._current_regime

        adx = self._calc_adx(df)
        atr = self._calc_atr(df)
        atr_ma = atr.rolling(self.atr_ma_period, min_periods=self.atr_ma_period).mean()

        adx_last = float(adx.iloc[-1]) if not np.isnan(adx.iloc[-1]) else 0.0
        atr_last = float(atr.iloc[-1]) if not np.isnan(atr.iloc[-1]) else 0.0
        atr_ma_last = float(atr_ma.iloc[-1]) if not np.isnan(atr_ma.iloc[-1]) else 0.0

        candidate = self._classify(adx_last, atr_last, atr_ma_last)
        self._update_state(candidate, index=df.index[-1])
        return self._current_regime

    def get_history(self) -> List[dict]:
        """레짐 전환 히스토리 반환. 각 항목: {index, from, to}"""
        return list(self._history)

    @classmethod
    def get_position_scale(cls, regime: str) -> float:
        """레짐별 포지션 스케일 반환."""
        return cls._SCALE.get(regime, 1.0)

    # ── private helpers ───────────────────────────────────────────────────────

    def _classify(self, adx: float, atr: float, atr_ma: float) -> Optional[str]:
        """현재 지표값으로 레짐 후보 반환. 조건 불충족 시 None(이전 유지)."""
        if atr_ma > 0 and atr > 2.0 * atr_ma:
            return "CRISIS"
        if adx > 25:
            return "TREND"
        if atr_ma > 0 and atr < atr_ma and adx < 20:
            return "RANGE"
        return None  # 이전 상태 유지

    def _update_state(self, candidate: Optional[str], index=None) -> None:
        """confirm_bars 연속 동일 후보일 때만 상태 전환."""
        if candidate is None or candidate == self._current_regime:
            self._pending_regime = None
            self._pending_count = 0
            return

        if candidate == self._pending_regime:
            self._pending_count += 1
        else:
            self._pending_regime = candidate
            self._pending_count = 1

        if self._pending_count >= self.confirm_bars:
            prev = self._current_regime
            self._current_regime = candidate
            self._history.append({"index": index, "from": prev, "to": candidate})
            self._pending_regime = None
            self._pending_count = 0

    # ── indicator calculations ─────────────────────────────────────────────────

    def _calc_atr(self, df: pd.DataFrame) -> pd.Series:
        high = df["high"]
        low = df["low"]
        close = df["close"]
        prev_close = close.shift(1)
        tr = pd.concat(
            [high - low, (high - prev_close).abs(), (low - prev_close).abs()],
            axis=1,
        ).max(axis=1)
        atr = tr.ewm(span=self.atr_period, adjust=False, min_periods=self.atr_period).mean()
        return atr

    def _calc_adx(self, df: pd.DataFrame) -> pd.Series:
        high = df["high"]
        low = df["low"]
        close = df["close"]
        period = self.adx_period

        # True Range
        prev_close = close.shift(1)
        tr = pd.concat(
            [high - low, (high - prev_close).abs(), (low - prev_close).abs()],
            axis=1,
        ).max(axis=1)

        # Directional Movement
        up_move = high.diff()
        down_move = -low.diff()
        plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
        minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)

        plus_dm_s = pd.Series(plus_dm, index=df.index)
        minus_dm_s = pd.Series(minus_dm, index=df.index)

        # Wilder smoothing (EWM with alpha=1/period)
        atr_s = tr.ewm(alpha=1.0 / period, adjust=False, min_periods=period).mean()
        plus_di = 100 * plus_dm_s.ewm(alpha=1.0 / period, adjust=False, min_periods=period).mean() / atr_s.replace(0, np.nan)
        minus_di = 100 * minus_dm_s.ewm(alpha=1.0 / period, adjust=False, min_periods=period).mean() / atr_s.replace(0, np.nan)

        dx = (100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan))
        adx = dx.ewm(alpha=1.0 / period, adjust=False, min_periods=period).mean()
        return adx
