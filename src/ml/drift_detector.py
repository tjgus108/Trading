"""
Concept Drift Detector — ML 예측 정확도 모니터링 및 드리프트 감지.

river 라이브러리 없이 순수 numpy로 구현.

알고리즘:
  - Page-Hinkley (PHT): 점진적 drift 감지에 최적화.
    평균 대비 누적 편차가 임계값 초과 시 드리프트 신호.
  - CUSUM: 이분점(changepoint) 감지. PHT의 대칭 버전.
  - PSI (Population Stability Index): 피처 분포 변화 감지.
    학습 시점 분포 vs 실시간 분포를 비교하여 재학습 필요성 판단.
    PSI > 0.1 약간 변화, > 0.2 유의미 (재학습 필요), > 0.25 심각.
  - ADWIN (ADaptive WINdowing): 가변 윈도우 기반 drift 감지.
    두 부분 윈도우의 평균 차이가 통계적으로 유의미하면 오래된 쪽 제거.
    delta=0.05~0.1 (금융 시계열 권장).
  - DualGateADWINMonitor: 이중 게이트 패턴.
    피처 ADWIN + 모델출력 ADWIN 모두 확인, 재학습 트리거.

사용법:
    detector = PageHinkleyDriftDetector(delta=0.005, lambda_=50.0)
    for correct in [1, 1, 0, 1, 0, 0, 0, ...]:
        detector.update(correct)
        if detector.drift_detected:
            print("Drift detected — trigger retrain")
            detector.reset()

    # 또는 AccuracyDriftMonitor로 window 기반 모니터링
    monitor = AccuracyDriftMonitor(window=50, min_accuracy=0.55)
    monitor.update(prediction=1, actual=1)
    if monitor.should_retrain:
        trigger_retrain()

    # PSI 기반 피처 분포 드리프트 감지
    monitor = PSIDriftMonitor(n_bins=10)
    monitor.set_reference(training_feature_values)
    psi = monitor.compute_psi(current_feature_values)
    if monitor.drift_detected:
        trigger_retrain()

    # ADWIN 이중 게이트 드리프트 감지 (금융 시계열 권장)
    monitor = DualGateADWINMonitor(delta=0.05, feature_names=["rsi", "ema_ratio"])
    monitor.update_feature(feature_name="rsi", value=0.65)
    monitor.update_model_output(proba=0.72)
    if monitor.should_retrain:
        trigger_retrain()
        monitor.reset()
"""

import logging
import math
from collections import deque
from typing import Dict, Deque, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


class PageHinkleyDriftDetector:
    """
    Page-Hinkley Test (PHT) 기반 concept drift detector.

    점진적 정확도 저하(개념 드리프트)를 감지한다.
    각 스텝에서 binary 정확도(1=맞음, 0=틀림)를 입력받아
    누적 편차가 lambda_ 초과 시 드리프트 신호를 발생시킨다.

    Args:
        delta: 허용 편차 (기본 0.005). 노이즈 대비 민감도 조절.
               작을수록 더 빠르게 감지, 클수록 false positive 감소.
        lambda_: 드리프트 임계값 (기본 50.0). 누적 편차 합산 기준.
                 클수록 드리프트 선언 지연 (안정적), 작을수록 빠른 반응.
        min_samples: 드리프트 체크 최소 샘플 수 (기본 30).
    """

    def __init__(
        self,
        delta: float = 0.005,
        lambda_: float = 50.0,
        min_samples: int = 30,
    ):
        self.delta = delta
        self.lambda_ = lambda_
        self.min_samples = min_samples
        self.reset()

    def reset(self) -> None:
        """상태 초기화. 드리프트 감지 후 호출."""
        self._sum = 0.0
        self._x_mean = 0.0
        self._n = 0
        self._min_sum = 0.0
        self.drift_detected = False
        logger.debug("PageHinkley: reset")

    def update(self, correct: float) -> bool:
        """
        새 관측값으로 상태 업데이트.

        Args:
            correct: 1.0 (정답) 또는 0.0 (오답). float 허용.

        Returns:
            bool: 드리프트 감지 여부.
        """
        self._n += 1
        self._x_mean += (correct - self._x_mean) / self._n
        self._sum += correct - self._x_mean - self.delta
        self._min_sum = min(self._min_sum, self._sum)

        if self._n >= self.min_samples:
            ph_stat = self._sum - self._min_sum
            if ph_stat > self.lambda_:
                self.drift_detected = True
                logger.info(
                    "PageHinkley DRIFT DETECTED: n=%d, ph_stat=%.2f > lambda=%.1f, "
                    "running_mean=%.3f",
                    self._n, ph_stat, self.lambda_, self._x_mean,
                )
                return True

        self.drift_detected = False
        return False

    @property
    def n_samples(self) -> int:
        return self._n

    @property
    def running_accuracy(self) -> float:
        """지금까지의 누적 평균 정확도."""
        return self._x_mean

    def summary(self) -> str:
        ph_stat = self._sum - self._min_sum
        return (
            f"PageHinkley(n={self._n}, acc={self._x_mean:.3f}, "
            f"ph_stat={ph_stat:.2f}, threshold={self.lambda_}, "
            f"drift={'YES' if self.drift_detected else 'NO'})"
        )


