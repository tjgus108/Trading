"""
WickReversalStrategy v2: 긴 꼬리(wick)를 이용한 반전 감지.
개선 (Cycle 120): 선택적 강화 필터 (거래수 유지 + 품질 향상)
개선 (Cycle 250): ATR 기반 최소 변동성 필터 추가 (저변동성 구간 신호 차단)
개선 (Cycle 270): Shooting Star에 rsi < 70 추가 (강한 bull 레짐 억제)
개선 (Cycle 271): EMA 방향 필터 실험 → 역효과 (avg 1.200→-0.416), 롤백함
개선 (Cycle 272): ADX14 필터 추가 (adx14 < adx_threshold → 횡보 구간에서만 진입)
- ADX > 25 = 강한 트렌드 → wick 반전 패턴 신뢰 불가 (bull/bear run에서 차단)
- ADX < 25 = 약한/횡보 → wick 패턴 유효
- Hammer (lower_wick_ratio >= self.min_wick_ratio, close > SMA20*0.95, trend_up, vol_ok OR rsi<=70, adx14<adx_threshold) → BUY
- Shooting Star (upper_wick_ratio >= self.min_wick_ratio, close < SMA20*1.03, trend_down, rsi<70, vol_ok OR rsi>=30, adx14<adx_threshold) → SELL
- ATR 필터: atr/close < min_volatility(0.002) → HOLD (저변동성 차단)
"""

from typing import Optional

import numpy as np
import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


