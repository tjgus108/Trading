"""
LOB OFI Strategy: Order Flow Imbalance + VPIN 기반 전략.

근거: arxiv 2506.05764 (LOB ML AUC>0.55), EFMA 2025 (OFI와 암호화폐 수익 관계)
- OFI: 매수/매도 압력 측정 (bid/ask 볼륨 불균형 또는 proxy)
- VPIN: 고독성 거래 활동 감지 (신호 강도 조절)
"""

import pandas as pd

from src.data.order_flow import VPINCalculator
from .base import Action, BaseStrategy, Confidence, Signal


class LOBOFIStrategy(BaseStrategy):
    name = "lob_maker"

    def __init__(
        self,
        ofi_buy_threshold: float = 0.3,
        ofi_sell_threshold: float = -0.3,
        vpin_high_threshold: float = 0.6,
        vpin_low_threshold: float = 0.35,
        vpin_buckets: int = 50,
    ):
        self.ofi_buy_threshold = ofi_buy_threshold
        self.ofi_sell_threshold = ofi_sell_threshold
        self.vpin_high_threshold = vpin_high_threshold
        self.vpin_low_threshold = vpin_low_threshold
        self._vpin_calc = VPINCalculator(n_buckets=vpin_buckets)

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < 3:
            return self._hold(df, "Insufficient data")

        last = self._last(df)
        last_idx = len(df) - 2

        # OFI 계산: bid_vol/ask_vol 있으면 사용, 없으면 proxy
        if "bid_vol" in df.columns and "ask_vol" in df.columns:
            bid = float(df["bid_vol"].iloc[last_idx])
            ask = float(df["ask_vol"].iloc[last_idx])
            total = bid + ask
            ofi = (bid - ask) / total if total > 0 else 0.0
        else:
            # proxy: volume * (close - open) / (high - low + 1e-9)
            hl = float(last["high"] - last["low"] + 1e-9)
            co = float(last["close"] - last["open"])
            proxy_raw = float(last["volume"]) * co / hl
            # 정규화: 최근 window에서 min/max 스케일
            window = df.iloc[max(0, last_idx - 49): last_idx + 1]
            hl_arr = window["high"] - window["low"] + 1e-9
            proxy_series = window["volume"] * (window["close"] - window["open"]) / hl_arr
            pmax = proxy_series.abs().max()
            ofi = float(proxy_raw / pmax) if pmax > 0 else 0.0
            ofi = max(-1.0, min(1.0, ofi))

        # VPIN 계산
        vpin = self._vpin_calc.get_latest(df.iloc[: last_idx + 1])

        entry_price = float(last["close"])
        reasoning_base = f"OFI={ofi:.3f}, VPIN={vpin:.3f}"

        # 신호 결정
        if ofi > self.ofi_buy_threshold:
            if vpin > self.vpin_high_threshold:
                confidence = Confidence.HIGH
                reasoning = f"BUY signal: {reasoning_base} — high toxicity reinforces buy pressure"
            else:
                confidence = Confidence.MEDIUM
                reasoning = f"BUY signal: {reasoning_base} — moderate buy pressure"
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry_price,
                reasoning=reasoning,
                invalidation=f"OFI drops below {self.ofi_buy_threshold}",
                bull_case=f"OFI={ofi:.3f} > {self.ofi_buy_threshold}, VPIN={vpin:.3f}",
                bear_case=f"VPIN={vpin:.3f} below high threshold {self.vpin_high_threshold}",
            )

        if ofi < self.ofi_sell_threshold:
            if vpin > self.vpin_high_threshold:
                confidence = Confidence.HIGH
                reasoning = f"SELL signal: {reasoning_base} — high toxicity reinforces sell pressure"
            else:
                confidence = Confidence.MEDIUM
                reasoning = f"SELL signal: {reasoning_base} — moderate sell pressure"
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry_price,
                reasoning=reasoning,
                invalidation=f"OFI rises above {self.ofi_sell_threshold}",
                bull_case=f"VPIN={vpin:.3f} below high threshold {self.vpin_high_threshold}",
                bear_case=f"OFI={ofi:.3f} < {self.ofi_sell_threshold}, VPIN={vpin:.3f}",
            )

        return self._hold(df, f"HOLD: {reasoning_base} — within neutral zone")

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