class CUSUMDriftDetector:
    """
    CUSUM (Cumulative Sum) 기반 양방향 drift detector.

    정확도 상승/하락 모두 감지한다.
    PHT가 단방향(하락)인 반면 CUSUM은 양방향 변화를 탐지.

    Args:
        k: 허용 기준선 이탈 크기 (기본 0.5). 보통 shift_size / 2.
        h: 드리프트 임계값 (기본 5.0). 누적 통계가 h 초과 시 drift.
        min_samples: 체크 시작 최소 샘플 수 (기본 30).
    """

    def __init__(self, k: float = 0.5, h: float = 5.0, min_samples: int = 30):
        self.k = k
        self.h = h
        self.min_samples = min_samples
        self.reset()

    def reset(self) -> None:
        self._n = 0
        self._mean = 0.0
        self._g_pos = 0.0   # 상승 CUSUM
        self._g_neg = 0.0   # 하락 CUSUM
        self.drift_detected = False
        logger.debug("CUSUM: reset")

    def update(self, correct: float) -> bool:
        self._n += 1
        self._mean += (correct - self._mean) / self._n
        # CUSUM 통계 (정규화: 현재 오차 - 허용 편차 k)
        self._g_pos = max(0.0, self._g_pos + correct - self._mean - self.k)
        self._g_neg = max(0.0, self._g_neg - correct + self._mean - self.k)

        if self._n >= self.min_samples:
            if self._g_pos > self.h or self._g_neg > self.h:
                direction = "UP" if self._g_pos > self.h else "DOWN"
                logger.info(
                    "CUSUM DRIFT DETECTED: n=%d, direction=%s, "
                    "g_pos=%.2f, g_neg=%.2f, threshold=%.1f",
                    self._n, direction, self._g_pos, self._g_neg, self.h,
                )
                self.drift_detected = True
                return True

        self.drift_detected = False
        return False

    @property
    def n_samples(self) -> int:
        return self._n

    def summary(self) -> str:
        return (
            f"CUSUM(n={self._n}, mean={self._mean:.3f}, "
            f"g_pos={self._g_pos:.2f}, g_neg={self._g_neg:.2f}, h={self.h}, "
            f"drift={'YES' if self.drift_detected else 'NO'})"
        )


