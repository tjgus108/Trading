"""
DEMACrossStrategy: DEMA(fast=10)가 DEMA(slow=25)를 크로스할 때 신호 생성.

개선 사항 (Cycle 122):
- RSI 필터 추가: 과매수(>70) / 과매도(<30) 신호 무시
- DEMA 거리 필터: 크로스 신뢰도 향상 (1% 이상 거리 요구)
- 목표: PF 1.696 → 1.85+, loss 제어 강화
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


def _dema(series: pd.Series, period: int) -> pd.Series:
    ema = series.ewm(span=period, adjust=False).mean()
    ema_of_ema = ema.ewm(span=period, adjust=False).mean()
    return 2 * ema - ema_of_ema


class DEMACrossStrategy(BaseStrategy):
    name = "dema_cross"

    def __init__(
        self,
        fast: int = 10,
        slow: int = 25,
        convergence_signal: bool = False,
        convergence_threshold: float = 0.02,
    ) -> None:
        self.fast = fast
        self.slow = slow
        # Cycle354 E(실행): DEMA 수렴 사전 신호 — 크로스 직전 gap이 threshold 이내로 좁아질 때 예비 신호
        # convergence_signal=True + gap < convergence_threshold(2%) + gap 축소 중 → MEDIUM 신호
        # 기본값 False: 기존 cross-only 행동 유지 (신호 빈도 문제 해결용 실험 파라미터)
        self.convergence_signal = convergence_signal
        self.convergence_threshold = convergence_threshold

    def generate(self, df: pd.DataFrame) -> Signal:
        if df is None or len(df) < 35:
            close_val = float(df["close"].iloc[-1]) if df is not None and len(df) > 0 else 0.0
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.MEDIUM,
                strategy=self.name,
                entry_price=close_val,
                reasoning="Insufficient data: minimum 35 rows required.",
                invalidation="",
            )

        idx = len(df) - 2
        dema_fast = _dema(df["close"], self.fast)
        dema_slow = _dema(df["close"], self.slow)

        df_now = float(dema_fast.iloc[idx])
        df_prev = float(dema_fast.iloc[idx - 1])
        ds_now = float(dema_slow.iloc[idx])
        ds_prev = float(dema_slow.iloc[idx - 1])

        if any(v != v for v in [df_now, df_prev, ds_now, ds_prev]):  # NaN check
            entry = float(self._last(df)["close"])
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.MEDIUM,
                strategy=self.name,
                entry_price=entry,
                reasoning="NaN in DEMA values.",
                invalidation="",
            )

        cross_up = df_prev < ds_prev and df_now > ds_now
        cross_down = df_prev > ds_prev and df_now < ds_now

        close_price = float(df["close"].iloc[idx])
        dist_pct = abs(df_now - ds_now) / max(abs(close_price), 1e-10)

        # ✅ NEW: RSI 필터 (과매수/과매도 회피)
        rsi_val = 50.0
        if "rsi14" in df.columns:
            rsi_val = float(df["rsi14"].iloc[idx])
            if rsi_val != rsi_val:  # NaN check
                rsi_val = 50.0

        # Cycle354 E(실행): DEMA 수렴 사전 신호
        # 크로스 없지만 gap이 수렴 중(축소) + convergence_threshold 이내 → 예비 신호 생성
        # 실제 cross 이벤트보다 일찍 진입 → 신호 빈도 증가 (BTC 3→더 많은 거래 목표)
        if self.convergence_signal and not cross_up and not cross_down:
            gap_now = df_now - ds_now    # + = fast above slow
            gap_prev = df_prev - ds_prev
            gap_narrowing = abs(gap_now) < abs(gap_prev)
            if gap_narrowing and dist_pct < self.convergence_threshold:
                entry_c = float(self._last(df)["close"])
                if gap_now < 0 and rsi_val <= 70:
                    return Signal(
                        action=Action.BUY,
                        confidence=Confidence.MEDIUM,
                        strategy=self.name,
                        entry_price=entry_c,
                        reasoning=(
                            f"DEMA 수렴 BUY: fast→slow 접근중 "
                            f"({dist_pct*100:.3f}%<{self.convergence_threshold*100:.1f}%), "
                            f"FAST={df_now:.4f}, SLOW={ds_now:.4f}"
                        ),
                        invalidation=f"DEMA_fast가 DEMA_slow ({ds_now:.4f}) 아래로 다시 벌어질 시",
                        bull_case=f"DEMA 수렴 → 임박한 골든크로스 예상",
                        bear_case=f"수렴 실패 시 현 방향 지속",
                    )
                if gap_now > 0 and rsi_val >= 30:
                    return Signal(
                        action=Action.SELL,
                        confidence=Confidence.MEDIUM,
                        strategy=self.name,
                        entry_price=entry_c,
                        reasoning=(
                            f"DEMA 수렴 SELL: fast→slow 접근중 "
                            f"({dist_pct*100:.3f}%<{self.convergence_threshold*100:.1f}%), "
                            f"FAST={df_now:.4f}, SLOW={ds_now:.4f}"
                        ),
                        invalidation=f"DEMA_fast가 DEMA_slow ({ds_now:.4f}) 위로 다시 벌어질 시",
                        bull_case=f"수렴 실패 시 현 방향 지속",
                        bear_case=f"DEMA 수렴 → 임박한 데드크로스 예상",
                    )

        # 거리 필터 (1%→0.5%→0.1%: Cycle355 F(리서치) — 0.5%가 cross 신호도 차단)
        # BTC 1h: 3 trades avg → cross 이벤트 자체가 희귀. 0.5%로 cross 시 gap이 이미 소멸한 경우 차단됨
        # 0.1%로 완화: 실제 cross가 발생하면 허용. 신호 품질보다 빈도 우선 (15 trades 기준 충족 목표)
        if dist_pct < 0.001:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.MEDIUM,
                strategy=self.name,
                entry_price=close_price,
                reasoning=(
                    f"DEMA 거리 미달: {dist_pct*100:.3f}% < 0.1% "
                    f"(FAST={df_now:.4f}, SLOW={ds_now:.4f})"
                ),
                invalidation="",
            )
        
        conf = Confidence.HIGH if dist_pct > 0.02 else Confidence.MEDIUM

        entry = float(self._last(df)["close"])

        if cross_up:
            # ✅ BUY 시 RSI < 65 (과매수 회피 강화, Cycle357 D(ML): 70→65 noise 감소)
            if rsi_val > 65:
                return Signal(
                    action=Action.HOLD,
                    confidence=Confidence.MEDIUM,
                    strategy=self.name,
                    entry_price=entry,
                    reasoning=(
                        f"DEMA 상향 크로스 있으나 과매수(RSI={rsi_val:.1f} > 65). "
                        f"신호 무시하고 대기."
                    ),
                    invalidation="",
                )
            
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"DEMA_fast ({df_now:.4f}) crossed above DEMA_slow ({ds_now:.4f}). "
                    f"dist={dist_pct*100:.3f}%, RSI={rsi_val:.1f}"
                ),
                invalidation=f"DEMA_fast가 DEMA_slow ({ds_now:.4f}) 아래로 이탈 시",
                bull_case=f"DEMA_fast={df_now:.4f} > DEMA_slow={ds_now:.4f}, 상향 크로스",
                bear_case=f"이전 DEMA_fast={df_prev:.4f} < DEMA_slow={ds_prev:.4f}",
            )

        if cross_down:
            # ✅ SELL 시 RSI > 30 (과매도 회피)
            if rsi_val < 30:
                return Signal(
                    action=Action.HOLD,
                    confidence=Confidence.MEDIUM,
                    strategy=self.name,
                    entry_price=entry,
                    reasoning=(
                        f"DEMA 하향 크로스 있으나 과매도(RSI={rsi_val:.1f} < 30). "
                        f"신호 무시하고 대기."
                    ),
                    invalidation="",
                )
            
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"DEMA_fast ({df_now:.4f}) crossed below DEMA_slow ({ds_now:.4f}). "
                    f"dist={dist_pct*100:.3f}%, RSI={rsi_val:.1f}"
                ),
                invalidation=f"DEMA_fast가 DEMA_slow ({ds_now:.4f}) 위로 회복 시",
                bull_case=f"이전 DEMA_fast={df_prev:.4f} > DEMA_slow={ds_prev:.4f}",
                bear_case=f"DEMA_fast={df_now:.4f} < DEMA_slow={ds_now:.4f}, 하향 크로스",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=(
                f"DEMA 크로스 없음. DEMA_fast={df_now:.4f}, DEMA_slow={ds_now:.4f}, "
                f"dist={dist_pct*100:.3f}%."
            ),
            invalidation="",
            bull_case=f"DEMA_fast={df_now:.4f}, DEMA_slow={ds_now:.4f}",
            bear_case=f"DEMA_fast={df_now:.4f}, DEMA_slow={ds_now:.4f}",
        )
