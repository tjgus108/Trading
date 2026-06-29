# Current Cycle Briefing

_Last updated: 2026-06-29 (Cycle 367 완료)_

## 현재 상태 요약

- **완료 사이클**: 367
- **카테고리**: B(리스크) + D(ML) + F(리서치)
- **1h PASS 연속 FAIL**: 52연속 0/19 (BTC/ETH/SOL 모두 0 PASS)
- **Bundle OOS**: 5/5 PASS 유지 (BTC 4h real CSV)

## Cycle 367 핵심 성과

### ✅ 완료

1. **B(리스크): KellySizer BTC 1h 실데이터 시나리오 테스트**
   - max_fraction=0.10이 binding constraint 확인 (kelly_cap=0.20은 dead param)
   - kelly_f=0.125 → fractional_f=0.0625 (6.25% 자본) < kelly_cap=0.20
   - DrawdownMonitor WARN(-7% DD) → mdd_multiplier=0.5 → 포지션 절반 동작 확인
   - kelly_reduce_at_mdd(-9%>8%) → kelly_fraction_multiplier=0.5 → fraction 절반 동작
   - 4개 테스트 추가 (38→42 passed)

2. **D(ML): dema_cross slow=25 실험 → 악화 확정**
   - slow=25로 paper_sim 실행: dema_cross top5 완전 탈락
   - slow=15→PF1.45 / slow=20→PF1.35 / slow=25→탈락: 간격 확장 = 과도한 필터링
   - 결론: slow=20 고정. dema_cross slow 탐색 완료
   - paper_simulation.py slow=20 복원 완료

3. **F(리서치): roc_ma_cross 신호 구조 분석**
   - rank2(with slow=25 exp), Sharpe=0.34, trades=36
   - ma=3(현재): EMA50/200 강한 필터로 36/60d 최종 신호
   - ma=5 후보: 36.8/60d (더 스무딩, PF 개선 가능성) → Cycle368 F에서 실험 예정

### 🔍 핵심 발견
- **dema_cross 방향 소진**: slow(15/20/25), fast(7/8), threshold(45/50) 전부 검증 완료
  - 현재 최적: fast=8/slow=20/thr=45 (Sharpe=0.55, PF=1.35, rank2)
  - PF 1.50 달성 경로: 다른 전략 (roc_ma_cross ma=5) 또는 근본적인 접근 변경 필요
- **52연속 FAIL**: 1h 구조적 한계 지속 — 4h Bundle OOS로 보완 (5/5 PASS)

## 다음 우선순위 (Cycle 368 — E+A+F, 368 mod 5 = 3)

| 우선순위 | 카테고리 | 작업 |
|---------|---------|------|
| 1 | F(리서치) | roc_ma_cross ma=5 실험 (PF 1.22→1.30+ 목표) |
| 2 | E(실행) | PaperConnector 슬리피지 모델 점검 (use_tiered_slippage 미검증) |
| 3 | A(품질) | 테스트 커버리지 점검 (walk_forward, paper_connector 엣지케이스) |

## 코드 변경 현황

| 파일 | 변경 | 사이클 |
|------|------|-------|
| `tests/test_kelly_integration.py` | BTC 1h 시나리오 테스트 4개 추가 | 367 B |
| `scripts/paper_simulation.py` | dema_cross slow=20 복원 + 실험 주석 | 367 D |

## 환경 상태

- 테스트: **42 passed** (test_kelly_integration.py), 전체 ~8440 예상
- 데이터: BTC real (12000 1h rows), ETH/SOL synthetic (각 12000 1h rows)
- Bundle OOS 5/5: cmf(Sh=2.51), order_flow_imbalance_v2(Sh=4.35), supertrend_multi(Sh=2.64+), vwap_cross(Sh=2.47+), value_area(Sh=PASS)
- dema_cross 현재 파라미터: fast=8, slow=20, rsi_dir_filter=True, rsi_dir_threshold=45 (확정)
