"""
Connors RSI (CRSI) 전략:
- CRSI = (RSI(3) + StreakRSI(2) + PercentRank(100)) / 3
  1. RSI(3): 단기 RSI
  2. StreakRSI(2): 연속 상승/하락 일수의 RSI(2)
  3. PercentRank(100): 현재 수익률이 100일 중 몇 번째 퍼센타일
- BUY:  CRSI < 20 (과매도) AND CRSI 상승 중
- SELL: CRSI > 80 (과매수) AND CRSI 하락 중
- confidence: HIGH if CRSI < 10 or CRSI > 90, MEDIUM otherwise
- 최소 110행 필요, idx = len(df) - 2
"""

import numpy as np
import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 110
_BUY_THRESHOLD = 20.0
_SELL_THRESHOLD = 80.0
_HIGH_CONF_LOW = 10.0
_HIGH_CONF_HIGH = 90.0


def _rsi(series: pd.Series, period: int) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss.replace(0, 1e-10)
    return 100 - (100 / (1 + rs))


def _compute_streak(close_values: np.ndarray) -> np.ndarray:
    streak = np.zeros(len(close_values))
    for i in range(1, len(close_values)):
        if close_values[i] > close_values[i - 1]:
            streak[i] = streak[i - 1] + 1 if streak[i - 1] > 0 else 1
        elif close_values[i] < close_values[i - 1]:
            streak[i] = streak[i - 1] - 1 if streak[i - 1] < 0 else -1
        else:
            streak[i] = 0
    return streak


def _compute_crsi(df: pd.DataFrame) -> pd.Series:
    # Component 1: RSI(3)
    rsi3 = _rsi(df["close"], 3)

    # Component 2: Streak RSI(2)
    close = df["close"].values
    streak = _compute_streak(close)
    streak_series = pd.Series(streak, index=df.index)
    streak_rsi = _rsi(streak_series, 2)

    # Component 3: Percent Rank(100)
    roc_1 = df["close"].pct_change()
    pct_rank = roc_1.rolling(100).apply(
        lambda x: (x[:-1] < x[-1]).sum() / 99 * 100, raw=True
    )

    crsi = (rsi3 + streak_rsi + pct_rank) / 3
    return crsi


class ConnorsRSIStrategy(BaseStrategy):
    """Connors RSI 과매수/과매도 역추세 전략."""

    name = "connors_rsi"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=float(df["close"].iloc[-2]),
                reasoning=f"데이터 부족: {len(df)}행 < {_MIN_ROWS}행 필요",
                invalidation="충분한 히스토리 데이터 확보 후 재시도",
            )

        idx = len(df) - 2
        crsi = _compute_crsi(df)

        current_crsi = crsi.iloc[idx]
        prev_crsi = crsi.iloc[idx - 1]
        close = float(df["close"].iloc[idx])

        if pd.isna(current_crsi) or pd.isna(prev_crsi):
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=close,
                reasoning="CRSI 계산 불가 (NaN)",
                invalidation="지표 계산 가능 시점까지 대기",
            )

        crsi_rising = current_crsi > prev_crsi

        # Confidence 결정
        if current_crsi < _HIGH_CONF_LOW or current_crsi > _HIGH_CONF_HIGH:
            confidence = Confidence.HIGH
        else:
            confidence = Confidence.MEDIUM

        # BUY: 과매도 + 상승 반전
        if current_crsi < _BUY_THRESHOLD and crsi_rising:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"CRSI={current_crsi:.1f} < {_BUY_THRESHOLD} (과매도) "
                    f"AND 상승 전환 (prev={prev_crsi:.1f})"
                ),
                invalidation=f"CRSI가 다시 {_BUY_THRESHOLD} 아래로 하락 시 무효",
                bull_case="단기 과매도 반등 기대",
                bear_case="추세 하락 지속 시 손실 가능",
            )

        # SELL: 과매수 + 하락 반전
        if current_crsi > _SELL_THRESHOLD and not crsi_rising:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"CRSI={current_crsi:.1f} > {_SELL_THRESHOLD} (과매수) "
                    f"AND 하락 전환 (prev={prev_crsi:.1f})"
                ),
                invalidation=f"CRSI가 다시 {_SELL_THRESHOLD} 위로 상승 시 무효",
                bull_case="단기 눌림 후 추가 상승 가능",
                bear_case="과매수 해소 하락 기대",
            )

        # HOLD
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=close,
            reasoning=(
                f"CRSI={current_crsi:.1f}: 매수/매도 조건 미충족 "
                f"(방향={'상승' if crsi_rising else '하락'})"
            ),
            invalidation="CRSI < 20 반등 또는 CRSI > 80 하락 시 재평가",
        )
