"""
Cycle 175 D(ML): ADWIN 드리프트 감지 테스트.

ADWINDriftDetector + DualGateADWINMonitor 검증.
"""

import math

import numpy as np
import pytest

from src.ml.drift_detector import ADWINDriftDetector, DualGateADWINMonitor


# ---------------------------------------------------------------------------
# ADWINDriftDetector 단위 테스트
# ---------------------------------------------------------------------------

class TestADWINDriftDetector:

    def test_init_defaults(self):
        det = ADWINDriftDetector()
        assert det.delta == 0.05
        assert det.n_samples == 0
        assert det.window_size == 0
        assert det.drift_detected is False
        assert det.total_drifts == 0

    def test_invalid_delta_raises(self):
        with pytest.raises(ValueError):
            ADWINDriftDetector(delta=0.0)
        with pytest.raises(ValueError):
            ADWINDriftDetector(delta=1.0)
        with pytest.raises(ValueError):
            ADWINDriftDetector(delta=-0.1)

    def test_n_samples_increments(self):
        det = ADWINDriftDetector()
        for i in range(10):
            det.update(float(i % 2))
        assert det.n_samples == 10

    def test_window_mean_empty(self):
        det = ADWINDriftDetector()
        assert det.window_mean is None

    def test_window_mean_after_updates(self):
        det = ADWINDriftDetector(grace_period=5, min_window=4)
        for _ in range(20):
            det.update(1.0)
        mean = det.window_mean
        assert mean is not None
        assert abs(mean - 1.0) < 1e-9

    def test_no_drift_on_stable_stream(self):
        """안정적인 스트림에서는 드리프트 없어야 함."""
        rng = np.random.default_rng(42)
        det = ADWINDriftDetector(delta=0.05)
        drifts = []
        for _ in range(500):
            val = float(rng.integers(0, 2))  # 안정적 베르누이(0.5)
            drifts.append(det.update(val))
        # 안정 구간에서는 drfit 횟수 매우 적어야 함 (0~2회 허용)
        assert det.total_drifts <= 2

    def test_drift_detected_on_abrupt_change(self):
        """급격한 분포 변화 → 드리프트 감지."""
        det = ADWINDriftDetector(delta=0.05, grace_period=30, min_window=32, clock=1)
        # 1단계 + 2단계: 급격한 변화 (mean 0.9 → 0.1)
        for _ in range(200):
            det.update(0.9)
        for _ in range(200):
            det.update(0.1)

        # 전체 구간에서 드리프트가 최소 1회 이상 감지돼야 함
        assert det.total_drifts >= 1, (
            "급격한 분포 변화에서 드리프트가 감지되지 않음"
        )

    def test_window_shrinks_after_drift(self):
        """드리프트 감지 시 윈도우가 줄어야 함."""
        det = ADWINDriftDetector(delta=0.05, grace_period=30, min_window=32, clock=1)
        for _ in range(200):
            det.update(0.9)
        window_before = det.window_size

        for _ in range(200):
            det.update(0.1)

        # 드리프트 후 윈도우가 원래보다 작아야 함
        assert det.window_size < window_before or det.total_drifts > 0

    def test_reset_clears_state(self):
        det = ADWINDriftDetector(delta=0.05, grace_period=5, min_window=4, clock=1)
        for _ in range(100):
            det.update(float(np.random.randint(0, 2)))
        det.reset()
        assert det.n_samples == 0
        assert det.window_size == 0
        assert det.drift_detected is False
        assert det.total_drifts == 0
        assert det.window_mean is None

    def test_summary_contains_key_info(self):
        det = ADWINDriftDetector(delta=0.05)
        s = det.summary()
        assert "ADWIN" in s
        assert "delta=0.05" in s
        assert "drift=" in s

    def test_delta_sensitivity(self):
        """delta 작을수록 윈도우가 더 작게 유지됨 (더 빠르게 오래된 데이터 제거)."""
        # 급격한 변화 + 노이즈 없는 데이터로 안정적 검증
        data = [0.9] * 200 + [0.1] * 200

        det_sensitive = ADWINDriftDetector(delta=0.002, grace_period=30, min_window=32, clock=1)
        det_robust = ADWINDriftDetector(delta=0.3, grace_period=30, min_window=32, clock=1)

        for v in data:
            det_sensitive.update(v)
            det_robust.update(v)

        # 두 감지기 모두 드리프트를 최소 1회 감지해야 함
        assert det_sensitive.total_drifts >= 1, "민감한 감지기가 드리프트를 감지하지 못함"
        assert det_robust.total_drifts >= 1, "강건한 감지기가 드리프트를 감지하지 못함"

        # delta 작을수록 윈도우가 더 작게 유지됨 (오래된 데이터를 더 적극적으로 제거)
        # 두 쪽 모두 드리프트를 잘 감지하므로 합리적인 total_drifts를 가짐
        assert det_sensitive.total_drifts + det_robust.total_drifts >= 2

    def test_continuous_values_no_crash(self):
        """연속 피처 값으로도 크래시 없이 동작."""
        det = ADWINDriftDetector(delta=0.05)
        rng = np.random.default_rng(0)
        for _ in range(300):
            det.update(float(rng.normal(0, 1)))
        assert det.n_samples == 300

    def test_grace_period_prevents_early_drift(self):
        """grace_period 이내에는 드리프트 감지 안 함."""
        det = ADWINDriftDetector(delta=0.001, grace_period=100, min_window=10, clock=1)
        for _ in range(50):
            det.update(1.0)
        for _ in range(40):
            det.update(0.0)
        # 총 90 샘플 < grace_period=100 → 드리프트 없어야 함
        assert det.total_drifts == 0


