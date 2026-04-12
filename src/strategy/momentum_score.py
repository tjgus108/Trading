"""
MomentumScore 전략:
- 다양한 모멘텀 지표 점수 합산 후 방향성 판단.
- score_up/score_down 각각 누적, BUY: score_up >= 4, SELL: score_down >= 4
- confidence: score >= 4.5 → HIGH, else MEDIUM
- 최소 행: 30
"""

from typing import Optional

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 30


def _rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss.replace(0, 1e-10)
    return 100 - (100 / (1 + rs))


def _ema(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(span=period, adjust=False).mean()


def _macd_hist(series: pd.Series) -> pd.Series:
    fast = _ema(series, 12)
    slow = _ema(series, 26)
    macd_line = fast - slow
    signal_line = _ema(macd_line, 9)
    return macd_line - signal_line


class MomentumScoreStrategy(BaseStrategy):
    name = "momentum_score"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            return self._hold(df, f"데이터 부족: {len(df)} < {_MIN_ROWS}")

        idx = len(df) - 2  # _last index

        close_series = df["close"]
        volume_series = df["volume"]

        rsi_val = float(_rsi(close_series).iloc[idx])
        hist_val = float(_macd_hist(close_series).iloc[idx])
        ema20_val = float(_ema(close_series, 20).iloc[idx])
        close_val = float(close_series.iloc[idx])
        close_5ago = float(close_series.iloc[idx - 5]) if idx >= 5 else close_val
        avg_vol = float(volume_series.iloc[max(0, idx - 20):idx].mean())
        vol_val = float(volume_series.iloc[idx])

        score_up = 0.0
        score_down = 0.0

        # RSI14
        if rsi_val > 55:
            score_up += 1
        elif rsi_val < 45:
            score_down += 1

        # MACD hist
        if hist_val > 0:
            score_up += 1
        elif hist_val < 0:
            score_down += 1

        # EMA20
        if close_val > ema20_val:
            score_up += 1
        elif close_val < ema20_val:
            score_down += 1

        # 5봉 모멘텀
        if close_val > close_5ago:
            score_up += 1
        elif close_val < close_5ago:
            score_down += 1

        # Volume
        if avg_vol > 0:
            if vol_val > avg_vol:
                score_up += 0.5
            elif vol_val < avg_vol:
                score_down += 0.5

        context = (
            f"close={close_val:.4f} RSI={rsi_val:.1f} MACD_hist={hist_val:.4f} "
            f"EMA20={ema20_val:.4f} close_5ago={close_5ago:.4f} "
            f"vol={vol_val:.0f} avg_vol={avg_vol:.0f} "
            f"score_up={score_up} score_down={score_down}"
        )

        if score_up >= 4:
            conf = Confidence.HIGH if score_up >= 4.5 else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=close_val,
                reasoning=f"모멘텀 점수 상승 우위: score_up={score_up}. {context}",
                invalidation="score_up이 4 미만으로 하락 시",
                bull_case=f"다중 모멘텀 상승 정렬 (score_up={score_up})",
                bear_case="모멘텀 약화 시 빠른 청산",
            )

        if score_down >= 4:
            conf = Confidence.HIGH if score_down >= 4.5 else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=close_val,
                reasoning=f"모멘텀 점수 하락 우위: score_down={score_down}. {context}",
                invalidation="score_down이 4 미만으로 하락 시",
                bull_case="모멘텀 회복 시 숏 포지션 청산",
                bear_case=f"다중 모멘텀 하락 정렬 (score_down={score_down})",
            )

        return self._hold(df, f"모멘텀 점수 신호 없음: {context}")

    def _hold(self, df: pd.DataFrame, reason: str) -> Signal:
        try:
            price = float(self._last(df)["close"])
        except Exception:
            price = 0.0
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=price,
            reasoning=reason,
            invalidation="",
        )
