"""
VPT Signal 전략 (vpt.py와 다른 접근법: EMA vs Signal line 크로스):
- VPT = cumsum(volume * (close - prev_close) / prev_close)
- VPT_EMA = EWM(VPT, span=14)
- VPT_Signal = EWM(VPT, span=21)
- BUY:  VPT_EMA crosses above VPT_Signal AND close > EMA50
- SELL: VPT_EMA crosses below VPT_Signal AND close < EMA50
- 크로스 = 이전봉 VPT_EMA <= VPT_Signal, 현재봉 VPT_EMA > VPT_Signal
- confidence: HIGH if |VPT_EMA - VPT_Signal| > std(VPT, 20), MEDIUM 그 외
- 최소 데이터: 30행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 30
_EMA_SPAN = 14
_SIG_SPAN = 21
_STD_PERIOD = 20


class VPTSignalStrategy(BaseStrategy):
    name = "vpt_signal"

    def generate(self, df: pd.DataFrame) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning="데이터 부족",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        idx = len(df) - 2

        price_change = df["close"].pct_change()
        vpt = (df["volume"] * price_change).cumsum()
        vpt_ema = vpt.ewm(span=_EMA_SPAN, adjust=False).mean()
        vpt_signal = vpt.ewm(span=_SIG_SPAN, adjust=False).mean()
        vpt_std = vpt.rolling(_STD_PERIOD).std()

        ema_now = float(vpt_ema.iloc[idx])
        ema_prev = float(vpt_ema.iloc[idx - 1])
        sig_now = float(vpt_signal.iloc[idx])
        sig_prev = float(vpt_signal.iloc[idx - 1])
        std_now = float(vpt_std.iloc[idx])
        close = float(df["close"].iloc[idx])
        ema50 = float(df["ema50"].iloc[idx])

        cross_up = ema_prev <= sig_prev and ema_now > sig_now
        cross_down = ema_prev >= sig_prev and ema_now < sig_now

        diff = abs(ema_now - sig_now)
        conf_high = (not pd.isna(std_now)) and diff > std_now

        bull_case = (
            f"VPT_EMA={ema_now:.2f} 상향 크로스 VPT_Signal={sig_now:.2f}. "
            f"볼륨 모멘텀 전환 상승."
        )
        bear_case = (
            f"VPT_EMA={ema_now:.2f} 하향 크로스 VPT_Signal={sig_now:.2f}. "
            f"볼륨 모멘텀 전환 하락."
        )

        if cross_up and close > ema50:
            conf = Confidence.HIGH if conf_high else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"VPT_EMA 상향 크로스: EMA={ema_now:.2f} > Signal={sig_now:.2f} "
                    f"(prev EMA={ema_prev:.2f} <= Signal={sig_prev:.2f}), "
                    f"close={close:.4f} > EMA50={ema50:.4f}"
                ),
                invalidation="VPT_EMA < VPT_Signal 또는 close < EMA50",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        if cross_down and close < ema50:
            conf = Confidence.HIGH if conf_high else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"VPT_EMA 하향 크로스: EMA={ema_now:.2f} < Signal={sig_now:.2f} "
                    f"(prev EMA={ema_prev:.2f} >= Signal={sig_prev:.2f}), "
                    f"close={close:.4f} < EMA50={ema50:.4f}"
                ),
                invalidation="VPT_EMA > VPT_Signal 또는 close > EMA50",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=close,
            reasoning=(
                f"크로스 없음 또는 EMA50 조건 미충족: "
                f"VPT_EMA={ema_now:.2f}, VPT_Signal={sig_now:.2f}, "
                f"close={close:.4f}, EMA50={ema50:.4f}"
            ),
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
