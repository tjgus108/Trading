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
        atr_vol_min_pct: float = 0.0,
        rsi_dir_filter: bool = False,
        rsi_dir_threshold: int = 50,
        dist_pct_min: float = 0.002,
    ) -> None:
        self.fast = fast
        self.slow = slow
        # Cycle354 E(실행): DEMA 수렴 사전 신호 — 크로스 직전 gap이 threshold 이내로 좁아질 때 예비 신호
        # convergence_signal=True + gap < convergence_threshold(2%) + gap 축소 중 → MEDIUM 신호
        # 기본값 False: 기존 cross-only 행동 유지 (신호 빈도 문제 해결용 실험 파라미터)
        self.convergence_signal = convergence_signal
        self.convergence_threshold = convergence_threshold
        # Cycle359 D(ML): ATR 최소 변동성 필터 — 극저변동성 구간 cross 차단
        # atr14/close < atr_vol_min_pct 이면 신호 억제 (0.0=비활성, 예: 0.005=0.5%)
        # 배경: BTC 1h ATR ~1.49% → 임계값 0.5%는 dead param. 다른 심볼/타임프레임용으로 보존
        self.atr_vol_min_pct = atr_vol_min_pct
        # Cycle359 D(ML): RSI 방향성 필터 — 크로스 방향과 모멘텀이 일치할 때만 신호
        # BUY 시 RSI > rsi_dir_threshold, SELL 시 RSI < (100 - rsi_dir_threshold)
        # 기본값 False: 기존 과매수/과매도 회피 필터만 유지
        # Cycle365 A(품질)/F(리서치): rsi_dir_threshold 파라미터화 — 45 완화 실험
        #   BTC 1h 신호 분석: fast=8/slow=20/thr=50 → 10.1/60d, thr=45 → 13.4/60d (+32%)
        #   fast=8/slow=25/thr=45 → 16.5/60d (항상 min_trades=15 초과)
        self.rsi_dir_filter = rsi_dir_filter
        self.rsi_dir_threshold = rsi_dir_threshold
        # Cycle370 C(데이터): DEMA 거리 필터 파라미터화 — dist_pct_min 탐색 (PF 1.50 목표)
        # 0.002(기본=Cycle358 확정): SharpeStd 2.69→2.32, trades 48→30
        # 0.003: 더 강한 거리 필터 → 노이즈 신호 제거 → PF↑ 기대 (trades↓ trade-off)
        self.dist_pct_min = dist_pct_min

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

        # ATR 최소 변동성 필터 (Cycle359 D(ML): 극저변동성 구간 cross 차단)
        if self.atr_vol_min_pct > 0.0 and "atr14" in df.columns:
            atr14_val = float(df["atr14"].iloc[idx])
            if atr14_val == atr14_val and atr14_val > 0:  # NaN check
                atr_ratio = atr14_val / max(abs(close_price), 1e-10)
                if atr_ratio < self.atr_vol_min_pct:
                    return Signal(
                        action=Action.HOLD,
                        confidence=Confidence.MEDIUM,
                        strategy=self.name,
                        entry_price=close_price,
                        reasoning=(
                            f"ATR 저변동성 차단: ATR/close={atr_ratio*100:.3f}% "
                            f"< min={self.atr_vol_min_pct*100:.2f}% "
                            f"(atr14={atr14_val:.4f})"
                        ),
                        invalidation="",
                    )

        # 거리 필터 (1%→0.5%→0.1%→0.2%: Cycle358 F(리서치) — SharpeStd=2.69 불안정)
        # BTC 1h fast=8/slow=20: 48 trades, Sharpe=0.47, SharpeStd=2.69 (std>2.5 위험 수준)
        # 0.001→0.002: 매우 약한 cross(gap<0.2%) 차단으로 noise 감소 → 30~40 trades 예상, Sharpe 안정 기대
        # Cycle370 C(데이터): dist_pct_min 파라미터화 (기본=0.002 유지, 0.003 실험 가능)
        if dist_pct < self.dist_pct_min:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.MEDIUM,
                strategy=self.name,
                entry_price=close_price,
                reasoning=(
                    f"DEMA 거리 미달: {dist_pct*100:.3f}% < {self.dist_pct_min*100:.1f}% "
                    f"(FAST={df_now:.4f}, SLOW={ds_now:.4f})"
                ),
                invalidation="",
            )
        
        conf = Confidence.HIGH if dist_pct > 0.02 else Confidence.MEDIUM

        entry = float(self._last(df)["close"])

        if cross_up:
            # ✅ BUY 시 RSI < 65 (과매수 회피, Cycle357 D: 70→65 noise 감소)
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
            # Cycle359 D(ML): RSI 방향성 필터 — 상방 모멘텀 확인 (RSI > rsi_dir_threshold)
            if self.rsi_dir_filter and rsi_val <= self.rsi_dir_threshold:
                return Signal(
                    action=Action.HOLD,
                    confidence=Confidence.MEDIUM,
                    strategy=self.name,
                    entry_price=entry,
                    reasoning=(
                        f"DEMA 상향 크로스 있으나 RSI 방향 미확인(RSI={rsi_val:.1f} <= {self.rsi_dir_threshold}). "
                        f"상방 모멘텀 부재."
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
            # Cycle359 D(ML): RSI 방향성 필터 — 하방 모멘텀 확인 (RSI < 100 - rsi_dir_threshold)
            if self.rsi_dir_filter and rsi_val >= (100 - self.rsi_dir_threshold):
                return Signal(
                    action=Action.HOLD,
                    confidence=Confidence.MEDIUM,
                    strategy=self.name,
                    entry_price=entry,
                    reasoning=(
                        f"DEMA 하향 크로스 있으나 RSI 방향 미확인(RSI={rsi_val:.1f} >= {100 - self.rsi_dir_threshold}). "
                        f"하방 모멘텀 부재."
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
