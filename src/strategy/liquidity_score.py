"""
LiquidityScoreStrategy: 유동성 점수 기반 진입.
spread + volume + 변동성을 종합한 유동성 점수로 진입 판단.
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


class LiquidityScoreStrategy(BaseStrategy):
    name = "liquidity_score"

    MIN_ROWS = 20

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < self.MIN_ROWS:
            last_close = float(df["close"].iloc[-1]) if len(df) > 0 else 0.0
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=last_close,
                reasoning="데이터 부족: 최소 20행 필요",
                invalidation="",
            )

        close = df["close"]
        high = df["high"]
        low = df["low"]
        volume = df["volume"]

        # 유동성 지표 계산
        spread_proxy = (high - low) / close
        vol_score = volume / (volume.rolling(20, min_periods=1).mean() + 1e-10)
        price_impact = spread_proxy / (vol_score + 1e-10)
        liquidity_score = vol_score / (spread_proxy * 100 + 1e-10)
        liq_ma = liquidity_score.rolling(10, min_periods=1).mean()
        close_ma = close.ewm(span=10, adjust=False).mean()

        row = self._last(df)
        idx = len(df) - 2

        entry = float(row["close"])

        liq_val = float(liquidity_score.iloc[idx])
        liq_ma_val = float(liq_ma.iloc[idx])
        vol_score_val = float(vol_score.iloc[idx])
        close_ma_val = float(close_ma.iloc[idx])

        # NaN 체크
        if pd.isna(liq_val) or pd.isna(liq_ma_val) or pd.isna(vol_score_val) or pd.isna(close_ma_val):
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning="지표 NaN",
                invalidation="",
            )

        # Confidence
        if vol_score_val > 2.0 and liq_val > liq_ma_val * 1.5:
            conf = Confidence.HIGH
        else:
            conf = Confidence.MEDIUM

        liq_ok = liq_val > liq_ma_val
        vol_ok = vol_score_val > 1.2

        bull_case = (
            f"LiqScore={liq_val:.4f} > LiqMA={liq_ma_val:.4f}, "
            f"close={entry:.4f} > closeMA={close_ma_val:.4f}, VolScore={vol_score_val:.2f}"
        )
        bear_case = (
            f"LiqScore={liq_val:.4f} > LiqMA={liq_ma_val:.4f}, "
            f"close={entry:.4f} < closeMA={close_ma_val:.4f}, VolScore={vol_score_val:.2f}"
        )

        if liq_ok and entry > close_ma_val and vol_ok:
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"유동성 BUY: LiqScore={liq_val:.4f} > LiqMA={liq_ma_val:.4f}, "
                    f"close={entry:.4f} > closeMA={close_ma_val:.4f}, VolScore={vol_score_val:.2f}"
                ),
                invalidation=f"close < closeMA ({close_ma_val:.4f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )
        elif liq_ok and entry < close_ma_val and vol_ok:
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"유동성 SELL: LiqScore={liq_val:.4f} > LiqMA={liq_ma_val:.4f}, "
                    f"close={entry:.4f} < closeMA={close_ma_val:.4f}, VolScore={vol_score_val:.2f}"
                ),
                invalidation=f"close > closeMA ({close_ma_val:.4f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )
        else:
            reasons = []
            if not liq_ok:
                reasons.append(f"LiqScore={liq_val:.4f} <= LiqMA={liq_ma_val:.4f}")
            if not vol_ok:
                reasons.append(f"VolScore={vol_score_val:.2f} <= 1.2")
            return Signal(
                action=Action.HOLD,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"조건 미충족: {'; '.join(reasons)}",
                invalidation="",
                bull_case=bull_case,
                bear_case=bear_case,
            )
