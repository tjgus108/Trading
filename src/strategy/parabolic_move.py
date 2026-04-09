"""
ParabolicMoveStrategy: 포물선형 가격 급등/급락 감지 후 소진 역매매.

- ROC_5 = (close / close.shift(5) - 1) * 100
- ROC_10 = (close / close.shift(10) - 1) * 100
- Parabolic up:  ROC_5 > 5% AND ROC_10 > 10% AND ROC_5 > ROC_5.shift(1)
- Parabolic down: ROC_5 < -5% AND ROC_10 < -10% AND ROC_5 < ROC_5.shift(1)
- SELL (exhaustion): Parabolic up + RSI14 > 80
- BUY  (exhaustion): Parabolic down + RSI14 < 20
- confidence: HIGH if RSI > 85 (SELL) or RSI < 15 (BUY), else MEDIUM
- 최소 행: 20
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 20
_RSI_PERIOD = 14


def _rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = (-delta).clip(lower=0)
    avg_gain = gain.ewm(com=period - 1, adjust=False).mean()
    avg_loss = loss.ewm(com=period - 1, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, float("nan"))
    return 100 - (100 / (1 + rs))


class ParabolicMoveStrategy(BaseStrategy):
    name = "parabolic_move"

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

        close = df["close"]
        roc5 = (close / close.shift(5) - 1) * 100
        roc10 = (close / close.shift(10) - 1) * 100
        rsi = _rsi(close, _RSI_PERIOD)

        idx = len(df) - 2
        r5 = float(roc5.iloc[idx])
        r5_prev = float(roc5.iloc[idx - 1])
        r10 = float(roc10.iloc[idx])
        rsi_val = float(rsi.iloc[idx])
        entry = float(close.iloc[idx])

        parabolic_up = r5 > 5.0 and r10 > 10.0 and r5 > r5_prev
        parabolic_down = r5 < -5.0 and r10 < -10.0 and r5 < r5_prev

        # SELL: 포물선 급등 + RSI 과매수
        if parabolic_up and rsi_val > 80:
            conf = Confidence.HIGH if rsi_val > 85 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"포물선 급등 소진: ROC5={r5:.2f}%, ROC10={r10:.2f}%, "
                    f"RSI={rsi_val:.1f} (과매수 극단)"
                ),
                invalidation="RSI 80 아래로 하락 + 가격 신고점 갱신 시",
                bull_case="모멘텀 지속 시 추가 상승 가능",
                bear_case=f"RSI {rsi_val:.1f} 과매수, 급반락 위험",
            )

        # BUY: 포물선 급락 + RSI 과매도
        if parabolic_down and rsi_val < 20:
            conf = Confidence.HIGH if rsi_val < 15 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"포물선 급락 소진: ROC5={r5:.2f}%, ROC10={r10:.2f}%, "
                    f"RSI={rsi_val:.1f} (과매도 극단)"
                ),
                invalidation="RSI 20 위로 회복 + 가격 신저점 갱신 시",
                bull_case=f"RSI {rsi_val:.1f} 과매도, 급반등 기대",
                bear_case="낙폭 과대 지속 시 추가 하락 가능",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=(
                f"포물선 조건 미충족: ROC5={r5:.2f}%, ROC10={r10:.2f}%, "
                f"RSI={rsi_val:.1f}"
            ),
            invalidation="",
            bull_case="",
            bear_case="",
        )
