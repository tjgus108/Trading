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
import logging
import pandas as pd
from typing import Dict, List, Optional, Tuple


DEFAULT_FORWARD_N = 5       # 5캔들 후 수익률로 레이블 생성

logger = logging.getLogger(__name__)
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
        if df.empty or "close" not in df.columns:
            return pd.DataFrame(), pd.Series(dtype=float)
        feat = self._compute_features(df)
        labels = self._compute_labels(df)

        # 공통 인덱스 정렬 + NaN 제거
        combined = feat.join(labels, how="inner").dropna()
        X = combined.drop(columns=["label"])
        y = combined["label"]
        return X, y

    def build_features_only(self, df: pd.DataFrame) -> pd.DataFrame:
        """레이블 없이 피처만 반환 (추론용)."""
        if df.empty or "close" not in df.columns:
            return pd.DataFrame()
        return self._compute_features(df).dropna()

    def build_with_feature_selection(
        self,
        df: pd.DataFrame,
        drop_features: List[str],
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """낮은 중요도 피처를 제거하고 build() 수행.

        MLSignalGenerator.get_low_importance_features()와 연계:
            low_feats = gen.get_low_importance_features(threshold=0.01)
            X, y = builder.build_with_feature_selection(df, low_feats)

        Args:
            df: OHLCV DataFrame
            drop_features: 제거할 피처 이름 목록

        Returns:
            X, y — drop_features 제거 후의 피처 행렬 + 레이블
        """
        X, y = self.build(df)
        if X.empty or not drop_features:
            return X, y
        cols_to_drop = [c for c in drop_features if c in X.columns]
        if cols_to_drop:
            logger.debug("FeatureBuilder: dropping %d low-importance features: %s", len(cols_to_drop), cols_to_drop)
            X = X.drop(columns=cols_to_drop)
        return X, y

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

        # 온체인 피처 (Cycle 194: Glassnode/CryptoQuant 기반)
        # exchange_netflow: 거래소 순유입(양수)/순유출(음수) — 대규모 유입 시 매도 압력 신호
        # sopr: Spent Output Profit Ratio — >1이면 평균 이익 실현, <1이면 손실 패닉 매도
        if "exchange_netflow" in df.columns:
            netflow = df["exchange_netflow"]
            netflow_ma = netflow.rolling(20, min_periods=1).mean()
            feat["exchange_netflow_norm"] = netflow / (netflow_ma.abs() + 1e-9)

        if "sopr" in df.columns:
            sopr = df["sopr"]
            sopr_std = sopr.rolling(28, min_periods=5).std()
            feat["sopr_delta"] = sopr.diff(28) / (sopr_std + 1e-9)

        # VPIN (Volume-Synchronized Probability of Informed Trading) — Cycle 232
        # OHLCV만으로 계산 가능: close>open → BUY fraction, close<open → SELL fraction
        # 50봉 롤링 윈도우, [0, 1] 범위. 0.5=중립, 0.8+= 강한 방향성 주문 흐름
        # 연구: Easley et al. (2012) VPIN이 플래시 크래시 선행 지표임을 확인
        if "volume" in df.columns and len(df) >= 10:
            _vol = volume.fillna(0.0).clip(lower=0.0)
            _buy_frac = pd.Series(0.5, index=df.index, dtype=float)
            _buy_frac[close > df["open"]] = 1.0
            _buy_frac[close < df["open"]] = 0.0
            _buy_frac[_vol == 0] = 0.5
            _imbalance = (_vol * _buy_frac - _vol * (1.0 - _buy_frac)).abs()
            _roll_vol = _vol.rolling(50, min_periods=10).sum()
            _roll_imb = _imbalance.rolling(50, min_periods=10).sum()
            _vpin = (_roll_imb / _roll_vol.replace(0, float("nan"))).fillna(0.5).clip(0.0, 1.0)
            feat["vpin_50"] = _vpin

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


# ---------------------------------------------------------------------------
# Regime Detection + Dynamic Feature Selection (Cycle 170+)
# ---------------------------------------------------------------------------

# 레짐별 PFI/SHAP 기반 top-K 피처 사전 정의.
# bull: 추세 피처 우선 (EMA, 수익률, 볼륨)
# bear: 변동성·위험 피처 우선 (ATR, Donchian, BB)
# ranging: 오실레이터 피처 우선 (BB, MACD, 볼륨)
# crisis: 보수적 — 변동성·단기 수익률만
REGIME_FEATURE_CONFIG: Dict[str, List[str]] = {
    "bull": [
        "return_1", "return_3", "return_5", "return_10",
        "ema_ratio", "price_vs_ema20", "price_vs_ema50",
        "volume_ratio_20", "donchian_pct",
        "macd_hist",
    ],
    "bear": [
        "return_1", "return_3", "return_5",
        "atr_pct", "volatility_20",
        "donchian_pct", "bb_position",
        "macd_hist", "price_vs_ema50",
    ],
    "ranging": [
        "return_1", "return_3",
        "atr_pct", "volatility_20",
        "bb_position", "macd_hist",
        "volume_ratio_20", "donchian_pct",
    ],
    "crisis": [
        "return_1", "return_3",
        "atr_pct", "volatility_20",
        "bb_position",
    ],
}

# 각 레짐의 base 피처 외에 선택적 피처 (df에 컬럼 있으면 추가)
REGIME_OPTIONAL_FEATURES: Dict[str, List[str]] = {
    "bull":    ["btc_close_lag1", "delta_fr", "fr_oi_interaction", "exchange_netflow_norm", "sopr_delta"],
    "bear":    ["delta_fr", "fr_oi_interaction", "exchange_netflow_norm", "sopr_delta"],
    "ranging": ["btc_close_lag1", "sopr_delta"],
    "crisis":  ["delta_fr", "exchange_netflow_norm", "sopr_delta"],
}


def detect_regime(df: pd.DataFrame, lookback: int = 20) -> str:
    """
    최근 lookback 캔들의 가격 움직임으로 시장 레짐 감지.

    로직:
    - EMA20 vs EMA50 기울기: bull/bear 판별
    - ATR 기반 변동성: crisis 판별 (ATR_pct > 2σ)
    - Donchian 채널 폭: ranging 판별 (채널 폭 < 중앙값)

    Returns:
        str: "bull" | "bear" | "ranging" | "crisis"
    """
    if len(df) < lookback + 1:
        return "ranging"

    close = df["close"].values
    high = df["high"].values
    low = df["low"].values

    recent = close[-lookback:]

    # EMA20/EMA50 (전체 시계열로 계산 후 최근 값 사용)
    close_s = pd.Series(close)
    ema20 = close_s.ewm(span=20, adjust=False).mean().values
    ema50 = close_s.ewm(span=50, adjust=False).mean().values
    ema20_now = ema20[-1]
    ema50_now = ema50[-1]

    # 변동성 (ATR_pct)
    atr_vals = (high[-lookback:] - low[-lookback:]) / (close[-lookback:] + 1e-9)
    atr_mean = float(np.mean(atr_vals))
    atr_std_hist = float(np.std(atr_vals)) if len(atr_vals) > 1 else 0.0

    # 이전 60봉 ATR 기준 z-score
    lookback_long = min(60, len(close))
    atr_long = (high[-lookback_long:] - low[-lookback_long:]) / (close[-lookback_long:] + 1e-9)
    atr_long_mean = float(np.mean(atr_long))
    atr_long_std = float(np.std(atr_long)) if len(atr_long) > 1 else 1e-9
    atr_zscore = (atr_mean - atr_long_mean) / (atr_long_std + 1e-9)

    # Donchian 채널 폭 (최근 lookback)
    high20 = np.max(high[-lookback:])
    low20 = np.min(low[-lookback:])
    channel_width = (high20 - low20) / (low20 + 1e-9)

    # 이전 60봉 채널 폭 중앙값
    lookback_long2 = min(60, len(close) - lookback)
    if lookback_long2 > 0:
        channel_widths_hist = [
            (np.max(high[i:i+lookback]) - np.min(low[i:i+lookback])) / (np.min(low[i:i+lookback]) + 1e-9)
            for i in range(lookback_long2)
        ]
        channel_median = float(np.median(channel_widths_hist)) if channel_widths_hist else channel_width
    else:
        channel_median = channel_width

    # 레짐 판별
    # 1. Crisis: ATR z-score > 2.0 (비정상 변동성)
    if atr_zscore > 2.0:
        return "crisis"

    # 2. Ranging: 채널 폭 < 중앙값 (좁은 박스권)
    if channel_width < channel_median * 0.8:
        return "ranging"

    # 3. Bull / Bear: EMA 방향
    if ema20_now > ema50_now:
        return "bull"
    else:
        return "bear"


class RegimeAwareFeatureBuilder:
    """
    레짐별 동적 피처 선택 파이프라인 (Cycle 170+).

    기존 FeatureBuilder를 래핑하여:
    1. detect_regime()으로 현재 레짐 감지
    2. REGIME_FEATURE_CONFIG에서 해당 레짐 피처 서브셋 선택
    3. 선택된 피처만 반환 (학습/예측 모두 동일 로직)

    사용법:
        builder = RegimeAwareFeatureBuilder()
        X, y, regime = builder.build_with_regime(df)
        # 예측 시:
        X_live, regime = builder.build_features_regime(df)
    """

    def __init__(
        self,
        forward_n: int = DEFAULT_FORWARD_N,
        threshold: float = DEFAULT_THRESHOLD,
        binary: bool = False,
        triple_barrier: bool = False,
        tb_tp_pct: float = DEFAULT_TB_TP_PCT,
        tb_sl_pct: float = DEFAULT_TB_SL_PCT,
        regime_lookback: int = 20,
        feature_config: Optional[Dict[str, List[str]]] = None,
    ):
        self._base = FeatureBuilder(
            forward_n=forward_n,
            threshold=threshold,
            binary=binary,
            triple_barrier=triple_barrier,
            tb_tp_pct=tb_tp_pct,
            tb_sl_pct=tb_sl_pct,
        )
        self.regime_lookback = regime_lookback
        # 외부에서 커스텀 config 주입 가능
        self._config: Dict[str, List[str]] = feature_config or REGIME_FEATURE_CONFIG

    # ----------------------------------------------------------------
    # Public API
    # ----------------------------------------------------------------

    def build_with_regime(
        self, df: pd.DataFrame
    ) -> Tuple[pd.DataFrame, pd.Series, str]:
        """
        레짐 감지 후 해당 레짐 피처 서브셋으로 X, y 반환.

        Returns:
            X: 레짐별 피처 서브셋 DataFrame
            y: 레이블 Series
            regime: 감지된 레짐 문자열
        """
        regime = detect_regime(df, lookback=self.regime_lookback)
        X_all, y = self._base.build(df)
        X = self._select(X_all, regime, df)
        return X, y, regime

    def build_features_regime(
        self, df: pd.DataFrame
    ) -> Tuple[pd.DataFrame, str]:
        """
        레짐 감지 후 피처만 반환 (추론 전용).

        Returns:
            X: 레짐별 피처 서브셋 DataFrame
            regime: 감지된 레짐 문자열
        """
        regime = detect_regime(df, lookback=self.regime_lookback)
        X_all = self._base.build_features_only(df)
        X = self._select(X_all, regime, df)
        return X, regime

    def get_regime_features(self, regime: str, df: Optional[pd.DataFrame] = None) -> List[str]:
        """
        레짐별 피처 리스트 반환.

        Args:
            regime: "bull" | "bear" | "ranging" | "crisis"
            df: 선택적 피처(FR/OI/BTC) 존재 여부 확인용

        Returns:
            List[str]: 해당 레짐에서 사용될 피처명 목록
        """
        base_feats = list(self._config.get(regime, self._config.get("ranging", [])))
        if df is not None:
            optionals = REGIME_OPTIONAL_FEATURES.get(regime, [])
            for feat in optionals:
                # 선택적 피처는 실제 컬럼 존재 여부로 판별
                source_col = {
                    "btc_close_lag1": "btc_close",
                    "delta_fr": "funding_rate",
                    "fr_oi_interaction": "open_interest",
                    "exchange_netflow_norm": "exchange_netflow",
                    "sopr_delta": "sopr",
                }.get(feat, feat)
                if source_col in df.columns:
                    base_feats.append(feat)
        return base_feats

    # ----------------------------------------------------------------
    # Internal helpers
    # ----------------------------------------------------------------

    def _select(
        self, X_all: pd.DataFrame, regime: str, df: pd.DataFrame
    ) -> pd.DataFrame:
        """X_all에서 regime에 해당하는 피처 컬럼만 추출."""
        wanted = self.get_regime_features(regime, df)
        available = [c for c in wanted if c in X_all.columns]
        if len(available) < 2:
            # fallback: 전체 피처 사용
            return X_all
        return X_all[available]

    def get_feature_importance(
        self, df: pd.DataFrame, regime: Optional[str] = None
    ) -> Dict[str, float]:
        """빠른 RF fit으로 레짐별 피처 중요도 반환.

        Args:
            df: OHLCV DataFrame
            regime: 사용할 레짐 (None이면 detect_regime()으로 자동 감지)

        Returns:
            {feature_name: importance} — 합계 1.0으로 정규화. 데이터 부족 시 빈 dict.
        """
        try:
            from sklearn.ensemble import RandomForestClassifier
        except ImportError:
            return {}

        if regime is None:
            regime = detect_regime(df, lookback=self.regime_lookback)

        X_all, y = self._base.build(df)
        X = self._select(X_all, regime, df)

        if X.empty or len(X) < 20:
            return {}

        # y에 NaN이 남아있을 수 있으므로 제거하고 int 변환 (sklearn 호환)
        valid = y.notna()
        X = X.loc[valid]
        y = y.loc[valid].astype(int)

        if X.empty or len(X) < 20:
            return {}

        rf = RandomForestClassifier(
            n_estimators=50, max_depth=4, random_state=42, n_jobs=1
        )
        rf.fit(X.values, y.values)
        importances = rf.feature_importances_
        return {col: round(float(imp), 4) for col, imp in zip(X.columns, importances)}

    def get_feature_importance_by_regime(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        regime_labels: pd.Series,
        min_samples: int = 30,
    ) -> Dict[str, Dict[str, float]]:
        """레짐별로 분리된 피처 중요도를 반환.

        각 레짐에 해당하는 샘플만 필터링하여 독립적으로
        RandomForestClassifier를 학습시키고 feature_importances_를 추출한다.

        Args:
            X: 피처 행렬 (build() 결과의 X)
            y: 레이블 시리즈 (build() 결과의 y)
            regime_labels: 각 행에 대응하는 레짐 레이블 (예: "bull", "TREND" 등).
                          X, y와 동일 인덱스여야 함.
            min_samples: 레짐별 최소 샘플 수. 미달 시 해당 레짐 스킵. 기본 30.

        Returns:
            dict[regime_label, dict[feature_name, importance]]
            각 레짐별 {피처명: 중요도} 딕셔너리. 중요도 합계 ≈ 1.0.
            샘플 부족 레짐은 결과에서 제외.
        """
        try:
            from sklearn.ensemble import RandomForestClassifier
        except ImportError:
            return {}

        if X.empty or y.empty:
            return {}

        # 인덱스 정렬
        common_idx = X.index.intersection(y.index).intersection(regime_labels.index)
        X_aligned = X.loc[common_idx]
        y_aligned = y.loc[common_idx]
        regime_aligned = regime_labels.loc[common_idx]

        # NaN 제거
        valid = y_aligned.notna()
        X_aligned = X_aligned.loc[valid]
        y_aligned = y_aligned.loc[valid]
        regime_aligned = regime_aligned.loc[valid]

        result: Dict[str, Dict[str, float]] = {}

        for regime_label in regime_aligned.unique():
            mask = regime_aligned == regime_label
            X_regime = X_aligned.loc[mask]
            y_regime = y_aligned.loc[mask]

            if len(X_regime) < min_samples:
                logger.debug(
                    "get_feature_importance_by_regime: skip regime '%s' "
                    "(samples=%d < min=%d)",
                    regime_label, len(X_regime), min_samples,
                )
                continue

            # y에 1개 클래스만 있으면 RF 학습 불가 → 스킵
            if y_regime.nunique() < 2:
                logger.debug(
                    "get_feature_importance_by_regime: skip regime '%s' "
                    "(only %d class)",
                    regime_label, y_regime.nunique(),
                )
                continue

            rf = RandomForestClassifier(
                n_estimators=50, max_depth=4, random_state=42, n_jobs=1,
            )
            rf.fit(X_regime.values, y_regime.astype(int).values)
            importances = rf.feature_importances_
            result[regime_label] = {
                col: round(float(imp), 4)
                for col, imp in zip(X_regime.columns, importances)
            }

        return result

    # 기존 FeatureBuilder API 위임 (기존 코드와 호환)
    def build(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """기존 FeatureBuilder.build() 호환 — 레짐 감지 없이 전체 피처 반환."""
        return self._base.build(df)

    def build_features_only(self, df: pd.DataFrame) -> pd.DataFrame:
        """기존 FeatureBuilder.build_features_only() 위임."""
        return self._base.build_features_only(df)

    @property
    def feature_names(self) -> List[str]:
        return self._base.feature_names

    def build_with_cached_regime(
        self, df: pd.DataFrame, feed_regime: Optional[str] = None
    ) -> Tuple[pd.DataFrame, pd.Series, str]:
        """
        DataFeed 캐시 레짐을 사용하는 방식 (Cycle 174+).
        
        DataFeed.fetch_with_regime() 또는 get_cached_regime()의 결과를
        직접 전달하여 사용, detect_regime()을 재계산하지 않음.
        
        Args:
            df: OHLCV DataFrame
            feed_regime: DataFeed에서 캐시된 레짐 ("bull", "bear", "ranging", "crisis")
                        None이면 내부 detect_regime() 호출 (기존 동작)
        
        Returns:
            X: 선택된 피처 DataFrame
            y: 레이블 Series
            regime: 사용된 레짐 문자열
        
        Example:
            >>> feed = DataFeed(connector)
            >>> summary, feed_regime = feed.fetch_with_regime("BTC/USDT", "1h")
            >>> builder = RegimeAwareFeatureBuilder()
            >>> X, y, regime = builder.build_with_cached_regime(summary.df, feed_regime)
            >>> # regime == feed_regime (DataFeed와 동일한 레짐 사용)
        """
        if feed_regime is None:
            # Fallback: 내부 detect_regime() 호출
            return self.build_with_regime(df)
        
        # feed_regime 검증
        if feed_regime not in self._config:
            logger.warning(
                "Invalid regime '%s' from feed, falling back to detect_regime()",
                feed_regime
            )
            return self.build_with_regime(df)
        
        # 캐시된 레짐 사용
        X_all, y = self._base.build(df)
        X = self._select(X_all, feed_regime, df)
        return X, y, feed_regime

    def build_features_with_cached_regime(
        self, df: pd.DataFrame, feed_regime: Optional[str] = None
    ) -> Tuple[pd.DataFrame, str]:
        """
        DataFeed 캐시 레짐 기반 피처 추출 (추론용).
        
        Args:
            df: OHLCV DataFrame
            feed_regime: DataFeed 캐시 레짐 (None이면 내부 detect_regime())
        
        Returns:
            X: 선택된 피처 DataFrame
            regime: 사용된 레짐 문자열
        """
        if feed_regime is None:
            return self.build_features_regime(df)
        
        if feed_regime not in self._config:
            logger.warning(
                "Invalid regime '%s' from feed, falling back to detect_regime()",
                feed_regime
            )
            return self.build_features_regime(df)
        
        X_all = self._base.build_features_only(df)
        X = self._select(X_all, feed_regime, df)
        return X, feed_regime


# ---------------------------------------------------------------------------
# On-chain Feature Interface (Cycle 195)
# Cycle 193 리서치 결과: Exchange Netflow, SOPR delta, DeFiLlama TVL
# 실 API 미연동 — 메서드 시그니처 + 합성 데이터 폴백
# ---------------------------------------------------------------------------

class OnChainFeatureStub:
    """
    온체인 피처 인터페이스 (stub).

    Cycle 193 리서치 기반 피처:
      - exchange_netflow: 거래소 순유입 (BTC/ETH). 양수 = 매도 압력 증가.
      - sopr_delta: SOPR 1봉 변화량. SOPR > 1 = 수익 실현 구간.
      - defi_tvl_ratio: DeFiLlama TVL / 30일 평균 (체인 수요 프록시).

    실 API 연동 시 override할 메서드:
      - fetch_exchange_netflow(symbol, n)
      - fetch_sopr(n)
      - fetch_defi_tvl(chain, n)

    폴백: 합성 0 시리즈 (실 데이터 없을 때 피처 파이프라인 유지용).
    """

    def __init__(self, use_synthetic: bool = True):
        """
        Args:
            use_synthetic: True면 실 API 없이 0 기반 합성 폴백 반환.
                           False면 fetch_* 메서드가 실 API 호출을 시도해야 함.
        """
        self.use_synthetic = use_synthetic

    # ------------------------------------------------------------------
    # Public API (FeatureBuilder와 동일한 반환 형식: pd.Series)
    # ------------------------------------------------------------------

    def fetch_exchange_netflow(self, symbol: str = "BTC", n: int = 500) -> pd.Series:
        """
        거래소 순유입 시계열 반환 (BTC/ETH 기준, 단위: 코인).

        실 데이터 소스 (미연동):
          - CryptoQuant Exchange Netflow API
          - Glassnode Exchange Net Position Change

        Returns:
            pd.Series (name="exchange_netflow"), 합성 폴백 시 0.0 시리즈.
        """
        if self.use_synthetic:
            return self._synthetic_series(n, "exchange_netflow")
        raise NotImplementedError(
            "실 API 연동 필요: CryptoQuant 또는 Glassnode exchange_netflow"
        )

    def fetch_sopr(self, n: int = 500) -> pd.Series:
        """
        SOPR (Spent Output Profit Ratio) 시계열 반환.

        실 데이터 소스 (미연동):
          - Glassnode SOPR API (/v1/metrics/indicators/sopr)
          - LookIntoBitcoin SOPR

        Returns:
            pd.Series (name="sopr_delta"): SOPR 1봉 변화량.
            합성 폴백 시 0.0 시리즈.
        """
        if self.use_synthetic:
            return self._synthetic_series(n, "sopr_delta")
        raise NotImplementedError(
            "실 API 연동 필요: Glassnode SOPR (/v1/metrics/indicators/sopr)"
        )

    def fetch_defi_tvl(self, chain: str = "ethereum", n: int = 500) -> pd.Series:
        """
        DeFiLlama TVL / 30일 평균 비율 반환.

        실 데이터 소스 (미연동):
          - DeFiLlama /v2/chains API
          - URL: https://api.llama.fi/v2/historicalChainTvl/{chain}

        Returns:
            pd.Series (name="defi_tvl_ratio"): TVL / 30d_mean 비율.
            합성 폴백 시 1.0 시리즈 (중립값).
        """
        if self.use_synthetic:
            idx = pd.RangeIndex(n)
            return pd.Series(np.ones(n), index=idx, name="defi_tvl_ratio")
        raise NotImplementedError(
            "실 API 연동 필요: DeFiLlama /v2/historicalChainTvl/{chain}"
        )

    def enrich_df(self, df: pd.DataFrame, symbol: str = "BTC") -> pd.DataFrame:
        """
        기존 OHLCV DataFrame에 온체인 피처 컬럼을 추가 반환.

        추가 컬럼:
          - exchange_netflow: 거래소 순유입
          - sopr_delta: SOPR 변화량
          - defi_tvl_ratio: TVL 비율

        실 데이터 미연동(use_synthetic=True) 시 합성 폴백으로 파이프라인 형태 유지.

        Args:
            df: OHLCV DataFrame (index가 DatetimeIndex 권장).
            symbol: 온체인 데이터 심볼 (예: "BTC", "ETH").

        Returns:
            온체인 컬럼이 추가된 DataFrame (원본 복사본).
        """
        n = len(df)
        out = df.copy()

        netflow = self.fetch_exchange_netflow(symbol=symbol, n=n)
        sopr = self.fetch_sopr(n=n)
        tvl = self.fetch_defi_tvl(n=n)

        # 인덱스 정렬 — 합성 폴백은 RangeIndex이므로 df 인덱스로 재할당
        out["exchange_netflow"] = netflow.values[:n] if len(netflow) >= n else 0.0
        out["sopr_delta"] = sopr.values[:n] if len(sopr) >= n else 0.0
        out["defi_tvl_ratio"] = tvl.values[:n] if len(tvl) >= n else 1.0

        logger.debug(
            "OnChainFeatureStub.enrich_df: added 3 on-chain cols to df(len=%d), synthetic=%s",
            n, self.use_synthetic,
        )
        return out

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _synthetic_series(n: int, name: str) -> pd.Series:
        """합성 폴백: 0.0으로 채운 시리즈."""
        return pd.Series(np.zeros(n), index=pd.RangeIndex(n), name=name)
