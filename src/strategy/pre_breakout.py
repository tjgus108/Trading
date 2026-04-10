"""
PreBreakoutStrategy: 돌파 직전 수축 패턴 감지 (VCP 유사하지만 다른 방식).

range_ratio = ATR14 / ATR14.rolling(20).mean()
Contraction:     range_ratio < 0.7  (평균보다 30% 이상 수축)
Vol contraction: volume < volume.rolling(20).mean() * 0.8

BUY:  contraction AND vol_contraction AND close > SMA50
SELL: contraction AND vol_contraction AND close < SMA50

confidence: range_ratio < 0.5 AND volume < avg_vol * 0.6 → HIGH, 그 외 MEDIUM
최소 행: 25
"""

import numpy as np
import pandas as pd
from typing import Optional

from .base import Action, BaseStrategy, Confidence, Signal

MIN_ROWS = 25
ATR_PERIOD = 14
VOL_PERIOD = 20
CONTRACTION_THRESH = 0.7
VOL_CONTRACTION_THRESH = 0.8
HIGH_CONF_RATIO = 0.5
HIGH_CONF_VOL = 0.6


def _compute_atr(df: pd.DataFrame, idx: int) -> float:
    """ATR14 at index idx."""
    high_s = df["high"].iloc[idx - ATR_PERIOD + 1: idx + 1].values
    low_s = df["low"].iloc[idx - ATR_PERIOD + 1: idx + 1].values
    prev_close_s = df["close"].iloc[idx - ATR_PERIOD: idx].values

    tr = np.maximum(
        high_s - low_s,
        np.maximum(
            np.abs(high_s - prev_close_s),
            np.abs(low_s - prev_close_s),
        )
    )
    return float(tr.mean())


class PreBreakoutStrategy(BaseStrategy):
    name = "pre_breakout"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < MIN_ROWS:
            last_close = float(df["close"].iloc[-1]) if len(df) > 0 else 0.0
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=last_close,
                reasoning="데이터 부족: 최소 25행 필요",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        idx = len(df) - 2  # _last = iloc[-2]

        # ATR14 series: 각 idx마다 계산 (마지막 20개)
        atr_vals = []
        for i in range(idx - VOL_PERIOD + 1, idx + 1):
            if i < ATR_PERIOD:
                atr_vals.append(float("nan"))
            else:
                atr_vals.append(_compute_atr(df, i))

        atr_series = pd.Series(atr_vals)
        current_atr = atr_series.iloc[-1]
        avg_atr = float(atr_series.mean(skipna=True))

        # range_ratio
        range_ratio = current_atr / max(avg_atr, 1e-10)

        # 볼륨 (마지막 완성봉 기준)
        current_vol = float(df["volume"].iloc[idx])
        avg_vol = float(df["volume"].iloc[idx - VOL_PERIOD + 1: idx + 1].mean())

        # SMA50
        sma50_window = df["close"].iloc[max(0, idx - 49): idx + 1]
        sma50 = float(sma50_window.mean())

        close = float(df["close"].iloc[idx])

        contraction = range_ratio < CONTRACTION_THRESH
        vol_contraction = current_vol < avg_vol * VOL_CONTRACTION_THRESH
        high_conf = range_ratio < HIGH_CONF_RATIO and current_vol < avg_vol * HIGH_CONF_VOL

        confidence = Confidence.HIGH if high_conf else Confidence.MEDIUM

        bull_case = (
            f"수축 패턴: range_ratio={range_ratio:.3f} < {CONTRACTION_THRESH}, "
            f"vol_ratio={current_vol / max(avg_vol, 1e-10):.3f} < {VOL_CONTRACTION_THRESH}, "
            f"close={close:.4f} > SMA50={sma50:.4f}"
        )
        bear_case = (
            f"수축 패턴: range_ratio={range_ratio:.3f} < {CONTRACTION_THRESH}, "
            f"vol_ratio={current_vol / max(avg_vol, 1e-10):.3f} < {VOL_CONTRACTION_THRESH}, "
            f"close={close:.4f} < SMA50={sma50:.4f}"
        )

        if contraction and vol_contraction:
            if close > sma50:
                return Signal(
                    action=Action.BUY,
                    confidence=confidence,
                    strategy=self.name,
                    entry_price=close,
                    reasoning=(
                        f"PreBreakout BUY: 변동성 수축(range_ratio={range_ratio:.3f}), "
                        f"거래량 수축(vol_ratio={current_vol / max(avg_vol, 1e-10):.3f}), "
                        f"상방 방향(close={close:.4f} > SMA50={sma50:.4f})"
                    ),
                    invalidation=f"range_ratio >= {CONTRACTION_THRESH} 또는 close < SMA50({sma50:.4f})",
                    bull_case=bull_case,
                    bear_case=bear_case,
                )
            else:
                return Signal(
                    action=Action.SELL,
                    confidence=confidence,
                    strategy=self.name,
                    entry_price=close,
                    reasoning=(
                        f"PreBreakout SELL: 변동성 수축(range_ratio={range_ratio:.3f}), "
                        f"거래량 수축(vol_ratio={current_vol / max(avg_vol, 1e-10):.3f}), "
                        f"하방 방향(close={close:.4f} < SMA50={sma50:.4f})"
                    ),
                    invalidation=f"range_ratio >= {CONTRACTION_THRESH} 또는 close > SMA50({sma50:.4f})",
                    bull_case=bull_case,
                    bear_case=bear_case,
                )

        reason_parts = []
        if not contraction:
            reason_parts.append(f"변동성 미수축(range_ratio={range_ratio:.3f} >= {CONTRACTION_THRESH})")
        if not vol_contraction:
            reason_parts.append(
                f"거래량 미수축(vol_ratio={current_vol / max(avg_vol, 1e-10):.3f} >= {VOL_CONTRACTION_THRESH})"
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=close,
            reasoning="수축 조건 미충족: " + ", ".join(reason_parts),
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
