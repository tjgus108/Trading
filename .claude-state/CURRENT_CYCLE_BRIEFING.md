# Current Cycle Briefing

_Last updated: 2026-06-29 (Cycle 366 완료)_

## 현재 상태 요약

- **완료 사이클**: 366
- **카테고리**: B(리스크) + D(ML) + F(리서치)
- **1h PASS 연속 FAIL**: 50연속 0/19 (BTC/ETH/SOL 모두 0 PASS)
- **Bundle OOS**: 5/5 PASS 유지 (BTC 4h real CSV)

## Cycle 366 핵심 성과

### ✅ 완료

1. **B(리스크): DrawdownMonitor BTC 실데이터 시나리오 검증**
   - 12000봉 시나리오: 일일/주간/월간 서킷브레이커 모두 정상 작동
   - 직렬화 round-trip(to_dict/from_dict) 완벽 복원 ✅
   - ATR 급등 감지(2x → size_mult 0.5) / 정상화(1.2x → 1.0) 작동 확인 ✅
   - 2개 테스트 추가: 일중 DD 회복 → WARNING 자동 해제, 주간 DD HALT + reset_weekly() 해제

2. **D(ML): rsi_dir_threshold=45 결과 확인 — 조건부 성공**
   - Sharpe: **0.40→0.55** (+0.15 ↑↑), PF: **1.45→1.35** (-0.10 mild↓), Trades: **18→26** (+8 ↑↑)
   - Rank: **5→2** — 최근 rank2 달성 (rank1: price_cluster, rank2: dema_cross)
   - fast=7 패턴(PF 1.45→1.00 대폭 하락) 아님 → threshold=45 유지 확정
   - test_optimize_dema_cross_helper 테스트 추가

3. **F(리서치): slow=25+threshold=45 신호빈도 사전 분석**
   - fast=8/slow=25/thr=45: 276 signals (33.1/60d) vs slow=20/thr=45: 223 (26.8/60d)
   - 신호빈도 충분. PF 영향은 다음 paper_sim 실험 필요

### 🔍 핵심 발견
- **threshold=45 net positive**: Sharpe ↑ + Trades ↑ + rank ↑, PF 소폭↓(허용 가능)
- **PF 한계 지속**: 현재 PF=1.35 < 목표 1.50 — slow=25 실험이 PF 회복 유일한 미검증 방향
- **50연속 FAIL**: 1h 구조적 한계 지속 — 4h Bundle OOS로 보완 (5/5 PASS)

## 다음 우선순위 (Cycle 367 — B+D+F, 367 mod 5 = 2)

| 우선순위 | 카테고리 | 작업 |
|---------|---------|------|
| 1 | D(ML) | paper_simulation.py에서 slow=25 실험 (fast=8, slow=25, thr=45) |
| 2 | B(리스크) | KellySizer 현황 점검 (kelly_fraction, max_fraction 파라미터 실효성) |
| 3 | F(리서치) | roc_ma_cross PF=1.22 개선 가능성 탐색 |

## 코드 변경 현황

| 파일 | 변경 | 사이클 |
|------|------|-------|
| `tests/test_drawdown_monitor.py` | 일중 DD 회복 + 주간 DD HALT 테스트 2개 추가 | 366 B |
| `tests/test_phase_d.py` | test_optimize_dema_cross_helper 추가 | 366 D |
| `src/backtest/walk_forward.py` | DEFAULT_GRIDS["dema_cross"] 주석 Cycle366 결과 반영 | 366 D |

## 환경 상태

- 테스트: 8434 passed, 23 skipped ✅ (신규 테스트 포함 시 +2 예상)
- 데이터: BTC real (12000 1h rows), ETH/SOL synthetic (각 12000 1h rows)
- Bundle OOS 5/5: cmf(Sh=2.51), order_flow_imbalance_v2(Sh=4.35), supertrend_multi(Sh=3.89), vwap_cross(Sh=3.05), value_area(Sh=3.07)
- dema_cross 현재 파라미터: fast=8, slow=20, rsi_dir_filter=True, **rsi_dir_threshold=45 (확정)**
