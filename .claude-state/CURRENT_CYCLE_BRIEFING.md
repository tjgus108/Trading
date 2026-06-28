# Current Cycle Briefing

_Last updated: 2026-06-28 (Cycle 363 완료)_

## 현재 상태 요약

- **완료 사이클**: 363
- **카테고리**: C(데이터) + B(리스크) + F(리서치)
- **1h PASS 연속 FAIL**: 47연속 0/19 (BTC/ETH/SOL 모두 0 PASS)
- **Bundle OOS**: 5/5 PASS 유지 (BTC 4h real CSV, Cycle363 갱신)

## Cycle 363 핵심 성과

### ✅ 완료
1. **C(데이터): dema_cross 신호 빈도 분석 + fast=7 실험 설정**
   - BTC 1h 실데이터 직접 분석: fast=8/slow=20/rsi_dir=True → 22.6 trade/60d avg
   - fast=7/slow=20/rsi_dir=True → 31.0 trade/60d (+37%) → 경계 윈도우(14→~19) 해결 기대
   - `paper_simulation.py` dema_cross: fast=8→7 (Cycle364에서 검증)
   - `walk_forward.py` DEFAULT_GRIDS["dema_cross"] fast=[7,8,10,12]로 확장

2. **B(리스크): CircuitBreaker rapid_decline 실증 검토**
   - BTC 1h 12000봉 실증: window=5, pct=5% → 156 이벤트 (1.30%, 77h당 1회) ✅ 적정
   - window=5, pct=4% → 369 (3.08%, daily → 과도), window=3, pct=5% → 31 (희귀 → 부족)
   - 결론: 현재 설정 유지. 독스트링에 실증 데이터 기록.

3. **F(리서치): frama DEFAULT_GRIDS atr_period 탐색 추가**
   - frama BTC rank3 (Sharpe=0.24, SharpeStd=1.60 안정!, PF=1.12)
   - ATR 수축 필터(atr_period=14) 최적화를 위해 atr_period=[10,14,18] 그리드 추가
   - 기존 period=[14,16,18], rsi_period=[12,14,16]과 조합 탐색 가능

### 🔍 핵심 발견
- **dema_cross**: fast=8/slow=20 시 avg 22.6/60d이나 2개 윈도우가 14<15
  - fast=7 → ~31/60d로 해결 가능하나 PF 영향 모니터링 필요
  - 현재 PF=1.45 (목표 1.5까지 +0.05)
- **frama**: SharpeStd=1.60 (최안정 전략!), PF=1.12가 병목
  - atr_period 탐색이 PF 개선 가능성을 열어줌
- **Bundle OOS 5/5 PASS 유지**: 4h 강건성 계속 확인됨

## 다음 우선순위 (Cycle 364 — D+E+F)

| 우선순위 | 카테고리 | 작업 |
|---------|---------|------|
| 1 | D(ML) | dema_cross fast=7 실험 결과 검증 (PF 유지/향상 여부) |
| 2 | E(실행) | Paper Connector fee/slippage 모델 재검토 |
| 3 | F(리서치) | frama atr_period 탐색 효과 분석 |

## 코드 변경 현황

| 파일 | 변경 | 사이클 |
|------|------|-------|
| `scripts/paper_simulation.py` | dema_cross fast=8→7 (실험) | 363 C |
| `src/backtest/walk_forward.py` | dema_cross DEFAULT_GRIDS fast 7 추가 | 363 C |
| `src/backtest/walk_forward.py` | frama DEFAULT_GRIDS atr_period=[10,14,18] 추가 | 363 F |
| `src/risk/circuit_breaker.py` | 독스트링/파라미터 주석 BTC 실증 데이터 반영 | 363 B |
| `src/risk/kelly_sizer.py` | kelly_cap > max_fraction 시 debug 로그 추가 | 362 B |
| `src/ml/trainer.py` | select_features_pfi(): X_train<100행 시 n_repeats=10 | 362 D |

## 환경 상태

- 테스트: 8434 passed, 23 skipped (Cycle 363 전체 실행 ✅)
- 데이터: BTC real (12000 1h rows), ETH/SOL synthetic (각 12000 1h rows)
- Bundle OOS 5/5: cmf(Sh=2.51), order_flow_imbalance_v2(Sh=4.35), supertrend_multi(Sh=3.89), vwap_cross(Sh=3.05), value_area(Sh=3.07)
