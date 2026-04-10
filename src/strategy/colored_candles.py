"""
ColoredCandles 전략.

연속 색깔 캔들 패턴: 연속 양봉/음봉 + 거래량 확인.

  bullish = (close > open) = 1 (양봉)
  bearish = (close < open) = 1 (음봉)
  bull_run = 최근 4봉 중 양봉 수
  bear_run = 최근 4봉 중 음봉 수
  vol_ma = volume 10기간 이동평균
  vol_increasing = volume > volume.shift(1)

BUY:  bull_run >= 3 AND vol_increasing AND volume > vol_ma
SELL: bear_run >= 3 AND vol_increasing AND volume > vol_ma

confidence:
  HIGH   if bull_run == 4 (BUY) or bear_run == 4 (SELL)
  MEDIUM 그 외

최소 데이터: 20행
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 20


class ColoredCandlesStrategy(BaseStrategy):
    name = "colored_candles"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data for ColoredCandles (need 20 rows)")

        idx = len(df) - 2  # _last() = iloc[-2]

        close = df["close"]
        open_ = df["open"]
        volume = df["volume"]

        bullish = (close > open_).astype(int)
        bearish = (close < open_).astype(int)

        bull_run = bullish.rolling(4, min_periods=1).sum()
        bear_run = bearish.rolling(4, min_periods=1).sum()

        vol_ma = volume.rolling(10, min_periods=1).mean()
        vol_increasing = (volume > volume.shift(1)).astype(int)

        br_now = float(bull_run.iloc[idx])
        ber_now = float(bear_run.iloc[idx])
        vi_now = bool(vol_increasing.iloc[idx])
        vol_now = float(volume.iloc[idx])
        vol_ma_now = float(vol_ma.iloc[idx])
        close_now = float(close.iloc[idx])

        # NaN 체크
        if pd.isna(br_now) or pd.isna(ber_now) or pd.isna(vol_ma_now):
            return self._hold(df, "NaN in indicators")

        context = (
            f"close={close_now:.4f} bull_run={br_now:.0f} bear_run={ber_now:.0f} "
            f"vol={vol_now:.0f} vol_ma={vol_ma_now:.0f} vol_increasing={vi_now}"
        )

        # BUY: bull_run >= 3 AND vol_increasing AND volume > vol_ma
        if br_now >= 3 and vi_now and vol_now > vol_ma_now:
            confidence = Confidence.HIGH if br_now == 4 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_now,
                reasoning=(
                    f"ColoredCandles BUY: 연속 양봉 {br_now:.0f}개 + 거래량 증가 "
                    f"(bull_run={br_now:.0f}, vol={vol_now:.0f})"
                ),
                invalidation="음봉 전환 또는 거래량 감소",
                bull_case=context,
                bear_case=context,
            )

        # SELL: bear_run >= 3 AND vol_increasing AND volume > vol_ma
        if ber_now >= 3 and vi_now and vol_now > vol_ma_now:
            confidence = Confidence.HIGH if ber_now == 4 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_now,
                reasoning=(
                    f"ColoredCandles SELL: 연속 음봉 {ber_now:.0f}개 + 거래량 증가 "
                    f"(bear_run={ber_now:.0f}, vol={vol_now:.0f})"
                ),
                invalidation="양봉 전환 또는 거래량 감소",
                bull_case=context,
                bear_case=context,
            )

        return self._hold(
            df,
            f"No signal: bull_run={br_now:.0f} bear_run={ber_now:.0f} vol_increasing={vi_now}",
            context,
            context,
        )

    def _hold(
        self,
        df: pd.DataFrame,
        reason: str,
        bull_case: str = "",
        bear_case: str = "",
    ) -> Signal:
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
