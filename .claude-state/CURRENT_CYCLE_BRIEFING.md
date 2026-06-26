# Current Cycle Briefing

_Last updated: 2026-06-26 (Cycle 357 완료)_

## 현재 상태 요약

- **완료 사이클**: 357
- **카테고리**: B(리스크) + D(ML) + F(리서치)
- **1h PASS 연속 FAIL**: 37연속 0/19 (BTC/ETH/SOL 모두 0 PASS)
- **Bundle OOS**: 5/5 PASS 유지 (BTC 4h real CSV 사용)

## Cycle 357 핵심 성과

### ✅ 완료
1. **DrawdownMonitor to_dict/from_dict 직렬화 보완** (`src/risk/drawdown_monitor.py`)
   - 누락 필드 5개 추가: `_atr_vol_elevated`, `_atr_vol_mult`, `_sharpe_decay_mult`, `_ranging_macro_neutral`, `_current_regime`
   - 라이브 재시작 시 ATR 급등/Sharpe decay/레짐 상태 소실 버그 수정
   - `DrawdownStatus.cooldown_active` 문서화 (single loss only, not streak)

2. **dema_cross BUY RSI 필터 강화** (`src/strategy/dema_cross.py`)
   - RSI 임계값 70→65 (BUY 차단 강화)
   - 목적: BTC SharpeStd=2.61 불안정 → noise trade 제거
   - 결과: Sharpe=0.47 (0.37→0.47 소폭 개선), trades=48 (50→48 소폭 감소), 2/8 consistency 유지

3. **price_cluster vol_regime_filter=False 비활성화 실험** (`scripts/paper_simulation.py`, `src/backtest/walk_forward.py`)
   - paper_sim 파라미터: `{"vol_regime_filter": False}` (Cycle354부터 True 사용 → 비활성화)
   - WFO 그리드: `"vol_regime_filter": [False, True]` 추가
   - 결과: Sharpe=0.87 (filter=True와 동일) — 필터 활성/비활성 무관한 성능

### 🔍 핵심 발견
- **price_cluster vol_regime_filter 무효**: filter=True vs False 모두 Sharpe=0.87
  - 결론: vol_regime_filter 파라미터 자체가 BTC 1h에서 실효 없음
  - 다음 단계: 파라미터 완전 제거 검토 (bounce_pct/n_bins 중심 재평가)
- **dema_cross RSI 65**: Sharpe 0.37→0.47 개선, trades 50→48 (noise 일부 제거)
  - SharpeStd: 2.69 (이전 2.61 대비 소폭 증가, 추가 모니터링 필요)

## 다음 우선순위 (Cycle 358 — C+B+F)

| 우선순위 | 카테고리 | 작업 |
|---------|---------|------|
| 1 | C(데이터) | roc_ma_cross 파라미터 탐색 (현재 2/8 consistency, 상위권) |
| 2 | B(리스크) | DrawdownMonitor ATR/Sharpe 직렬화 round-trip 단위 테스트 추가 |
| 3 | F(리서치) | price_cluster vol_regime_filter 파라미터 완전 제거 검토 |
| 4 | 모니터링 | dema_cross RSI=65 BTC Sharpe 추이 지속 모니터링 |

## 코드 변경 현황

| 파일 | 변경 | 사이클 |
|------|------|-------|
| `src/risk/drawdown_monitor.py` | to_dict/from_dict 5개 필드 추가 | 357 B |
| `src/strategy/dema_cross.py` | BUY RSI 70→65 강화 | 357 D |
| `scripts/paper_simulation.py` | price_cluster vol_regime_filter=False | 357 F |
| `src/backtest/walk_forward.py` | price_cluster vol_regime_filter=[False, True] | 357 F |
| `scripts/paper_simulation.py` | dema_cross fast=8, slow=20 추가 | 356 D |
| `src/backtest/walk_forward.py` | dema_cross DEFAULT_GRIDS 추가 [8,10,12]×[15,20,25] | 356 D |
| `src/strategy/dema_cross.py` | 거리 필터 0.5%→0.1% | 355 F |

## 환경 상태

- 테스트: 8434 passed, 23 skipped (Cycle 357 전체 실행)
- 데이터: BTC real (12000 1h rows), ETH/SOL synthetic (각 12000 1h rows)
- Bundle OOS 5/5: cmf(Sh=2.51), order_flow_imbalance_v2(Sh=4.35), supertrend_multi(Sh=3.89), vwap_cross(Sh=3.05), value_area(Sh=3.07)