class WickReversalStrategy(BaseStrategy):
    name = "wick_reversal"

    def __init__(
        self,
        min_wick_ratio: float = 0.55,
        vol_mult: float = 0.8,
        sma_period: int = 20,
        trend_period: int = 14,
        min_volatility: float = 0.002,
        adx_threshold: float = 25.0,
        **kwargs,
    ):
        self.min_wick_ratio = min_wick_ratio
        self.vol_mult = vol_mult
        self.sma_period = sma_period
        self.trend_period = trend_period
        self.min_volatility = min_volatility
        self.adx_threshold = adx_threshold

    MIN_ROWS = 25

    def generate(self, df: Optional[pd.DataFrame]) -> Signal:
        hold = Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=0.0,
            reasoning="No signal",
            invalidation="",
            bull_case="",
            bear_case="",
        )

        if df is None or len(df) < 25:
            hold.reasoning = "데이터 부족"
            return hold

        last = self._last(df)
        entry = float(last["close"])
        hold.entry_price = entry

        high = float(last["high"])
        low = float(last["low"])
        open_ = float(last["open"])
        close = float(last["close"])
        volume = float(last["volume"])

        total_range = high - low
        if total_range == 0:
            hold.reasoning = "total_range=0, 캔들 이상"
            return hold

        lower_wick = min(open_, close) - low
        upper_wick = high - max(open_, close)

        lower_wick_ratio = lower_wick / total_range
        upper_wick_ratio = upper_wick / total_range

        # SMA20
        lookback = min(self.sma_period, len(df) - 1)
        sma20 = float(df["close"].iloc[-lookback - 1:-1].mean())

        # ATR 기반 최소 변동성 필터 (Cycle 250)
        atr_period = 14
        atr_lookback = min(atr_period, len(df) - 1)
        atr_slice = df.iloc[-atr_lookback - 1:-1]
        tr = pd.concat([
            atr_slice["high"] - atr_slice["low"],
            (atr_slice["high"] - atr_slice["close"].shift(1)).abs(),
            (atr_slice["low"] - atr_slice["close"].shift(1)).abs(),
        ], axis=1).max(axis=1)
        atr_val = float(tr.mean()) if len(tr) > 0 else 0.0
        atr_ratio = atr_val / close if close > 0 else 0.0

        if atr_ratio < self.min_volatility:
            hold.reasoning = (
                f"저변동성 필터: ATR14/close={atr_ratio:.6f} < min_volatility={self.min_volatility}"
            )
            return hold

        # 볼륨: 기존 기준 유지 (0.8배)
        vol_lookback = min(10, len(df) - 1)
        avg_vol_10 = float(df["volume"].iloc[-vol_lookback - 1:-1].mean())
        vol_ok = volume > avg_vol_10 * self.vol_mult

        # 추세 필터: 14기간 최고가/최저가 대비
        trend_lookback = min(self.trend_period, len(df) - 1)
        high_14 = float(df["high"].iloc[-trend_lookback - 1:-1].max())
        low_14 = float(df["low"].iloc[-trend_lookback - 1:-1].min())

        trend_up = high >= high_14 * 0.99
        trend_down = low <= low_14 * 1.01

        # RSI 14 (선택적 강화 조건)
        rsi = self._calculate_rsi(df, 14)

        # ADX 14 필터: 강한 트렌드 구간(ADX>threshold) 진입 차단 (Cycle 272)
        adx = self._calculate_adx(df, 14)
        adx_ok = adx < self.adx_threshold

        bull_case = (
            f"lower_wick_ratio={lower_wick_ratio:.3f}, "
            f"close={close:.4f}, SMA20={sma20:.4f}, "
            f"vol={volume:.1f}, avg_vol10={avg_vol_10:.1f}, trend_up={trend_up}, rsi={rsi:.1f}, "
            f"adx14={adx:.1f}(<{self.adx_threshold}={adx_ok})"
        )
        bear_case = (
            f"upper_wick_ratio={upper_wick_ratio:.3f}, "
            f"close={close:.4f}, SMA20={sma20:.4f}, "
            f"vol={volume:.1f}, avg_vol10={avg_vol_10:.1f}, trend_down={trend_down}, rsi={rsi:.1f}, "
            f"adx14={adx:.1f}(<{self.adx_threshold}={adx_ok})"
        )

        # Hammer: BUY
        # 기본: lower_wick_ratio >= self.min_wick_ratio + trend_up + close > SMA20*0.95
        # 강화: + (vol_ok OR rsi <= 70) + adx14 < adx_threshold (Cycle 272: 횡보 구간만)
        hammer = (
            lower_wick_ratio >= self.min_wick_ratio and
            close > sma20 * 0.95 and  # Cycle 267: 0.97→0.95 완화, 하락 추세 구간 신호 빈도 개선
            trend_up and
            (vol_ok or rsi <= 70) and
            adx_ok
        )
        if hammer:
            confidence = Confidence.HIGH if lower_wick_ratio > 0.7 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Hammer 패턴 (v2): lower_wick_ratio={lower_wick_ratio:.3f} >= 0.65, "
                    f"close({close:.4f}) > SMA20*0.95({sma20*0.95:.4f}), trend_up={trend_up}, "
                    f"(vol_ok={vol_ok} OR rsi={rsi:.1f}<=70)"
                ),
                invalidation=f"Close below SMA20*0.95 ({sma20*0.95:.4f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        # Shooting Star: SELL
        # 기본: upper_wick_ratio >= self.min_wick_ratio + trend_down + close < SMA20*1.03
        # 강화: + rsi < 70 (Cycle 270: 강한 bull 레짐 억제 — Q4 bull 구간 오신호 차단)
        #       + (vol_ok OR rsi >= 30) + adx14 < adx_threshold (Cycle 272: 횡보 구간만)
        shooting_star = (
            upper_wick_ratio >= self.min_wick_ratio and
            close < sma20 * 1.03 and
            trend_down and
            rsi < 70 and
            (vol_ok or rsi >= 30) and
            adx_ok
        )
        if shooting_star:
            confidence = Confidence.HIGH if upper_wick_ratio > 0.7 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Shooting Star 패턴 (v2): upper_wick_ratio={upper_wick_ratio:.3f} >= 0.65, "
                    f"close({close:.4f}) < SMA20*1.03({sma20*1.03:.4f}), trend_down={trend_down}, "
                    f"(vol_ok={vol_ok} OR rsi={rsi:.1f}>=30)"
                ),
                invalidation=f"Close above SMA20*1.03 ({sma20*1.03:.4f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        hold.reasoning = (
            f"패턴 없음: lower_wick_ratio={lower_wick_ratio:.3f}, "
            f"upper_wick_ratio={upper_wick_ratio:.3f}, vol_ok={vol_ok}, "
            f"trend_up={trend_up}, trend_down={trend_down}, rsi={rsi:.1f}, "
            f"adx14={adx:.1f}(ok={adx_ok})"
        )
        hold.bull_case = bull_case
        hold.bear_case = bear_case
        return hold

    def _calculate_adx(self, df: pd.DataFrame, period: int = 14) -> float:
        """Wilder ADX14 계산. 데이터 부족 시 0.0 반환 (필터 통과)."""
        n = len(df)
        if n < period + 2:
            return 0.0
        high = df["high"]
        low = df["low"]
        close = df["close"]
        prev_close = close.shift(1)
        prev_high = high.shift(1)
        prev_low = low.shift(1)

        tr = pd.concat([
            high - low,
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ], axis=1).max(axis=1)

        plus_dm = (high - prev_high).clip(lower=0)
        minus_dm = (prev_low - low).clip(lower=0)
        # +DM이 -DM보다 크지 않으면 0
        plus_dm = plus_dm.where(plus_dm > minus_dm, 0.0)
        minus_dm = minus_dm.where(minus_dm > plus_dm.where(plus_dm > minus_dm, 0.0).shift(-1).fillna(0), 0.0)
        # 재계산: 중복 방지
        raw_plus = (high - prev_high).clip(lower=0)
        raw_minus = (prev_low - low).clip(lower=0)
        cond = raw_plus > raw_minus
        plus_dm_clean = raw_plus.where(cond, 0.0)
        minus_dm_clean = raw_minus.where(~cond, 0.0)

        alpha = 1.0 / period
        atr_s = tr.ewm(alpha=alpha, adjust=False).mean()
        plus_di = 100.0 * plus_dm_clean.ewm(alpha=alpha, adjust=False).mean() / atr_s.replace(0, np.nan)
        minus_di = 100.0 * minus_dm_clean.ewm(alpha=alpha, adjust=False).mean() / atr_s.replace(0, np.nan)

        di_sum = plus_di + minus_di
        dx = (100.0 * (plus_di - minus_di).abs() / di_sum.replace(0, np.nan)).fillna(0.0)
        adx_series = dx.ewm(alpha=alpha, adjust=False).mean()
        val = float(adx_series.iloc[-1])
        return 0.0 if np.isnan(val) else val

    def _calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> float:
        """RSI 계산."""
        if len(df) < period + 1:
            return 50.0
        delta = df["close"].diff()
        gain = delta.clip(lower=0).rolling(period).mean()
        loss = (-delta.clip(upper=0)).rolling(period).mean()
        rs = gain / loss.replace(0, np.nan)
        rsi = 100 - (100 / (1 + rs))
        val = float(rsi.iloc[-1])
        return 50.0 if np.isnan(val) else val
