"""
Dark Cloud Cover / Piercing Line 반전 패턴 전략:
- Piercing Line (BUY): 이전봉 큰 음봉 + 현재봉 양봉이 이전봉 중간 이상 침투 + RSI14 < 45
- Dark Cloud Cover (SELL): 이전봉 큰 양봉 + 현재봉 음봉이 이전봉 중간 이하 침투 + RSI14 > 55
- confidence: HIGH if 50% 이상 침투, MEDIUM otherwise
- 최소 20행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 20


def _rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss.replace(0, 1e-10)
    return 100 - (100 / (1 + rs))


class CloudCoverStrategy(BaseStrategy):
    name = "cloud_cover"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        idx = len(df) - 2
        curr = df.iloc[idx]
        prev = df.iloc[idx - 1]
        atr = float(df["atr14"].iloc[idx])
        rsi_val = float(_rsi(df["close"]).iloc[idx])

        prev_open = float(prev["open"])
        prev_close = float(prev["close"])
        curr_open = float(curr["open"])
        curr_close = float(curr["close"])

        prev_body = abs(prev_close - prev_open)
        prev_mid = (prev_open + prev_close) / 2.0
        prev_is_bearish = prev_open > prev_close
        prev_is_bullish = prev_close > prev_open
        curr_is_bullish = curr_close > curr_open
        curr_is_bearish = curr_close < curr_open

        close = curr_close

        # Piercing Line (BUY)
        if (
            prev_is_bearish
            and prev_body > atr * 0.5
            and curr_is_bullish
            and curr_open < prev_close
            and curr_close > prev_mid
            and rsi_val < 45
        ):
            # 침투율: (curr_close - prev_close) / prev_body
            penetration = (curr_close - prev_close) / prev_body if prev_body > 0 else 0
            confidence = Confidence.HIGH if penetration >= 0.5 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=f"Piercing Line: penetration={penetration:.2f} RSI={rsi_val:.1f}",
                invalidation=f"Close below prev low ({float(prev['low']):.2f})",
                bull_case="Piercing Line reversal after strong bearish candle",
                bear_case="",
            )

        # Dark Cloud Cover (SELL)
        if (
            prev_is_bullish
            and prev_body > atr * 0.5
            and curr_is_bearish
            and curr_open > prev_close
            and curr_close < prev_mid
            and rsi_val > 55
        ):
            # 침투율: (prev_close - curr_close) / prev_body
            penetration = (prev_close - curr_close) / prev_body if prev_body > 0 else 0
            confidence = Confidence.HIGH if penetration >= 0.5 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=f"Dark Cloud Cover: penetration={penetration:.2f} RSI={rsi_val:.1f}",
                invalidation=f"Close above prev high ({float(prev['high']):.2f})",
                bull_case="",
                bear_case="Dark Cloud Cover reversal after strong bullish candle",
            )

        return self._hold(
            df,
            f"No pattern: prev_body={prev_body:.4f} prev_mid={prev_mid:.4f} rsi={rsi_val:.1f}",
        )

    def _hold(self, df: pd.DataFrame, reason: str) -> Signal:
        last = df.iloc[len(df) - 2] if len(df) >= 2 else df.iloc[-1]
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=float(last["close"]),
            reasoning=reason,
            invalidation="",
            bull_case="",
            bear_case="",
        )
