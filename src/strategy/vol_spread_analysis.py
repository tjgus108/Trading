"""
VolSpreadAnalysisStrategy: VSA (Volume Spread Analysis) 전략.
- 가격 스프레드 + 볼륨 상호작용 분석
- Upthrust bar (공급 과잉): spread 큼 + volume 큼 + close near low → SELL
- Test for supply (매도 세력 없음): spread 작음 + volume 작음 + close near high → BUY
- confidence: 볼륨 극단값 (> 2x avg or < 0.5x avg) → HIGH
- 최소 행: 25
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 25
_SPREAD_WINDOW = 20
_VOL_WINDOW = 20

# Upthrust 기준
_UPTHRUST_SPREAD_MULT = 1.5
_UPTHRUST_VOL_MULT = 1.5
_UPTHRUST_CLOSE_RATIO = 0.3  # (close - low) / spread < 0.3

# Test for supply 기준
_TEST_SPREAD_MULT = 0.7
_TEST_VOL_MULT = 0.7
_TEST_CLOSE_RATIO = 0.7  # (close - low) / spread > 0.7

# HIGH confidence 기준
_VOL_HIGH_MULT = 2.0
_VOL_LOW_MULT = 0.5


class VolSpreadAnalysisStrategy(BaseStrategy):
    name = "vol_spread_analysis"

    def generate(self, df: pd.DataFrame) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            entry = float(df["close"].iloc[-1]) if df is not None and len(df) > 0 else 0.0
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"데이터 부족 (최소 {_MIN_ROWS}행).",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        spread = df["high"] - df["low"]
        volume = df["volume"]

        avg_spread = spread.rolling(_SPREAD_WINDOW).mean()
        avg_vol = volume.rolling(_VOL_WINDOW).mean()

        close_ratio = (df["close"] - df["low"]) / spread.replace(0, float("nan"))

        last_idx = -2  # _last(df) = df.iloc[-2]
        last = self._last(df)

        s = float(spread.iloc[last_idx])
        v = float(volume.iloc[last_idx])
        avg_s = float(avg_spread.iloc[last_idx])
        avg_v = float(avg_vol.iloc[last_idx])
        cr = float(close_ratio.iloc[last_idx])
        close_val = float(last["close"])
        high_val = float(last["high"])
        low_val = float(last["low"])

        reasoning_base = (
            f"spread={s:.4f}(avg={avg_s:.4f}), vol={v:.0f}(avg={avg_v:.0f}), "
            f"close_ratio={cr:.3f}, close={close_val:.4f}"
        )

        if pd.isna(avg_s) or pd.isna(avg_v) or pd.isna(cr):
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=close_val,
                reasoning="평균 계산 불가 (NaN).",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        upthrust = (
            s > avg_s * _UPTHRUST_SPREAD_MULT
            and v > avg_v * _UPTHRUST_VOL_MULT
            and cr < _UPTHRUST_CLOSE_RATIO
        )

        test_supply = (
            s < avg_s * _TEST_SPREAD_MULT
            and v < avg_v * _TEST_VOL_MULT
            and cr > _TEST_CLOSE_RATIO
        )

        # HIGH confidence: 볼륨이 극단적으로 크거나 작을 때
        vol_extreme = v > avg_v * _VOL_HIGH_MULT or v < avg_v * _VOL_LOW_MULT
        confidence = Confidence.HIGH if vol_extreme else Confidence.MEDIUM

        if upthrust:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_val,
                reasoning=f"Upthrust bar: 공급 과잉 신호. {reasoning_base}",
                invalidation="close가 고점 근처 유지 시 신호 무효.",
                bull_case="Upthrust 실패 시 강한 상승 반전 가능.",
                bear_case=f"공급 과잉으로 하락 압력 우세.",
            )

        if test_supply:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_val,
                reasoning=f"Test for supply: 매도 세력 없음, 상승 예상. {reasoning_base}",
                invalidation="볼륨 급증 + close 저가 근처 전환 시 무효.",
                bull_case=f"매도 세력 부재 확인, 상승 추세 지속 예상.",
                bear_case="추가 공급 출현 시 반전 위험.",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=close_val,
            reasoning=f"VSA 신호 없음. {reasoning_base}",
            invalidation="",
            bull_case="",
            bear_case="",
        )
