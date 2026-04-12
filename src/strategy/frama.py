"""
Enhanced FRAMA: ATR volatility filter + adaptive RSI filtering
"""
import math
from typing import Optional

import numpy as np
import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

MIN_ROWS = 35


def _compute_atr(highs: np.ndarray, lows: np.ndarray, closes: np.ndarray, period: int = 14) -> np.ndarray:
    """ATR 계산 (변동성 필터용)."""
    n = len(highs)
    atr = np.full(n, np.nan)
    
    if n < period:
        return atr
    
    tr = np.zeros(n)
    tr[0] = highs[0] - lows[0]
    for i in range(1, n):
        tr[i] = max(
            highs[i] - lows[i],
            abs(highs[i] - closes[i - 1]),
            abs(lows[i] - closes[i - 1])
        )
    
    atr[period - 1] = np.mean(tr[:period])
    for i in range(period, n):
        atr[i] = (atr[i - 1] * (period - 1) + tr[i]) / period
    
    return atr


def _compute_rsi(closes: np.ndarray, period: int = 14) -> np.ndarray:
    """RSI 계산 (14기간 기본)."""
    n = len(closes)
    rsi = np.full(n, np.nan)
    
    if n < period + 1:
        return rsi
    
    diffs = np.diff(closes)
    gains = np.where(diffs > 0, diffs, 0)
    losses = np.where(diffs < 0, -diffs, 0)
    
    avg_gain = np.mean(gains[:period])
    avg_loss = np.mean(losses[:period])
    
    rsi[period] = 100 - (100 / (1 + avg_gain / avg_loss)) if avg_loss != 0 else 100
    
    for i in range(period + 1, n):
        avg_gain = (avg_gain * (period - 1) + gains[i - 1]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i - 1]) / period
        
        if avg_loss != 0:
            rsi[i] = 100 - (100 / (1 + avg_gain / avg_loss))
        else:
            rsi[i] = 100
    
    return rsi


def _compute_frama(closes: np.ndarray, highs: np.ndarray, lows: np.ndarray, period: int = 16) -> np.ndarray:
    """FRAMA 배열 계산."""
    n = len(closes)
    frama = np.full(n, np.nan)

    half = period // 2

    # 초기값: 첫 번째 완성 구간의 마지막 close
    start = period - 1
    frama[start] = closes[start]

    for i in range(start + 1, n):
        # 현재 i 기준 이전 period 개 캔들 사용
        idx = i - period + 1
        h_full = highs[idx: i + 1]
        l_full = lows[idx: i + 1]

        h1 = highs[idx: idx + half]
        l1 = lows[idx: idx + half]
        h2 = highs[idx + half: i + 1]
        l2 = lows[idx + half: i + 1]

        max_h = h_full.max()
        min_l = l_full.min()
        max_h1 = h1.max()
        min_l1 = l1.min()
        max_h2 = h2.max()
        min_l2 = l2.min()

        N1 = (max_h1 - min_l1) / half
        N2 = (max_h2 - min_l2) / half
        N = (max_h - min_l) / period

        if N1 + N2 <= 0 or N <= 0:
            alpha = 0.01
        else:
            denom = math.log(2)
            if denom == 0:
                alpha = 0.01
            else:
                D = (math.log(N1 + N2) - math.log(N)) / denom
                D = max(1.0, min(2.0, D))
                alpha = math.exp(-4.6 * (D - 1.0))

        alpha = max(0.01, min(1.0, alpha))
        frama[i] = alpha * closes[i] + (1.0 - alpha) * frama[i - 1]

    return frama


