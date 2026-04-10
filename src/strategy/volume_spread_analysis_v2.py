"""
VolumeSpreadAnalysisV2Strategy: VSA (Volume Spread Analysis) v2 전략.

- spread = high - low
- spread_ma = spread.rolling(10, min_periods=1).mean()
- vol_ma = volume.rolling(10, min_periods=1).mean()
- close_position = (close - low) / (spread + 1e-10)  # 0~1
- wide_spread = spread > spread_ma * 1.2
- high_vol = volume > vol_ma * 1.2
- BUY:  wide_spread AND high_vol AND close_position > 0.7
- SELL: wide_spread AND high_vol AND close_position < 0.3
- confidence: HIGH if spread > spread_ma * 1.5 AND volume > vol_ma * 1.5 else MEDIUM
- 최소 행: 20
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 20
_WINDOW = 10


class VolumeSpreadAnalysisV2Strategy(BaseStrategy):
    name = "volume_spread_analysis_v2"

    def generate(self, df: pd.DataFrame) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
            entry = float(df["close"].iloc[-1]) if df is not None and len(df) > 0 else 0.0
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"데이터 부족 (최소 {_MIN_ROWS}행)",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        high = df["high"]
        low = df["low"]
        close = df["close"]
        volume = df["volume"]

        spread = high - low
        spread_ma = spread.rolling(_WINDOW, min_periods=1).mean()
        vol_ma = volume.rolling(_WINDOW, min_periods=1).mean()
        close_position = (close - low) / (spread + 1e-10)

        idx = len(df) - 2  # 마지막 완성 캔들 (_last(df) = df.iloc[-2])

        s = float(spread.iloc[idx])
        s_ma = float(spread_ma.iloc[idx])
        v = float(volume.iloc[idx])
        v_ma = float(vol_ma.iloc[idx])
        cp = float(close_position.iloc[idx])
        close_val = float(close.iloc[idx])

        # NaN 체크
        if pd.isna(s_ma) or pd.isna(v_ma) or pd.isna(cp):
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=close_val,
                reasoning="NaN 값 감지: 계산 불가",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        info = (
            f"spread={s:.4f}(ma={s_ma:.4f}), vol={v:.0f}(ma={v_ma:.0f}), "
            f"close_pos={cp:.3f}, close={close_val:.4f}"
        )

        wide_spread = s > s_ma * 1.2
        high_vol = v > v_ma * 1.2

        # HIGH confidence: 더 강한 조건
        high_conf = s > s_ma * 1.5 and v > v_ma * 1.5
        confidence = Confidence.HIGH if high_conf else Confidence.MEDIUM

        if wide_spread and high_vol and cp > 0.7:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_val,
                reasoning=f"VSA v2 BUY: 넓은 스프레드 + 고거래량 + 상단 종가. {info}",
                invalidation="종가가 스프레드 하단 근처로 전환 시 무효",
                bull_case="강한 매수 압력으로 상승 지속 예상",
                bear_case="가짜 돌파(Upthrust) 가능성",
            )

        if wide_spread and high_vol and cp < 0.3:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_val,
                reasoning=f"VSA v2 SELL: 넓은 스프레드 + 고거래량 + 하단 종가. {info}",
                invalidation="종가가 스프레드 상단 근처로 전환 시 무효",
                bull_case="매도 흡수(Shakeout) 이후 반등 가능",
                bear_case="강한 공급 압력으로 하락 지속 예상",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=close_val,
            reasoning=f"VSA v2 신호 없음. {info}",
            invalidation="",
            bull_case="",
            bear_case="",
        )