class AccuracyDriftMonitor:
    """
    슬라이딩 윈도우 기반 정확도 모니터.

    단기(recent) 정확도가 장기(baseline) 정확도 대비 크게 떨어지면
    재학습 트리거를 발생시킨다.

    내부적으로 PageHinkley + CUSUM 두 개를 동시에 운용 →
    둘 중 하나라도 drift 감지 시 should_retrain=True.

    Args:
        window: 슬라이딩 윈도우 크기 (기본 100). 최근 N개 예측으로 단기 정확도 계산.
        min_accuracy: 재학습 트리거 최소 정확도 임계값 (기본 0.52).
                      단기 정확도가 이 이하이면 재학습 권고.
        ph_delta: PageHinkley delta (민감도).
        ph_lambda: PageHinkley lambda (임계값).
    """

    def __init__(
        self,
        window: int = 100,
        min_accuracy: float = 0.52,
        ph_delta: float = 0.005,
        ph_lambda: float = 30.0,
    ):
        self.window = window
        self.min_accuracy = min_accuracy
        self._buffer: Deque[float] = deque(maxlen=window)
        self._ph = PageHinkleyDriftDetector(delta=ph_delta, lambda_=ph_lambda)
        self._cusum = CUSUMDriftDetector(k=0.3, h=4.0)
        self._total_predictions = 0
        self._retrain_count = 0
        self.should_retrain = False

        # Optional PSI 피처 드리프트 모니터 (input drift 감지)
        self._psi_monitor: Optional[PSIDriftMonitor] = None
        self._psi_drift_detected: bool = False

    # ----- PSI 피처 드리프트 연동 -----

    def set_feature_reference(self, features: np.ndarray, **psi_kwargs) -> None:
        """
        학습 시점의 피처 분포를 PSIDriftMonitor에 저장.

        호출하면 내부 PSIDriftMonitor가 활성화되고,
        이후 check_feature_drift()로 input drift 체크 가능.
        should_retrain 판정에 PSI 결과가 포함된다.

        Args:
            features: 학습 데이터 피처 값 배열 (1-D).
            **psi_kwargs: PSIDriftMonitor 생성 파라미터
                          (n_bins, threshold_warning, threshold_drift, threshold_severe).
        """
        self._psi_monitor = PSIDriftMonitor(**psi_kwargs)
        self._psi_monitor.set_reference(features)
        self._psi_drift_detected = False
        logger.info(
            "AccuracyDriftMonitor: PSI feature reference set (n=%d)",
            np.asarray(features).size,
        )

    def check_feature_drift(self, current_features: np.ndarray) -> float:
        """
        현재 피처 분포를 reference와 비교하여 PSI 계산.

        Args:
            current_features: 현재 피처 값 배열 (1-D).

        Returns:
            PSI 값 (float). PSI 미설정 시 0.0 반환.
        """
        if self._psi_monitor is None:
            return 0.0
        psi_value = self._psi_monitor.compute_psi(current_features)
        self._psi_drift_detected = self._psi_monitor.drift_detected
        return psi_value

    @property
    def psi_drift_detected(self) -> bool:
        """PSI 기반 피처 드리프트 감지 여부. PSI 미설정 시 False."""
        return self._psi_drift_detected

    # ----- 메인 업데이트 -----

    def update(self, prediction: int, actual: int) -> bool:
        """
        예측값과 실제값을 입력하여 drift 모니터링 업데이트.

        Args:
            prediction: 모델 예측값 (정수)
            actual: 실제 레이블 (정수)

        Returns:
            bool: 재학습 권고 여부
        """
        correct = float(prediction == actual)
        self._buffer.append(correct)
        self._total_predictions += 1

        ph_drift = self._ph.update(correct)
        cusum_drift = self._cusum.update(correct)

        # 슬라이딩 윈도우 정확도 체크
        window_acc = float(np.mean(self._buffer)) if self._buffer else 1.0
        below_threshold = (
            len(self._buffer) >= self.window // 2
            and window_acc < self.min_accuracy
        )

        self.should_retrain = (
            ph_drift or cusum_drift or below_threshold
            or self._psi_drift_detected
        )

        if self.should_retrain:
            reason = []
            if ph_drift:
                reason.append(f"PageHinkley drift")
            if cusum_drift:
                reason.append(f"CUSUM drift")
            if below_threshold:
                reason.append(f"window_acc={window_acc:.3f} < {self.min_accuracy}")
            if self._psi_drift_detected:
                psi_val = (
                    self._psi_monitor.last_psi if self._psi_monitor else 0.0
                )
                reason.append(f"PSI feature drift (psi={psi_val:.4f})")
            logger.warning(
                "AccuracyDriftMonitor: RETRAIN RECOMMENDED — %s (total_preds=%d)",
                ", ".join(reason),
                self._total_predictions,
            )
            self._retrain_count += 1

        return self.should_retrain

    def reset_detectors(self) -> None:
        """재학습 완료 후 호출. PHT/CUSUM/PSI 상태 리셋, 윈도우와 reference는 유지."""
        self._ph.reset()
        self._cusum.reset()
        if self._psi_monitor is not None:
            self._psi_monitor.reset()
        self._psi_drift_detected = False
        self.should_retrain = False
        logger.info(
            "AccuracyDriftMonitor: detectors reset after retrain "
            "(total_retrains=%d)", self._retrain_count
        )

    @property
    def window_accuracy(self) -> Optional[float]:
        """최근 window 내 정확도. 샘플 부족 시 None."""
        if len(self._buffer) < self.window // 2:
            return None
        return float(np.mean(self._buffer))

    @property
    def total_predictions(self) -> int:
        return self._total_predictions

    def summary(self) -> str:
        win_acc = self.window_accuracy
        win_str = f"{win_acc:.3f}" if win_acc is not None else "N/A"
        lines = [
            f"AccuracyDriftMonitor("
            f"total={self._total_predictions}, "
            f"window_acc={win_str}/{self.min_accuracy}, "
            f"retrain_count={self._retrain_count}, "
            f"should_retrain={self.should_retrain})",
            f"  {self._ph.summary()}",
            f"  {self._cusum.summary()}",
        ]
        if self._psi_monitor is not None:
            lines.append(f"  {self._psi_monitor.summary()}")
        return "\n".join(lines)


