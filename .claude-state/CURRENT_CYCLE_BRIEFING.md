# Current Cycle Briefing

_Last updated: 2026-06-27 (Cycle 360 완료)_

## 현재 상태 요약

- **완료 사이클**: 360
- **카테고리**: A(품질) + C(데이터) + F(리서치)
- **1h PASS 연속 FAIL**: 43연속 0/19 (BTC/ETH/SOL 모두 0 PASS)
- **Bundle OOS**: 5/5 PASS 유지 (BTC 4h real CSV 사용)

## Cycle 360 핵심 성과

### ✅ 완료
1. **dema_cross rsi_dir_filter=True paper_sim 검증** (A(품질))
   - 결과: PF 1.26→1.45 (+0.19 개선, 목표 1.5까지 +0.05)
   - Sharpe 0.37→0.40 (+0.03), SharpeStd 2.32→2.25 (안정화)
   - Trades 31→18 (avg>15 OK; 단 2윈도우 14<15 경계 주의)
   - 판단: 개선 방향 확인 → rsi_dir_filter=True 유지 확정

2. **price_cluster close_window=40 실험 → 악화 확인 → 복원** (C(데이터))
   - 결과: Sharpe 0.72→0.07 (대폭 악화), PF 1.20→1.07
   - Cycle303 실험과 동일 결론 재확인 (close_window=40 역효과)
   - close_window 탐색 방향 완료 (기본값 50이 최적)

3. **Bundle OOS 재검증** (F(리서치))
   - 5/5 PASS 유지 (BTC 4h real CSV)
   - cmf/ofi_v2/supertrend_multi/vwap_cross/value_area 모두 안정

### 🔍 핵심 발견
- **dema_cross rsi_dir_filter=True**: PF 1.45 (1.5 목표까지 +0.05만 남음) — 가장 가까운 PASS 후보
- **price_cluster close_window**: 40 단축 → 클러스터 안정성 저하. 50이 최적 (탐색 완료)
- **roc_ma_cross rank1** (Cycle 360 paper_sim): Sharpe=0.34, 2/8 consistency → 다음 탐색 후보

## 다음 우선순위 (Cycle 361 — B+D+F)

| 우선순위 | 카테고리 | 작업 |
|---------|---------|------|
| 1 | B(리스크) | CircuitBreaker/VaR/Kelly Sizer 현황 점검 |
| 2 | D(ML) | dema_cross WFO 직접 실행 또는 앙상블 RF 피처 분석 |
| 3 | F(리서치) | roc_ma_cross 파라미터 최적화 탐색 (2/8 consistency → PASS 후보) |

## 코드 변경 현황

| 파일 | 변경 | 사이클 |
|------|------|-------|
| `scripts/paper_simulation.py` | dema_cross rsi_dir_filter=True 추가 확정 (PF 1.26→1.45) | 360 A |
| `scripts/paper_simulation.py` | close_window=40 실험 → 악화 확인 → default(50) 복원 | 360 C |
| `src/backtest/walk_forward.py` | close_window=40 Cycle360 재확인 악화 주석 추가 | 360 C |
| `src/strategy/dema_cross.py` | `atr_vol_min_pct=0.0` 파라미터 추가 (BTC dead param 확인) | 359 D |
| `src/strategy/dema_cross.py` | `rsi_dir_filter=False` 파라미터 추가 | 359 D |
| `src/backtest/walk_forward.py` | dema_cross DEFAULT_GRIDS에 rsi_dir_filter=[False,True] 추가 | 359 D |
| `src/exchange/paper_connector.py` | use_tiered_slippage=False 파라미터 노출 | 359 E |
| `scripts/paper_simulation.py` | n_bins=6 실험 → 악화 확인 → n_bins=5 복원 | 359 F |
| `src/strategy/dema_cross.py` | 거리 필터 0.001→0.002 (SharpeStd 2.69→2.32) | 358 F |
| `src/risk/drawdown_monitor.py` | cooldown_active 주석 보완 | 358 B |

## 환경 상태

- 테스트: 8434 passed, 23 skipped (Cycle 360 전체 실행 ✅)
- 데이터: BTC real (12000 1h rows), ETH/SOL synthetic (각 12000 1h rows)
- Bundle OOS 5/5: cmf(Sh=2.51), order_flow_imbalance_v2(Sh=4.35), supertrend_multi(Sh=3.89), vwap_cross(Sh=3.05), value_area(Sh=3.07)
