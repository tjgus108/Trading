"""
ApproximateEntropy 전략: Shannon entropy로 시장 무질서도 측정.

Low entropy (< 0.7): 방향성 강함 → 추세 추종
High entropy (> 1.0): 무작위성 강함 → 평균 회귀
"""

import numpy as np
import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

MIN_ROWS = 25
ENTROPY_WINDOW = 20
MAX_ENTROPY = np.log(3)  # ≈ 1.099


def _calc_entropy(close: pd.Series, window: int = ENTROPY_WINDOW) -> float:
    """최근 window봉 가격 변화 방향의 Shannon entropy 계산."""
    changes = np.sign(close.diff().dropna()).values[-window:]
    if len(changes) < window:
        return MAX_ENTROPY  # 데이터 부족 시 최대 엔트로피

    prob_up = float(np.sum(changes == 1)) / window
    prob_down = float(np.sum(changes == -1)) / window
    prob_flat = float(np.sum(changes == 0)) / window

    entropy = -sum(
        p * np.log(p + 1e-10)
        for p in [prob_up, prob_down, prob_flat]
    )
    return float(entropy)


class ApproximateEntropyStrategy(BaseStrategy):
    name = "entropy_strategy"

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < MIN_ROWS:
            last = df.iloc[-1]
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=float(last["close"]),
                reasoning=f"데이터 부족: 최소 {MIN_ROWS}행 필요 (현재 {len(df)}행)",
                invalidation="",
            )

        last = self._last(df)
        entry = float(last["close"])

        # 완성봉 기준으로 계산 (iloc[:-1])
        completed = df["close"].iloc[:-1]
        entropy = _calc_entropy(completed)

        # 방향 확률 (최근 20봉)
        changes = np.sign(completed.diff().dropna()).values[-ENTROPY_WINDOW:]
        n = len(changes)
        prob_up = float(np.sum(changes == 1)) / n if n > 0 else 0.0
        prob_down = float(np.sum(changes == -1)) / n if n > 0 else 0.0

        # SMA20
        sma20 = float(completed.iloc[-20:].mean())

        # Confidence
        if entropy < 0.5 or entropy > 1.05:
            confidence = Confidence.HIGH
        else:
            confidence = Confidence.MEDIUM

        bull_case = (
            f"entropy={entropy:.4f}, prob_up={prob_up:.3f}, "
            f"prob_down={prob_down:.3f}, SMA20={sma20:.4f}, close={entry:.4f}"
        )
        bear_case = bull_case

        # Low entropy: 방향성 강함 → 추세 추종
        if entropy < 0.7:
            if prob_up > 0.6:
                return Signal(
                    action=Action.BUY,
                    confidence=confidence,
                    strategy=self.name,
                    entry_price=entry,
                    reasoning=(
                        f"낮은 엔트로피: entropy={entropy:.4f} < 0.7. "
                        f"상승 방향성: prob_up={prob_up:.3f} > 0.6"
                    ),
                    invalidation=f"entropy > 0.7 또는 prob_up < 0.6",
                    bull_case=bull_case,
                    bear_case=bear_case,
                )
            if prob_down > 0.6:
                return Signal(
                    action=Action.SELL,
                    confidence=confidence,
                    strategy=self.name,
                    entry_price=entry,
                    reasoning=(
                        f"낮은 엔트로피: entropy={entropy:.4f} < 0.7. "
                        f"하락 방향성: prob_down={prob_down:.3f} > 0.6"
                    ),
                    invalidation=f"entropy > 0.7 또는 prob_down < 0.6",
                    bull_case=bull_case,
                    bear_case=bear_case,
                )

        # High entropy: 무작위성 강함 → 평균 회귀
        if entropy > 1.0:
            if entry < sma20 * 0.98:
                return Signal(
                    action=Action.BUY,
                    confidence=confidence,
                    strategy=self.name,
                    entry_price=entry,
                    reasoning=(
                        f"높은 엔트로피: entropy={entropy:.4f} > 1.0. "
                        f"과매도 복귀: close({entry:.4f}) < SMA20*0.98({sma20 * 0.98:.4f})"
                    ),
                    invalidation=f"close > SMA20({sma20:.4f}) 또는 entropy < 1.0",
                    bull_case=bull_case,
                    bear_case=bear_case,
                )
            if entry > sma20 * 1.02:
                return Signal(
                    action=Action.SELL,
                    confidence=confidence,
                    strategy=self.name,
                    entry_price=entry,
                    reasoning=(
                        f"높은 엔트로피: entropy={entropy:.4f} > 1.0. "
                        f"과매수 복귀: close({entry:.4f}) > SMA20*1.02({sma20 * 1.02:.4f})"
                    ),
                    invalidation=f"close < SMA20({sma20:.4f}) 또는 entropy < 1.0",
                    bull_case=bull_case,
                    bear_case=bear_case,
                )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=entry,
            reasoning=(
                f"entropy={entropy:.4f}: 진입 조건 미충족 "
                f"(prob_up={prob_up:.3f}, prob_down={prob_down:.3f}, SMA20={sma20:.4f})"
            ),
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
