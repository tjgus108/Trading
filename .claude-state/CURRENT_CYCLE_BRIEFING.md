# Current Cycle Briefing

_Last updated: 2026-06-25 (Cycle 357 완료)_

## 현재 상태 요약

- **완료 사이클**: 357
- **카테고리**: B(리스크) + D(ML) + F(리서치)
- **1h PASS 연속 FAIL**: 37연속 0/19 (BTC/ETH/SOL 모두 0 PASS)
- **Bundle OOS**: 5/5 PASS 유지 (BTC 4h real CSV 사용)

## Cycle 357 핵심 성과

### ✅ 완료
1. **DrawdownMonitor to_dict()/from_dict() ATR/Sharpe 직렬화 수정** (`src/risk/drawdown_monitor.py`)
   - 라이브 재시작 후 ATR 급등 상태(`_atr_vol_elevated`, `_atr_vol_mult`)와 Sharpe decay(`_sharpe_decay_mult`) 복원 가능
   - `DrawdownStatus.cooldown_active` 주석: single loss cooldown 전용(streak cooldown과 명확 구분)
   - **효과**: 봇 재시작 후 포지션 사이징이 마지막 상태를 올바르게 이어받음

2. **dema_cross dist_pct 0.001→0.002 실험 → 확정 실패 → 복원** (`src/strategy/dema_cross.py`)
   - 결과: trades 50→32, Sharpe 0.37→0.24 (악화!)
   - 결론: 0.002는 유효한 cross까지 차단 → dist_pct=0.001 확정
   - dema_cross fast=8/slow=20 + dist_pct=0.001 현재 최적 조합 유지

3. **price_cluster vol_regime_filter=False 실험 → 확정 실패 → 복원** (`scripts/paper_simulation.py`)
   - BTC: Sharpe=0.87 (filter=False 시 변화 없음)
   - ETH: Sharpe=-0.44 (filter=True, 1.2 대비 악화!)
   - 결론: vol_regime_filter=False 방향 영구 포기. vol_regime_filter=True, vol_atr_trend_min=1.2 확정
   - walk_forward 그리드에 [False, True] 추가는 유지 (WFO가 자동으로 비교 가능)

### 🔍 핵심 발견
- **price_cluster 튜닝 가능 방향 소진**: vol_atr_trend_min(1.0/1.2/1.5), vol_regime_filter(True/False) 모두 실험 완료
  - BTC Sharpe=0.87 (PASS 기준 1.0 미달)이 현 전략의 상한에 가까울 가능성
  - 다음 사이클: bounce_pct, n_bins 파라미터 직접 최적화로 방향 전환
- **dema_cross BTC 여전히 FAIL**: Sharpe=0.24, trades=32, 2/8 consistency (dist_pct 0.002 실험 영향)
  - dist_pct 복원 후 다음 사이클에서 Sharpe 0.37 복귀 예상
  - RSI>65 차단 실험 예정 (현재 70)

## 다음 우선순위 (Cycle 358 — C+B+F)

| 우선순위 | 카테고리 | 작업 |
|---------|---------|------|
| 1 | C(데이터) | DataFeed 캐시 점검, synthetic ETH/SOL 슬리피지 문제 분석 |
| 2 | B(리스크) | DrawdownMonitor kelly_reduce_at_mdd 적용 검토, streak 회복 로직 점검 |
| 3 | F(리서치) | dema_cross RSI>65 차단 실험, price_cluster bounce_pct 최적화 |

## 코드 변경 현황 (최신 → 과거)

| 파일 | 변경 | 사이클 |
|------|------|-------|
| `src/risk/drawdown_monitor.py` | to_dict/from_dict ATR/Sharpe 직렬화 추가 | 357 B |
| `src/risk/drawdown_monitor.py` | DrawdownStatus.cooldown_active 주석 명확화 | 357 B |
| `src/backtest/walk_forward.py` | price_cluster vol_regime_filter=[False,True] 추가 | 357 F |
| `scripts/paper_simulation.py` | price_cluster filter=False 실험→복원 (filter=True, 1.2 확정) | 357 F |
| `src/strategy/dema_cross.py` | dist_pct 0.002 실험→복원 (0.001 확정) | 357 D |
| `scripts/paper_simulation.py` | dema_cross fast=8, slow=20 추가 | 356 D |
| `scripts/paper_simulation.py` | price_cluster vol_atr_trend_min 1.2 복원(1.0 실패) | 356 F |
| `src/backtest/walk_forward.py` | dema_cross DEFAULT_GRIDS 추가 [8,10,12]×[15,20,25] | 356 D |
| `src/backtest/walk_forward.py` | price_cluster vol_atr_trend_min에 1.0 추가 | 356 F |

## 환경 상태

- 테스트: 8434 passed, 23 skipped (Cycle 357 전체 실행), 0 failures
- 데이터: BTC real (12000 1h rows), ETH/SOL synthetic (각 12000 1h rows)
- Bundle OOS 5/5: cmf(Sh=2.51), order_flow_imbalance_v2(Sh=4.35), supertrend_multi(Sh=3.89), vwap_cross(Sh=3.05), value_area(Sh=3.07)
