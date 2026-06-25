# Current Cycle Briefing

_Last updated: 2026-06-25 (Cycle 354 완료)_

## 현재 상태 요약

- **완료 사이클**: 354
- **카테고리**: D(ML) + E(실행) + F(리서치)
- **1h PASS 연속 FAIL**: 34연속 0/19 (BTC/ETH/SOL 모두 0 PASS)
- **Bundle OOS**: 5/5 PASS 유지 (BTC 4h real CSV 사용)

## Cycle 354 핵심 성과

### ✅ 완료
1. **walk_forward.py price_cluster 그리드 버그 수정** (`src/backtest/walk_forward.py`)
   - 기존 `vol_atr_trend_min: [1.5, 2.0, 2.5]`은 `vol_regime_filter=False` 기본값으로 인해 항상 dead parameter
   - `"vol_regime_filter": [True]` 추가 → sideways 필터 활성화 상태에서 최적 임계값 탐색 가능
   - 실질적인 WFO 최적화 개선 (불필요한 그리드 탐색 제거)

2. **price_cluster sideways 필터 실험 준비** (`scripts/paper_simulation.py`)
   - `PAPER_SIM_STRATEGY_PARAMS["price_cluster"] = {"vol_regime_filter": True, "vol_atr_trend_min": 1.5}` 추가
   - 목적: BTC 1h Sharpe 0.87→1.0, PF 1.20→1.5 개선 (다음 paper_sim에서 평가)

3. **dema_cross convergence_signal 파라미터 추가 + BTC 검증 실패 확인**
   - `src/strategy/dema_cross.py`에 `convergence_signal=False`, `convergence_threshold=0.02` 추가
   - BTC 1h 전체 데이터 즉시 검증:
     - Baseline: 23 trades, Sharpe=-0.035 (break even)
     - 0.5% threshold: 640 trades, Sharpe=-0.755, ret=-35.93%
     - 2.0% threshold: 867 trades, Sharpe=-2.372, ret=-76.15%
   - 결론: BTC real data에서 convergence 접근 완전 실패 → paper_sim 적용 보류
   - 파라미터 코드 보존 (기본값 False, ETH real data 검증 시 재활성화 가능)

### 🔍 핵심 발견
- **price_cluster vol_regime_filter 버그 수정**: WFO 그리드에서 vol_atr_trend_min이 실제로 동작하지 않았음
  - 다음 사이클 A(품질)에서 효과 평가 예정
- **dema_cross convergence 접근 실패**: 수렴 신호가 whipsaw를 대규모로 생성 → 치명적 손실
  - BTC 크로스 방식 자체가 1h에서 취약 (23 trades baseline도 Sharpe=-0.035)
  - 다음 방향: 거리 필터 완화(0.5%→0.1%) 또는 전략 교체 검토
- **F(리서치) 결론**: price_cluster BTC 전용 전략 확정
  - BTC: 가격 메모리 있음 (Hurst H>0.5) → 클러스터 = 실제 지지/저항
  - ETH/SOL synthetic: GARCH 과정 → 클러스터 = 통계 아티팩트 (가격 메모리 없음)

## 다음 우선순위 (Cycle 355 — A+C+F)

| 우선순위 | 카테고리 | 작업 |
|---------|---------|------|
| 1 | A(품질) | price_cluster vol_regime_filter 실험 결과 평가 (paper_sim 재실행) |
| 2 | C(데이터) | BTC 1h price_cluster PF=1.20 원인 분석 / roc_ma_cross PASS 윈도우 분석 |
| 3 | F(리서치) | dema_cross 대안 탐색: 거리 필터 완화 or 전략 교체 |

## 코드 변경 현황

| 파일 | 변경 | 사이클 |
|------|------|-------|
| `src/backtest/walk_forward.py` | price_cluster 그리드에 `vol_regime_filter: [True]` 추가 | 354 D |
| `src/strategy/dema_cross.py` | `convergence_signal=False`, `convergence_threshold` 파라미터 추가 | 354 E |
| `scripts/paper_simulation.py` | `PAPER_SIM_STRATEGY_PARAMS["price_cluster"]` 추가 (sideways filter) | 354 D |
| `scripts/paper_simulation.py` | `STRATEGIES_TIMEFRAME_EXCLUDE["1h"]`에 `"wick_reversal"` 추가 | 353 C |
| `scripts/paper_simulation.py` | `"supertrend_multi": {"atr_threshold": 0.5}` 추가 | 352 B |
| `src/risk/drawdown_monitor.py` | `set_atr_state()` atr_pct 절댓값 임계값 확장 | 352 D |

## 환경 상태

- 테스트: 8434 passed, 23 skipped (Cycle 354 실행 확인)
- 데이터: BTC real (12000 1h rows), ETH/SOL synthetic (각 12000 1h rows)
- Bundle OOS 5/5: cmf, order_flow_imbalance_v2, supertrend_multi, vwap_cross, value_area
