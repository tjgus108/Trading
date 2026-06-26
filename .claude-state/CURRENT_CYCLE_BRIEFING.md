# Current Cycle Briefing

_Last updated: 2026-06-26 (Cycle 358 완료)_

## 현재 상태 요약

- **완료 사이클**: 358
- **카테고리**: C(데이터) + B(리스크) + F(리서치)
- **1h PASS 연속 FAIL**: 40연속 0/19 (BTC/ETH/SOL 모두 0 PASS)
- **Bundle OOS**: 5/5 PASS 유지 (BTC 4h real CSV 사용)

## Cycle 358 핵심 성과

### ✅ 완료
1. **dema_cross dist_pct 0.001→0.002** (`src/strategy/dema_cross.py`)
   - SharpeStd: **2.69 → 2.32** (목표 <2.5 달성 ✓)
   - Trades: **48 → 31** (noise cross 차단 효과 확인)
   - Sharpe: 0.47→0.37 (소폭 하락, 허용 수준)
   - 결론: 변경 유지

2. **price_cluster bounce_pct=0.020 실험 → 악화 확인 → 복원** (`scripts/paper_simulation.py`)
   - 0.020 결과: BTC Sharpe 0.87→0.72, PF 1.20→1.15 (악화)
   - 결론: bounce_pct=0.010(기본값) 확정, 탐색 방향 n_bins=6으로 전환
   - paper_sim 복원: `{"vol_regime_filter": False}` (bounce_pct 기본값)

3. **DrawdownStatus.cooldown_active 주석 보완** (`src/risk/drawdown_monitor.py`)
   - single loss cooldown만 반영 명확화
   - streak cooldown → `DrawdownMonitor.is_in_streak_cooldown()` 직접 호출 안내

### 🔍 핵심 발견
- **price_cluster bounce_pct**: 0.020은 0.010보다 불리. WFO 그리드 탐색은 유지 (조합 효과 가능)
  - 다음 방향: n_bins=6 탐색 (현재 5 → 더 세밀한 클러스터 분할)
- **dema_cross SharpeStd 목표 달성**: 2.69→2.32 (2.5 미만 진입)
  - ETH에서는 여전히 Sharpe=-2.07 (합성 데이터 특성, BTC만 평가)

## 다음 우선순위 (Cycle 359 — D+E+F)

| 우선순위 | 카테고리 | 작업 |
|---------|---------|------|
| 1 | F(리서치) | price_cluster n_bins=6 탐색 |
| 2 | D(ML) | dema_cross 추가 안정화 탐색 (ATR 기반 최소 변동성 필터 등) |
| 3 | E(실행) | TWAP 실행기 또는 슬리피지 모델 정확도 검토 |

## 코드 변경 현황

| 파일 | 변경 | 사이클 |
|------|------|-------|
| `src/strategy/dema_cross.py` | 거리 필터 0.001→0.002 (SharpeStd 2.69→2.32) | 358 F |
| `src/risk/drawdown_monitor.py` | cooldown_active 주석 보완 | 358 B |
| `scripts/paper_simulation.py` | price_cluster bounce_pct=0.020 실험→악화→복원 | 358 C |
| `src/backtest/walk_forward.py` | price_cluster bounce_pct=0.020 악화 기록 주석 | 358 C |
| `src/risk/drawdown_monitor.py` | to_dict()/from_dict() 5개 필드 + transition_cushion 추가 | 357 B |
| `src/strategy/dema_cross.py` | RSI 임계값 70→65 (효과없음 확인) | 357 D |
| `scripts/paper_simulation.py` | price_cluster vol_regime_filter=False | 357 F |
| `src/backtest/walk_forward.py` | price_cluster DEFAULT_GRIDS vol_regime_filter=[False,True] | 357 F |

## 환경 상태

- 테스트: 8434 passed, 23 skipped (Cycle 358 전체 실행 ✅)
- 데이터: BTC real (12000 1h rows), ETH/SOL synthetic (각 12000 1h rows)
- Bundle OOS 5/5: cmf(Sh=2.51), order_flow_imbalance_v2(Sh=4.35), supertrend_multi(Sh=3.89), vwap_cross(Sh=3.05), value_area(Sh=3.07)
