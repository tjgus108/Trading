# Current Cycle Briefing

_Last updated: 2026-06-26 (Cycle 357 완료)_

## 현재 상태 요약

- **완료 사이클**: 357
- **카테고리**: B(리스크) + D(ML) + F(리서치)
- **1h PASS 연속 FAIL**: 37연속 0/19 (BTC/ETH/SOL 모두 0 PASS)
- **Bundle OOS**: 5/5 PASS 유지 (BTC 4h real CSV 사용)

## Cycle 357 핵심 성과

### ✅ 완료
1. **DrawdownMonitor to_dict/from_dict 7필드 직렬화 보완** (`src/risk/drawdown_monitor.py`)
   - 누락된 런타임 상태: `_atr_vol_elevated`, `_atr_vol_mult`, `_sharpe_decay_mult`
   - 누락된 레짐 상태: `_ranging_macro_neutral`, `_current_regime`
   - 누락된 파라미터: `transition_cushion_enabled`, `transition_cushion_threshold`
   - 효과: 라이브 봇 재시작 시 ATR 급등/Sharpe decay/레짐 쿨다운 상태 손실 없이 복원

2. **dema_cross RSI 필터 70 → 65 강화** (`src/strategy/dema_cross.py`)
   - 목적: BTC SharpeStd=2.61(Cycle356) — 과매수 구간 noise trade 차단
   - 결과: BTC Sharpe **0.37 → 0.47**, Return +2.94%→+3.46%, Trades 50→48
   - SharpeStd: 2.61→2.69 (불안정 지속 — 구조적 문제, RSI 단독으론 한계)

3. **price_cluster vol_regime_filter=False 비활성화 실험** (paper_sim + walk_forward.py)
   - 핵심 발견: BTC Sharpe **-0.30 → 0.87** (대폭 개선! filter=False 효과 확인)
   - Consistency: 0/8 → 1/8 (소폭 개선, 일관성 부족)
   - 결론: 필터 비활성화가 신호 복원에 효과적 → 다음 사이클 일관성 향상 방법 탐색

### 🔍 핵심 발견
- **price_cluster filter=False 효과**: Sharpe 0.87로 복원. vol_regime_filter가 유용한 신호를 과도 차단했음 확인
  - 1/8 consistency: 특정 레짐(RANGING+neutral macro?)에서만 작동 — 레짐별 성과 분석 필요
- **dema_cross RSI 65 개선 한계**: Sharpe 개선(0.37→0.47)이지만 SharpeStd 악화(2.61→2.69)
  - dist_pct 상향(0.001→0.002) 또는 trend 필터(EMA slope) 추가 방향 탐색

## 다음 우선순위 (Cycle 358 — C+B+F)

| 우선순위 | 카테고리 | 작업 |
|---------|---------|------|
| 1 | C(데이터) | price_cluster filter=False 8개 윈도우 레짐별 분석 → 1/8 consistency 원인 파악 |
| 2 | B(리스크) | DrawdownStatus.cooldown_active 문서화 + streak_cooldown_active 필드 추가 검토 |
| 3 | F(리서치) | dema_cross SharpeStd 불안정 원인 분석 + dist_pct 상향 또는 trend 필터 실험 |

## 코드 변경 현황

| 파일 | 변경 | 사이클 |
|------|------|-------|
| `src/risk/drawdown_monitor.py` | to_dict/from_dict 7필드 직렬화 보완 | 357 B |
| `src/strategy/dema_cross.py` | BUY RSI 필터 70→65 | 357 D |
| `scripts/paper_simulation.py` | price_cluster vol_regime_filter=False | 357 F |
| `src/backtest/walk_forward.py` | price_cluster vol_regime_filter=[False, True] | 357 F |
| `scripts/paper_simulation.py` | dema_cross fast=8, slow=20 추가 | 356 D |
| `src/backtest/walk_forward.py` | dema_cross DEFAULT_GRIDS 추가 [8,10,12]×[15,20,25] | 356 D |

## 환경 상태

- 테스트: **8434 passed, 23 skipped** (Cycle 357 전체 실행) ✅
- 데이터: BTC real (12000 1h rows), ETH/SOL synthetic (각 12000 1h rows)
- Bundle OOS 5/5: cmf(Sh=2.51), order_flow_imbalance_v2(Sh=4.35), supertrend_multi(Sh=3.89), vwap_cross(Sh=3.05), value_area(Sh=3.07)