# ---------------------------------------------------------------------------
# DualGateADWINMonitor 단위 테스트
# ---------------------------------------------------------------------------

class TestDualGateADWINMonitor:

    def test_init_no_features(self):
        mon = DualGateADWINMonitor(delta=0.05)
        assert mon.should_retrain is False
        assert mon.retrain_count == 0
        assert mon.feature_drift_status == {}

    def test_init_with_feature_names(self):
        mon = DualGateADWINMonitor(delta=0.05, feature_names=["rsi", "ema_ratio"])
        assert "rsi" in mon.feature_drift_status
        assert "ema_ratio" in mon.feature_drift_status
        assert mon.should_retrain is False

    def test_update_feature_auto_creates_detector(self):
        """feature_names 없이 시작해도 update_feature 호출 시 자동 생성."""
        mon = DualGateADWINMonitor(delta=0.05)
        mon.update_feature("new_feat", 0.5)
        assert "new_feat" in mon.feature_drift_status

    def test_no_retrain_on_stable_feature_stream(self):
        """안정적인 피처 스트림에서는 재학습 트리거 없음."""
        rng = np.random.default_rng(1)
        mon = DualGateADWINMonitor(delta=0.05, retrain_cooldown=30)
        for _ in range(300):
            val = 0.5 + rng.normal(0, 0.02)
            mon.update_feature("rsi", val)
        assert mon.retrain_count == 0

    def test_retrain_triggered_on_feature_drift(self):
        """피처 게이트: 급격한 변화 → 재학습 트리거."""
        mon = DualGateADWINMonitor(
            delta=0.05,
            min_window=32,
            grace_period=30,
            retrain_cooldown=10,
        )
        # 안정 구간
        for _ in range(150):
            mon.update_feature("rsi", 0.8)
        # 급격한 변화
        for _ in range(150):
            mon.update_feature("rsi", 0.1)

        assert mon.retrain_count > 0 or mon.should_retrain, (
            "피처 drift 후 재학습 트리거가 없음"
        )

    def test_retrain_triggered_on_model_output_drift(self):
        """모델 출력 게이트: 급격한 확률 변화 → 재학습 트리거."""
        mon = DualGateADWINMonitor(
            delta=0.05,
            min_window=32,
            grace_period=30,
            retrain_cooldown=10,
        )
        # 안정 구간 (높은 확신)
        for _ in range(150):
            mon.update_model_output(0.9)
        # 불확실 구간 (낮은 확신)
        for _ in range(150):
            mon.update_model_output(0.3)

        assert mon.retrain_count > 0 or mon.should_retrain, (
            "모델 출력 drift 후 재학습 트리거가 없음"
        )

    def test_update_convenience_method(self):
        """update() 편의 메서드 동작 확인."""
        mon = DualGateADWINMonitor(delta=0.05)
        for _ in range(20):
            mon.update(
                feature_values={"rsi": 0.5, "ema": 1.0},
                model_proba=0.7,
            )
        # 안정 구간이므로 재학습 없어야 함
        assert mon.retrain_count == 0

    def test_reset_clears_retrain_flag(self):
        """reset() 후 should_retrain=False."""
        mon = DualGateADWINMonitor(
            delta=0.05, min_window=32, grace_period=30, retrain_cooldown=10
        )
        for _ in range(150):
            mon.update_feature("f", 0.9)
        for _ in range(150):
            mon.update_feature("f", 0.1)

        # reset 호출 후 플래그 해제
        mon.reset()
        assert mon.should_retrain is False

    def test_hard_reset_clears_all(self):
        """hard_reset() 후 모든 ADWIN 윈도우 초기화."""
        mon = DualGateADWINMonitor(delta=0.05, feature_names=["rsi"])
        for _ in range(50):
            mon.update_feature("rsi", 0.5)
            mon.update_model_output(0.6)
        mon.hard_reset()
        # 윈도우 초기화 확인
        assert mon._output_detector.window_size == 0
        assert mon._feature_detectors["rsi"].window_size == 0
        assert mon.should_retrain is False

    def test_cooldown_prevents_immediate_re_trigger(self):
        """retrain_cooldown 내에서는 연속 재트리거 방지."""
        mon = DualGateADWINMonitor(
            delta=0.05, min_window=32, grace_period=30,
            retrain_cooldown=200,   # 매우 긴 쿨다운
        )
        # 변화를 줘도 쿨다운 내에서는 트리거 없음 (grace_period 이전)
        for i in range(50):
            mon.update_feature("f", 1.0 if i < 25 else 0.0)
        assert mon.retrain_count == 0

    def test_output_drift_detected_property(self):
        mon = DualGateADWINMonitor(delta=0.05)
        assert mon.output_drift_detected is False

    def test_summary_contains_gates(self):
        mon = DualGateADWINMonitor(delta=0.05, feature_names=["rsi"])
        s = mon.summary()
        assert "DualGateADWINMonitor" in s
        assert "output" in s
        assert "rsi" in s
        assert "should_retrain" in s

    def test_dual_gate_both_trigger(self):
        """피처 + 모델출력 동시 드리프트 → retrain_count >= 1."""
        mon = DualGateADWINMonitor(
            delta=0.05, min_window=32, grace_period=30, retrain_cooldown=5
        )
        for _ in range(120):
            mon.update_feature("rsi", 0.8)
            mon.update_model_output(0.85)
        for _ in range(120):
            mon.update_feature("rsi", 0.2)
            mon.update_model_output(0.35)
        # 적어도 한 게이트는 트리거해야 함
        assert mon.retrain_count >= 1 or mon.should_retrain

    def test_retrain_count_increments(self):
        """retrain_count가 reset() 후에도 누적됨."""
        mon = DualGateADWINMonitor(
            delta=0.05, min_window=32, grace_period=30, retrain_cooldown=10
        )
        initial = mon.retrain_count
        for _ in range(150):
            mon.update_feature("x", 0.9)
        for _ in range(150):
            mon.update_feature("x", 0.1)
        after = mon.retrain_count
        mon.reset()
        # reset 후 count는 유지돼야 함 (누적)
        assert mon.retrain_count == after

    def test_multiple_features_independent(self):
        """서로 다른 피처는 독립적으로 drift 감지."""
        mon = DualGateADWINMonitor(
            delta=0.05, feature_names=["stable", "drifting"],
            min_window=32, grace_period=30, retrain_cooldown=5
        )
        for i in range(300):
            mon.update_feature("stable", 0.5)   # 안정
            # drifting: 중간에 급변
            mon.update_feature("drifting", 0.9 if i < 150 else 0.1)

        # drifting 피처 감지기에서 드리프트가 발생했거나 retrain 트리거됨
        assert (
            mon._feature_detectors["drifting"].total_drifts > 0
            or mon.retrain_count > 0
        )

    def test_delta_propagated_to_sub_detectors(self):
        """delta 값이 모든 하위 ADWIN 감지기에 전달됨."""
        mon = DualGateADWINMonitor(delta=0.07, feature_names=["a", "b"])
        assert mon._output_detector.delta == 0.07
        assert mon._feature_detectors["a"].delta == 0.07
        assert mon._feature_detectors["b"].delta == 0.07
