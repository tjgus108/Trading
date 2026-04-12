"""
MarketRegimeClassifierStrategy: 시장 레짐 자동 분류 전략.

4가지 레짐:
- TRENDING_UP:   EMA20 > EMA50, close > EMA20, ADX > 25 → BUY
- TRENDING_DOWN: EMA20 < EMA50, close < EMA20, ADX > 25 → SELL
- SIDEWAYS:      ADX < 20, 가격 범위 비율 < 5% → HOLD (LOW)
- CRASH:         5봉 중 4봉 이상 음봉 + 5봉 대비 -8% 이상 하락 → SELL (HIGH)

confidence:
- ADX > 40 또는 CRASH → HIGH
- ADX 25~40 → MEDIUM
- 나머지 → LOW

최소 행: 30
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal

_MIN_ROWS = 30
_ADX_TRENDING = 25.0
_ADX_SIDEWAYS = 20.0
_ADX_HIGH = 40.0
_EWM_ALPHA = 1 / 14
_CRASH_DROP = -0.08
_CRASH_BEARISH_MIN = 4
_SIDEWAYS_RANGE_RATIO = 0.05


class MarketRegimeClassifierStrategy(BaseStrategy):
    name = "market_regime_classifier"

    def _compute_adx(self, df: pd.DataFrame):
        """ADX, +DI, -DI 계산 (EWM alpha=1/14)."""
        high = df["high"]
        low = df["low"]
        close = df["close"]

        tr = pd.concat(
            [
                high - low,
                (high - close.shift(1)).abs(),
                (low - close.shift(1)).abs(),
            ],
            axis=1,
        ).max(axis=1)
        atr = tr.ewm(alpha=_EWM_ALPHA, adjust=False).mean()

        up_move = high.diff()
        down_move = -low.diff()

        plus_dm = up_move.where((up_move > down_move) & (up_move > 0), 0)
        minus_dm = down_move.where((down_move > up_move) & (down_move > 0), 0)

        plus_di = 100 * plus_dm.ewm(alpha=_EWM_ALPHA, adjust=False).mean() / atr
        minus_di = 100 * minus_dm.ewm(alpha=_EWM_ALPHA, adjust=False).mean() / atr

        dx = (100 * (plus_di - minus_di).abs() / (plus_di + minus_di)).fillna(0)
        adx = dx.ewm(alpha=_EWM_ALPHA, adjust=False).mean()

        return adx, plus_di, minus_di

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < _MIN_ROWS:
            entry = float(df["close"].iloc[-1]) if len(df) > 0 else 0.0
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning="MarketRegimeClassifier 계산에 필요한 데이터 부족 (최소 30행).",
                invalidation="",
            )

        adx_s, plus_di_s, minus_di_s = self._compute_adx(df)
        idx = len(df) - 2

        close = df["close"]
        ema20 = close.ewm(span=20, adjust=False).mean()
        ema50 = close.ewm(span=50, adjust=False).mean()

        close_val = float(close.iloc[idx])
        ema20_val = float(ema20.iloc[idx])
        ema50_val = float(ema50.iloc[idx])
        adx_val = float(adx_s.iloc[idx])
        plus_di_val = float(plus_di_s.iloc[idx])
        minus_di_val = float(minus_di_s.iloc[idx])

        # CRASH 감지: 5봉 중 4봉 이상 음봉 + 5봉 대비 -8% 이상 하락
        window = df.iloc[max(0, idx - 4): idx + 1]
        bearish_count = int((window["close"] < window["open"]).sum())
        pct_change_5 = float(close.pct_change(5).iloc[idx])

        if bearish_count >= _CRASH_BEARISH_MIN and pct_change_5 < _CRASH_DROP:
            return Signal(
                action=Action.SELL,
                confidence=Confidence.HIGH,
                strategy=self.name,
                entry_price=close_val,
                reasoning=(
                    f"CRASH 감지: 5봉 중 {bearish_count}봉 음봉, "
                    f"5봉 대비 {pct_change_5*100:.1f}% 하락. "
                    f"ADX={adx_val:.1f}"
                ),
                invalidation="가격 반등 후 EMA20 상향 돌파 시 무효.",
                bull_case="단기 과매도로 반등 가능성 있음.",
                bear_case=f"급락 추세 지속, 5봉 {pct_change_5*100:.1f}% 낙폭.",
            )

        context = (
            f"ADX={adx_val:.1f} EMA20={ema20_val:.4f} EMA50={ema50_val:.4f} "
            f"close={close_val:.4f} +DI={plus_di_val:.1f} -DI={minus_di_val:.1f}"
        )

        # TRENDING_UP
        if ema20_val > ema50_val and close_val > ema20_val and adx_val > _ADX_TRENDING:
            confidence = Confidence.HIGH if adx_val > _ADX_HIGH else Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_val,
                reasoning=f"TRENDING_UP: EMA20>EMA50, close>EMA20, ADX>{_ADX_TRENDING:.0f}. {context}",
                invalidation="EMA20이 EMA50 아래로 또는 ADX < 20 하락 시 무효.",
                bull_case=f"ADX={adx_val:.1f} 강한 상승 추세, EMA 정배열.",
                bear_case="EMA 역배열 전환 시 추세 반전 위험.",
            )

        # TRENDING_DOWN
        if ema20_val < ema50_val and close_val < ema20_val and adx_val > _ADX_TRENDING:
            confidence = Confidence.HIGH if adx_val > _ADX_HIGH else Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=confidence,
                strategy=self.name,
                entry_price=close_val,
                reasoning=f"TRENDING_DOWN: EMA20<EMA50, close<EMA20, ADX>{_ADX_TRENDING:.0f}. {context}",
                invalidation="EMA20이 EMA50 위로 또는 ADX < 20 하락 시 무효.",
                bull_case="EMA 정배열 전환 시 반등 가능.",
                bear_case=f"ADX={adx_val:.1f} 강한 하락 추세, EMA 역배열.",
            )

        # SIDEWAYS
        rolling_max = close.rolling(20).max().iloc[idx]
        rolling_min = close.rolling(20).min().iloc[idx]
        range_ratio = (rolling_max - rolling_min) / close_val if close_val != 0 else 0.0

        if adx_val < _ADX_SIDEWAYS and range_ratio < _SIDEWAYS_RANGE_RATIO:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=close_val,
                reasoning=(
                    f"SIDEWAYS: ADX={adx_val:.1f}<{_ADX_SIDEWAYS:.0f}, "
                    f"가격 범위 비율={range_ratio*100:.2f}%<5%. {context}"
                ),
                invalidation=f"ADX >= {_ADX_TRENDING:.0f} 또는 가격 범위 확대 시 재평가.",
            )

        # 조건 미충족 → HOLD LOW
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=close_val,
            reasoning=f"레짐 분류 불명확 (조건 미충족). {context}",
            invalidation="추세 또는 횡보 조건 확립 시 재평가.",
        )
