"""
Concept Drift Detector — ML 예측 정확도 모니터링 및 드리프트 감지.

river 라이브러리 없이 순수 numpy로 구현.

알고리즘:
  - Page-Hinkley (PHT): 점진적 drift 감지에 최적화.
    평균 대비 누적 편차가 임계값 초과 시 드리프트 신호.
  - CUSUM: 이분점(changepoint) 감지. PHT의 대칭 버전.

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
"""

import logging
from collections import deque
from typing import Deque, List, Optional

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

        self.should_retrain = ph_drift or cusum_drift or below_threshold

        if self.should_retrain:
            reason = []
            if ph_drift:
                reason.append(f"PageHinkley drift")
            if cusum_drift:
                reason.append(f"CUSUM drift")
            if below_threshold:
                reason.append(f"window_acc={window_acc:.3f} < {self.min_accuracy}")
            logger.warning(
                "AccuracyDriftMonitor: RETRAIN RECOMMENDED — %s (total_preds=%d)",
                ", ".join(reason),
                self._total_predictions,
            )
            self._retrain_count += 1

        return self.should_retrain

    def reset_detectors(self) -> None:
        """재학습 완료 후 호출. PHT/CUSUM 상태 리셋, 윈도우는 유지."""
        self._ph.reset()
        self._cusum.reset()
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
        return (
            f"AccuracyDriftMonitor("
            f"total={self._total_predictions}, "
            f"window_acc={win_str}/{self.min_accuracy}, "
            f"retrain_count={self._retrain_count}, "
            f"should_retrain={self.should_retrain})\n"
            f"  {self._ph.summary()}\n"
            f"  {self._cusum.summary()}"
        )
