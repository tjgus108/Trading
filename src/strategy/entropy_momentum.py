"""
EntropyMomentumStrategy: 가격 변화 엔트로피 + 모멘텀 결합 전략.

낮은 엔트로피(방향성) + 상승 모멘텀 → BUY
낮은 엔트로피(방향성) + 하락 모멘텀 → SELL
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

MIN_ROWS = 25


class EntropyMomentumStrategy(BaseStrategy):
    name = "entropy_momentum"

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

        idx = len(df) - 2
        last = self._last(df)
        entry = float(last["close"])

        close = df["close"]
        returns = close.pct_change().fillna(0)

        # 엔트로피 근사
        abs_returns = returns.abs()
        avg_abs = abs_returns.rolling(20, min_periods=1).mean()
        entropy_proxy = abs_returns / (avg_abs + 1e-10)
        entropy_ma = entropy_proxy.rolling(10, min_periods=1).mean()

        # 모멘텀
        mom = close.pct_change(10)
        mom_ma = mom.rolling(5, min_periods=1).mean()

        ep = float(entropy_proxy.iloc[idx])
        ema = float(entropy_ma.iloc[idx])
        m = float(mom.iloc[idx]) if not pd.isna(mom.iloc[idx]) else 0.0
        mma = float(mom_ma.iloc[idx]) if not pd.isna(mom_ma.iloc[idx]) else 0.0

        # NaN 체크
        if pd.isna(ep) or pd.isna(ema):
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning="NaN 값 존재: 지표 계산 불가",
                invalidation="",
            )

        low_entropy = ep < ema * 0.7

        if ep < ema * 0.5:
            confidence = Confidence.HIGH
        else:
            confidence = Confidence.MEDIUM

        bull_case = (
            f"entropy_proxy={ep:.4f}, entropy_ma={ema:.4f}, "
            f"mom={m:.4f}, mom_ma={mma:.4f}, close={entry:.4f}"
        )
        bear_case = bull_case

        if low_entropy and m > mma and m > 0:
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"낮은 엔트로피: ep={ep:.4f} < ema*0.7={ema*0.7:.4f}. "
                    f"상승 모멘텀: mom={m:.4f} > mom_ma={mma:.4f} > 0"
                ),
                invalidation=f"ep >= ema*0.7 또는 mom <= mom_ma 또는 mom <= 0",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        if low_entropy and m < mma and m < 0:
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"낮은 엔트로피: ep={ep:.4f} < ema*0.7={ema*0.7:.4f}. "
                    f"하락 모멘텀: mom={m:.4f} < mom_ma={mma:.4f} < 0"
                ),
                invalidation=f"ep >= ema*0.7 또는 mom >= mom_ma 또는 mom >= 0",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=entry,
            reasoning=(
                f"진입 조건 미충족: ep={ep:.4f}, ema={ema:.4f}, "
                f"low_entropy={low_entropy}, mom={m:.4f}, mom_ma={mma:.4f}"
            ),
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
