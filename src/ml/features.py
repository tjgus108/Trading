"""
C1. FeatureBuilder: OHLCV + 기술 지표 → ML 학습 피처.

피처 목록:
  - 수익률: return_1, return_3, return_5, return_10, return_20
  - 변동성: atr_pct (ATR / close), volatility_20
  - 추세: ema_ratio (ema20/ema50), price_vs_ema20, price_vs_ema50
  - 볼륨: volume_ratio_20 (현재/20일 평균)
  - Donchian: donchian_pct (현재 가격의 채널 내 위치)
  - 기타: macd_hist, bb_position
  - BTC 시차 (선택): btc_close_lag1 — df에 'btc_close' 컬럼이 있을 때만 추가
  - FR/OI (선택): delta_fr, fr_oi_interaction — df에 'funding_rate'/'open_interest' 컬럼 필요

제거된 피처 (PFI near-zero, Cycle 149):
  - rsi14: MDI=0.0, PFI=0.0 (BTC/ETH/SOL 공통)
  - rsi_zscore: MDI=0.0, PFI=0.0 (BTC/ETH/SOL 공통)
  - price_vs_vwap: MDI=0.0, PFI=0.0 (BTC/ETH/SOL 공통)

타겟 레이블 (두 가지 방식):
  1. 기본 (forward_return 기반):
     - BUY(+1): forward_n 캔들 후 수익률 > threshold (기본 +0.3%)
     - SELL(-1): < -threshold
     - HOLD(0): 중립
  2. Triple Barrier (triple_barrier=True):
     - TP/SL 배리어 + 최대 보유기간(forward_n) 중 먼저 도달한 기준으로 레이블
     - UP(1): TP 배리어 먼저 도달 (entry * (1 + tp_pct))
     - DOWN(0): SL 배리어 먼저 도달 (entry * (1 - sl_pct))
     - 시간 초과(HOLD): 배리어 미도달 시 NaN 처리(binary 모드에서 제거)
     - 연구 결과: Precision 향상, 불명확한 중립 구간 제거 효과

walk-forward validation: 시계열 순서 반드시 유지.
"""

import numpy as np
import pandas as pd
from typing import Optional, Tuple, List


DEFAULT_FORWARD_N = 5       # 5캔들 후 수익률로 레이블 생성
DEFAULT_THRESHOLD = 0.003   # 0.3% 초과 시 BUY/SELL
DEFAULT_BINARY_THRESHOLD = 0.01  # 2-class 모드: 1% 이상만 학습
DEFAULT_TB_TP_PCT = 0.02    # Triple Barrier: TP 배리어 2% (기본)
DEFAULT_TB_SL_PCT = 0.01    # Triple Barrier: SL 배리어 1% (기본, R:R=2:1)


