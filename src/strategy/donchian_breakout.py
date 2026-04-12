"""
Donchian Channel Breakout 전략: 20봉 최고가 돌파 시 BUY, 최저가 하향 돌파 시 SELL.
43.8% APR 사례에서 사용된 전략. 단순하지만 트렌드 추종에 강함.

개선사항:
- ADX 필터: ADX < 15이면 횡보 구간 → HOLD
- 변동성 필터: 최근 5봉 중 4봉 이상 같은 방향 연속 움직임 확인
- 볼륨 확인 필터: 브레이크아웃 시 볼륨 > 20봉 평균의 1.5배 → HIGH confidence 부여
- ATR 이격 필터: close가 채널 경계에서 ATR * 0.5 이상 돌파 시 신호 강화
- EMA50 추세 필터: BUY는 close > ema50, SELL은 close < ema50 조건으로 confidence 상향
"""

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


def _calc_adx(df: pd.DataFrame, idx: int) -> float:
    tr = pd.concat(
        [
            df["high"] - df["low"],
            (df["high"] - df["close"].shift(1)).abs(),
            (df["low"] - df["close"].shift(1)).abs(),
        ],
        axis=1,
    ).max(axis=1)
    atr_raw = tr.ewm(alpha=1 / 14, adjust=False).mean()
    up_move = df["high"].diff()
    dn_move = -df["low"].diff()
    plus_dm = up_move.where((up_move > dn_move) & (up_move > 0), 0.0)
    minus_dm = dn_move.where((dn_move > up_move) & (dn_move > 0), 0.0)
    plus_di = 100 * plus_dm.ewm(alpha=1 / 14, adjust=False).mean() / atr_raw.replace(0, 1e-9)
    minus_di = 100 * minus_dm.ewm(alpha=1 / 14, adjust=False).mean() / atr_raw.replace(0, 1e-9)
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di + 1e-9)
    adx = dx.ewm(alpha=1 / 14, adjust=False).mean()
    return float(adx.iloc[idx])


class DonchianBreakoutStrategy(BaseStrategy):
    name = "donchian_breakout"

    def generate(self, df: pd.DataFrame) -> Signal:
        prev = df.iloc[-3]
        last = self._last(df)

        idx = len(df) - 2
        adx_val = _calc_adx(df, idx)

        entry = last["close"]
        rsi = last["rsi14"]
        atr = last["atr14"]

        # ADX 필터: 횡보 구간 필터링
        if adx_val < 15:
            bull_case = (
                f"Donchian high ({last['donchian_high']:.2f}) / low ({last['donchian_low']:.2f}), "
                f"ADX={adx_val:.1f}"
            )
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.HIGH,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"ADX 낮음: 횡보 구간 (ADX={adx_val:.1f} < 15)",
                invalidation="",
                bull_case=bull_case,
                bear_case=bull_case,
            )

        broke_high = prev["close"] <= prev["donchian_high"] and last["close"] > last["donchian_high"]
        broke_low = prev["close"] >= prev["donchian_low"] and last["close"] < last["donchian_low"]

        # --- 변동성 필터: 최근 5봉 중 4봉 이상 같은 방향 연속 움직임 ---
        recent_moves = df["close"].diff().iloc[-6:-1]  # 최근 5봉의 방향
        up_count = int((recent_moves > 0).sum())
        dn_count = int((recent_moves < 0).sum())
        momentum_bull = up_count >= 4
        momentum_bear = dn_count >= 4

        # --- 볼륨 필터 ---
        vol_window = df["volume"].iloc[-21:-1]
        avg_vol = vol_window.mean() if len(vol_window) > 0 else 0.0
        vol_surge = avg_vol > 0 and last["volume"] >= avg_vol * 1.5

        # --- ATR 이격 필터 ---
        atr_breakout_high = last["close"] - last["donchian_high"] >= atr * 0.5
        atr_breakout_low = last["donchian_low"] - last["close"] >= atr * 0.5

        # --- EMA50 추세 필터 ---
        ema50 = last.get("ema50", entry)
        trend_bull = entry > ema50
        trend_bear = entry < ema50

        bull_case = (
            f"Price ({entry:.2f}) broke above 20-bar high ({last['donchian_high']:.2f}). "
            f"ATR={atr:.2f}, RSI={rsi:.1f}, ADX={adx_val:.1f}, "
            f"VolSurge={vol_surge}, ATRBreak={atr_breakout_high}, Momentum={momentum_bull}"
        )
        bear_case = (
            f"Price ({entry:.2f}) broke below 20-bar low ({last['donchian_low']:.2f}). "
            f"ATR={atr:.2f}, RSI={rsi:.1f}, ADX={adx_val:.1f}, "
            f"VolSurge={vol_surge}, ATRBreak={atr_breakout_low}, Momentum={momentum_bear}"
        )

        if broke_high and rsi < 80:
            # HIGH confidence: ADX > 25 + RSI < 70 + (볼륨 급증 OR ATR 이격) + EMA50 상향
            strong_signal = (vol_surge or atr_breakout_high) and trend_bull and momentum_bull
            if adx_val > 25 and rsi < 70 and strong_signal:
                conf = Confidence.HIGH
            else:
                conf = Confidence.MEDIUM
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Breakout above Donchian high {last['donchian_high']:.2f}. RSI={rsi:.1f}. "
                    f"ADX={adx_val:.1f}, VolSurge={vol_surge}, ATRBreak={atr_breakout_high}, "
                    f"Momentum={momentum_bull}, EMA50Trend={trend_bull}."
                ),
                invalidation=f"Close back below Donchian high ({last['donchian_high']:.2f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        if broke_low and rsi > 20:
            # HIGH confidence: ADX > 25 + RSI > 30 + (볼륨 급증 OR ATR 이격) + EMA50 하향
            strong_signal = (vol_surge or atr_breakout_low) and trend_bear and momentum_bear
            if adx_val > 25 and rsi > 30 and strong_signal:
                conf = Confidence.HIGH
            else:
                conf = Confidence.MEDIUM
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=(
                    f"Breakdown below Donchian low {last['donchian_low']:.2f}. RSI={rsi:.1f}. "
                    f"ADX={adx_val:.1f}, VolSurge={vol_surge}, ATRBreak={atr_breakout_low}, "
                    f"Momentum={momentum_bear}, EMA50Trend={trend_bear}."
                ),
                invalidation=f"Close back above Donchian low ({last['donchian_low']:.2f})",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        return Signal(
            action=Action.HOLD,
            confidence=Confidence.HIGH,
            strategy=self.name,
            entry_price=entry,
            reasoning="No Donchian channel breakout.",
            invalidation="",
            bull_case=bull_case,
            bear_case=bear_case,
        )
