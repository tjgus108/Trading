"""
MultiScoreStrategy: 여러 지표의 점수 합산(앙상블) 전략.

score 구성 (각 +1):
  +1 if close > EMA50
  +1 if RSI14 > 50
  +1 if close > SMA20
  +1 if volume > vol_sma20 * 1.1
  +1 if MACD_histogram > 0

BUY:  bull_score >= 4
SELL: bear_score >= 4
confidence: HIGH if score == 5, MEDIUM if == 4
최소 데이터: 30행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 30


def _ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()


class MultiScoreStrategy(BaseStrategy):
    name = "multi_score"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            entry = float(df["close"].iloc[-1]) if len(df) > 0 else 0.0
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning="멀티 스코어 계산에 필요한 데이터 부족 (최소 30행).",
                invalidation="",
            )

        close = df["close"]
        volume = df["volume"]

        ema50 = _ema(close, 50)
        sma20 = close.rolling(20).mean()
        vol_sma20 = volume.rolling(20).mean()

        rsi_period = 14
        delta = close.diff()
        gain = delta.clip(lower=0)
        loss = (-delta).clip(lower=0)
        avg_gain = gain.ewm(span=rsi_period, adjust=False).mean()
        avg_loss = loss.ewm(span=rsi_period, adjust=False).mean()
        rs = avg_gain / avg_loss.replace(0, float("nan"))
        rsi = 100 - (100 / (1 + rs))

        macd_line = _ema(close, 12) - _ema(close, 26)
        signal_line = _ema(macd_line, 9)
        histogram = macd_line - signal_line

        last = self._last(df)
        idx = df.index[-2]

        close_val = float(last["close"])
        ema50_val = float(ema50.iloc[-2])
        sma20_val = float(sma20.iloc[-2])
        rsi_val = float(rsi.iloc[-2])
        vol_val = float(volume.iloc[-2])
        vol_sma20_val = float(vol_sma20.iloc[-2])
        hist_val = float(histogram.iloc[-2])

        bull_score = (
            int(close_val > ema50_val)
            + int(rsi_val > 50)
            + int(close_val > sma20_val)
            + int(vol_val > vol_sma20_val * 1.1)
            + int(hist_val > 0)
        )

        bear_score = (
            int(close_val < ema50_val)
            + int(rsi_val < 50)
            + int(close_val < sma20_val)
            + int(vol_val > vol_sma20_val * 1.1)  # 볼륨 지지 (하락에도 동일)
            + int(hist_val < 0)
        )

        context = (
            f"close={close_val:.4f} ema50={ema50_val:.4f} sma20={sma20_val:.4f} "
            f"rsi={rsi_val:.1f} hist={hist_val:.6f} "
            f"bull={bull_score} bear={bear_score}"
        )

        if bull_score >= 4:
            confidence = Confidence.HIGH if bull_score == 5 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_val,
                reasoning=f"멀티 지표 강세 합의 (bull_score={bull_score}/5). {context}",
                invalidation="bull_score < 4 하락 시 신호 무효.",
                bull_case=f"5개 지표 중 {bull_score}개 강세 지지.",
                bear_case="추세 전환 시 score 급락 가능.",
            )

        if bear_score >= 4:
            confidence = Confidence.HIGH if bear_score == 5 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_val,
                reasoning=f"멀티 지표 약세 합의 (bear_score={bear_score}/5). {context}",
                invalidation="bear_score < 4 하락 시 신호 무효.",
                bull_case="추세 전환 시 bear_score 급락 가능.",
                bear_case=f"5개 지표 중 {bear_score}개 약세 지지.",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=close_val,
            reasoning=f"합의 미달 (bull={bull_score}, bear={bear_score}). {context}",
            invalidation="bull_score 또는 bear_score >= 4 시 신호 발생.",
        )
