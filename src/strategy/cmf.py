"""
CMF (Chaikin Money Flow) 전략 개선 - Cycle 113:
- BUY: CMF > 0.08 AND close > ema50 AND ema20 > ema50 AND 볼륨 > 85% AND RSI < 75 (약한 필터)
- SELL: CMF < -0.08 AND close < ema50 AND ema20 < ema50 AND 볼륨 > 85% AND RSI > 25 (약한 필터)
- Confidence: HIGH if |CMF| > 0.15, MEDIUM otherwise
- 최소 25행 필요
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_PERIOD = 20
_MIN_ROWS = 25
_BUY_THRESH = 0.08
_SELL_THRESH = -0.08
_HIGH_CONF = 0.15
_VOL_PERCENTILE = 0.85  # 상위 15% 볼륨 (강화)


class CMFStrategy(BaseStrategy):
    name = "cmf"

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

        h = df["high"].iloc[idx - _PERIOD + 1: idx + 1]
        l = df["low"].iloc[idx - _PERIOD + 1: idx + 1]
        c = df["close"].iloc[idx - _PERIOD + 1: idx + 1]
        v = df["volume"].iloc[idx - _PERIOD + 1: idx + 1]

        hl_range = h - l
        mfm = ((c - l) - (h - c)) / hl_range.where(hl_range != 0, 1.0)
        cmf = float((mfm * v).sum() / v.sum())

        close = float(df["close"].iloc[idx])
        ema20 = float(df["ema20"].iloc[idx])
        ema50 = float(df["ema50"].iloc[idx])
        rsi = float(df["rsi14"].iloc[idx])
        
        # 볼륨 필터: 지난 _PERIOD 기간 중앙값 대비
        vol_median = float(v.median())
        current_vol = float(df["volume"].iloc[idx])
        vol_ratio = current_vol / vol_median if vol_median > 0 else 1.0

        conf = Confidence.HIGH if abs(cmf) > _HIGH_CONF else Confidence.MEDIUM

        # BUY: CMF > 0.08 AND close > ema50 AND ema20 > ema50 AND 볼륨 양호 AND RSI < 75
        if cmf > _BUY_THRESH and close > ema50 and ema20 > ema50 and vol_ratio >= _VOL_PERCENTILE and rsi < 75:
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=f"CMF 자금 유입+추세+RSI: CMF={cmf:.4f}, RSI={rsi:.1f}, close={close:.2f} > ema50={ema50:.2f}, ema20={ema20:.2f} > ema50, vol={vol_ratio:.2f}x",
                invalidation=f"CMF < 0.08 또는 close < ema50 또는 ema20 < ema50 또는 RSI >= 75",
                bull_case=f"CMF={cmf:.4f}, 강한 자금 유입 + 상승 추세",
                bear_case="단기 반등일 수 있음",
            )

        # SELL: CMF < -0.08 AND close < ema50 AND ema20 < ema50 AND 볼륨 양호 AND RSI > 25
        if cmf < _SELL_THRESH and close < ema50 and ema20 < ema50 and vol_ratio >= _VOL_PERCENTILE and rsi > 25:
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=f"CMF 자금 유출+추세+RSI: CMF={cmf:.4f}, RSI={rsi:.1f}, close={close:.2f} < ema50={ema50:.2f}, ema20={ema20:.2f} < ema50, vol={vol_ratio:.2f}x",
                invalidation=f"CMF > -0.08 또는 close > ema50 또는 ema20 > ema50 또는 RSI <= 25",
                bull_case="단기 반등일 수 있음",
                bear_case=f"CMF={cmf:.4f}, 강한 자금 유출 + 하락 추세",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=close,
            reasoning=f"CMF 중립 또는 조건 미충족: CMF={cmf:.4f}, RSI={rsi:.1f}, ema20={ema20:.2f} vs ema50={ema50:.2f}",
            invalidation="",
            bull_case="",
            bear_case="",
        )
