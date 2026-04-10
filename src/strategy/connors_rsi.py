"""
Connors RSI (CRSI) 전략:
- CRSI = (RSI(3) + StreakRSI(2) + PercentRank(100)) / 3
  1. RSI(3): 단기 RSI (EWM)
  2. StreakRSI(2): 연속 상승/하락 일수의 RSI(2)
  3. PercentRank(100): 현재 수익률이 100일 중 몇 번째 퍼센타일

- BUY:  crsi crosses above 10 (이전 < 10, 현재 >= 10) — 극단 과매도 탈출
- SELL: crsi crosses below 90 (이전 > 90, 현재 <= 90) — 극단 과매수 이탈
- confidence: HIGH if crsi < 5 (BUY) or crsi > 95 (SELL) else MEDIUM
- 최소 110행 필요, idx = len(df) - 2
"""

from typing import Optional

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 110
_BUY_CROSS = 10.0
_SELL_CROSS = 90.0
_HIGH_CONF_LOW = 5.0
_HIGH_CONF_HIGH = 95.0


def _compute_streak(close: pd.Series) -> pd.Series:
    streak = pd.Series(0.0, index=close.index)
    for i in range(1, len(close)):
        if float(close.iloc[i]) > float(close.iloc[i - 1]):
            streak.iloc[i] = max(float(streak.iloc[i - 1]), 0) + 1
        elif float(close.iloc[i]) < float(close.iloc[i - 1]):
            streak.iloc[i] = min(float(streak.iloc[i - 1]), 0) - 1
        else:
            streak.iloc[i] = 0
    return streak


def _compute_crsi(df: pd.DataFrame) -> pd.Series:
    # 1. RSI(3)
    delta = df["close"].diff()
    gain3 = delta.clip(lower=0).ewm(com=2, adjust=False).mean()
    loss3 = (-delta.clip(upper=0)).ewm(com=2, adjust=False).mean()
    rsi3 = 100 - 100 / (1 + gain3 / loss3.replace(0, 1e-10))

    # 2. Streak RSI(2)
    streak = _compute_streak(df["close"])
    streak_delta = streak.diff()
    streak_gain = streak_delta.clip(lower=0).ewm(com=1, adjust=False).mean()
    streak_loss = (-streak_delta.clip(upper=0)).ewm(com=1, adjust=False).mean()
    streak_rsi = 100 - 100 / (1 + streak_gain / streak_loss.replace(0, 1e-10))

    # 3. ROC Percentile rank (100-period)
    roc1 = df["close"].pct_change(1) * 100
    pct_rank = roc1.rolling(100).apply(
        lambda x: (x[:-1] < x[-1]).sum() / max(len(x) - 1, 1) * 100, raw=True
    )

    crsi = (rsi3 + streak_rsi + pct_rank) / 3
    return crsi


class ConnorsRSIStrategy(BaseStrategy):
    """Connors RSI 극단 과매수/과매도 크로스오버 전략."""

    name = "connors_rsi"

    def generate(self, df: Optional[pd.DataFrame]) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            rows = len(df) if df is not None else 0
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning=f"Insufficient data: {rows} rows < {_MIN_ROWS} required",
                invalidation="충분한 히스토리 데이터 확보 후 재시도",
                bull_case="",
                bear_case="",
            )

        idx = len(df) - 2
        crsi = _compute_crsi(df)

        current = float(crsi.iloc[idx])
        prev = float(crsi.iloc[idx - 1])
        close = float(df["close"].iloc[idx])

        if pd.isna(current) or pd.isna(prev):
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=close,
                reasoning="CRSI 계산 불가 (NaN)",
                invalidation="지표 계산 가능 시점까지 대기",
                bull_case="",
                bear_case="",
            )

        # BUY: crosses above 10
        if prev < _BUY_CROSS and current >= _BUY_CROSS:
            conf = Confidence.HIGH if current < _HIGH_CONF_LOW else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"CRSI 극단 과매도 탈출: crsi={current:.1f} crosses above {_BUY_CROSS} "
                    f"(prev={prev:.1f})"
                ),
                invalidation=f"CRSI가 다시 {_BUY_CROSS} 아래로 하락 시 무효",
                bull_case=f"CRSI {current:.1f} 극단 과매도 탈출 — 반등 기대",
                bear_case="크로스가 노이즈일 가능성",
            )

        # SELL: crosses below 90
        if prev > _SELL_CROSS and current <= _SELL_CROSS:
            conf = Confidence.HIGH if current > _HIGH_CONF_HIGH else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"CRSI 극단 과매수 이탈: crsi={current:.1f} crosses below {_SELL_CROSS} "
                    f"(prev={prev:.1f})"
                ),
                invalidation=f"CRSI가 다시 {_SELL_CROSS} 위로 상승 시 무효",
                bull_case="단기 눌림 후 재상승 가능성",
                bear_case=f"CRSI {current:.1f} 극단 과매수 이탈 — 하락 기대",
            )

        # HOLD
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=close,
            reasoning=(
                f"CRSI={current:.1f}: 크로스 조건 미충족 (prev={prev:.1f})"
            ),
            invalidation="CRSI < 10 탈출 또는 CRSI > 90 이탈 시 재평가",
            bull_case="",
            bear_case="",
        )
