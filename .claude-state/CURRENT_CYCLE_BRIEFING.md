# Current Cycle Briefing

_Last updated: 2026-06-25 (Cycle 355 완료)_

## 현재 상태 요약

- **완료 사이클**: 355
- **카테고리**: A(품질) + C(데이터) + F(리서치)
- **1h PASS 연속 FAIL**: 35연속 0/19 (BTC/ETH/SOL 모두 0 PASS)
- **Bundle OOS**: 5/5 PASS 유지 (BTC 4h real CSV 사용)

## Cycle 355 핵심 성과

### ✅ 완료
1. **price_cluster vol_atr_trend_min 강화** (`scripts/paper_simulation.py`)
   - vol_atr_trend_min=1.5 → 1.5에서 Sharpe=0.87, PF=1.20 변화 없음 확인
   - 1.5 임계값(ATR이 MA대비 50% 이상) → 너무 관대 → 1.2로 강화 (20% 이상)
   - 목표: WR 37.2%→42.5%, PF 1.20→1.5+

2. **walk_forward 그리드 확장** (`src/backtest/walk_forward.py`)
   - vol_atr_trend_min 그리드: [1.5, 2.0, 2.5] → [1.2, 1.5, 2.0, 2.5]
   - WFO가 더 공격적인 sideways 필터 탐색 가능

3. **dema_cross 거리 필터 완화** (`src/strategy/dema_cross.py`)
   - 0.5%(0.005) → 0.1%(0.001)로 완화
   - BTC 1h: 3 trades avg → cross 이벤트 자체 희귀 → 0.5% 필터가 실제 cross도 차단
   - 목표: 3 trades → 10+ trades (15 기준 접근)

### 🔍 핵심 발견 (C(데이터) 분석)
- **roc_ma_cross 2/8 PASS 원인 확인**: W1(Sh=4.45), W2(Sh=3.49) → Jan~May 2023 강한 상승추세 구간
  - W3~W8: Sh 범위 -3.55~0.40 → 2023 중반 이후 choppy market에서 FAIL
  - 결론: roc_ma_cross는 강추세 시장에서만 PASS 가능한 전략
  - 추가 필터 추가 불필요 (Cycle 339 전례: 필터 추가 → trades 57→18 → FAIL)
  
- **price_cluster PF=1.20 원인**:
  - WR=37.2%, W/L비=2.03 → PF=1.20
  - PF=1.5 달성에 WR 42.5% 또는 W/L비 2.53 필요
  - vol_regime_filter 강화(1.2)로 trending 구간 bad trade 제거 → WR 개선 기대

- **vol_atr_trend_min=1.5 비효과 확인**: 두 번의 시뮬레이션(05:12, 10:11)에서 동일 결과
  - Sharpe=0.87, PF=1.20 → 변화 없음 (1.5 임계값이 너무 관대)

## 다음 우선순위 (Cycle 356 — B+D+F)

| 우선순위 | 카테고리 | 작업 |
|---------|---------|------|
| 1 | D(ML) | dema_cross 0.1% 필터 효과 평가 (paper_sim 재실행 필수) |
| 2 | A(품질)→확인 | price_cluster vol_atr_trend_min=1.2 효과 평가 |
| 3 | B(리스크) | DrawdownMonitor 손실 스케일링 현황 점검 |
| 4 | F(리서치) | 두 실험 결과 분석 및 다음 방향 설정 |

## 코드 변경 현황

| 파일 | 변경 | 사이클 |
|------|------|-------|
| `scripts/paper_simulation.py` | price_cluster vol_atr_trend_min 1.5→1.2 | 355 A |
| `src/backtest/walk_forward.py` | price_cluster 그리드에 vol_atr_trend_min=1.2 추가 | 355 A |
| `src/strategy/dema_cross.py` | 거리 필터 0.5%→0.1% | 355 F |
| `src/backtest/walk_forward.py` | price_cluster 그리드에 `vol_regime_filter: [True]` 추가 | 354 D |
| `src/strategy/dema_cross.py` | convergence_signal=False 파라미터 추가 | 354 E |
| `scripts/paper_simulation.py` | STRATEGIES_TIMEFRAME_EXCLUDE["1h"]에 wick_reversal 추가 | 353 C |
| `scripts/paper_simulation.py` | supertrend_multi atr_threshold=0.5 추가 | 352 B |
| `src/risk/drawdown_monitor.py` | set_atr_state() atr_pct 절댓값 임계값 확장 | 352 D |

## 환경 상태

- 테스트: 8434 passed, 23 skipped (Cycle 355 전체 실행), 108 passed (타겟 실행)
- 데이터: BTC real (12000 1h rows), ETH/SOL synthetic (각 12000 1h rows)
- Bundle OOS 5/5: cmf(Sh=2.51), order_flow_imbalance_v2(Sh=4.35), supertrend_multi(Sh=3.89), vwap_cross(Sh=3.05), value_area(Sh=3.07)
