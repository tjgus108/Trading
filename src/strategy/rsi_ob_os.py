"""
RSI Overbought/Oversold with Volume Confirmation 전략:
- RSI14 = 14기간 RSI
- vol_avg = volume.rolling(20).mean()

- BUY:  RSI14 < 30 (과매도) AND volume > vol_avg * 1.2
        AND RSI14 > RSI14.shift(1) (RSI 반전 시작)

- SELL: RSI14 > 70 (과매수) AND volume > vol_avg * 1.2
        AND RSI14 < RSI14.shift(1) (RSI 꺾임)

- confidence: HIGH if RSI14 < 25 or > 75, MEDIUM if < 30 or > 70
- 최소 데이터: 25행
"""

from typing import Optional

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 25
_RSI_PERIOD = 14
_VOL_PERIOD = 20
_VOL_MULT = 1.2
_RSI_OB = 70
_RSI_OS = 30
_RSI_HIGH_OB = 75
_RSI_HIGH_OS = 25


def _compute_rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = (-delta).clip(lower=0)
    avg_gain = gain.ewm(com=period - 1, adjust=False).mean()
    avg_loss = loss.ewm(com=period - 1, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, float("nan"))
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50.0)


class RSIOBOSStrategy(BaseStrategy):
    name = "rsi_ob_os"

    def generate(self, df: Optional[pd.DataFrame]) -> Signal:
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

        idx = len(df) - 2  # 마지막 완성 캔들

        rsi = _compute_rsi(df["close"], _RSI_PERIOD)
        vol_avg = df["volume"].rolling(_VOL_PERIOD).mean()

        rsi_now = float(rsi.iloc[idx])
        rsi_prev = float(rsi.iloc[idx - 1])
        vol_now = float(df["volume"].iloc[idx])
        vol_avg_now = float(vol_avg.iloc[idx])
        close_now = float(df["close"].iloc[idx])

        vol_confirmed = vol_now > vol_avg_now * _VOL_MULT
        rsi_turning_up = rsi_now > rsi_prev
        rsi_turning_down = rsi_now < rsi_prev

        # BUY: 과매도 + 볼륨 확인 + RSI 반전 시작
        if rsi_now < _RSI_OS and vol_confirmed and rsi_turning_up:
            conf = Confidence.HIGH if rsi_now < _RSI_HIGH_OS else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=close_now,
                reasoning=(
                    f"RSI 과매도 반전: RSI={rsi_now:.1f} < {_RSI_OS} (반전중), "
                    f"volume={vol_now:.0f} > vol_avg*1.2={vol_avg_now * _VOL_MULT:.0f}"
                ),
                invalidation=f"RSI < {_RSI_OS} 지속 또는 볼륨 감소",
                bull_case=f"RSI {rsi_now:.1f} 과매도 반전, 강한 볼륨 확인",
                bear_case="추세 반전 실패 가능성",
            )

        # SELL: 과매수 + 볼륨 확인 + RSI 꺾임
        if rsi_now > _RSI_OB and vol_confirmed and rsi_turning_down:
            conf = Confidence.HIGH if rsi_now > _RSI_HIGH_OB else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=close_now,
                reasoning=(
                    f"RSI 과매수 꺾임: RSI={rsi_now:.1f} > {_RSI_OB} (하락중), "
                    f"volume={vol_now:.0f} > vol_avg*1.2={vol_avg_now * _VOL_MULT:.0f}"
                ),
                invalidation=f"RSI > {_RSI_OB} 지속 또는 볼륨 감소",
                bull_case="단기 조정 후 재상승 가능성",
                bear_case=f"RSI {rsi_now:.1f} 과매수 꺾임, 강한 볼륨 확인",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=close_now,
            reasoning=(
                f"조건 미충족: RSI={rsi_now:.1f}, "
                f"vol_ratio={vol_now / vol_avg_now:.2f}x" if vol_avg_now > 0 else
                f"조건 미충족: RSI={rsi_now:.1f}"
            ),
            invalidation="",
            bull_case="",
            bear_case="",
        )
