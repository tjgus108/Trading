"""
VolumeMomentumStrategy:
- Volume_Momentum = volume.pct_change(5)  (5봉 대비 거래량 변화율)
- Vol_MA = volume.rolling(20).mean()
- Price_Mom = close.pct_change(5)
- BUY:  Price_Mom > 0.01 AND Volume_Momentum > 0.3 AND close > Vol_MA
- SELL: Price_Mom < -0.01 AND Volume_Momentum > 0.3 AND close < Vol_MA
- confidence: HIGH if Volume_Momentum > 0.6 AND |Price_Mom| > 0.02
- 최소 데이터: 25행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 25
_PRICE_MOM_BUY = 0.01
_PRICE_MOM_SELL = -0.01
_VOL_MOM_THRESH = 0.3
_HIGH_VOL_MOM = 0.6
_HIGH_PRICE_MOM = 0.02


class VolumeMomentumStrategy(BaseStrategy):
    name = "volume_momentum"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        vol_mom = df["volume"].pct_change(5)
        vol_ma = df["volume"].rolling(20).mean()
        price_mom = df["close"].pct_change(5)

        # iloc[-2]: 마지막 완성 봉
        curr_vol_mom = float(vol_mom.iloc[-2])
        curr_vol_ma = float(vol_ma.iloc[-2])
        curr_price_mom = float(price_mom.iloc[-2])

        if pd.isna(curr_vol_mom) or pd.isna(curr_vol_ma) or pd.isna(curr_price_mom):
            return self._hold(df, "Volume Momentum: NaN (데이터 부족)")

        last = self._last(df)
        close = float(last["close"])
        volume = float(last["volume"])

        context = (
            f"close={close:.2f} price_mom={curr_price_mom:.4f} "
            f"vol_mom={curr_vol_mom:.4f} vol_ma={curr_vol_ma:.2f} vol={volume:.0f}"
        )

        vol_surge = curr_vol_mom > _VOL_MOM_THRESH
        above_vol_ma = close > curr_vol_ma
        below_vol_ma = close < curr_vol_ma

        # BUY: 가격 상승 + 거래량 급증 + 가격이 Vol_MA 위
        if curr_price_mom > _PRICE_MOM_BUY and vol_surge and above_vol_ma:
            high_conf = curr_vol_mom > _HIGH_VOL_MOM and curr_price_mom > _HIGH_PRICE_MOM
            confidence = Confidence.HIGH if high_conf else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"Volume Momentum BUY: price_mom={curr_price_mom:.4f}>{_PRICE_MOM_BUY} "
                    f"vol_mom={curr_vol_mom:.4f}>{_VOL_MOM_THRESH} close>vol_ma"
                ),
                invalidation=f"price_mom <= 0 또는 vol_mom <= {_VOL_MOM_THRESH}",
                bull_case=context,
                bear_case=context,
            )

        # SELL: 가격 하락 + 거래량 급증 + 가격이 Vol_MA 아래
        if curr_price_mom < _PRICE_MOM_SELL and vol_surge and below_vol_ma:
            high_conf = curr_vol_mom > _HIGH_VOL_MOM and curr_price_mom < -_HIGH_PRICE_MOM
            confidence = Confidence.HIGH if high_conf else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"Volume Momentum SELL: price_mom={curr_price_mom:.4f}<{_PRICE_MOM_SELL} "
                    f"vol_mom={curr_vol_mom:.4f}>{_VOL_MOM_THRESH} close<vol_ma"
                ),
                invalidation=f"price_mom >= 0 또는 vol_mom <= {_VOL_MOM_THRESH}",
                bull_case=context,
                bear_case=context,
            )

        return self._hold(df, f"No signal: {context}", context, context)

    def _hold(self, df: pd.DataFrame, reason: str,
              bull_case: str = "", bear_case: str = "") -> Signal:
        try:
            close = float(self._last(df)["close"])
        except Exception:
            close = 0.0
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=close,
            reasoning=reason,
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
