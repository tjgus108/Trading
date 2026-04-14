"""
TSI (True Strength Index) 전략:
- TSI: 이중 평활화된 모멘텀 지표
- 계산:
  - PC = close.diff()
  - Double_Smoothed_PC = EMA(EMA(PC, 25), 13)
  - Double_Smoothed_APC = EMA(EMA(|PC|, 25), 13)
  - TSI = 100 * Double_Smoothed_PC / Double_Smoothed_APC
  - Signal = EMA(TSI, 7)
- BUY:  TSI > Signal AND TSI > 0 AND 상향 크로스 (이전 TSI <= 이전 Signal)
- SELL: TSI < Signal AND TSI < 0 AND 하향 크로스 (이전 TSI >= 이전 Signal)
- confidence: HIGH if |TSI| > 25, MEDIUM otherwise
- 최소 데이터: 50행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 50


def _calc_tsi(df: pd.DataFrame) -> "Tuple[float, float, float, float]":
    """idx = len(df) - 2 기준 TSI, Signal, prev_TSI, prev_Signal 계산."""
    idx = len(df) - 2

    pc = df["close"].diff()
    ds_pc = pc.ewm(span=25, adjust=False).mean().ewm(span=13, adjust=False).mean()
    ds_apc = pc.abs().ewm(span=25, adjust=False).mean().ewm(span=13, adjust=False).mean()
    tsi = 100 * ds_pc / ds_apc.replace(0, 1e-10)
    signal = tsi.ewm(span=7, adjust=False).mean()

    tsi_now = float(tsi.iloc[idx])
    sig_now = float(signal.iloc[idx])
    tsi_prev = float(tsi.iloc[idx - 1])
    sig_prev = float(signal.iloc[idx - 1])
    return tsi_now, sig_now, tsi_prev, sig_prev


class TSIStrategy(BaseStrategy):
    name = "tsi"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=float(df["close"].iloc[-2]),
                reasoning=f"데이터 부족: {len(df)} < {_MIN_ROWS}",
                invalidation="데이터 충분 시 재평가",
            )

        tsi_now, sig_now, tsi_prev, sig_prev = _calc_tsi(df)
        entry = float(df["close"].iloc[-2])

        cross_up = tsi_prev <= sig_prev and tsi_now > sig_now
        cross_down = tsi_prev >= sig_prev and tsi_now < sig_now

        is_buy = tsi_now > sig_now and tsi_now > 0 and cross_up
        is_sell = tsi_now < sig_now and tsi_now < 0 and cross_down

        if is_buy:
            confidence = Confidence.HIGH if abs(tsi_now) > 25 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"TSI 상향 크로스(TSI={tsi_now:.2f} > Signal={sig_now:.2f}) + TSI > 0",
                invalidation=f"TSI가 Signal 하향 이탈 시",
                bull_case=f"TSI={tsi_now:.2f}, Signal={sig_now:.2f}, 상승 모멘텀 확인",
                bear_case="크로스 이후 재하락 가능",
            )

        if is_sell:
            confidence = Confidence.HIGH if abs(tsi_now) > 25 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"TSI 하향 크로스(TSI={tsi_now:.2f} < Signal={sig_now:.2f}) + TSI < 0",
                invalidation=f"TSI가 Signal 상향 돌파 시",
                bull_case="하락 모멘텀 소진 후 반등 가능",
                bear_case=f"TSI={tsi_now:.2f}, Signal={sig_now:.2f}, 하락 모멘텀 확인",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=entry,
            reasoning=f"TSI={tsi_now:.2f}, Signal={sig_now:.2f} — 크로스 조건 미충족",
            invalidation="TSI 크로스 발생 시 재평가",
        )
