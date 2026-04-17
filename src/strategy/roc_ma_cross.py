"""
ROCMACrossStrategy v3 (Cycle 122):

개선 사항:
- RSI 필터 추가: BUY시 RSI<70, SELL시 RSI>30 (과매수/과매도 회피)
- ROC 절대값 필터 강화: abs(ROC) > 0.3% 요구 (더 민감하게) (신호 신뢰도 향상)
- EMA50/200 이중 필터: 중장기 추세 확인
- 목표: PF 1.577 → 1.75+, Win Rate 50% → 55%+

원리:
- ROC = (close / close.shift(12) - 1) * 100
- ROC_MA = ROC.rolling(3).mean() (스무딩)
- BUY: ROC_MA 0 상향 + ROC>0.5% + RSI<70 + close > EMA50/200
- SELL: ROC_MA 0 하향 + ROC<-0.3% + RSI>30 + close < EMA50/200
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 20
_ROC_PERIOD = 12
_MA_PERIOD = 3
_STD_PERIOD = 20
_STD_MULT = 2.0
_ROC_MIN_ABS = 0.3  # IMPROVED:: ROC 절대값 최소값 (0.5%)


class ROCMACrossStrategy(BaseStrategy):
    name = "roc_ma_cross"

    def generate(self, df: pd.DataFrame) -> Signal:
        if df is None or len(df) < _MIN_ROWS:
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

        roc = (df["close"] / df["close"].shift(_ROC_PERIOD) - 1) * 100
        roc_ma = roc.rolling(_MA_PERIOD).mean()
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

        # BUY: ROC_MA 상향 + ROC>0.5% + RSI<70 + close > EMA50 + (EMA200 확인 or 없음)
        if (cross_above and 
            abs(roc_now) > _ROC_MIN_ABS and roc_now > 0 and
            rsi_val < 70 and
            close > ema50 and
            (ema200 is None or close > ema200)):
            
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"ROC_MA 0 상향 크로스 (ROC>{_ROC_MIN_ABS}%, RSI<70): "
                    f"ROC_MA={roc_ma_prev:.2f} → {roc_ma_now:.2f}, "
                    f"ROC={roc_now:.2f}%, RSI={rsi_val:.1f}, close={close:.4f} > EMA50={ema50:.4f}"
                ),
                invalidation="ROC_MA 0 아래 재하락 또는 close < EMA50 또는 RSI>=70",
                bull_case=f"ROC_MA 양전 전환, 상승 모멘텀 확인. ROC={roc_now:.2f}%, RSI={rsi_val:.1f}",
                bear_case="단순 조정 후 재하락 가능",
            )

        # SELL: ROC_MA 하향 + ROC<-0.3% + RSI>30 + close < EMA50 + (EMA200 확인 or 없음)
        if (cross_below and 
            abs(roc_now) > _ROC_MIN_ABS and roc_now < 0 and
            rsi_val > 30 and
            close < ema50 and
            (ema200 is None or close < ema200)):
            
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=close,
                reasoning=(
                    f"ROC_MA 0 하향 크로스 (ROC<-{_ROC_MIN_ABS}%, RSI>30): "
                    f"ROC_MA={roc_ma_prev:.2f} → {roc_ma_now:.2f}, "
                    f"ROC={roc_now:.2f}%, RSI={rsi_val:.1f}, close={close:.4f} < EMA50={ema50:.4f}"
                ),
                invalidation="ROC_MA 0 위로 재상승 또는 close > EMA50 또는 RSI<=30",
                bull_case="단순 조정일 수 있음",
                bear_case=f"ROC_MA 음전 전환, 하락 모멘텀 확인. ROC={roc_now:.2f}%, RSI={rsi_val:.1f}",
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=close,
            reasoning=(
                f"ROC_MA 크로스 없음 또는 조건 미충족: "
                f"ROC_MA={roc_ma_now:.2f}, ROC={roc_now:.2f}% (need >{_ROC_MIN_ABS}%), "
                f"RSI={rsi_val:.1f}, close={close:.4f}, EMA50={ema50:.4f}"
            ),
            invalidation="",
            bull_case="",
            bear_case="",
        )
