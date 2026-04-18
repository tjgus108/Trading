"""
drift_detector.py 단위 테스트.

PageHinkleyDriftDetector, CUSUMDriftDetector, AccuracyDriftMonitor 검증:
- 정상 데이터(안정적 정확도)에서는 drift 감지 안 됨
- 급변 데이터(정확도 급락)에서는 drift 감지 됨
- reset 후 상태가 깨끗하게 초기화됨
"""

import pytest
import numpy as np

from src.ml.drift_detector import (
    PageHinkleyDriftDetector,
    CUSUMDriftDetector,
    AccuracyDriftMonitor,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _feed(detector, values):
    """값 목록을 순서대로 detector에 주입하고 마지막 결과 반환."""
    result = False
    for v in values:
        result = detector.update(v)
    return result


def _stable_correct(n: int = 80, accuracy: float = 0.75, seed: int = 42) -> list:
    """안정적인 정확도의 바이너리 시퀀스 생성."""
    rng = np.random.default_rng(seed)
    return [float(rng.random() < accuracy) for _ in range(n)]


def _degraded_stream(n_good: int = 50, n_bad: int = 60, seed: int = 0) -> list:
    """초반 고정확도 → 후반 저정확도로 급변하는 스트림."""
    rng = np.random.default_rng(seed)
    good = [float(rng.random() < 0.80) for _ in range(n_good)]
    bad = [float(rng.random() < 0.20) for _ in range(n_bad)]
    return good + bad


# ---------------------------------------------------------------------------
# PageHinkleyDriftDetector
# ---------------------------------------------------------------------------

class TestPageHinkleyDriftDetector:
    def test_initial_state(self):
        det = PageHinkleyDriftDetector()
        assert det.n_samples == 0
        assert not det.drift_detected
        assert det.running_accuracy == 0.0

    def test_no_drift_stable_stream(self):
        """안정적 정확도에서는 min_samples 이후에도 drift 없어야 함."""
        det = PageHinkleyDriftDetector(delta=0.005, lambda_=50.0, min_samples=30)
        values = _stable_correct(n=100, accuracy=0.70)
        _feed(det, values)
        assert not det.drift_detected

    def test_drift_detected_on_sudden_change(self):
        """PHT는 베이스라인 대비 급격한 상승 변화를 감지한다.

        PHT 통계 ph_stat = sum - min_sum 은 누적 합산이
        최솟값보다 크게 올라갈 때 임계값을 초과한다.
        초반 모두 0.0(오답) → min_sum 낮게 형성.
        이후 연속 1.0(정답) → correct > mean + delta → sum 급등 → drift 감지.
        """
        det = PageHinkleyDriftDetector(delta=0.005, lambda_=5.0, min_samples=30)
        # 초반 30개 모두 오답 (베이스라인 0, min_sum 낮게 고정)
        for _ in range(30):
            det.update(0.0)
        # 이후 모두 정답 → ph_stat 급등
        detected_any = False
        for _ in range(30):
            if det.update(1.0):
                detected_any = True
                break
        assert detected_any, "초반 저정확 → 후반 전부 정답 스트림에서 PHT drift 미감지"

    def test_reset_clears_state(self):
        """reset 후 모든 내부 상태가 초기화되어야 함."""
        det = PageHinkleyDriftDetector(min_samples=5, lambda_=1.0)
        _feed(det, [0.0] * 10)
        det.reset()
        assert det.n_samples == 0
        assert not det.drift_detected
        assert det.running_accuracy == 0.0

    def test_update_returns_bool(self):
        det = PageHinkleyDriftDetector()
        result = det.update(1.0)
        assert isinstance(result, bool)

    def test_running_accuracy_converges(self):
        """누적 평균 정확도가 실제 입력 비율로 수렴해야 함."""
        det = PageHinkleyDriftDetector(min_samples=1)
        for _ in range(1000):
            det.update(1.0)
        assert abs(det.running_accuracy - 1.0) < 0.01

        det.reset()
        for _ in range(1000):
            det.update(0.0)
        assert abs(det.running_accuracy - 0.0) < 0.01

    def test_n_samples_increments(self):
        det = PageHinkleyDriftDetector()
        for i in range(1, 6):
            det.update(1.0)
            assert det.n_samples == i

    def test_summary_string(self):
        det = PageHinkleyDriftDetector()
        _feed(det, [1.0, 0.0, 1.0])
        s = det.summary()
        assert "PageHinkley" in s
        assert "drift=" in s

    def test_no_drift_below_min_samples(self):
        """min_samples 미만에서는 drift 감지 안 됨."""
        det = PageHinkleyDriftDetector(min_samples=30, lambda_=1.0)
        # min_samples - 1 개만 입력
        for _ in range(29):
            assert not det.update(0.0)


# ---------------------------------------------------------------------------
# CUSUMDriftDetector
# ---------------------------------------------------------------------------

class TestCUSUMDriftDetector:
    def test_initial_state(self):
        det = CUSUMDriftDetector()
        assert det.n_samples == 0
        assert not det.drift_detected

    def test_no_drift_stable_stream(self):
        det = CUSUMDriftDetector(k=0.5, h=5.0, min_samples=30)
        values = _stable_correct(n=100, accuracy=0.65)
        _feed(det, values)
        assert not det.drift_detected

    def test_drift_detected_on_degradation(self):
        """급락 스트림에서 CUSUM drift 감지."""
        det = CUSUMDriftDetector(k=0.3, h=3.0, min_samples=30)
        stream = _degraded_stream(n_good=40, n_bad=80)
        detected_any = False
        for v in stream:
            if det.update(v):
                detected_any = True
                break
        assert detected_any, "CUSUM: 급락 스트림에서 drift 미감지"

    def test_reset_clears_state(self):
        det = CUSUMDriftDetector(min_samples=5, h=1.0)
        _feed(det, [0.0] * 10)
        det.reset()
        assert det.n_samples == 0
        assert not det.drift_detected

    def test_update_returns_bool(self):
        det = CUSUMDriftDetector()
        result = det.update(1.0)
        assert isinstance(result, bool)

    def test_no_drift_below_min_samples(self):
        det = CUSUMDriftDetector(min_samples=30, h=0.01)
        for _ in range(29):
            assert not det.update(0.0)

    def test_summary_string(self):
        det = CUSUMDriftDetector()
        _feed(det, [1.0, 0.0])
        s = det.summary()
        assert "CUSUM" in s
        assert "drift=" in s

    def test_n_samples_increments(self):
        det = CUSUMDriftDetector()
        for i in range(1, 4):
            det.update(0.5)
            assert det.n_samples == i


# ---------------------------------------------------------------------------
# AccuracyDriftMonitor
# ---------------------------------------------------------------------------

class TestAccuracyDriftMonitor:
    def test_initial_state(self):
        mon = AccuracyDriftMonitor()
        assert not mon.should_retrain
        assert mon.total_predictions == 0
        assert mon.window_accuracy is None

    def test_no_retrain_good_accuracy(self):
        """높은 정확도 유지 시 재학습 불필요."""
        mon = AccuracyDriftMonitor(window=50, min_accuracy=0.52, ph_lambda=100.0)
        # 정확도 0.80 → should_retrain=False 유지
        for _ in range(80):
            mon.update(prediction=1, actual=1)
        assert not mon.should_retrain

    def test_retrain_triggered_on_degradation(self):
        """급격한 정확도 저하 시 재학습 트리거."""
        mon = AccuracyDriftMonitor(window=50, min_accuracy=0.52, ph_lambda=20.0)
        # 초반 정확 예측
        for _ in range(40):
            mon.update(prediction=1, actual=1)
        # 후반 전부 틀림
        triggered = False
        for _ in range(60):
            if mon.update(prediction=1, actual=0):
                triggered = True
                break
        assert triggered, "정확도 저하 시 재학습 트리거 미발생"

    def test_window_accuracy_none_when_insufficient(self):
        """window//2 미만 샘플에서는 window_accuracy가 None."""
        mon = AccuracyDriftMonitor(window=100)
        for _ in range(49):
            mon.update(prediction=1, actual=1)
        assert mon.window_accuracy is None

    def test_window_accuracy_computed_after_threshold(self):
        """window//2 이상 샘플에서는 float 반환."""
        mon = AccuracyDriftMonitor(window=100, ph_lambda=1000.0)
        for _ in range(50):
            mon.update(prediction=1, actual=1)
        assert isinstance(mon.window_accuracy, float)
        assert 0.0 <= mon.window_accuracy <= 1.0

    def test_total_predictions_increments(self):
        mon = AccuracyDriftMonitor()
        for i in range(1, 6):
            mon.update(prediction=1, actual=1)
            assert mon.total_predictions == i

    def test_reset_detectors_clears_drift_flags(self):
        """reset_detectors 후 should_retrain=False."""
        mon = AccuracyDriftMonitor(window=50, min_accuracy=0.90, ph_lambda=5.0)
        # 전부 틀려서 트리거 유발
        for _ in range(60):
            mon.update(prediction=1, actual=0)
        # should_retrain이 True인 상태에서 리셋
        mon.should_retrain = True  # 강제 설정도 지워야 함
        mon.reset_detectors()
        assert not mon.should_retrain

    def test_below_min_accuracy_triggers_retrain(self):
        """window_acc < min_accuracy 조건으로도 트리거 가능."""
        mon = AccuracyDriftMonitor(window=20, min_accuracy=0.80, ph_lambda=999.0)
        # ph/cusum이 감지 못하도록 lambda 크게, 하지만 window 정확도 낮게
        # 전부 틀린 예측 50개
        triggered = False
        for _ in range(50):
            if mon.update(prediction=1, actual=0):
                triggered = True
                break
        assert triggered, "window_acc 기반 트리거 미발생"

    def test_summary_string(self):
        mon = AccuracyDriftMonitor()
        mon.update(prediction=1, actual=1)
        s = mon.summary()
        assert "AccuracyDriftMonitor" in s
        assert "PageHinkley" in s
        assert "CUSUM" in s

    def test_update_returns_bool(self):
        mon = AccuracyDriftMonitor()
        result = mon.update(prediction=1, actual=0)
        assert isinstance(result, bool)

    def test_correct_classification(self):
        """prediction == actual → correct=1.0, else 0.0."""
        mon = AccuracyDriftMonitor(window=10, ph_lambda=1000.0)
        # 10번 모두 정답
        for _ in range(10):
            mon.update(prediction=0, actual=0)
        # window가 채워졌으면 정확도 1.0에 가까워야 함
        acc = mon.window_accuracy
        if acc is not None:
            assert acc > 0.8
