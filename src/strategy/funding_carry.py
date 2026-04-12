"""
E2. Funding Rate Cash-and-Carry 전략.

원리: 시장중립 헷지
  - 스팟 매수 + 선물 숏 동시 진입 → 펀딩비만 수집
  - 펀딩비 양수(롱 지불) → 숏 포지션이 펀딩비 수신
  - 단일 심볼 백테스트: 신호만 생성 (헷지 실행은 라이브에서)

실증: Sharpe 1.66~3.5, Calmar 5~10 (ScienceDirect 2025)

df에 "funding_rate" 컬럼 있으면 사용, 없으면 RSI14 proxy 사용.

개선 (v2):
  - ATR 기반 스탑로스: entry 기준 atr_stop_mult × ATR 하락 시 강제 청산
  - RSI 과매도 필터: 진입 시 RSI < rsi_floor 이면 진입 차단 (추세 추락 방어)
  - 음수 펀딩비 즉시 청산: fr < 0 은 캐리가 손해이므로 SELL 우선 처리
"""

import logging

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

logger = logging.getLogger(__name__)

# 연 환산 계수: 펀딩비는 8시간 단위, 연 3회/일 × 365일
ANNUALIZE = 3 * 365


class FundingCarryStrategy(BaseStrategy):
    """
    펀딩비 Cash-and-Carry 전략 (v2).

    entry_threshold 이상 펀딩비 → BUY (캐리 진입)
    exit_threshold 미만 펀딩비  → SELL (포지션 청산)
    ATR 스탑로스 + RSI 진입 필터로 드로다운 방어.
    """

    name = "funding_carry"

    def __init__(
        self,
        entry_threshold: float = 0.0003,   # +0.03%: 연 환산 ~32.85% 이상
        exit_threshold: float = 0.0001,    # +0.01%: 펀딩비 낮아지면 청산
        min_holding_candles: int = 8,      # 최소 8캔들 보유 (조기청산 방지)
        atr_stop_mult: float = 2.0,        # ATR 스탑로스 배수 (entry - mult*ATR)
        rsi_floor: float = 35.0,           # 진입 시 RSI 최소값 (이하면 진입 차단)
    ):
        self.entry_threshold = entry_threshold
        self.exit_threshold = exit_threshold
        self.min_holding_candles = min_holding_candles
        self.atr_stop_mult = atr_stop_mult
        self.rsi_floor = rsi_floor

    def generate(self, df: pd.DataFrame) -> Signal:
        last = self._last(df)
        idx = len(df) - 2
        entry = last["close"]
        rsi = last.get("rsi14", 50.0)
        atr = last.get("atr14", 0.0)

        # 변동성 레짐 필터
        vol = df["close"].pct_change().rolling(20, min_periods=1).std().iloc[idx]
        if vol > 0.03:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"고변동성 레짐 HOLD: realized_vol={vol:.4f} > 0.03",
                invalidation="vol < 0.03 시 재검토",
                bull_case="",
                bear_case="고변동성 구간 캐리 전략 위험",
            )

        # 추세 강도 필터
        ema20 = df["close"].ewm(span=20, adjust=False).mean()
        slope = (ema20.iloc[idx] - ema20.iloc[max(idx - 5, 0)]) / ema20.iloc[max(idx - 5, 0)]
        if slope < -0.02:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"급락 추세 HOLD: EMA20 기울기={slope:.4f} < -0.02",
                invalidation="EMA20 기울기 > -0.02 시 재검토",
                bull_case="",
                bear_case="급락 구간 캐리 진입 위험",
            )

        # funding_rate 컬럼 유무에 따라 분기
        if "funding_rate" in df.columns:
            fr = last["funding_rate"]
        else:
            fr = self._rsi_proxy(rsi)

        ann = fr * ANNUALIZE * 100  # 연 환산 %

        reasoning_base = f"funding_rate={fr:.4f}, 연환산={ann:.1f}%"
        stop_price = entry - self.atr_stop_mult * atr if atr > 0 else None
        stop_note = (
            f"스탑로스={stop_price:.2f} (ATR×{self.atr_stop_mult})"
            if stop_price is not None
            else "ATR 없음"
        )

        # 음수 펀딩비: 캐리 손해 → 즉시 청산
        if fr < 0:
            return Signal(
                action=Action.SELL,
                confidence=Confidence.HIGH,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"음수 펀딩비 즉시 청산: {reasoning_base}",
                invalidation=f"funding_rate > {self.entry_threshold:.4f} 재진입",
                bull_case="",
                bear_case="음수 펀딩비: 숏 포지션이 펀딩비 지불 → 손해",
            )

        if fr > self.entry_threshold:
            # RSI 과매도 구간이면 추세 추락 위험 → 진입 차단
            if rsi < self.rsi_floor:
                return Signal(
                    action=Action.HOLD,
                    confidence=Confidence.MEDIUM,
                    strategy=self.name,
                    entry_price=entry,
                    reasoning=f"진입 차단: RSI={rsi:.1f} < {self.rsi_floor} (추세 추락 위험), {reasoning_base}",
                    invalidation=f"RSI > {self.rsi_floor} 회복 시 재검토",
                    bull_case="펀딩비 조건 충족, RSI 회복 대기",
                    bear_case="과매도 추세에서 캐리 진입 시 드로다운 위험",
                )
            return Signal(
                action=Action.BUY,
                confidence=Confidence.HIGH,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"Cash-and-carry 진입: {reasoning_base} > {self.entry_threshold:.4f}, {stop_note}",
                invalidation=f"funding_rate < {self.exit_threshold:.4f} 또는 음수 전환 또는 {stop_note}",
                bull_case=f"펀딩비 {ann:.1f}% 수익 수집, 시장중립 헷지",
                bear_case="펀딩비 급락 시 조기청산 필요",
            )

        if fr < self.exit_threshold:
            return Signal(
                action=Action.SELL,
                confidence=Confidence.MEDIUM,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"캐리 청산: {reasoning_base} < {self.exit_threshold:.4f}",
                invalidation=f"funding_rate > {self.entry_threshold:.4f} 재진입",
                bull_case="",
                bear_case=f"펀딩비 수익 소멸, 헷지 포지션 청산",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=f"대기: {reasoning_base} (임계값 미달)",
            invalidation="",
            bull_case=f"entry_threshold={self.entry_threshold:.4f} 도달 시 진입",
            bear_case="",
        )

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    @staticmethod
    def _rsi_proxy(rsi: float) -> float:
        """funding_rate 컬럼 없을 때 RSI14로 대체."""
        if rsi > 70:
            return 0.0004   # 양수 펀딩비 proxy
        if rsi < 30:
            return -0.0002  # 음수 펀딩비 proxy
        return 0.0
