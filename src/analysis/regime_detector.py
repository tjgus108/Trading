"""
SimpleRegimeDetector: EMA50 기울기로 시장 레짐(bull/bear/sideways)을 감지.
"""

import pandas as pd


class SimpleRegimeDetector:
    """EMA50 기울기로 bull/bear/sideways 판단."""

    SLOPE_THRESHOLD = 0.001  # 0.1%

    @staticmethod
    def detect(df: pd.DataFrame, lookback: int = 20) -> str:
        """
        Returns:
            "bull"     — 최근 20봉 EMA50 기울기 > +0.001%
            "bear"     — 최근 20봉 EMA50 기울기 < -0.001%
            "sideways" — 그 외
            "unknown"  — 데이터 부족 (EMA50 계산 불가)
        """
        if df is None or len(df) < 50:
            return "unknown"

        ema50 = df["close"].ewm(span=50, adjust=False).mean()

        window = ema50.iloc[-lookback:]
        if len(window) < 2:
            return "unknown"

        start_val = window.iloc[0]
        end_val = window.iloc[-1]

        if start_val == 0:
            return "unknown"

        slope_pct = (end_val - start_val) / start_val

        if slope_pct > SimpleRegimeDetector.SLOPE_THRESHOLD:
            return "bull"
        elif slope_pct < -SimpleRegimeDetector.SLOPE_THRESHOLD:
            return "bear"
        else:
            return "sideways"
