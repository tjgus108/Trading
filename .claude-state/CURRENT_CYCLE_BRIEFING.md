# Current Cycle Briefing

_Last updated: 2026-06-29 (Cycle 369 완료)_

## 현재 상태 요약

- **완료 사이클**: 369
- **카테고리**: D(ML) + E(실행) + F(리서치)
- **1h PASS 연속 FAIL**: 54연속 0/19 (BTC/ETH/SOL 모두 0 PASS)
- **Bundle OOS**: 5/5 PASS 유지 (BTC 4h real CSV 기준, Cycle367)

## Cycle 369 핵심 성과

### ✅ 완료

1. **D(ML): dema_cross rsi_dir_threshold=40 실험 → rank1 달성**
   - 결과: Sharpe 0.55→**0.80** (+0.25↑), PF 1.35→1.38 (+0.03↑), Trades 26→30 (+4↑)
   - Rank: 2/19 → **1/19** (rank1 달성) 🏆
   - 결론: RSI 임계값 완화(45→40) = 신호 빈도↑ + 품질 유지 → thr=40 확정
   - DEFAULT_GRIDS["dema_cross"] rsi_dir_threshold [45,50]→[40,45] 업데이트

2. **E(실행): WalkForwardOptimizer.run() 타이밍 로깅 추가**
   - `import time as _time` 추가 및 `_win_t0`, `_is_t0`, `_is_elapsed`, `_win_elapsed` 측정
   - logger.info에 `IS_opt=%.2fs total=%.2fs (%d combos)` 출력 추가
   - 목적: 각 윈도우별 IS 최적화 시간 vs OOS 검증 시간 분리 측정 → 병목 파악
   - dema_cross 36 combos × 8 windows = 288 backtests 시간 측정 가능

3. **F(리서치): roc_ma_cross roc_period=10 실험 → 역효과 확정**
   - 결과: Sharpe=-1.45, PF=0.88, Trades=39, rank16+ (roc_period=12: Sh=0.34, rank2 대비 대폭 악화)
   - ma=5(Sh=-0.91) 보다도 더 나쁜 결과 → roc 단축은 noise 증가로 역효과
   - roc_ma_cross 기본값(roc_period=12) 확정, 다음 탐색: roc_period=15

### 🔍 핵심 발견

- **dema_cross thr=40 대성공**: 임계값 완화가 단순히 신호만 늘린 게 아니라 품질도 유지
  - PF 1.38도 이전 thr=45 PF=1.35 대비 소폭 개선 → signal selection quality 향상
  - dema_cross 현재 파라미터: fast=8, slow=20, rsi_dir_filter=True, rsi_dir_threshold=40
  - 다음 탐색: dist_pct=0.003 (현재 0.002, 더 강한 거리 필터 → PF 1.50 목표)
- **roc_ma_cross roc_period=10 역효과**: 단기 ROC는 BTC 1h에서 노이즈 과다
  - roc_period=12가 현 데이터에 최적. 남은 탐색: roc_period=15 (더 느린 ROC)
- **54연속 FAIL**: 1h PASS 기준(Sh≥1.0, PF≥1.5)은 여전히 높은 장벽
  - dema_cross Sh=0.80은 1.0에 근접. PF=1.38은 1.50에 근접.
  - 한 번의 개선으로 PASS 가능성 있음 (다음 사이클 dist_pct=0.003 탐색)

## 다음 우선순위 (Cycle 370 — A+C+F, 370 mod 5 = 0)

| 우선순위 | 카테고리 | 작업 |
|---------|---------|------|
| 1 | A(품질) | optimize_dema_cross() WFO 실행으로 thr=40 WFO 검증 |
| 2 | C(데이터) | dema_cross dist_pct=0.003 실험 (PF 1.38→1.50 목표) |
| 3 | F(리서치) | roc_ma_cross roc_period=15 실험 (더 느린 ROC → 신호 품질↑) |

## 코드 변경 현황

| 파일 | 변경 | 사이클 |
|------|------|-------|
| `scripts/paper_simulation.py` | dema_cross thr=40 확정 + roc_ma_cross roc_period=10 실험→복원 | 369 D+F |
| `src/backtest/walk_forward.py` | `import time as _time` + run()에 타이밍 로깅 추가 | 369 E |
| `src/backtest/walk_forward.py` | DEFAULT_GRIDS["dema_cross"] rsi_dir_threshold [45,50]→[40,45] | 369 D |

## 환경 상태

- 테스트: 전체 **8449** passed, 23 skipped
- 데이터: BTC real (12000 1h rows), ETH/SOL synthetic (각 12000 1h rows)
- Bundle OOS 5/5 (Cycle367 실데이터 기준): cmf(Sh=2.51), order_flow_imbalance_v2(Sh=4.35), supertrend_multi(Sh=3.89), vwap_cross(Sh=3.05), value_area(Sh=3.07)
- dema_cross 현재 파라미터: fast=8, slow=20, rsi_dir_filter=True, **rsi_dir_threshold=40** (Cycle369 확정, rank1)
- roc_ma_cross 현재: roc_period=12(기본값, 확정), ma_period=3 — roc_period 방향 탐색 중