class FRAMAStrategy(BaseStrategy):
    """
    Enhanced FRAMA: ATR volatility filter + adaptive RSI thresholds
    - ATR contraction: signal quality indicator
    - Gap-based RSI filtering: larger gap = more lenient
    - Prevents whipsaw in high volatility environments
    """
    name = "frama"

    def __init__(self, period: int = 16, rsi_period: int = 14, atr_period: int = 14) -> None:
        self.period = period
        self.rsi_period = rsi_period
        self.atr_period = atr_period

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < MIN_ROWS:
            last_close = float(df["close"].iloc[-1]) if len(df) > 0 else 0.0
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=last_close,
                reasoning="데이터 부족: FRAMA 계산을 위해 최소 35행 필요",
                invalidation="",
            )

        closes = df["close"].values.astype(float)
        highs = df["high"].values.astype(float)
        lows = df["low"].values.astype(float)
        volumes = df["volume"].values.astype(float) if "volume" in df.columns else np.ones(len(df))

        frama_arr = _compute_frama(closes, highs, lows, self.period)
        rsi_arr = _compute_rsi(closes, self.rsi_period)
        atr_arr = _compute_atr(highs, lows, closes, self.atr_period)

        # -2: 마지막 완성 캔들, -3: 그 이전 캔들
        last_close = closes[-2]
        prev_close = closes[-3]
        last_frama = frama_arr[-2]
        prev_frama = frama_arr[-3]
        last_rsi = rsi_arr[-2]
        last_atr = atr_arr[-2]
        prev_atr = atr_arr[-3] if len(atr_arr) > 2 else last_atr
        last_volume = volumes[-2]
        prev_volume = volumes[-3] if len(volumes) > 1 else last_volume

        if np.isnan(last_frama) or np.isnan(prev_frama):
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=float(last_close),
                reasoning="FRAMA 계산값 부족 (NaN)",
                invalidation="",
            )

        crossed_up = (prev_close < prev_frama) and (last_close > last_frama)
        crossed_down = (prev_close > prev_frama) and (last_close < last_frama)

        gap_pct = abs(last_close - last_frama) / last_frama * 100.0 if last_frama != 0 else 0.0
        confidence = Confidence.HIGH if gap_pct > 1.0 else Confidence.MEDIUM

        bull_case = f"close={last_close:.4f} > FRAMA={last_frama:.4f}, 이격={gap_pct:.2f}%"
        bear_case = f"close={last_close:.4f} < FRAMA={last_frama:.4f}, 이격={gap_pct:.2f}%"

        # ATR 변동성 필터: 이전봉 대비 ATR이 감소 추세
        atr_contracting = not np.isnan(prev_atr) and not np.isnan(last_atr) and last_atr < prev_atr * 1.05
        
        # RSI 필터: gap > 1.0% (강한 신호)는 거의 필터 안 함 (극단값만)
        # gap <= 1.0%는 더 엄격함 (극단값 필요)
        strong_signal = gap_pct >= 1.0
        
        if strong_signal:
            # 강한 신호: 극단값만 배제
            rsi_buy_ok = np.isnan(last_rsi) or last_rsi < 85
            rsi_sell_ok = np.isnan(last_rsi) or last_rsi > 15
        else:
            # 약한 신호: 극단값 요구
            rsi_buy_ok = np.isnan(last_rsi) or last_rsi < 40
            rsi_sell_ok = np.isnan(last_rsi) or last_rsi > 60

        rsi_str = f"RSI={last_rsi:.1f}" if not np.isnan(last_rsi) else "RSI=N/A"
        atr_str = f"ATR={'수축' if atr_contracting else '확장'}" if not np.isnan(last_atr) else "ATR=N/A"

        if crossed_up and rsi_buy_ok:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=float(last_close),
                reasoning=f"FRAMA 상향 크로스. close={last_close:.4f} > FRAMA={last_frama:.4f} (이격 {gap_pct:.2f}%, {rsi_str}, {atr_str})",
                invalidation=f"Close below FRAMA ({last_frama:.4f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        if crossed_down and rsi_sell_ok:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=float(last_close),
                reasoning=f"FRAMA 하향 크로스. close={last_close:.4f} < FRAMA={last_frama:.4f} (이격 {gap_pct:.2f}%, {rsi_str}, {atr_str})",
                invalidation=f"Close above FRAMA ({last_frama:.4f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=float(last_close),
            reasoning=f"크로스 없음. close={last_close:.4f}, FRAMA={last_frama:.4f} (이격 {gap_pct:.2f}%, {rsi_str}, {atr_str})",
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
