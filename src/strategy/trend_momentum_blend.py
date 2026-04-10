"""
TrendMomentumBlendStrategy: 추세와 모멘텀 블렌딩
추세 방향으로만 모멘텀 신호 채택.
"""

import pandas as pd

from src.strategy.base import Action, BaseStrategy, Confidence, Signal


class TrendMomentumBlendStrategy(BaseStrategy):
    name = "trend_momentum_blend"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < 60:
            entry = float(df["close"].iloc[-1]) if len(df) > 0 else 0.0
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning="Insufficient data (minimum 60 rows required)",
                invalidation="N/A",
            )

        close = df["close"].astype(float)

        # 추세: EMA50 기울기
        ema50 = close.ewm(span=50, adjust=False).mean()
        ema50_slope = ema50.diff(5) / close

        # 모멘텀: ROC(10) 크로스오버
        roc10 = close.pct_change(10) * 100
        roc_ma = roc10.rolling(5).mean()

        # RSI(14)
        delta = close.diff()
        gain = delta.clip(lower=0).ewm(com=13, adjust=False).mean()
        loss = (-delta.clip(upper=0)).ewm(com=13, adjust=False).mean()
        rsi = 100 - 100 / (1 + gain / loss.replace(0, 1e-10))

        idx = len(df) - 2  # 마지막 완성 캔들

        slope_val = float(ema50_slope.iloc[idx])
        roc_val = float(roc10.iloc[idx])
        roc_ma_val = float(roc_ma.iloc[idx])
        rsi_val = float(rsi.iloc[idx])

        entry = float(close.iloc[idx])

        # NaN 체크
        if any(pd.isna(v) for v in [slope_val, roc_val, roc_ma_val, rsi_val]):
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning="NaN 값 존재 (HOLD)",
                invalidation="N/A",
            )

        # Confidence: 추세 강도 기반
        std20 = float(close.rolling(20).std().iloc[idx])
        close_val = float(close.iloc[idx])
        threshold = (std20 / close_val) * 0.005 if close_val > 0 else 0.0
        confidence = Confidence.HIGH if abs(slope_val) > threshold else Confidence.MEDIUM

        # BUY: 상승 추세 + 모멘텀 상승 + RSI 50~70
        buy_signal = (
            slope_val > 0
            and roc_val > roc_ma_val
            and rsi_val > 50
            and rsi_val < 70
        )

        # SELL: 하락 추세 + 모멘텀 하락 + RSI 30~50
        sell_signal = (
            slope_val < 0
            and roc_val < roc_ma_val
            and rsi_val < 50
            and rsi_val > 30
        )

        if buy_signal:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"상승 추세(EMA50 slope={slope_val:.6f}) + "
                    f"ROC({roc_val:.2f})>ROC_MA({roc_ma_val:.2f}) + "
                    f"RSI={rsi_val:.1f} (50~70). BUY."
                ),
                invalidation=f"EMA50 기울기 음전환 또는 RSI 50 하회 시 무효",
                bull_case="추세+모멘텀 일치로 상승 지속 기대",
                bear_case="RSI 과매수권 진입 시 조정 가능",
            )

        if sell_signal:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"하락 추세(EMA50 slope={slope_val:.6f}) + "
                    f"ROC({roc_val:.2f})<ROC_MA({roc_ma_val:.2f}) + "
                    f"RSI={rsi_val:.1f} (30~50). SELL."
                ),
                invalidation=f"EMA50 기울기 양전환 또는 RSI 50 상회 시 무효",
                bull_case="과매도권 접근 시 반등 가능",
                bear_case="추세+모멘텀 일치로 하락 지속 기대",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=(
                f"추세/모멘텀 불일치 또는 극단 RSI "
                f"(slope={slope_val:.6f}, RSI={rsi_val:.1f}). HOLD."
            ),
            invalidation="N/A",
        )
