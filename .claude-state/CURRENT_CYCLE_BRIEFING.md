======================================================================
🔄 CYCLE 242 — 2026-05-29
======================================================================

## 이번 사이클 배정 카테고리

**Cycle 242** (242 mod 5 = 2 → B(리스크) + D(ML) + F(리서치))

---

### [B] Risk Management — 완료
- `PerformanceMonitor.check_all()`에 distribution drift 통합
  - `baseline_n: int = 30` 파라미터 추가
  - `set_baseline(strategy, returns)` 수동 baseline 설정 메서드 추가
  - `_check_drift_for(strategy)` 내부 헬퍼: 자동 baseline 추출(초기 baseline_n 거래) or 수동
  - `check_all()` 결과에 `drift` 키 포함, warn 시 on_alert 콜백 연동
- `_baseline_returns: Dict[str, List[float]]` 전략별 baseline 저장
- 테스트 8개 추가 (`tests/test_performance_tracker.py`)

### [D] ML — 완료
- `compute_ensemble_weight()`에 안정성 패널티 추가
  - `stability_threshold=0.05`: val-test gap 허용 임계값
  - `stability_scale=0.10`: gap이 threshold+scale이면 가중치 0
  - OOS Sharpe std 높은 모델 자동 하향 → 앙상블 안정성 향상
- 테스트 3개 추가 (`tests/test_trainer.py`)

### [F] Research — OOS 결과 기반 WFE 분석
- WFE < 0 주요 원인:
  1. IS Sharpe 양수 + OOS Sharpe 음수 (elder_impulse fold2: IS=0.685→OOS=-5.556)
  2. 파라미터 범위 과다 → OOS 구간별 결과 분산 극대화
- narrow_range OOS Sharpe std=6.35: fold2 outlier(-15.6) 주도
  - 권장: entry 파라미터(lookback, multiplier) 범위 30% 축소
- value_area 거래 수 2-7개: Sharpe 신뢰구간 ±3.0 이상 → trades 필터 강화 필요
- 적응형 vs 고정 파라미터: 고정이 overfitting 낮지만, regime별 조정은 WFE 개선 가능
- 다음 사이클 권장: run_bundle_oos에 trades 최소 10개 필터 추가

---

## 시뮬레이션 결과 (이전 사이클 241 데이터 참조)

### Paper Sim (Walk-Forward, 1h봉)
- **PASS: 0/22** (합성 데이터, 0/4 consistency 전략)
- Top: price_action_momentum(Sharpe 4.12, PF 1.48), momentum_quality(Sharpe 4.78, PF 1.67)

### Bundle OOS (5-bundle, 4h봉)
- **PASS: 0/5** (OOS Sharpe std 모두 > 1.5)
- narrow_range std=6.35 (최악), value_area 저거래 문제

---

## 테스트 결과
- **154 passed, 3 skipped** (관련 테스트 기준; 전체 테스트 실행 중)
- 신규 테스트: 8개(PerformanceMonitor) + 3개(stability penalty) = 11개 추가
