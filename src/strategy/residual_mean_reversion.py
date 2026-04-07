"""
A2. BTC-Neutral 잔차 평균회귀 전략.

원리: 알트코인 수익률에서 BTC 영향을 제거(rolling OLS regression)한 뒤
      잔차(residual)의 z-score가 ±2를 넘으면 평균 회귀 방향으로 진입.

  residual = altcoin_return - (alpha + beta * btc_return)
  z-score > +2 → SELL (잔차 과열, 하락 기대)
  z-score < -2 → BUY  (잔차 과냉, 상승 기대)

실증: Sharpe 2.3 (2021년 이후 특히 강함, Medium briplotnik)

사용법:
  strategy = ResidualMeanReversionStrategy()
  strategy.set_btc_data(btc_df)   # orchestrator가 BTC 데이터 주입
  signal = strategy.generate(alt_df)

BTC 데이터가 없으면 df 내부 returns 기반 단순 z-score 평균회귀로 fallback.
"""

import logging
from typing import Optional

import numpy as np
import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

logger = logging.getLogger(__name__)

ZSCORE_ENTRY = 2.0    # 진입 임계값
ZSCORE_STRONG = 2.5   # 강한 신호 임계값
ROLLING_WINDOW = 30   # rolling regression 윈도우 (캔들 수)


class ResidualMeanReversionStrategy(BaseStrategy):
    """
    BTC 중립 잔차 평균회귀 전략.

    set_btc_data()로 BTC OHLCV DataFrame을 주입한다.
    BTC 데이터 없으면 returns z-score fallback.
    """

    name = "residual_mean_reversion"

    def __init__(
        self,
        window: int = ROLLING_WINDOW,
        entry_zscore: float = ZSCORE_ENTRY,
    ):
        self.window = window
        self.entry_zscore = entry_zscore
        self._btc_df: Optional[pd.DataFrame] = None

    def set_btc_data(self, btc_df: pd.DataFrame) -> None:
        """BTC close 데이터 주입. orchestrator가 alt generate() 전에 호출."""
        self._btc_df = btc_df
        logger.debug("BTC reference data set: %d rows", len(btc_df))

    def generate(self, df: pd.DataFrame) -> Signal:
        last = self._last(df)
        entry = last["close"]
        rsi = last["rsi14"]

        if self._btc_df is not None and len(self._btc_df) >= self.window + 2:
            return self._signal_with_btc(df, entry, rsi)
        else:
            return self._fallback_signal(df, entry, rsi)

    # ------------------------------------------------------------------
    # BTC-neutral residual computation
    # ------------------------------------------------------------------

    def _compute_residual_zscore(self, alt_df: pd.DataFrame, btc_df: pd.DataFrame) -> float:
        """Rolling OLS로 BTC 베타 제거 후 최신 잔차 z-score 반환."""
        # 공통 인덱스 정렬
        alt_ret = alt_df["close"].pct_change().dropna()
        btc_ret = btc_df["close"].pct_change().dropna()
        common_idx = alt_ret.index.intersection(btc_ret.index)

        if len(common_idx) < self.window + 1:
            return 0.0

        alt_ret = alt_ret.loc[common_idx]
        btc_ret = btc_ret.loc[common_idx]

        # 최근 window+1 개
        alt_w = alt_ret.iloc[-(self.window + 1):].values
        btc_w = btc_ret.iloc[-(self.window + 1):].values

        # 현재 기간 residuals (rolling window)
        residuals = []
        for i in range(self.window):
            a_slice = alt_w[:i + 1]
            b_slice = btc_w[:i + 1]
            if len(a_slice) < 3:
                residuals.append(0.0)
                continue
            beta, alpha = np.polyfit(b_slice, a_slice, 1)
            pred = alpha + beta * b_slice[-1]
            residuals.append(a_slice[-1] - pred)

        residuals = np.array(residuals)
        if residuals.std() < 1e-10:
            return 0.0

        zscore = (residuals[-1] - residuals.mean()) / residuals.std()
        return float(zscore)

    def _signal_with_btc(self, alt_df: pd.DataFrame, entry: float, rsi: float) -> Signal:
        try:
            z = self._compute_residual_zscore(alt_df, self._btc_df)
        except Exception as e:
            logger.warning("Residual z-score 계산 실패: %s", e)
            return self._fallback_signal(alt_df, entry, rsi)

        bull_case = f"잔차 z-score={z:.2f} < -{self.entry_zscore}: BTC 대비 저평가 → 롱"
        bear_case = f"잔차 z-score={z:.2f} > +{self.entry_zscore}: BTC 대비 고평가 → 숏"

        if z > ZSCORE_STRONG:
            return Signal(
                action=Action.SELL,
                confidence=Confidence.HIGH,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"잔차 z={z:.2f} > {ZSCORE_STRONG}: 강한 과열 → 평균 회귀 매도",
                invalidation=f"z-score < {self.entry_zscore} 또는 RSI > 75",
                bull_case=bull_case,
                bear_case=bear_case,
            )
        if z > self.entry_zscore:
            return Signal(
                action=Action.SELL,
                confidence=Confidence.MEDIUM,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"잔차 z={z:.2f} > {self.entry_zscore}: 과열 → 평균 회귀 매도",
                invalidation=f"z-score < 1.0",
                bull_case=bull_case,
                bear_case=bear_case,
            )
        if z < -ZSCORE_STRONG:
            return Signal(
                action=Action.BUY,
                confidence=Confidence.HIGH,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"잔차 z={z:.2f} < -{ZSCORE_STRONG}: 강한 과냉 → 평균 회귀 매수",
                invalidation=f"z-score > -{self.entry_zscore} 또는 RSI < 25",
                bull_case=bull_case,
                bear_case=bear_case,
            )
        if z < -self.entry_zscore:
            return Signal(
                action=Action.BUY,
                confidence=Confidence.MEDIUM,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"잔차 z={z:.2f} < -{self.entry_zscore}: 과냉 → 평균 회귀 매수",
                invalidation=f"z-score > -1.0",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.HIGH,
            strategy=self.name,
            entry_price=entry,
            reasoning=f"잔차 z={z:.2f}: ±{self.entry_zscore} 범위 내 → 중립",
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )

    # ------------------------------------------------------------------
    # Fallback: BTC 데이터 없을 때 단순 returns z-score
    # ------------------------------------------------------------------

    def _fallback_signal(self, df: pd.DataFrame, entry: float, rsi: float) -> Signal:
        """BTC 데이터 없을 때: 수익률 자체 z-score 평균회귀 (보수적)."""
        ret = df["close"].pct_change().dropna()
        if len(ret) < self.window:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning="데이터 부족 (fallback)",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        recent = ret.iloc[-self.window:]
        z = float((recent.iloc[-1] - recent.mean()) / recent.std()) if recent.std() > 0 else 0.0

        note = f"BTC 데이터 없음, returns z-score={z:.2f} 사용 (보수적)"

        if z > self.entry_zscore:
            return Signal(
                action=Action.SELL,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning=note,
                invalidation="z-score < 1.0",
                bull_case="",
                bear_case=note,
            )
        if z < -self.entry_zscore:
            return Signal(
                action=Action.BUY,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning=note,
                invalidation="z-score > -1.0",
                bull_case=note,
                bear_case="",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=entry,
            reasoning=f"BTC 없음, returns z={z:.2f} 중립",
            invalidation="",
            bull_case="",
            bear_case="",
        )
