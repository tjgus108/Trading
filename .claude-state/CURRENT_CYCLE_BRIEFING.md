# Current Cycle Briefing

_Last updated: 2026-06-25 (Cycle 356 완료)_

## 현재 상태 요약

- **완료 사이클**: 356
- **카테고리**: B(리스크) + D(ML) + F(리서치)
- **1h PASS 연속 FAIL**: 36연속 0/19 (BTC/ETH/SOL 모두 0 PASS)
- **Bundle OOS**: 5/5 PASS 유지 (BTC 4h real CSV 사용)

## Cycle 356 핵심 성과

### ✅ 완료
1. **dema_cross fast=8/slow=20 적용** (`scripts/paper_simulation.py`, `src/backtest/walk_forward.py`)
   - 핵심 발견: BTC 1h trades **3 → 50** (대폭 증가!), Sharpe **-2.08 → 0.37** (36사이클 최대 개선)
   - 결론: 거리 필터가 아닌 fast/slow 주기가 cross 빈도의 핵심
   - 여전히 FAIL(Sharpe 0.37 < 1.0) but 구조적 진전

2. **price_cluster vol_atr_trend_min=1.0 실험 → 확정 실패 → 1.2 복원** (`scripts/paper_simulation.py`)
   - 1.0 결과: Sharpe -0.30, 0/8 (전 cycle 0.87, 1/8 대비 대폭 악화)
   - 결론: vol_atr_trend_min 하향 방향은 한계 (1.5, 1.2, 1.0 모두 개선 없거나 악화)
   - 다음 방향: vol_regime_filter=False 비활성화 실험

3. **DrawdownMonitor 검증** (코드 변경 없음, 로직 정상 확인)
   - MDD > 20% FULL_HALT + size_mult=0.0 ✅
   - 2단계 연속손실 스케일 정상 (BacktestEngine: threshold=5, DrawdownMonitor: threshold=3)

4. **walk_forward DEFAULT_GRIDS["dema_cross"] 추가** (`src/backtest/walk_forward.py`)
   - `{"fast": [8,10,12], "slow": [15,20,25]}` — WFO가 최적 파라미터 탐색 가능

### 🔍 핵심 발견
- **dema_cross ETH 고슬리피지**: 37.3% HIGH slippage (ETH synthetic HL ratio 2.12% 특성)
  - BTC만으로 평가 권장, ETH는 synthetic 데이터 노이즈
- **SharpeStd=2.61**: dema_cross fast=8/slow=20 불안정 (8 windows 간 큰 변동)
  - 다음 단계: noise 감소 방법 (RSI 강화 또는 dist_pct 0.001→0.002)
- **price_cluster 방향 전환**: vol_atr_trend_min 하향 실패 → vol_regime_filter 비활성화로 전략 변경

## 다음 우선순위 (Cycle 357 — B+D+F)

| 우선순위 | 카테고리 | 작업 |
|---------|---------|------|
| 1 | D(ML) | dema_cross noise 감소: RSI 강화(70→65) or dist_pct 0.001→0.002 검토 |
| 2 | F(리서치) | price_cluster vol_regime_filter=False 비활성화 실험 |
| 3 | B(리스크) | DrawdownMonitor to_dict()/from_dict() ATR 상태 직렬화 보완 |
| 4 | 모니터링 | dema_cross BTC Sharpe 추이 (2/8 consistency 유지 여부) |

## 코드 변경 현황

| 파일 | 변경 | 사이클 |
|------|------|-------|
| `scripts/paper_simulation.py` | dema_cross fast=8, slow=20 추가 | 356 D |
| `scripts/paper_simulation.py` | price_cluster vol_atr_trend_min 1.2 복원(1.0 실패) | 356 F |
| `src/backtest/walk_forward.py` | dema_cross DEFAULT_GRIDS 추가 [8,10,12]×[15,20,25] | 356 D |
| `src/backtest/walk_forward.py` | price_cluster vol_atr_trend_min에 1.0 추가 | 356 F |
| `scripts/paper_simulation.py` | price_cluster vol_atr_trend_min 1.5→1.2 | 355 A |
| `src/backtest/walk_forward.py` | price_cluster 그리드에 vol_atr_trend_min=1.2 추가 | 355 A |
| `src/strategy/dema_cross.py` | 거리 필터 0.5%→0.1% | 355 F |
| `src/backtest/walk_forward.py` | price_cluster `vol_regime_filter: [True]` 추가 | 354 D |

## 환경 상태

- 테스트: 8434 passed, 23 skipped (Cycle 356 전체 실행), 218 passed (타겟 실행)
- 데이터: BTC real (12000 1h rows), ETH/SOL synthetic (각 12000 1h rows)
- Bundle OOS 5/5: cmf(Sh=2.51), order_flow_imbalance_v2(Sh=4.35), supertrend_multi(Sh=3.89), vwap_cross(Sh=3.05), value_area(Sh=3.07)