class FeatureBuilder:
    """
    DataFeed.fetch()의 DataFrame → 학습 피처 + 레이블 생성.
    """

    def __init__(
        self,
        forward_n: int = DEFAULT_FORWARD_N,
        threshold: float = DEFAULT_THRESHOLD,
        binary: bool = False,
        binary_threshold: float = DEFAULT_BINARY_THRESHOLD,
        triple_barrier: bool = False,
        tb_tp_pct: float = DEFAULT_TB_TP_PCT,
        tb_sl_pct: float = DEFAULT_TB_SL_PCT,
    ):
        """
        Args:
            forward_n: 레이블 생성 기준 — N 캔들 후 수익률 참조 (최대 보유기간).
            threshold: BUY/SELL 판정 최소 수익률 (기본 0.003 = 0.3%).
            binary: True면 2-class (UP=1/DOWN=0), |fwd_ret| < binary_threshold 제외.
            binary_threshold: 2-class 모드에서 중립 구간 폭 (기본 1%).
            triple_barrier: True면 TP/SL/시간 배리어 기반 레이블링 (binary 모드에만 적용).
            tb_tp_pct: Triple Barrier TP 배리어 크기 (기본 2%).
            tb_sl_pct: Triple Barrier SL 배리어 크기 (기본 1%).
        """
        self.forward_n = forward_n
        self.threshold = threshold
        self.binary = binary
        self.binary_threshold = binary_threshold
        self.triple_barrier = triple_barrier
        self.tb_tp_pct = tb_tp_pct
        self.tb_sl_pct = tb_sl_pct

    def build(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """
        피처 + 레이블 반환.

        Returns:
            X (pd.DataFrame): 피처 행렬 (NaN 행 제거됨)
            y (pd.Series): 레이블 {-1: SELL, 0: HOLD, 1: BUY}
        """
        feat = self._compute_features(df)
        labels = self._compute_labels(df)

        # 공통 인덱스 정렬 + NaN 제거
        combined = feat.join(labels, how="inner").dropna()
        X = combined.drop(columns=["label"])
        y = combined["label"]
        return X, y

    def build_features_only(self, df: pd.DataFrame) -> pd.DataFrame:
        """레이블 없이 피처만 반환 (추론용)."""
        return self._compute_features(df).dropna()

    # ------------------------------------------------------------------
    # Feature computation
    # ------------------------------------------------------------------

    def _compute_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        피처 계산 (look-ahead bias 방지).
        
        Look-ahead bias 주의:
        - rolling/ewm: 현재 바 포함 → shift(1) 적용하여 이전 데이터만 사용
        - RSI: 이전 20바 기준으로 정규화
        - 변동성: 이전 20바 기준
        - Donchian: 이전 20바의 고저 기준
        """
        close = df["close"]
        volume = df["volume"]
        high = df["high"]
        low = df["low"]

        feat = pd.DataFrame(index=df.index)

        # 수익률 (로그 수익률)
        log_ret = np.log(close / close.shift(1))
        feat["return_1"] = log_ret
        feat["return_3"] = np.log(close / close.shift(3))
        feat["return_5"] = np.log(close / close.shift(5))
        feat["return_10"] = np.log(close / close.shift(10))
        feat["return_20"] = np.log(close / close.shift(20))

        # ATR 변동성
        if "atr14" in df.columns:
            feat["atr_pct"] = df["atr14"] / close
        else:
            feat["atr_pct"] = (high - low) / close

        # 변동성: 이전 20바 기준 (현재 바 제외)
        feat["volatility_20"] = log_ret.shift(1).rolling(20).std()

        # EMA 비율: 이전 바 기준 EMA 사용
        if "ema20" in df.columns and "ema50" in df.columns:
            ema20_prev = df["ema20"].shift(1)
            ema50_prev = df["ema50"].shift(1)
            feat["ema_ratio"] = ema20_prev / ema50_prev
            feat["price_vs_ema20"] = (close - ema20_prev) / (ema20_prev + 1e-9)
            feat["price_vs_ema50"] = (close - ema50_prev) / (ema50_prev + 1e-9)
        else:
            close_prev = close.shift(1)
            ema20 = close_prev.ewm(span=20, adjust=False).mean()
            ema50 = close_prev.ewm(span=50, adjust=False).mean()
            feat["ema_ratio"] = ema20 / ema50
            feat["price_vs_ema20"] = (close - ema20) / (ema20 + 1e-9)
            feat["price_vs_ema50"] = (close - ema50) / (ema50 + 1e-9)

        # 볼륨: 이전 20바의 평균값 기준
        vol_ma20 = volume.shift(1).rolling(20).mean()
        feat["volume_ratio_20"] = volume / (vol_ma20 + 1e-9)

        # Donchian 채널 위치: 이전 20바 기준 (0~1)
        if "donchian_high" in df.columns and "donchian_low" in df.columns:
            chan_range = df["donchian_high"] - df["donchian_low"]
            feat["donchian_pct"] = (close - df["donchian_low"]) / (chan_range + 1e-9)
        else:
            high_prev = high.shift(1)
            low_prev = low.shift(1)
            high20 = high_prev.rolling(20).max()
            low20 = low_prev.rolling(20).min()
            chan_range = high20 - low20
            feat["donchian_pct"] = (close - low20) / (chan_range + 1e-9)

        # MACD 히스토그램: 이전 바 기준 (shift(1) 적용)
        close_prev = close.shift(1)
        ema12 = close_prev.ewm(span=12, adjust=False).mean()
        ema26 = close_prev.ewm(span=26, adjust=False).mean()
        macd_line = ema12 - ema26
        signal_line = macd_line.ewm(span=9, adjust=False).mean()
        feat["macd_hist"] = (macd_line - signal_line) / (close + 1e-9)

        # Bollinger Band 위치: 이전 20바 기준 (0~1, 밴드 내 상대 위치)
        bb_mid = close_prev.rolling(20).mean()
        bb_std = close_prev.rolling(20).std()
        bb_upper = bb_mid + 2 * bb_std
        bb_lower = bb_mid - 2 * bb_std
        bb_range = bb_upper - bb_lower
        feat["bb_position"] = (close - bb_lower) / (bb_range + 1e-9)

        # BTC 시차 피처 (ETH/SOL 개선용): df에 'btc_close' 컬럼이 있을 때만 추가
        # Cycle 150: ETH/SOL은 BTC 가격 움직임에 후행하는 경향 → 1봉 시차 수익률 사용
        if "btc_close" in df.columns:
            btc_close = df["btc_close"]
            feat["btc_close_lag1"] = np.log(btc_close.shift(1) / btc_close.shift(2))

        # Funding Rate + OI 파생 피처 (Cycle 158: SSRN 기반)
        # df에 'funding_rate' 컬럼이 있으면 delta_fr 추가
        # df에 'funding_rate' + 'open_interest' 둘 다 있으면 fr_oi_interaction 추가
        if "funding_rate" in df.columns:
            fr = df["funding_rate"]
            feat["delta_fr"] = fr.diff()
            if "open_interest" in df.columns:
                oi = df["open_interest"]
                oi_norm = oi / (oi.rolling(20, min_periods=1).mean() + 1e-9)
                feat["fr_oi_interaction"] = fr * oi_norm

        # inf/-inf → NaN 변환 (close=0 등 극단값 방어)
        feat = feat.replace([np.inf, -np.inf], np.nan)

        return feat

    def _compute_labels(self, df: pd.DataFrame) -> pd.Series:
        """
        레이블 생성. triple_barrier=True이면 TP/SL 배리어 기반, 아니면 forward_return 기반.

        Triple Barrier 모드 (binary=True, triple_barrier=True):
          각 바에서 이후 forward_n 캔들 내에 TP(+tb_tp_pct) 또는 SL(-tb_sl_pct)에
          먼저 도달하는 방향으로 레이블 결정.
          - UP(1): TP 배리어 먼저 도달
          - DOWN(0): SL 배리어 먼저 도달
          - 시간 초과: NaN → build() 에서 dropna로 제거

        기본 forward_return 모드:
          3-class: 1(BUY) / -1(SELL) / 0(HOLD)
          2-class (binary=True): 1(UP) / 0(DOWN), 중립 구간 NaN으로 제거
        """
        if self.triple_barrier and self.binary:
            return self._compute_triple_barrier_labels(df)

        close = df["close"]
        fwd_ret = close.shift(-self.forward_n) / close - 1.0

        if self.binary:
            label = pd.Series(np.nan, index=df.index, name="label", dtype=float)
            label[fwd_ret >= self.binary_threshold] = 1.0
            label[fwd_ret <= -self.binary_threshold] = 0.0
            return label.astype("Int64")

        label = pd.Series(np.nan, index=df.index, name="label", dtype=float)
        label[fwd_ret > self.threshold] = 1.0
        label[fwd_ret < -self.threshold] = -1.0
        label[~fwd_ret.isna()] = label[~fwd_ret.isna()].fillna(0.0)
        return label.astype("Int64")

    def _compute_triple_barrier_labels(self, df: pd.DataFrame) -> pd.Series:
        """
        Triple Barrier 레이블링 (Marcos Lopez de Prado 방식).

        각 바의 종가를 진입가로 보고, 이후 forward_n 캔들의 고가/저가를 순서대로
        확인하여 TP 또는 SL 배리어에 먼저 도달하는 레이블을 부여.

        - high/low 데이터 사용 → 캔들 내 배리어 터치 더 정확히 감지
        - 시간 배리어(forward_n) 내 미도달 시 NaN (build() dropna로 제거)
        - 계산 복잡도: O(n * forward_n), 대용량 데이터에서도 vectorized로 처리

        Returns:
            pd.Series with Int64: 1(UP) / 0(DOWN) / NaN(시간초과 또는 마지막 forward_n 바)
        """
        close = df["close"].values
        high = df["high"].values
        low = df["low"].values
        n = len(close)

        labels = np.full(n, np.nan)

        tp_mult = 1.0 + self.tb_tp_pct
        sl_mult = 1.0 - self.tb_sl_pct

        for i in range(n - self.forward_n):
            entry = close[i]
            tp_level = entry * tp_mult
            sl_level = entry * sl_mult

            hit = np.nan
            for j in range(i + 1, i + self.forward_n + 1):
                if high[j] >= tp_level:
                    hit = 1.0
                    break
                if low[j] <= sl_level:
                    hit = 0.0
                    break
            labels[i] = hit  # NaN if neither barrier hit within forward_n

        result = pd.Series(labels, index=df.index, name="label", dtype=float)
        # NaN 유지 (build() dropna로 제거됨) → 시간 초과 바 자동 제외
        return result.astype("Int64")

    @property
    def feature_names(self) -> List[str]:
        """모델 학습/추론에 사용되는 피처 컬럼명 목록 (순서 고정).

        Cycle 149: rsi14, rsi_zscore, price_vs_vwap 제거 (PFI near-zero).
        Cycle 150: btc_close_lag1 추가 (선택적 — df에 'btc_close' 컬럼 필요).
        Cycle 158: delta_fr, fr_oi_interaction 추가 (선택적 — df에 'funding_rate'/'open_interest' 필요).
        base 14피처만 반환. 선택적 피처는 build() 시 자동 추가됨.
        """
        return [
            "return_1", "return_3", "return_5", "return_10", "return_20",
            "atr_pct", "volatility_20",
            "ema_ratio", "price_vs_ema20", "price_vs_ema50",
            "volume_ratio_20",
            "donchian_pct",
            "macd_hist",
            "bb_position",
        ]
