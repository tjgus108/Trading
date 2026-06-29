# Current Cycle Briefing

_Last updated: 2026-06-29 (Cycle 368 완료)_

## 현재 상태 요약

- **완료 사이클**: 368
- **카테고리**: E(실행) + A(품질) + F(리서치)
- **1h PASS 연속 FAIL**: 53연속 0/19 (BTC/ETH/SOL 모두 0 PASS)
- **Bundle OOS**: 5/5 PASS 유지 (BTC 4h real CSV)

## Cycle 368 핵심 성과

### ✅ 완료

1. **E(실행): PaperConnector 티어드 슬리피지 분석**
   - BTC/ETH(large) = 0.05%, SOL(mid) = 0.2% (4배), small = 1.0%
   - BTC paper_sim: tiered=True/False 무관 (large tier = flat 기본값 동일)
   - SOL 합성 데이터만 차이 발생 (합성 데이터 신뢰도 낮으므로 실효 영향 미미)
   - 테스트 6개 추가 (TestPaperConnectorTieredSlippage)

2. **A(품질): optimize_dema_cross() 엣지케이스 테스트**
   - 빈 DataFrame: WalkForwardOptimizer.run() n<200 체크로 is_stable=False 정상 반환
   - 50행 데이터: 동일 경로로 is_stable=False 반환 확인
   - 테스트 2개 추가 (test_optimize_dema_cross_empty_df, test_optimize_dema_cross_insufficient_data)

3. **F(리서치): roc_ma_cross ma_period=5 실험 → 역효과 확정**
   - ma=3(기존): Sharpe=0.34, PF=1.22, rank2
   - ma=5(Cycle368): Sharpe=-0.91, PF=1.00, rank15 (대폭 악화)
   - 신호 지연으로 진입/청산 타이밍 악화 → ma=3 고정 확정
   - paper_sim ma=5 제거 (주석에 결과 기록)

### 🔍 핵심 발견
- **roc_ma_cross ma 조정 방향 소진**: ma=3 최적 확정 (ma=5 역효과)
  - 다음 탐색: roc_period=10 실험 (현재 기본값 12)
- **dema_cross rank2 안정 유지**: Sh=0.55, PF=1.35, Trades=26 (Cycle367 이후 변화 없음)
- **53연속 FAIL**: 1h 구조적 한계 지속 — 4h Bundle OOS로 보완 (5/5 PASS)

## 다음 우선순위 (Cycle 369 — D+E+F, 369 mod 5 = 4)

| 우선순위 | 카테고리 | 작업 |
|---------|---------|------|
| 1 | D(ML) | roc_ma_cross roc_period=10 실험 (ma=3 확정, roc_period 탐색 전환) |
| 2 | E(실행) | PaperConnector partial_fill 시나리오 테스트 추가 |
| 3 | F(리서치) | roc_period=10 paper_sim 실행 후 PF/Sharpe 변화 관찰 |

## 코드 변경 현황

| 파일 | 변경 | 사이클 |
|------|------|-------|
| `tests/test_exchange.py` | TestPaperConnectorTieredSlippage 6개 추가 | 368 E |
| `tests/test_phase_d.py` | optimize_dema_cross 엣지케이스 2개 추가 | 368 A |
| `scripts/paper_simulation.py` | roc_ma_cross ma=5 실험 → 역효과 → 주석 기록 후 복원 | 368 F |

## 환경 상태

- 테스트: **8449 passed** (전체, +9 vs Cycle367)
- 데이터: BTC real (12000 1h rows), ETH/SOL synthetic (각 12000 1h rows)
- Bundle OOS 5/5: cmf(Sh=2.51), order_flow_imbalance_v2(Sh=4.35), supertrend_multi(Sh=2.64+), vwap_cross(Sh=2.47+), value_area(PASS)
- dema_cross 파라미터: fast=8, slow=20, rsi_dir_filter=True, rsi_dir_threshold=45 (확정)
- roc_ma_cross 파라미터: roc_period=12, ma_period=3 (ma=3/5 비교 완료, ma=3 확정)
