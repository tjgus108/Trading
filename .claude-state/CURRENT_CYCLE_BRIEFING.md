# Current Cycle Briefing

_Last updated: 2026-06-28 (Cycle 362 완료)_

## 현재 상태 요약

- **완료 사이클**: 362
- **카테고리**: B(리스크) + D(ML) + F(리서치)
- **1h PASS 연속 FAIL**: 46연속 0/19 (BTC/ETH/SOL 모두 0 PASS)
- **Bundle OOS**: 5/5 PASS 유지 (BTC 4h real CSV, Cycle361 기준)

## Cycle 362 핵심 성과

### ✅ 완료
1. **B(리스크): KellySizer kelly_cap vs max_fraction 분석**
   - kelly_cap=0.20 > max_fraction=0.10 → max_fraction이 최종 binding constraint
   - kelly_cap은 regime scale 이전에 적용되지만 max_fraction으로 최종 클리핑
   - `__init__`에 debug 로그 추가: dead param 상황 명시
   - CircuitBreaker rapid_decline_window=5 (5h 내 5% 하락): 권장범위(3~10) 내 적절

2. **D(ML): select_features_pfi() 소표본 PFI 신뢰도 개선**
   - X_train.shape[0] < 100이면 n_repeats=5→10으로 자동 증가
   - 경고 로그 추가 (소표본 상황 가시화)
   - 배경: Cycle361에서 n_test_samples=50 소표본 PFI(macd_hist=-0.060) 신뢰도 불확실

3. **F(리서치): price_cluster vol_atr_trend_min 분석**
   - vol_regime_filter=False(확정) → vol_atr_trend_min은 dead param 확인
   - WFO에서 vol_regime_filter=True인 경우에만 vol_atr_trend_min이 의미 있음
   - price_cluster 개선보다 frama/dema_cross 문제가 더 urgent

### 🔍 핵심 발견
- **dema_cross trades<15** (2 윈도우에서 14건): PF=1.45(목표 1.5까지 +0.05) 좋으나 trades 문제
- **frama**: BTC rank3(Sharpe=0.24, PF=1.12) + ETH rank2(Sharpe=0.51): 다심볼 일관성 ★
  - SharpeStd 낮음(BTC 1.60): 안정적! 탐색 가치 높음
- **price_cluster**: rank1 유지 (Sharpe=0.87, SharpeStd=1.10, 1/8)

## 다음 우선순위 (Cycle 363 — C+B+F)

| 우선순위 | 카테고리 | 작업 |
|---------|---------|------|
| 1 | C(데이터) | dema_cross trades<15 문제 분석 및 신호 빈도 개선 방안 탐색 |
| 2 | F(리서치) | frama 전략 심층 탐색 (파라미터 파악, DEFAULT_GRIDS 추가 검토) |
| 3 | B(리스크) | CircuitBreaker rapid_decline_window=5 실 데이터 이벤트 빈도 검증 |

## 코드 변경 현황

| 파일 | 변경 | 사이클 |
|------|------|-------|
| `src/risk/kelly_sizer.py` | kelly_cap > max_fraction 시 debug 로그 추가 (dead param 명시) | 362 B |
| `src/ml/trainer.py` | select_features_pfi(): X_train<100행 시 n_repeats=10 자동 증가 | 362 D |
| `src/strategy/roc_ma_cross.py` | EMA200 조건 정리(ema50 체크 제거), rsi_val dead code 제거 | 361 F |
| `src/backtest/walk_forward.py` | roc_ma_cross 주석 업데이트 (rank1 상태) | 361 F |
| `scripts/paper_simulation.py` | dema_cross rsi_dir_filter=True 추가 확정 (PF 1.26→1.45) | 360 A |

## 환경 상태

- 테스트: 8434 passed, 23 skipped (Cycle 362 전체 실행 ✅)
- 데이터: BTC real (12000 1h rows), ETH/SOL synthetic (각 12000 1h rows)
- Bundle OOS 5/5: cmf(Sh=2.51), order_flow_imbalance_v2(Sh=4.35), supertrend_multi(Sh=3.89), vwap_cross(Sh=3.05), value_area(Sh=3.07)
