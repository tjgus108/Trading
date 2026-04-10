"""
SpreadAnalysis 전략:
- Bid-Ask Spread 추정 (High-Low / close) 으로 유동성 및 방향 판단
- BUY: low_spread AND close_pos > 0.7 AND close_pos > close_pos_ma
- SELL: low_spread AND close_pos < 0.3 AND close_pos < close_pos_ma
- Confidence: HIGH if spread_proxy < spread_ma * 0.6, else MEDIUM
- 최소 20행 필요
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 20


class SpreadAnalysisStrategy(BaseStrategy):
    name = "spread_analysis"

    def generate(self, df: pd.DataFrame) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning="Insufficient data for spread_analysis",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        idx = len(df) - 2

        high = df["high"]
        low = df["low"]
        close = df["close"]

        # 스프레드 프록시: 상대적 변동성
        spread_proxy = (high - low) / close
        spread_ma = spread_proxy.rolling(14).mean()

        # 가격 위치 (0~1)
        close_pos = (close - low) / (high - low + 1e-10)
        close_pos_ma = close_pos.rolling(5).mean()

        sp_now = spread_proxy.iloc[idx]
        sp_ma_now = spread_ma.iloc[idx]
        cp_now = close_pos.iloc[idx]
        cp_ma_now = close_pos_ma.iloc[idx]

        # NaN 체크
        if any(pd.isna(v) for v in [sp_now, sp_ma_now, cp_now, cp_ma_now]):
            entry = float(df["close"].iloc[idx])
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.MEDIUM,
                strategy=self.name,
                entry_price=entry,
                reasoning="NaN in spread analysis indicators",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        low_spread = sp_now < sp_ma_now * 0.8
        entry = float(df["close"].iloc[idx])
        conf = Confidence.HIGH if sp_now < sp_ma_now * 0.6 else Confidence.MEDIUM

        if low_spread and cp_now > 0.7 and cp_now > cp_ma_now:
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"낮은 스프레드+위쪽 마감+상승: "
                    f"spread={sp_now:.4f}<ma*0.8={sp_ma_now*0.8:.4f}, "
                    f"close_pos={cp_now:.2f}>0.7"
                ),
                invalidation="스프레드 확대 또는 close_pos < 0.5",
                bull_case="유동성 높고 매수세 강함",
                bear_case="단기 과매수 가능",
            )

        if low_spread and cp_now < 0.3 and cp_now < cp_ma_now:
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"낮은 스프레드+아래쪽 마감+하락: "
                    f"spread={sp_now:.4f}<ma*0.8={sp_ma_now*0.8:.4f}, "
                    f"close_pos={cp_now:.2f}<0.3"
                ),
                invalidation="스프레드 확대 또는 close_pos > 0.5",
                bull_case="단기 반등 가능",
                bear_case="유동성 높고 매도세 강함",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=(
                f"스프레드 조건 미충족: "
                f"spread={sp_now:.4f}, ma={sp_ma_now:.4f}, "
                f"close_pos={cp_now:.2f}"
            ),
            invalidation="",
            bull_case="",
            bear_case="",
        )
