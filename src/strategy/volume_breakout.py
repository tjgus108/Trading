"""
Volume Breakout 전략 (개선 v3):
- ATR 필터: 극단적 변동성만 필터 (범위 확대)
- 추세 필터: EMA 추세는 confidence에만 영향 (신호 조건에서 제외 → 거래 빈도 증가)
- Volume Spike: 1.5x (공격적)
- 핵심 조건: spike + 양봉/음봉 + close vs ema20 + ATR 유효 (4조건)
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 50  # EMA50 필요
_VOL_LOOKBACK = 20
_SPIKE_MULT = 1.5  # 1.8 → 1.5 (더 공격적)
_HIGH_CONF_MULT = 2.2  # 2.5 → 2.2
# ATR 필터: 절대값 대신 가격 대비 비율 사용 (BTC 등 고가 자산 호환)
_ATR_LOW_PCT = 0.001   # ATR/price 최소 0.1% (극저변동성 제외)
_ATR_HIGH_PCT = 0.10   # ATR/price 최대 10% (극고변동성 제외)


class VolumeBreakoutStrategy(BaseStrategy):
    name = "volume_breakout"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, "Insufficient data")

        last = self._last(df)
        close = float(last["close"])
        open_ = float(last["open"])
        volume = float(last["volume"])
        ema20 = float(last["ema20"])
        ema50 = float(last.get("ema50", close))
        atr14 = float(last.get("atr14", 1.0))

        avg_vol = float(df["volume"].iloc[-_VOL_LOOKBACK - 2 : -2].mean())
        spike = volume > avg_vol * _SPIKE_MULT
        bull_candle = close > open_
        bear_candle = close < open_
        above_ema = close > ema20
        below_ema = close < ema20

        # ATR 필터: 가격 대비 비율로 체크 (고가 자산 호환)
        atr_pct = atr14 / close if close > 0 else 0
        atr_valid = _ATR_LOW_PCT <= atr_pct <= _ATR_HIGH_PCT

        # 추세 필터: confidence 판단에만 사용 (신호 조건에서 제외)
        uptrend = ema20 > ema50
        downtrend = ema20 < ema50

        bull_case = f"close={close:.2f} open={open_:.2f} ema20={ema20:.2f} ema50={ema50:.2f} vol={volume:.0f} atr={atr14:.2f}"
        bear_case = bull_case

        # BUY: spike + 양봉 + close>ema20 + ATR 유효 (4조건)
        # 추세 일치 시 confidence 상승
        if spike and bull_candle and above_ema and atr_valid:
            if volume > avg_vol * _HIGH_CONF_MULT and uptrend:
                confidence = Confidence.HIGH
            elif uptrend:
                confidence = Confidence.MEDIUM
            else:
                confidence = Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=f"Vol breakout BUY: vol={volume:.0f}>avg*{_SPIKE_MULT}({avg_vol*_SPIKE_MULT:.0f}), 양봉, close({close:.2f})>ema20({ema20:.2f}), atr={atr14:.2f}",
                invalidation=f"Close below EMA20 ({ema20:.2f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        # SELL: spike + 음봉 + close<ema20 + ATR 유효 (4조건)
        if spike and bear_candle and below_ema and atr_valid:
            if volume > avg_vol * _HIGH_CONF_MULT and downtrend:
                confidence = Confidence.HIGH
            elif downtrend:
                confidence = Confidence.MEDIUM
            else:
                confidence = Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=f"Vol breakout SELL: vol={volume:.0f}>avg*{_SPIKE_MULT}({avg_vol*_SPIKE_MULT:.0f}), 음봉, close({close:.2f})<ema20({ema20:.2f}), atr={atr14:.2f}",
                invalidation=f"Close above EMA20 ({ema20:.2f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        return self._hold(df, f"No signal: vol={volume:.0f} avg={avg_vol:.0f} spike={spike}", bull_case, bear_case)

    def _hold(self, df: pd.DataFrame, reason: str,
              bull_case: str = "", bear_case: str = "") -> Signal:
        last = self._last(df)
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=float(last["close"]),
            reasoning=reason,
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
