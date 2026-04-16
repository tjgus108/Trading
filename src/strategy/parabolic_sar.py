"""
Parabolic SAR 전략: 추세 전환 시 BUY/SELL 신호.
AF 초기=0.02, 스텝=0.02, max=0.20
RSI14 확인으로 HIGH/MEDIUM confidence 구분.
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal
from typing import List, Tuple


class ParabolicSARStrategy(BaseStrategy):
    name = "parabolic_sar"

    def __init__(self, af_init: float = 0.02, af_step: float = 0.02, af_max: float = 0.20):
        self.af_init = af_init
        self.af_step = af_step
        self.af_max = af_max

    def _compute_sar(self, df: pd.DataFrame) -> Tuple[List[float], List[bool]]:
        """
        전체 시리즈에 대해 Parabolic SAR 계산.
        Returns:
            sar: SAR 값 리스트
            bullish: True=상승 추세, False=하락 추세
        """
        closes = df["close"].tolist()
        highs = df["high"].tolist()
        lows = df["low"].tolist()
        n = len(closes)

        sar = [0.0] * n
        bullish = [True] * n
        ep = [0.0] * n
        af = [self.af_init] * n

        # 초기화: 첫 두 캔들로 초기 방향 결정
        bullish[0] = closes[1] > closes[0]
        if bullish[0]:
            sar[0] = lows[0]
            ep[0] = highs[0]
        else:
            sar[0] = highs[0]
            ep[0] = lows[0]
        af[0] = self.af_init

        for i in range(1, n):
            prev_bull = bullish[i - 1]
            prev_sar = sar[i - 1]
            prev_ep = ep[i - 1]
            prev_af = af[i - 1]

            # SAR 업데이트
            new_sar = prev_sar + prev_af * (prev_ep - prev_sar)

            if prev_bull:
                # 상승 추세: SAR는 이전 두 캔들 최저가보다 높으면 안 됨
                if i >= 2:
                    new_sar = min(new_sar, lows[i - 1], lows[i - 2])
                else:
                    new_sar = min(new_sar, lows[i - 1])

                # 반전 조건
                if closes[i] < new_sar:
                    bullish[i] = False
                    sar[i] = prev_ep  # 반전 시 SAR = 이전 EP
                    ep[i] = lows[i]
                    af[i] = self.af_init
                else:
                    bullish[i] = True
                    sar[i] = new_sar
                    if highs[i] > prev_ep:
                        ep[i] = highs[i]
                        af[i] = min(prev_af + self.af_step, self.af_max)
                    else:
                        ep[i] = prev_ep
                        af[i] = prev_af
            else:
                # 하락 추세: SAR는 이전 두 캔들 최고가보다 낮으면 안 됨
                if i >= 2:
                    new_sar = max(new_sar, highs[i - 1], highs[i - 2])
                else:
                    new_sar = max(new_sar, highs[i - 1])

                # 반전 조건
                if closes[i] > new_sar:
                    bullish[i] = True
                    sar[i] = prev_ep  # 반전 시 SAR = 이전 EP
                    ep[i] = highs[i]
                    af[i] = self.af_init
                else:
                    bullish[i] = False
                    sar[i] = new_sar
                    if lows[i] < prev_ep:
                        ep[i] = lows[i]
                        af[i] = min(prev_af + self.af_step, self.af_max)
                    else:
                        ep[i] = prev_ep
                        af[i] = prev_af

        return sar, bullish

    def _compute_rsi(self, close: pd.Series, period: int = 14) -> float:
        """RSI 계산 (내장). 마지막 완성 캔들(-2) 기준."""
        delta = close.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(period).mean()
        avg_loss = loss.rolling(period).mean()
        rs = avg_gain / avg_loss.replace(0, float("nan"))
        rsi = 100 - (100 / (1 + rs))
        return float(rsi.iloc[-2])

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < 30:
            last_close = float(df["close"].iloc[-1]) if len(df) > 0 else 0.0
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=last_close,
                reasoning="데이터 부족 (최소 30행 필요).",
                invalidation="",
            )

        sar, bullish = self._compute_sar(df)

        # _last(df) = df.iloc[-2] 패턴: 마지막 완성 캔들
        prev_bull = bullish[-3]   # 직전 완성 캔들 전
        last_bull = bullish[-2]   # 직전 완성 캔들
        entry = float(df["close"].iloc[-2])

        turned_buy = (not prev_bull) and last_bull
        turned_sell = prev_bull and (not last_bull)

        rsi = self._compute_rsi(df["close"])

        if turned_buy:
            high_conf = rsi < 60
            confidence = Confidence.HIGH if high_conf else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"SAR 하락→상승 전환 (SAR={sar[-2]:.4f}, RSI={rsi:.1f}).",
                invalidation="close가 SAR 아래로 하락 시 무효.",
                bull_case="Parabolic SAR 추세 전환 확인.",
                bear_case="추세 전환 실패 가능성.",
            )

        if turned_sell:
            high_conf = rsi > 40
            confidence = Confidence.HIGH if high_conf else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"SAR 상승→하락 전환 (SAR={sar[-2]:.4f}, RSI={rsi:.1f}).",
                invalidation="close가 SAR 위로 상승 시 무효.",
                bull_case="추세 전환 실패 가능성.",
                bear_case="Parabolic SAR 하락 추세 전환 확인.",
            )

        direction = "상승" if last_bull else "하락"
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=f"SAR {direction} 추세 지속 중 (전환 없음).",
            invalidation="",
        )
