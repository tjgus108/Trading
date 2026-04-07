"""
A3. BTC-ETH 페어 트레이딩 전략.

원리: Engle-Granger 공적분 기반 스프레드 트레이딩.
  spread = log(BTC_price) - beta * log(ETH_price)
  z-score > +2 → spread 과열 → BTC SELL (or ETH BUY)
  z-score < -2 → spread 과냉 → BTC BUY  (or ETH SELL)
  z-score 0 근처 → 청산

실증: 연 16.34%, Sharpe 2.45, 변동성 8.45% (2019~2024, Springer 2024)

이 전략은 BTC를 기준으로 신호를 생성한다.
  - generate(btc_df): BTC에 대한 액션 반환
  - set_eth_data(eth_df): ETH close 데이터 주입 (orchestrator가 호출)

ETH 데이터 없으면 BTC/ETH 내재 비율 proxy로 fallback.
"""

import logging
from typing import Optional

import numpy as np
import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

logger = logging.getLogger(__name__)

ZSCORE_ENTRY = 2.0     # 진입 임계값
ZSCORE_STRONG = 2.5    # 강한 신호 임계값
ZSCORE_EXIT = 0.5      # 청산 목표 (포지션 정리)
SPREAD_WINDOW = 60     # z-score 계산 윈도우
BETA_WINDOW = 90       # beta 추정 윈도우 (더 긴 기간)


class PairTradingStrategy(BaseStrategy):
    """
    BTC-ETH 공적분 페어 트레이딩 전략.

    set_eth_data()로 ETH OHLCV DataFrame 주입.
    ETH 없으면 BTC 단독 momentum fallback.
    """

    name = "pair_trading"

    def __init__(
        self,
        entry_zscore: float = ZSCORE_ENTRY,
        spread_window: int = SPREAD_WINDOW,
        beta_window: int = BETA_WINDOW,
    ):
        self.entry_zscore = entry_zscore
        self.spread_window = spread_window
        self.beta_window = beta_window
        self._eth_df: Optional[pd.DataFrame] = None

    def set_eth_data(self, eth_df: pd.DataFrame) -> None:
        """ETH close 데이터 주입. orchestrator가 BTC generate() 전에 호출."""
        self._eth_df = eth_df
        logger.debug("ETH reference data set: %d rows", len(eth_df))

    def generate(self, df: pd.DataFrame) -> Signal:
        """df = BTC OHLCV DataFrame (지표 포함)."""
        last = self._last(df)
        entry = last["close"]
        rsi = last["rsi14"]

        if self._eth_df is not None and len(self._eth_df) >= self.spread_window + 2:
            return self._signal_with_eth(df, entry, rsi)
        else:
            return self._fallback_signal(entry, rsi)

    # ------------------------------------------------------------------
    # Spread computation
    # ------------------------------------------------------------------

    def _compute_spread_zscore(self, btc_df: pd.DataFrame, eth_df: pd.DataFrame) -> tuple[float, float]:
        """
        log-spread z-score와 beta 반환.
        spread = log(BTC) - beta * log(ETH)
        """
        btc_close = btc_df["close"].dropna()
        eth_close = eth_df["close"].dropna()

        # 공통 인덱스 정렬
        common = btc_close.index.intersection(eth_close.index)
        if len(common) < self.spread_window + 1:
            return 0.0, 1.0

        btc_c = np.log(btc_close.loc[common])
        eth_c = np.log(eth_close.loc[common])

        # Beta 추정: 최근 beta_window 기간 OLS
        n_beta = min(self.beta_window, len(common))
        btc_b = btc_c.iloc[-n_beta:].values
        eth_b = eth_c.iloc[-n_beta:].values
        if eth_b.std() < 1e-10:
            return 0.0, 1.0
        beta = float(np.cov(btc_b, eth_b)[0, 1] / np.var(eth_b))

        # Spread 시계열
        spread = btc_c - beta * eth_c

        # z-score (최근 spread_window)
        recent = spread.iloc[-self.spread_window:]
        z = float((recent.iloc[-1] - recent.mean()) / recent.std()) if recent.std() > 0 else 0.0
        return z, beta

    def _signal_with_eth(self, btc_df: pd.DataFrame, entry: float, rsi: float) -> Signal:
        try:
            z, beta = self._compute_spread_zscore(btc_df, self._eth_df)
        except Exception as e:
            logger.warning("Pair spread 계산 실패: %s", e)
            return self._fallback_signal(entry, rsi)

        bull_case = f"spread z={z:.2f} < -{self.entry_zscore}: BTC/ETH 스프레드 저평가 → BTC 롱"
        bear_case = f"spread z={z:.2f} > +{self.entry_zscore}: BTC/ETH 스프레드 고평가 → BTC 숏"

        # Spread 과열: BTC 고평가 → SELL BTC
        if z > ZSCORE_STRONG:
            return Signal(
                action=Action.SELL,
                confidence=Confidence.HIGH,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"BTC-ETH spread z={z:.2f} > {ZSCORE_STRONG} (beta={beta:.3f}): BTC 고평가 → 공적분 역추세 매도",
                invalidation=f"z < {self.entry_zscore} 또는 강한 BTC 모멘텀",
                bull_case=bull_case,
                bear_case=bear_case,
            )
        if z > self.entry_zscore:
            return Signal(
                action=Action.SELL,
                confidence=Confidence.MEDIUM,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"BTC-ETH spread z={z:.2f} > {self.entry_zscore}: BTC 상대 고평가",
                invalidation=f"z < 1.0",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        # Spread 과냉: BTC 저평가 → BUY BTC
        if z < -ZSCORE_STRONG:
            return Signal(
                action=Action.BUY,
                confidence=Confidence.HIGH,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"BTC-ETH spread z={z:.2f} < -{ZSCORE_STRONG} (beta={beta:.3f}): BTC 저평가 → 공적분 역추세 매수",
                invalidation=f"z > -{self.entry_zscore}",
                bull_case=bull_case,
                bear_case=bear_case,
            )
        if z < -self.entry_zscore:
            return Signal(
                action=Action.BUY,
                confidence=Confidence.MEDIUM,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"BTC-ETH spread z={z:.2f} < -{self.entry_zscore}: BTC 상대 저평가",
                invalidation=f"z > -1.0",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.HIGH,
            strategy=self.name,
            entry_price=entry,
            reasoning=f"BTC-ETH spread z={z:.2f}: ±{self.entry_zscore} 범위 내 → 청산 대기 또는 중립",
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )

    # ------------------------------------------------------------------
    # Fallback: ETH 데이터 없을 때
    # ------------------------------------------------------------------

    def _fallback_signal(self, entry: float, rsi: float) -> Signal:
        """ETH 데이터 없을 때 HOLD 반환 (pair 전략 특성상 단독 신호 불가)."""
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=entry,
            reasoning="ETH 데이터 미제공: pair trading 신호 생성 불가 → HOLD",
            invalidation="",
            bull_case="set_eth_data()로 ETH DataFrame 주입 필요",
            bear_case="set_eth_data()로 ETH DataFrame 주입 필요",
        )
