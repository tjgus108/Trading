"""
ROCMACrossStrategy v5 (Cycle 330):

변경:
- ROC 절대값 필터: abs(ROC) > 0.3% 유지 (Cycle 330: 0.1% 실험 → Sharpe -0.41→-0.74 악화 → 즉시 되돌림)
  배경: _ROC_MIN_ABS=0.1 오신호 증가 확인, EMA50이 주 차단 요인
  결론: ROC 필터는 오신호 방어선 — 완화 효과 없음

원리:
- ROC = (close / close.shift(12) - 1) * 100
- ROC_MA = ROC.rolling(3).mean() (스무딩)
- BUY: ROC_MA 0 상향 + ROC>0.3% + close > EMA50/200
- SELL: ROC_MA 0 하향 + ROC<-0.3% + close < EMA50/200
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_STD_PERIOD = 20
_STD_MULT = 2.0
_ROC_MIN_ABS = 0.3


class ROCMACrossStrategy(BaseStrategy):
    name = "roc_ma_cross"

    def __init__(self, roc_period: int = 12, ma_period: int = 3):
        self.roc_period = roc_period
        self.ma_period = ma_period
        self._min_rows = max(roc_period + ma_period, 20)

    def generate(self, df: pd.DataFrame) -> Signal:
        if df is None or len(df) < self._min_rows:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning="데이터 부족",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        idx = len(df) - 2

        roc = (df["close"] / df["close"].shift(self.roc_period) - 1) * 100
        roc_ma = roc.rolling(self.ma_period).mean()
        roc_std = roc.rolling(_STD_PERIOD).std()

        roc_ma_now = float(roc_ma.iloc[idx])
        roc_ma_prev = float(roc_ma.iloc[idx - 1])
        roc_now = float(roc.iloc[idx])
        roc_std_now = float(roc_std.iloc[idx])

        close = float(df["close"].iloc[idx])
        ema50 = float(df["ema50"].iloc[idx])
        
        # ✅ NEW: EMA200 확인 (있으면 사용, 없으면 무시)
        ema200 = None
        if "ema50" in df.columns and len(df) >= 200:
            try:
                ema200 = float(df["close"].ewm(span=200, adjust=False).mean().iloc[idx])
            except:
                pass
        
        # ✅ NEW: RSI 필터
        rsi_val = 50.0
        if "rsi14" in df.columns:
            rsi_raw = float(df["rsi14"].iloc[idx])
            if rsi_raw == rsi_raw:  # NaN check
                rsi_val = rsi_raw

        if pd.isna(roc_ma_now) or pd.isna(roc_ma_prev):
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=close,
                reasoning="ROC_MA 계산 불가 (NaN)",
                invalidation="",
                bull_case="",
                bear_case="",
            )

        cross_above = roc_ma_prev < 0 and roc_ma_now >= 0
        cross_below = roc_ma_prev > 0 and roc_ma_now <= 0

        if not pd.isna(roc_std_now) and roc_std_now > 0:
            conf_high = abs(roc_now) > roc_std_now * _STD_MULT
        else:
            conf_high = False

        conf = Confidence.HIGH if conf_high else Confidence.MEDIUM

        # BUY: ROC_MA 상향 + ROC>0.3% + close > EMA50 + (EMA200 확인 or 없음)
        # Cycle 329: RSI 필터 제거 (Cycle 328 분석: BTC 1h에서 RSI<70 차단 0건)
        if (cross_above and
            abs(roc_now) > _ROC_MIN_ABS and roc_now > 0 and
            close > ema50 and
            (ema200 is None or close > ema200)):

            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"ROC_MA 0 상향 크로스 (ROC>{_ROC_MIN_ABS}%): "
                    f"ROC_MA={roc_ma_prev:.2f} → {roc_ma_now:.2f}, "
                    f"ROC={roc_now:.2f}%, close={close:.4f} > EMA50={ema50:.4f}"
                ),
                invalidation="ROC_MA 0 아래 재하락 또는 close < EMA50",
                bull_case=f"ROC_MA 양전 전환, 상승 모멘텀 확인. ROC={roc_now:.2f}%",
                bear_case="단순 조정 후 재하락 가능",
            )

        # SELL: ROC_MA 하향 + ROC<-0.3% + close < EMA50 + (EMA200 확인 or 없음)
        # Cycle 329: RSI 필터 제거 (대칭적으로)
        if (cross_below and
            abs(roc_now) > _ROC_MIN_ABS and roc_now < 0 and
            close < ema50 and
            (ema200 is None or close < ema200)):

            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"ROC_MA 0 하향 크로스 (ROC<-{_ROC_MIN_ABS}%): "
                    f"ROC_MA={roc_ma_prev:.2f} → {roc_ma_now:.2f}, "
                    f"ROC={roc_now:.2f}%, close={close:.4f} < EMA50={ema50:.4f}"
                ),
                invalidation="ROC_MA 0 위로 재상승 또는 close > EMA50",
                bull_case="단순 조정일 수 있음",
                bear_case=f"ROC_MA 음전 전환, 하락 모멘텀 확인. ROC={roc_now:.2f}%",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=close,
            reasoning=(
                f"ROC_MA 크로스 없음 또는 조건 미충족: "
                f"ROC_MA={roc_ma_now:.2f}, ROC={roc_now:.2f}% (need >{_ROC_MIN_ABS}%), "
                f"close={close:.4f}, EMA50={ema50:.4f}"
            ),
            invalidation="",
            bull_case="",
            bear_case="",
        )
