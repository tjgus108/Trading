"""
NarrowRangeStrategy (개선 Cycle 219): NR + ATR 축소 + 거래량 확인

- NR 감지: 최근 nr_lookback 봉 중 최소 range 감지
- NR 윈도우: 최근 NR_SCAN_WINDOW 봉 내 NR 발생 여부 확인 (지연 돌파 포착)
- ATR 필터: NR 기간 ATR이 평균보다 수축 (20봉 평균 기준)
- 돌파 거래량: 거래량이 20봉 평균의 VOL_SPIKE_MULT 이상
- Breakout: 스캔 윈도우 내 NR 감지 AND ATR 축소 AND close 돌파
- confidence: NR4+NR AND volume spike → HIGH, 아니면 MEDIUM
"""

from typing import Dict, Optional

import pandas as pd

from .base import Action, BaseStrategy, Confidence, Signal


class NarrowRangeStrategy(BaseStrategy):
    name = "narrow_range"
    MIN_ROWS = 25
    ATR_LOOKBACK = 20
    VOL_LOOKBACK = 20
    VOL_SPIKE_MULT = 1.0   # 완화: 1.2→1.0 (4h봉 거래 수 증가 목적, Cycle 206)
    ATR_THRESHOLD = 0.95   # 완화: 0.90→0.95 (Cycle 219: 저거래 해결)
    NR_SCAN_WINDOW = 3     # NR 발생 후 최대 3봉 내 돌파 허용 (5→3 복원: Cycle 313 C 실험 역효과)

    def __init__(
        self,
        nr_lookback: int = 5,
        trend_regime_filter: bool = False,
        atr_trend_max: float = 1.4,
        ema_slope_min_buy: float = 0.0,
        ema_slope_max_sell: float = 0.0,
        vol_spike_mult: float = 1.0,
        atr_threshold: float = 0.95,
        **kwargs,
    ):
        """
        Args:
            nr_lookback: NR lookback 기간 (NR5=5, NR7=7).
            trend_regime_filter: True면 ATR/ATR_MA > atr_trend_max 시 신호 억제
                (고변동성 추세장에서 NR breakout 오신호 감소).
            atr_trend_max: trend_regime_filter 활성 시 상한 임계값 (기본 1.4).
            ema_slope_min_buy: BUY 진입 최소 EMA20 slope (0.0=필터 없음, 양수=상승추세 필수).
            ema_slope_max_sell: SELL 진입 최대 EMA20 slope (0.0=필터 없음, 음수=하락추세 필수).
            vol_spike_mult: 거래량 스파이크 배율 (기본 1.0=클래스 상수, 완화 시 0.5 등).
            atr_threshold: ATR 축소 임계값 배율 (기본 0.95, 완화 시 1.05 등). Cycle 315 A 실험.
        """
        self.nr_lookback = max(4, int(nr_lookback))  # 최소 4봉 (NR4 확인용)
        self.trend_regime_filter = bool(trend_regime_filter)
        self.atr_trend_max = float(atr_trend_max)
        self.ema_slope_min_buy = float(ema_slope_min_buy)
        self.ema_slope_max_sell = float(ema_slope_max_sell)
        self._vol_spike_mult = float(vol_spike_mult)
        self._atr_threshold = float(atr_threshold)

    def _is_nr(self, ranges: pd.Series, idx: int, n: int) -> bool:
        """idx번 봉이 최근 n봉 중 최소 range인지 확인."""
        if idx < n - 1:
            return False
        window = ranges.iloc[idx - n + 1: idx + 1]
        return float(ranges.iloc[idx]) <= float(window.min())

    def _find_recent_nr(self, ranges: pd.Series, curr_idx: int) -> Optional[Dict]:
        """최근 NR_SCAN_WINDOW 봉 내에서 가장 최근 NR 봉을 찾아 반환."""
        scan_start = max(self.nr_lookback - 1, curr_idx - self.NR_SCAN_WINDOW)
        for offset in range(1, self.NR_SCAN_WINDOW + 1):
            check_idx = curr_idx - offset
            if check_idx < scan_start:
                break
            if self._is_nr(ranges, check_idx, self.nr_lookback):
                is_nr4 = self._is_nr(ranges, check_idx, 4)
                return {"idx": check_idx, "is_nr4": is_nr4, "offset": offset}
        return None

    def generate(self, df: pd.DataFrame) -> Signal:
        if len(df) < self.MIN_ROWS:
            return self._hold(df, f"데이터 부족: {len(df)} < {self.MIN_ROWS}")

        # current = 마지막 완성봉 (iloc[-2])
        curr_idx = len(df) - 2  # 완성봉

        if curr_idx < self.nr_lookback + self.NR_SCAN_WINDOW:
            return self._hold(df, f"NR{self.nr_lookback} 판단에 필요한 이전 봉 부족")

        ranges = df["high"] - df["low"]

        # Cycle304 E: 고변동성 추세장 억제 (trend_regime_filter=True 시)
        # ATR/ATR_MA(20) > atr_trend_max이면 NR breakout은 오신호 가능성 높음
        if self.trend_regime_filter and "atr14" in df.columns:
            atr_curr = float(df["atr14"].iloc[curr_idx])
            lookback_start = max(0, curr_idx - self.ATR_LOOKBACK)
            atr_ma = float(df["atr14"].iloc[lookback_start:curr_idx].mean())
            if atr_ma > 0 and atr_curr / atr_ma > self.atr_trend_max:
                return self._hold(
                    df,
                    f"trend_regime_filter: ATR/ATR_MA={atr_curr/atr_ma:.2f} > {self.atr_trend_max}",
                )

        # 최근 NR_SCAN_WINDOW 봉 내에서 NR 봉 탐색 (지연 돌파 포착)
        nr_info = self._find_recent_nr(ranges, curr_idx)

        if nr_info is None:
            return self._hold(
                df,
                f"NR{self.nr_lookback} 최근 {self.NR_SCAN_WINDOW}봉 내 미감지",
            )

        nr_idx = nr_info["idx"]
        is_nr4 = nr_info["is_nr4"]

        # ATR 축소 확인 (NR 봉 기준)
        atr_series = df["atr14"]
        nr_atr = float(atr_series.iloc[nr_idx])
        avg_atr = float(atr_series.iloc[nr_idx - self.ATR_LOOKBACK : nr_idx].mean())

        atr_shrunk = nr_atr <= avg_atr * self._atr_threshold

        if not atr_shrunk:
            return self._hold(
                df,
                f"ATR 축소 미충족: nr_atr={nr_atr:.4f} > avg*{self._atr_threshold}={avg_atr*self._atr_threshold:.4f}",
            )

        # 거래량 확인 (현재 봉)
        vol_current = float(df["volume"].iloc[curr_idx])
        avg_vol = float(df["volume"].iloc[curr_idx - self.VOL_LOOKBACK : curr_idx].mean())

        vol_spike = vol_current >= avg_vol * self._vol_spike_mult

        close_curr = float(df["close"].iloc[curr_idx])
        high_nr = float(df["high"].iloc[nr_idx])
        low_nr = float(df["low"].iloc[nr_idx])

        # confidence: NR4+NR AND volume spike → HIGH
        conf = Confidence.HIGH if (is_nr4 and vol_spike) else Confidence.MEDIUM

        nr_label = f"NR{self.nr_lookback}"
        bull_case = (
            f"{nr_label}={'Y'} NR4={'Y' if is_nr4 else 'N'} ATR_shrink={'Y'} "
            f"vol_spike={'Y' if vol_spike else 'N'}, "
            f"close={close_curr:.4f} > nr_high={high_nr:.4f}"
        )
        bear_case = (
            f"{nr_label}={'Y'} NR4={'Y' if is_nr4 else 'N'} ATR_shrink={'Y'} "
            f"vol_spike={'Y' if vol_spike else 'N'}, "
            f"close={close_curr:.4f} < nr_low={low_nr:.4f}"
        )

        # EMA slope 필터 (ema20_slope 컬럼 존재 시)
        ema_slope = None
        if "ema20_slope" in df.columns:
            ema_slope = float(df["ema20_slope"].iloc[curr_idx])

        # 상향 돌파 (NR 봉의 high 기준)
        if close_curr > high_nr:
            if ema_slope is not None and self.ema_slope_min_buy != 0.0 and ema_slope < self.ema_slope_min_buy:
                return self._hold(
                    df,
                    f"ema_slope_min_buy 미충족: slope={ema_slope:.5f} < {self.ema_slope_min_buy}",
                )
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=close_curr,
                reasoning=(
                    f"{nr_label} 상향돌파(off={nr_info['offset']}): "
                    f"close({close_curr:.4f})>high({high_nr:.4f}), "
                    f"ATR={nr_atr:.4f}<avg*{self._atr_threshold}({avg_atr*self._atr_threshold:.4f})"
                ),
                invalidation=f"close < nr_high({high_nr:.4f}) 복귀 시 무효",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        # 하향 돌파 (NR 봉의 low 기준)
        if close_curr < low_nr:
            if ema_slope is not None and self.ema_slope_max_sell != 0.0 and ema_slope > self.ema_slope_max_sell:
                return self._hold(
                    df,
                    f"ema_slope_max_sell 미충족: slope={ema_slope:.5f} > {self.ema_slope_max_sell}",
                )
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=close_curr,
                reasoning=(
                    f"{nr_label} 하향돌파(off={nr_info['offset']}): "
                    f"close({close_curr:.4f})<low({low_nr:.4f}), "
                    f"ATR={nr_atr:.4f}<avg*{self._atr_threshold}({avg_atr*self._atr_threshold:.4f})"
                ),
                invalidation=f"close > nr_low({low_nr:.4f}) 복귀 시 무효",
                bull_case=bull_case,
                bear_case=bear_case,
            )

        return self._hold(
            df,
            f"{nr_label}+ATR축소 감지(off={nr_info['offset']})됐으나 돌파 없음: "
            f"close={close_curr:.4f} in [{low_nr:.4f}, {high_nr:.4f}]",
        )

    def _hold(self, df: pd.DataFrame, reason: str) -> Signal:
        last = self._last(df)
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=float(last["close"]),
            reasoning=reason,
            invalidation="",
            bull_case="",
            bear_case="",
        )
