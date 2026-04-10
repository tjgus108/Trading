"""
PriceActionConfirmStrategy: Price Action + 볼륨 + 모멘텀 3중 확인 전략.

- PA 신호: body > ATR14 * 0.8 (큰 캔들)
- 볼륨 확인: volume > avg_vol_20 * 1.2
- 모멘텀 확인: close.pct_change(3) 방향과 일치
- BUY: 큰 양봉 + vol 확인 + mom3 > 0
- SELL: 큰 음봉 + vol 확인 + mom3 < 0
- confidence HIGH: body > ATR14 * 1.5 AND vol > avg * 1.5
- 최소 행: 25
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


class PriceActionConfirmStrategy(BaseStrategy):
    name = "pa_confirm"

    MIN_ROWS = 25

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < self.MIN_ROWS:
            last_close = float(df["close"].iloc[-1]) if len(df) > 0 else 0.0
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=last_close,
                reasoning="데이터 부족: 최소 25행 필요",
                invalidation="",
            )

        last = self._last(df)

        close = float(last["close"])
        open_ = float(last["open"])
        body = abs(close - open_)
        atr14 = float(last["atr14"])

        # 볼륨 확인: 최근 20봉 평균
        lookback = min(20, len(df) - 2)
        avg_vol = float(df["volume"].iloc[-lookback - 2 : -2].mean())
        vol = float(last["volume"])

        # 모멘텀: 3봉 전 대비 pct_change
        idx = len(df) - 2  # _last == df.iloc[-2]
        if idx < 3:
            mom3 = 0.0
        else:
            prev3_close = float(df["close"].iloc[idx - 3])
            mom3 = (close - prev3_close) / prev3_close if prev3_close != 0 else 0.0

        # 조건 평가
        big_candle = body > atr14 * 0.8
        vol_ok = vol > avg_vol * 1.2
        is_bull = close > open_
        is_bear = close < open_

        bull_pa = big_candle and is_bull
        bear_pa = big_candle and is_bear

        # confidence
        high_conf = body > atr14 * 1.5 and vol > avg_vol * 1.5

        bull_case = (
            f"body={body:.4f} ATR14={atr14:.4f} vol={vol:.0f} avg_vol={avg_vol:.0f} mom3={mom3:.4f}"
        )
        bear_case = bull_case

        if bull_pa and vol_ok and mom3 > 0:
            return Signal(
                action=Action.BUY,
                confidence=Confidence.HIGH if high_conf else Confidence.MEDIUM,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"PA BUY: 큰 양봉(body={body:.4f}>ATR*0.8={atr14*0.8:.4f}), "
                    f"vol={vol:.0f}>avg*1.2={avg_vol*1.2:.0f}, mom3={mom3:.4f}>0"
                ),
                invalidation=f"Close below open ({open_:.4f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        if bear_pa and vol_ok and mom3 < 0:
            return Signal(
                action=Action.SELL,
                confidence=Confidence.HIGH if high_conf else Confidence.MEDIUM,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"PA SELL: 큰 음봉(body={body:.4f}>ATR*0.8={atr14*0.8:.4f}), "
                    f"vol={vol:.0f}>avg*1.2={avg_vol*1.2:.0f}, mom3={mom3:.4f}<0"
                ),
                invalidation=f"Close above open ({open_:.4f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        reasons = []
        if not big_candle:
            reasons.append(f"body={body:.4f} < ATR*0.8={atr14*0.8:.4f}")
        if not vol_ok:
            reasons.append(f"vol={vol:.0f} < avg*1.2={avg_vol*1.2:.0f}")
        if mom3 == 0 or (bull_pa and mom3 <= 0) or (bear_pa and mom3 >= 0):
            reasons.append(f"mom3={mom3:.4f} 방향 불일치")

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=close,
            reasoning="; ".join(reasons) if reasons else "PA/볼륨/모멘텀 조건 미충족",
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