def compute_psi(
    reference: np.ndarray,
    current: np.ndarray,
    n_bins: int = 10,
    eps: float = 1e-6,
) -> float:
    """
    Population Stability Index (PSI) 계산.

    학습 시점 분포(reference)와 현재 분포(current)의 차이를 정량화.
    PSI = Σ (actual% - expected%) * ln(actual% / expected%)

    금융 업계 표준 해석:
      - PSI < 0.1  : 분포 변화 미미 (안정)
      - 0.1 ≤ PSI < 0.2 : 약간 변화 (모니터링 필요)
      - 0.2 ≤ PSI < 0.25 : 유의미 변화 (재학습 권고)
      - PSI ≥ 0.25 : 심각한 변화 (즉시 재학습)

    Args:
        reference: 학습 시점 피처 값 배열.
        current: 현재 피처 값 배열.
        n_bins: 히스토그램 빈 수 (기본 10).
        eps: 0 비율 방지용 스무딩 (기본 1e-6).

    Returns:
        PSI 값 (float). 음수 불가.

    Raises:
        ValueError: 입력 배열이 비어있거나 n_bins < 2인 경우.
    """
    reference = np.asarray(reference, dtype=float).ravel()
    current = np.asarray(current, dtype=float).ravel()

    if reference.size == 0 or current.size == 0:
        raise ValueError("reference와 current 배열이 비어있을 수 없습니다.")
    if n_bins < 2:
        raise ValueError("n_bins는 2 이상이어야 합니다.")

    # reference 기준으로 빈 경계 결정 (동일 빈 경계 사용)
    bin_edges = np.linspace(reference.min(), reference.max(), n_bins + 1)
    # current 범위가 reference 범위를 벗어나면 양쪽 경계 확장
    bin_edges[0] = min(bin_edges[0], current.min()) - eps
    bin_edges[-1] = max(bin_edges[-1], current.max()) + eps

    ref_counts = np.histogram(reference, bins=bin_edges)[0].astype(float)
    cur_counts = np.histogram(current, bins=bin_edges)[0].astype(float)

    # 비율 변환 + eps 스무딩 (0 방지)
    ref_pct = ref_counts / ref_counts.sum() + eps
    cur_pct = cur_counts / cur_counts.sum() + eps

    # PSI 계산
    psi_value = float(np.sum((cur_pct - ref_pct) * np.log(cur_pct / ref_pct)))
    return max(psi_value, 0.0)  # 수치 오차로 인한 음수 방지


