"""
SupertrendMultiStrategy: 3개의 Supertrend 지표를 조합한 추세 추종 전략.

ENHANCED VERSION:
- Supertrend 3개: (ATR10, mult=1.5), (ATR14, mult=2.0), (ATR20, mult=3.0)
- BUY:  3개 모두 bullish (trend == 1) + ATR volatility threshold + trend age confirmation
- SELL: 3개 모두 bearish (trend == -1) + ATR volatility threshold + trend age confirmation
- confidence: 3개 모두 일치 AND volume > avg_vol * 1.1 AND ATR momentum good → HIGH
- 최소 행: 25
- ATR 필터: 평균 ATR 대비 현재 ATR >= 0.9x (과도한 volatility 피함)
- 추세 유지: 마지막 2봉 모두 같은 추세 방향 (거짓 신호 제거)
"""

from typing import List, Optional, Tuple

import numpy as np
import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


class SupertrendMultiStrategy(BaseStrategy):
    name = "supertrend_multi"

    # (atr_period, multiplier)
    CONFIGS: List[Tuple[int, float]] = [
        (10, 1.5),
        (14, 2.0),
        (20, 3.0),
    ]
    MIN_ROWS = 25

    def __init__(self, atr_threshold: float = 0.9) -> None:
        # Cycle 274: atr_threshold 파라미터화 (그리드 탐색 지원)
        self.atr_threshold = atr_threshold
        # (n_rows, close_last) → trend 배열 캐시: 동일 데이터 재계산 방지
        self._trend_cache: dict = {}

    def _compute_atr(self, df: pd.DataFrame, period: int) -> pd.Series:
        """True Range 기반 ATR 계산."""
        high = df["high"]
        low = df["low"]
        close = df["close"]
        prev_close = close.shift(1)
        tr = pd.concat(
            [high - low, (high - prev_close).abs(), (low - prev_close).abs()],
            axis=1,
        ).max(axis=1)
        atr = tr.ewm(alpha=1.0 / period, adjust=False).mean()
        return atr

    def _compute_supertrend_trend(
        self, df: pd.DataFrame, atr_period: int, mult: float, _cache_key: tuple = ()
    ) -> pd.Series:
        """
        trend 시리즈 반환: 1 = bullish, -1 = bearish.

        Supertrend 계산:
          basic_upper = (high+low)/2 + mult * atr
          basic_lower = (high+low)/2 - mult * atr
          final_upper/lower 추적 후 trend 결정.
        """
        import numpy as np

        hl2 = (df["high"] + df["low"]) / 2.0
        atr = self._compute_atr(df, atr_period)

        bu_arr = (hl2 + mult * atr).to_numpy(dtype=float)
        bl_arr = (hl2 - mult * atr).to_numpy(dtype=float)
        close_arr = df["close"].to_numpy(dtype=float)
        n = len(close_arr)

        fu = bu_arr.copy()
        fl = bl_arr.copy()
        trend = np.ones(n, dtype=np.int8)

        for i in range(1, n):
            c_prev = close_arr[i - 1]
            fu[i] = bu_arr[i] if (bu_arr[i] < fu[i - 1] or c_prev < fu[i - 1]) else fu[i - 1]
            fl[i] = bl_arr[i] if (bl_arr[i] > fl[i - 1] or c_prev > fl[i - 1]) else fl[i - 1]
            c = close_arr[i]
            if c > fu[i - 1]:
                trend[i] = 1
            elif c < fl[i - 1]:
                trend[i] = -1
            else:
                trend[i] = trend[i - 1]

        return pd.Series(trend, index=df.index, dtype=int)

    def _atr_filter_pass(self, df: pd.DataFrame) -> bool:
        """
        ATR 필터: 현재 ATR이 평균의 ATR_THRESHOLD 이상이어야 신호 생성.
        목표: 과도한 변동성 피하기 (거짓 신호 감소).
        """
        if len(df) < self.MIN_ROWS:
            return False
        
        atr = self._compute_atr(df, 14)
        lookback = min(20, len(df) - 2)
        avg_atr = float(atr.iloc[-lookback - 2: -2].mean())
        cur_atr = float(atr.iloc[-2])
        
        return avg_atr > 0 and cur_atr >= avg_atr * self.atr_threshold

    def _trend_confirmation_pass(self, trends_series: List[pd.Series]) -> bool:
        """
        추세 확인: 지난 2봉 모두 같은 추세 방향이어야 신호 생성.
        목표: 추세 전환 초기의 거짓 신호 제거.
        """
        if not trends_series:
            return False
        
        # 각 Supertrend의 마지막 2봉(iloc[-2], iloc[-1]) 추세 비교
        for trend_series in trends_series:
            if len(trend_series) < 2:
                return False
            
            # 마지막 완성봉(-2)과 현재봉(-1)의 추세가 모두 같아야 함
            t_minus_2 = int(trend_series.iloc[-2])
            t_minus_1 = int(trend_series.iloc[-1])
            
            if t_minus_2 != t_minus_1:
                return False
        
        return True

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < self.MIN_ROWS:
            return self._hold(df, f"데이터 부족: {len(df)} < {self.MIN_ROWS}")

        # ATR 필터 체크
        if not self._atr_filter_pass(df):
            return self._hold(df, "ATR 필터 미충족: 변동성 부족")

        # 각 Supertrend의 마지막 완성봉(-2) trend 값 계산
        # 미리 계산된 컬럼이 있으면 사용 (O(n²) 방지), 없으면 직접 계산
        trends_series: List[pd.Series] = []
        for atr_period, mult in self.CONFIGS:
            col = f"st_trend_{atr_period}_{str(mult).replace('.', '_')}"
            if col in df.columns:
                trends_series.append(df[col])
            else:
                trends_series.append(self._compute_supertrend_trend(df, atr_period, mult))

        # 마지막 완성봉 기준으로 추세 확인
        last_trends = [int(t.iloc[-2]) for t in trends_series]
        
        all_bullish = all(t == 1 for t in last_trends)
        all_bearish = all(t == -1 for t in last_trends)

        # 추세 확인 필터 (마지막 2봉 일치 여부)
        trend_confirmed = self._trend_confirmation_pass(trends_series)

        last = self._last(df)
        entry = float(last["close"])

        # 볼륨 필터
        vol_high = False
        vol_info = ""
        if "volume" in df.columns:
            lookback = min(20, len(df) - 2)
            avg_vol = float(df["volume"].iloc[-lookback - 2: -2].mean())
            cur_vol = float(df["volume"].iloc[-2])
            vol_high = avg_vol > 0 and cur_vol > avg_vol * 1.1
            vol_info = f" vol={cur_vol:.0f} avg={avg_vol:.0f}"

        trend_str = str(last_trends)

        if all_bullish and trend_confirmed:
            conf = Confidence.HIGH if vol_high else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"3개 Supertrend 모두 bullish + 추세 확인{vol_info}. trends={trend_str}",
                invalidation="Supertrend 중 하나라도 bearish 전환 시 무효",
                bull_case=f"ATR 기반 3중 bullish 확인 + 추세 연속성. trends={trend_str}",
                bear_case="추세 반전 가능성 존재",
            )

        if all_bearish and trend_confirmed:
            conf = Confidence.HIGH if vol_high else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"3개 Supertrend 모두 bearish + 추세 확인{vol_info}. trends={trend_str}",
                invalidation="Supertrend 중 하나라도 bullish 전환 시 무효",
                bull_case="추세 반전 가능성 존재",
                bear_case=f"ATR 기반 3중 bearish 확인 + 추세 연속성. trends={trend_str}",
            )

        if all_bullish or all_bearish:
            return self._hold(df, f"Supertrend 일치하지만 추세 확인 대기: trends={trend_str}")

        return self._hold(df, f"Supertrend 불일치: trends={trend_str}")

    def _hold(self, df: pd.DataFrame, reason: str) -> Signal:
        last = self._last(df)
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=float(last["close"]),
            reasoning=reason,
            invalidation="",
            bull_case="",
            bear_case="",
        )
