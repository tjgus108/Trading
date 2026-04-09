"""
VolumePriceTrendConfirmStrategy:
- VPT = (close.pct_change() * volume).cumsum()
- VPT_Signal = VPT.ewm(span=14).mean()
- VPT Histogram = VPT - VPT_Signal
- BUY: VPT > VPT_Signal AND hist 상승 (hist > hist.shift(1)) AND close > EMA20
- SELL: VPT < VPT_Signal AND hist 하락 (hist < hist.shift(1)) AND close < EMA20
- confidence: HIGH if |VPT_hist| > VPT_hist.rolling(20).std(), MEDIUM 그 외
- 최소 25행 필요
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 25
_EWM_SPAN = 14
_STD_PERIOD = 20


class VolumePriceTrendConfirmStrategy(BaseStrategy):
    name = "vpt_confirm"

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
        vpt = (price_change * df["volume"]).cumsum()
        vpt_signal = vpt.ewm(span=_EWM_SPAN, adjust=False).mean()
        vpt_hist = vpt - vpt_signal
        hist_std = vpt_hist.rolling(_STD_PERIOD).std()

        vpt_now = float(vpt.iloc[idx])
        vpt_sig_now = float(vpt_signal.iloc[idx])
        hist_now = float(vpt_hist.iloc[idx])
        hist_prev = float(vpt_hist.iloc[idx - 1])
        hist_std_now = float(hist_std.iloc[idx])
        close = float(df["close"].iloc[idx])
        ema20 = float(df["ema20"].iloc[idx])

        bullish = vpt_now > vpt_sig_now
        bearish = vpt_now < vpt_sig_now
        hist_rising = hist_now > hist_prev
        hist_falling = hist_now < hist_prev

        if not pd.isna(hist_std_now) and hist_std_now > 0:
            conf_high = abs(hist_now) > hist_std_now
        else:
            conf_high = False

        conf = Confidence.HIGH if conf_high else Confidence.MEDIUM

        bull_case = (
            f"VPT={vpt_now:.2f} > Signal={vpt_sig_now:.2f}, "
            f"Hist 상승 ({hist_prev:.2f} → {hist_now:.2f})"
        )
        bear_case = (
            f"VPT={vpt_now:.2f} < Signal={vpt_sig_now:.2f}, "
            f"Hist 하락 ({hist_prev:.2f} → {hist_now:.2f})"
        )

        if bullish and hist_rising and close > ema20:
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"VPT 강세 확인: VPT={vpt_now:.2f} > Signal={vpt_sig_now:.2f}, "
                    f"Hist 상승, close={close:.4f} > EMA20={ema20:.4f}"
                ),
                invalidation="VPT < VPT_Signal 또는 Hist 하락 또는 close < EMA20",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        if bearish and hist_falling and close < ema20:
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"VPT 약세 확인: VPT={vpt_now:.2f} < Signal={vpt_sig_now:.2f}, "
                    f"Hist 하락, close={close:.4f} < EMA20={ema20:.4f}"
                ),
                invalidation="VPT > VPT_Signal 또는 Hist 상승 또는 close > EMA20",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=close,
            reasoning=(
                f"조건 미충족: VPT={vpt_now:.2f}, Signal={vpt_sig_now:.2f}, "
                f"Hist={hist_now:.2f}, close={close:.4f}, EMA20={ema20:.4f}"
            ),
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