class PSIDriftMonitor:
    """
    Population Stability Index (PSI) 기반 피처 분포 드리프트 모니터.

    학습 시점의 피처 분포를 저장하고, 실시간 피처 분포와 비교하여
    PSI가 임계값을 초과하면 재학습 플래그를 설정한다.

    기존 PHT/CUSUM이 예측 정확도 기반인 반면,
    PSI는 입력 피처 분포 자체의 변화를 감지하는 보완적 역할.

    Args:
        n_bins: 히스토그램 빈 수 (기본 10).
        threshold_warning: 경고 임계값 (기본 0.1).
        threshold_drift: 드리프트(재학습) 임계값 (기본 0.2).
        threshold_severe: 심각 임계값 (기본 0.25).
    """

    # 드리프트 수준 상수
    LEVEL_STABLE = "stable"
    LEVEL_WARNING = "warning"
    LEVEL_DRIFT = "drift"
    LEVEL_SEVERE = "severe"

    def __init__(
        self,
        n_bins: int = 10,
        threshold_warning: float = 0.1,
        threshold_drift: float = 0.2,
        threshold_severe: float = 0.25,
    ):
        self.n_bins = n_bins
        self.threshold_warning = threshold_warning
        self.threshold_drift = threshold_drift
        self.threshold_severe = threshold_severe

        self._reference: Optional[np.ndarray] = None
        self._last_psi: float = 0.0
        self._last_level: str = self.LEVEL_STABLE
        self.drift_detected: bool = False
        self._check_count: int = 0

    def set_reference(self, data: np.ndarray) -> None:
        """
        학습 시점의 피처 분포를 기준(reference)으로 저장.

        Args:
            data: 학습 데이터의 피처 값 배열.

        Raises:
            ValueError: 빈 배열인 경우.
        """
        data = np.asarray(data, dtype=float).ravel()
        if data.size == 0:
            raise ValueError("reference 데이터가 비어있습니다.")
        self._reference = data.copy()
        self._last_psi = 0.0
        self._last_level = self.LEVEL_STABLE
        self.drift_detected = False
        self._check_count = 0
        logger.debug(
            "PSIDriftMonitor: reference set (n=%d, mean=%.4f, std=%.4f)",
            data.size, data.mean(), data.std(),
        )

    def compute_psi(self, current: np.ndarray) -> float:
        """
        현재 분포를 reference와 비교하여 PSI를 계산하고 드리프트 상태 업데이트.

        Args:
            current: 현재 피처 값 배열.

        Returns:
            PSI 값 (float).

        Raises:
            RuntimeError: set_reference()가 호출되지 않은 경우.
            ValueError: current가 비어있는 경우.
        """
        if self._reference is None:
            raise RuntimeError("set_reference()를 먼저 호출해야 합니다.")

        current = np.asarray(current, dtype=float).ravel()
        if current.size == 0:
            raise ValueError("current 데이터가 비어있습니다.")

        self._last_psi = compute_psi(
            self._reference, current, n_bins=self.n_bins
        )
        self._check_count += 1

        # 수준 판정
        if self._last_psi >= self.threshold_severe:
            self._last_level = self.LEVEL_SEVERE
        elif self._last_psi >= self.threshold_drift:
            self._last_level = self.LEVEL_DRIFT
        elif self._last_psi >= self.threshold_warning:
            self._last_level = self.LEVEL_WARNING
        else:
            self._last_level = self.LEVEL_STABLE

        self.drift_detected = self._last_psi >= self.threshold_drift

        if self.drift_detected:
            logger.warning(
                "PSIDriftMonitor: DRIFT DETECTED — PSI=%.4f, level=%s, "
                "threshold=%.2f, check_count=%d",
                self._last_psi, self._last_level,
                self.threshold_drift, self._check_count,
            )
        elif self._last_level == self.LEVEL_WARNING:
            logger.info(
                "PSIDriftMonitor: warning — PSI=%.4f (< drift threshold %.2f)",
                self._last_psi, self.threshold_drift,
            )

        return self._last_psi

    @property
    def last_psi(self) -> float:
        """마지막으로 계산된 PSI 값."""
        return self._last_psi

    @property
    def last_level(self) -> str:
        """마지막 드리프트 수준 (stable/warning/drift/severe)."""
        return self._last_level

    @property
    def check_count(self) -> int:
        """PSI 체크 횟수."""
        return self._check_count

    def reset(self) -> None:
        """상태 초기화. reference는 유지."""
        self._last_psi = 0.0
        self._last_level = self.LEVEL_STABLE
        self.drift_detected = False
        self._check_count = 0
        logger.debug("PSIDriftMonitor: reset (reference preserved)")

    def summary(self) -> str:
        ref_info = f"n={self._reference.size}" if self._reference is not None else "unset"
        return (
            f"PSIDriftMonitor(ref={ref_info}, last_psi={self._last_psi:.4f}, "
            f"level={self._last_level}, checks={self._check_count}, "
            f"drift={'YES' if self.drift_detected else 'NO'})"
        )


# ---------------------------------------------------------------------------
# ADWIN (ADaptive WINdowing) — 순수 numpy/math 구현
# ---------------------------------------------------------------------------

