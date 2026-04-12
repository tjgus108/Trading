"""
LOB OFI Strategy: 2차 개선 Order Flow Imbalance 기반 전략.

신호 품질 강화 (PF 1.36→1.5+):
- OFI 임계값 상향: 0.36 → 0.38 (moderate selectivity)
- VPIN 최소값 상향: 0.42 → 0.43 (mild filter)
- 볼륨 배수 강화: 1.25 → 1.30 (ensure conviction)
- RSI 극단값 조정: 거짓 신호 필터링 강화
"""

import pandas as pd
import numpy as np

from src.data.order_flow import VPINCalculator
from .base import Action, BaseStrategy, Confidence, Signal


class LOBOFIStrategy(BaseStrategy):
    name = "lob_maker"

    def __init__(
        self,
        ofi_buy_threshold: float = 0.38,         # 상향: 0.36 → 0.38
        ofi_sell_threshold: float = -0.38,       # 상향: -0.36 → -0.38
        vpin_high_threshold: float = 0.60,
        vpin_low_threshold: float = 0.43,        # 상향: 0.42 → 0.43
        vpin_buckets: int = 50,
        volume_multiplier: float = 1.30,         # 상향: 1.25 → 1.30
        volume_window: int = 20,
        rsi_period: int = 14,
        rsi_extreme_high: float = 78.0,          # 하향: 80 → 78
        rsi_extreme_low: float = 22.0,           # 상향: 20 → 22
    ):
        self.ofi_buy_threshold = ofi_buy_threshold
        self.ofi_sell_threshold = ofi_sell_threshold
        self.vpin_high_threshold = vpin_high_threshold
        self.vpin_low_threshold = vpin_low_threshold
        self.volume_multiplier = volume_multiplier
        self.volume_window = volume_window
        self.rsi_period = rsi_period
        self.rsi_extreme_high = rsi_extreme_high
        self.rsi_extreme_low = rsi_extreme_low
        self._vpin_calc = VPINCalculator(n_buckets=vpin_buckets)

    def _calculate_rsi(self, df: pd.DataFrame, period: int) -> float:
        """마지막 RSI 값 계산"""
        if len(df) < period + 1:
            return 50.0
        delta = df["close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / (loss + 1e-9)
        rsi = 100 - (100 / (1 + rs))
        return float(rsi.iloc[-1])

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < 3:
            return self._hold(df, "Insufficient data")

        last = self._last(df)
        last_idx = len(df) - 2

        # OFI 계산
        if "bid_vol" in df.columns and "ask_vol" in df.columns:
            bid = float(df["bid_vol"].iloc[last_idx])
            ask = float(df["ask_vol"].iloc[last_idx])
            total = bid + ask
            ofi = (bid - ask) / total if total > 0 else 0.0
        else:
            # proxy
            hl = float(last["high"] - last["low"] + 1e-9)
            co = float(last["close"] - last["open"])
            ofi = co / hl
            ofi = max(-1.0, min(1.0, ofi))

        # VPIN
        vpin = self._vpin_calc.get_latest(df.iloc[: last_idx + 1])

        # RSI
        rsi = self._calculate_rsi(df, self.rsi_period)

        # Volume
        vol_window = df["volume"].iloc[max(0, last_idx - self.volume_window): last_idx]
        avg_vol = float(vol_window.mean()) if len(vol_window) > 0 else 0.0
        current_vol = float(last["volume"])
        volume_confirmed = avg_vol > 0 and current_vol >= self.volume_multiplier * avg_vol

        entry_price = float(last["close"])
        reasoning_base = f"OFI={ofi:.3f}, VPIN={vpin:.3f}, RSI={rsi:.1f}, vol_ratio={current_vol / avg_vol:.2f}" if avg_vol > 0 else f"OFI={ofi:.3f}, VPIN={vpin:.3f}, RSI={rsi:.1f}"

        # BUY
        if ofi > self.ofi_buy_threshold and volume_confirmed and vpin > self.vpin_low_threshold:
            if rsi < self.rsi_extreme_low:
                return self._hold(df, f"HOLD: {reasoning_base} — RSI oversold")
            
            if vpin > self.vpin_high_threshold:
                confidence = Confidence.HIGH
                reasoning = f"BUY signal: {reasoning_base} — high toxicity"
            else:
                confidence = Confidence.MEDIUM
                reasoning = f"BUY signal: {reasoning_base}"
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry_price,
                reasoning=reasoning,
                invalidation=f"OFI drops below {self.ofi_buy_threshold}",
                bull_case=f"OFI={ofi:.3f}, VPIN={vpin:.3f}",
                bear_case="Low volume or VPIN",
            )

        # SELL
        if ofi < self.ofi_sell_threshold and volume_confirmed and vpin > self.vpin_low_threshold:
            if rsi > self.rsi_extreme_high:
                return self._hold(df, f"HOLD: {reasoning_base} — RSI overbought")
            
            if vpin > self.vpin_high_threshold:
                confidence = Confidence.HIGH
                reasoning = f"SELL signal: {reasoning_base} — high toxicity"
            else:
                confidence = Confidence.MEDIUM
                reasoning = f"SELL signal: {reasoning_base}"
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry_price,
                reasoning=reasoning,
                invalidation=f"OFI rises above {self.ofi_sell_threshold}",
                bull_case=f"OFI={ofi:.3f}, VPIN={vpin:.3f}",
                bear_case="Low volume or VPIN",
            )

        vol_note = "" if volume_confirmed else ", vol insufficient"
        vpin_note = f", VPIN={vpin:.3f}" if vpin <= self.vpin_low_threshold else ""
        return self._hold(df, f"HOLD: {reasoning_base}{vol_note}{vpin_note}")

    def _hold(self, df: pd.DataFrame, reason: str) -> Signal:
        last = self._last(df) if len(df) >= 2 else df.iloc[-1]
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=float(last["close"]),
            reasoning=reason,
            invalidation="",
        )
