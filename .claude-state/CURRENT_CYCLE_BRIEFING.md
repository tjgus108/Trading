# Current Cycle Briefing

_Last updated: 2026-06-26 (Cycle 357 완료)_

## 현재 상태 요약

- **완료 사이클**: 357
- **카테고리**: B(리스크) + D(ML) + F(리서치)
- **1h PASS 연속 FAIL**: 38연속 0/19 (BTC/ETH/SOL 모두 0 PASS)
- **Bundle OOS**: 5/5 PASS 유지 (BTC 4h real CSV 사용)

## Cycle 357 핵심 성과

### ✅ 완료

1. **DrawdownMonitor to_dict()/from_dict() 수정** (`src/risk/drawdown_monitor.py`) — B(리스크)
   - 누락 필드 추가: `_atr_vol_elevated`, `_atr_vol_mult`, `_sharpe_decay_mult`, `_ranging_macro_neutral`
   - 라이브 재시작 시 ATR 급등/OOS Sharpe decay/RANGING 매크로 상태 복원 안 되던 버그 수정
   - `DrawdownStatus.cooldown_active` 문서화: single loss cooldown만 반영(size=0.0), streak cooldown 별도 확인

2. **dema_cross RSI BUY 필터 70→65 강화** (`src/strategy/dema_cross.py`) — D(ML)
   - 결과: Sharpe 0.37→0.47 소폭 개선, Trades 50→48 (소폭 감소)
   - SharpeStd 2.61→2.69 (여전히 불안정), 2/8 consistency 유지
   - 주 bottleneck: PF=1.40 < 1.5 (RSI 필터로는 PF 개선 불가)

3. **price_cluster vol_regime_filter=False 실험** (`scripts/paper_simulation.py`) — F(리서치)
   - 결과: Sharpe=0.87, PF=1.20, 1/8 — **vol_regime_filter True/False 완전 동일**
   - **핵심 발견**: vol_regime_filter는 price_cluster 성능에 영향 없음. PF<1.5가 구조적 문제
   - walk_forward 그리드: `vol_regime_filter: [True]` → `[False, True]` 추가

### 🔍 핵심 발견

- **price_cluster bottleneck 확인**: vol_regime_filter 설정(True/False)에 무관하게 PF=1.20 고정
  - 다음 방향: price_cluster 자체의 손실 패턴 분석 (어느 window/방향에서 손실?)
  - bounce_pct 조정 또는 방향 분리 실험 필요
- **dema_cross PF 1.40 고정**: RSI 필터(70→65)는 Sharpe만 소폭 개선, PF 미개선
  - 다음 방향: dist_pct 0.001→0.002 (신호 품질 강화) 실험 또는 max_hold 단축 실험

## 다음 우선순위 (Cycle 358 — C+B+F, 358 mod 5 = 3)

| 우선순위 | 카테고리 | 작업 |
|---------|---------|------|
| 1 | C(데이터) | price_cluster 손실 패턴 분석: PF 1.20 → 1.5 개선 방안 탐색 |
| 2 | B(리스크) | DriftMonitor 직렬화 상태 확인 (DrawdownMonitor 패턴 반복 가능성) |
| 3 | F(리서치) | dema_cross dist_pct 0.001→0.002 실험 (PF 개선 목표) |
| 4 | 모니터링 | dema_cross BTC Sharpe std 감소 여부 확인 |

## 코드 변경 현황

| 파일 | 변경 | 사이클 |
|------|------|-------|
| `src/risk/drawdown_monitor.py` | to_dict/from_dict 4개 누락 필드 추가 | 357 B |
| `src/risk/drawdown_monitor.py` | DrawdownStatus.cooldown_active 문서화 | 357 B |
| `src/strategy/dema_cross.py` | RSI BUY 필터 70→65 강화 | 357 D |
| `scripts/paper_simulation.py` | price_cluster vol_regime_filter=False | 357 F |
| `src/backtest/walk_forward.py` | price_cluster vol_regime_filter [False, True] | 357 F |
| `scripts/paper_simulation.py` | dema_cross fast=8, slow=20 추가 | 356 D |
| `src/backtest/walk_forward.py` | dema_cross DEFAULT_GRIDS 추가 [8,10,12]×[15,20,25] | 356 D |
| `src/strategy/dema_cross.py` | 거리 필터 0.5%→0.1% | 355 F |

## 환경 상태

- 테스트: 8434 passed, 23 skipped (전체), 224 passed (타겟)
- 데이터: BTC real (12000 1h rows), ETH/SOL synthetic (각 12000 1h rows)
- Bundle OOS 5/5: cmf(Sh=2.51), order_flow_imbalance_v2(Sh=4.35), supertrend_multi(Sh=3.89), vwap_cross(Sh=3.05), value_area(Sh=3.07)
- Paper Sim 38연속 0/19: BTC 1위 dema_cross(Sh=0.47), 2위 price_cluster(Sh=0.87)