class ADWINDriftDetector:
    """
    ADWIN (ADaptive WINdowing) 드리프트 감지기 — 순수 Python 구현.

    River 라이브러리 없이 ADWIN 알고리즘을 재현한다.
    가변 크기 윈도우를 유지하며, 두 부분 윈도우의 평균 차이가
    Hoeffding/Bernstein 경계를 초과하면 오래된 데이터를 제거한다.

    금융 시계열 권장값:
      - delta=0.05: 중간 민감도 (false positive 적고 반응 적당)
      - delta=0.1: 낮은 민감도 (안정적, 느린 감지)
      - delta=0.002: 높은 민감도 (빠른 감지, false positive 多)

    Args:
        delta: 신뢰 파라미터 (0 < delta < 1). 낮을수록 민감. 기본 0.05.
        min_window: 드리프트 체크 최소 윈도우 크기. 기본 32.
        grace_period: 초기 학습 기간 (이 샘플 수 이전에는 드리프트 미감지). 기본 30.
        clock: 내부 검사 주기 (매 clock 샘플마다 경계 재계산). 기본 32.

    Attributes:
        drift_detected (bool): 최신 update() 호출 후 드리프트 감지 여부.
        n_samples (int): 총 처리된 샘플 수.
        window_size (int): 현재 유효 윈도우 크기.
        total_drifts (int): 누적 드리프트 감지 횟수.
    """

    def __init__(
        self,
        delta: float = 0.05,
        min_window: int = 32,
        grace_period: int = 30,
        clock: int = 32,
    ):
        if not (0 < delta < 1):
            raise ValueError(f"delta는 (0, 1) 범위여야 합니다. 입력값: {delta}")
        self.delta = delta
        self.min_window = min_window
        self.grace_period = grace_period
        self.clock = clock
        self.reset()

    def reset(self) -> None:
        """윈도우와 통계 완전 초기화."""
        # 윈도우 데이터: deque of float
        self._window: Deque[float] = deque()
        self._n: int = 0           # 총 샘플 수
        self._total_drifts: int = 0
        self.drift_detected: bool = False
        logger.debug("ADWIN: reset")

    def update(self, value: float) -> bool:
        """
        새 관측값을 윈도우에 추가하고 드리프트 여부를 판정.

        Args:
            value: 새 관측값 (예: 정확도 0/1, 또는 연속 피처 값).

        Returns:
            bool: 드리프트 감지 여부.
        """
        self._n += 1
        self._window.append(float(value))
        self.drift_detected = False

        # grace_period 또는 min_window 미만이면 스킵
        if self._n < self.grace_period or len(self._window) < self.min_window:
            return False

        # clock 주기마다 경계 검사 (매 샘플마다 검사하면 O(n^2) 비용)
        if self._n % self.clock != 0:
            return False

        if self._detect_change():
            self.drift_detected = True
            self._total_drifts += 1
            logger.info(
                "ADWIN DRIFT DETECTED: n=%d, window_size=%d, drift_count=%d",
                self._n, len(self._window), self._total_drifts,
            )
            return True

        return False

    def _detect_change(self) -> bool:
        """
        ADWIN 경계 검사: 윈도우를 두 부분으로 나눠 평균 차이가
        Hoeffding 경계를 초과하면 오래된 부분을 제거.

        Returns:
            bool: 드리프트 감지 및 윈도우 축소 여부.
        """
        w = list(self._window)
        n = len(w)
        if n < self.min_window:
            return False

        total_sum = sum(w)
        total_mean = total_sum / n

        # 두 부분 윈도우를 순회하며 Hoeffding 경계 계산
        # 분할점: cut_idx in [min_window//2 .. n - min_window//2]
        drift_found = False
        cut_start = max(1, self.min_window // 2)
        cut_end = n - cut_start

        right_sum = total_sum
        right_n = n

        for cut in range(cut_start, cut_end):
            # 왼쪽: w[0..cut-1], 오른쪽: w[cut..n-1]
            left_val = w[cut - 1]
            right_sum -= left_val
            right_n -= 1
            left_n = cut
            left_sum = total_sum - right_sum

            left_mean = left_sum / left_n
            right_mean = right_sum / right_n

            # Hoeffding 경계: epsilon_cut
            # ADWIN 논문: ε = sqrt( (1/2n_0 + 1/2n_1) * ln(4*n/delta) )
            # 여기서 n = 전체 윈도우, delta = 신뢰 파라미터
            harmonic = 0.5 / left_n + 0.5 / right_n
            log_term = math.log(4.0 * n / self.delta)
            epsilon_cut = math.sqrt(harmonic * log_term)

            if abs(left_mean - right_mean) >= epsilon_cut:
                # 왼쪽(오래된 데이터) 제거
                for _ in range(cut):
                    self._window.popleft()
                drift_found = True
                logger.debug(
                    "ADWIN: window shrunk by %d (left_mean=%.4f, right_mean=%.4f, "
                    "epsilon=%.4f, new_window=%d)",
                    cut, left_mean, right_mean, epsilon_cut, len(self._window),
                )
                break

        return drift_found

    @property
    def n_samples(self) -> int:
        """총 처리된 샘플 수."""
        return self._n

    @property
    def window_size(self) -> int:
        """현재 유효 윈도우 크기."""
        return len(self._window)

    @property
    def total_drifts(self) -> int:
        """누적 드리프트 감지 횟수."""
        return self._total_drifts

    @property
    def window_mean(self) -> Optional[float]:
        """현재 윈도우의 평균. 윈도우가 비어있으면 None."""
        if not self._window:
            return None
        return float(sum(self._window) / len(self._window))

    def summary(self) -> str:
        mean_str = f"{self.window_mean:.4f}" if self.window_mean is not None else "N/A"
        return (
            f"ADWIN(delta={self.delta}, n={self._n}, window={self.window_size}, "
            f"mean={mean_str}, total_drifts={self._total_drifts}, "
            f"drift={'YES' if self.drift_detected else 'NO'})"
        )


class DualGateADWINMonitor:
    """
    이중 게이트 ADWIN 드리프트 모니터.

    두 개의 독립 ADWIN 게이트를 운용한다:
      1. 피처 게이트: 여러 피처별로 개별 ADWINDriftDetector 유지.
         피처 값의 분포 변화 감지 (input drift).
      2. 모델출력 게이트: 모델 출력 확률(proba)의 분포 변화 감지
         (output drift / concept drift).

    두 게이트 중 하나라도 드리프트 감지 시 should_retrain=True.
    금융 시계열 기본값 delta=0.05 (중간 민감도).

    Args:
        delta: ADWIN 신뢰 파라미터 (기본 0.05, 금융 시계열 권장).
        feature_names: 모니터링할 피처 이름 목록. 없으면 동적 추가.
        min_window: 각 ADWIN 최소 윈도우 크기 (기본 32).
        grace_period: 초기 학습 기간 (기본 30).
        retrain_cooldown: 재학습 후 최소 대기 샘플 수 (기본 50, 과잉 재학습 방지).

    Example::

        monitor = DualGateADWINMonitor(delta=0.05)
        # 피처 값 업데이트 (각 피처별로 독립 ADWIN)
        monitor.update_feature("rsi", 0.65)
        monitor.update_feature("ema_ratio", 1.02)
        # 모델 출력 확률 업데이트
        monitor.update_model_output(proba=0.72)
        if monitor.should_retrain:
            retrain_model()
            monitor.reset()
    """

    def __init__(
        self,
        delta: float = 0.05,
        feature_names: Optional[List[str]] = None,
        min_window: int = 32,
        grace_period: int = 30,
        retrain_cooldown: int = 50,
    ):
        self.delta = delta
        self.min_window = min_window
        self.grace_period = grace_period
        self.retrain_cooldown = retrain_cooldown

        # 게이트 1: 피처별 ADWIN (feature_name → detector)
        self._feature_detectors: Dict[str, ADWINDriftDetector] = {}
        if feature_names:
            for name in feature_names:
                self._feature_detectors[name] = ADWINDriftDetector(
                    delta=delta, min_window=min_window, grace_period=grace_period
                )

        # 게이트 2: 모델 출력 ADWIN
        self._output_detector = ADWINDriftDetector(
            delta=delta, min_window=min_window, grace_period=grace_period
        )

        self.should_retrain: bool = False
        self._retrain_count: int = 0
        self._samples_since_retrain: int = 0
        self._last_drift_gate: str = ""    # "feature:<name>" or "output"
        self._last_drift_feature: str = ""

    def update_feature(self, feature_name: str, value: float) -> bool:
        """
        피처 게이트 업데이트.

        Args:
            feature_name: 피처 이름 (없으면 자동 생성).
            value: 피처 값 (float).

        Returns:
            bool: 이 피처에서 드리프트 감지 여부.
        """
        if feature_name not in self._feature_detectors:
            self._feature_detectors[feature_name] = ADWINDriftDetector(
                delta=self.delta,
                min_window=self.min_window,
                grace_period=self.grace_period,
            )

        detector = self._feature_detectors[feature_name]
        drift = detector.update(value)
        self._samples_since_retrain += 1

        if drift and self._samples_since_retrain >= self.retrain_cooldown:
            self._trigger_retrain(gate=f"feature:{feature_name}")
            return True

        return False

    def update_model_output(self, proba: float) -> bool:
        """
        모델 출력 게이트 업데이트.

        Args:
            proba: 모델의 최대 클래스 확률 (0~1).

        Returns:
            bool: 모델 출력에서 드리프트 감지 여부.
        """
        drift = self._output_detector.update(proba)
        self._samples_since_retrain += 1

        if drift and self._samples_since_retrain >= self.retrain_cooldown:
            self._trigger_retrain(gate="output")
            return True

        return False

    def update(
        self,
        feature_values: Optional[Dict[str, float]] = None,
        model_proba: Optional[float] = None,
    ) -> bool:
        """
        피처와 모델 출력을 한 번에 업데이트하는 편의 메서드.

        Args:
            feature_values: {feature_name: value} 딕셔너리.
            model_proba: 모델 최대 클래스 확률.

        Returns:
            bool: 어느 게이트든 드리프트 감지 시 True.
        """
        any_drift = False

        if feature_values:
            for name, val in feature_values.items():
                if self.update_feature(name, val):
                    any_drift = True

        if model_proba is not None:
            if self.update_model_output(model_proba):
                any_drift = True

        return any_drift

    def _trigger_retrain(self, gate: str) -> None:
        """내부: 재학습 플래그 설정 및 로깅."""
        self.should_retrain = True
        self._retrain_count += 1
        self._last_drift_gate = gate
        self._samples_since_retrain = 0
        logger.warning(
            "DualGateADWIN: RETRAIN TRIGGERED — gate=%s, retrain_count=%d",
            gate, self._retrain_count,
        )

    def reset(self) -> None:
        """
        재학습 완료 후 호출. should_retrain 플래그와 쿨다운 리셋.
        각 ADWIN 윈도우는 유지 (연속성 보존).
        """
        self.should_retrain = False
        self._samples_since_retrain = 0
        # 개별 ADWIN의 drift_detected 플래그만 클리어
        for det in self._feature_detectors.values():
            det.drift_detected = False
        self._output_detector.drift_detected = False
        logger.info(
            "DualGateADWIN: reset after retrain (total_retrains=%d)",
            self._retrain_count,
        )

    def hard_reset(self) -> None:
        """
        완전 초기화. 모든 ADWIN 윈도우 포함.
        재학습이 아닌 모델 교체 시 호출.
        """
        for det in self._feature_detectors.values():
            det.reset()
        self._output_detector.reset()
        self.should_retrain = False
        self._samples_since_retrain = 0
        self._last_drift_gate = ""
        logger.info("DualGateADWIN: hard_reset — all windows cleared")

    @property
    def retrain_count(self) -> int:
        """누적 재학습 트리거 횟수."""
        return self._retrain_count

    @property
    def feature_drift_status(self) -> Dict[str, bool]:
        """각 피처별 ADWIN 드리프트 상태 딕셔너리."""
        return {name: det.drift_detected for name, det in self._feature_detectors.items()}

    @property
    def output_drift_detected(self) -> bool:
        """모델 출력 게이트 드리프트 여부."""
        return self._output_detector.drift_detected

    def summary(self) -> str:
        feat_summaries = "\n".join(
            f"    [{name}] {det.summary()}"
            for name, det in self._feature_detectors.items()
        ) or "    (no feature detectors)"
        return (
            f"DualGateADWINMonitor(\n"
            f"  delta={self.delta}, should_retrain={self.should_retrain}, "
            f"retrain_count={self._retrain_count},\n"
            f"  last_drift_gate={self._last_drift_gate!r},\n"
            f"  [output] {self._output_detector.summary()},\n"
            f"  [features]\n{feat_summaries}\n)"
        )
