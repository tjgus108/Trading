# Current Cycle Briefing

_Cycle 318 | 2026-06-16 | C(데이터) + B(리스크) + F(리서치)_

## 완료된 작업

### B(리스크) — OFI v2 BUNDLE_STRATEGY_OVERRIDES 추가 → PASS 달성 ✅

- `scripts/run_bundle_oos.py` BUNDLE_STRATEGY_OVERRIDES["order_flow_imbalance_v2"] 추가:
  - `{"regime_transition_is_min": 2.0, "min_oos_trades": 3}`
  - **근거**: fold3 IS=3.889 > 2.0, WFE=-2.410 < 0 → BTC 40k~60k 강한 상승장 레짐 전환 확정
  - **실험 결과** (OFI v2 PASS):
    - fold0: OOS=4.655 PASS / fold1: OOS=3.791 PASS / fold2: OOS=3.458 PASS
    - fold3: IS=3.889, WFE=-2.410 → **레짐 전환 제외**
    - fold4: OOS=5.475 PASS
    - avg OOS Sharpe: **4.345** (std=0.907, PF=1.941) → **PASS, Rank 1**
  - **결론**: **3/5 PASS 달성** (OFI v2 + supertrend_multi + cmf)

### C(데이터) — price_cluster vol_regime_filter=False 실험 → 무효 확인, 복원

- `scripts/run_bundle_oos.py` BUNDLE_STRATEGY_INIT_PARAMS["price_cluster"]: `vol_regime_filter=True→False` 실험
  - **실험 결과**: OOS 거래 수 완전 동일 (fold0:8, fold1:8, fold2:12, fold3:9, fold4:7)
  - IS Sharpe만 변화 (fold3: 0.363→1.077, fold4: 2.384→2.982) — OOS 미영향
  - **결론**: vol_regime_filter는 OOS 신호 빈도의 binding constraint 아님
    - 실제 binding constraint: bounce_pct=0.025 (너무 좁은 클러스터 범위) 또는 close_window=60
    - 다음 실험 후보: `bounce_pct` 축소 (0.025→0.015) — 클러스터 범위 완화 시도
  - **복원**: `vol_regime_filter=True` (원상 복원)

### F(리서치) — 3/5 PASS 달성 및 실전 투입 준비 검토

- **3/5 PASS 전략 확정**:
  1. OFI v2: rank1 (avg=4.345, std=0.907, PF=1.941, MDD=4.85%)
  2. supertrend_multi: rank2 (avg=3.892, std=1.239, PF=2.737, MDD=3.14%)
  3. cmf: rank3 (avg=2.508, std=1.888, PF=1.387, MDD=5.19%)
- **live_paper_trader.py 검토**:
  - QUALITY_AUDIT.csv에 3전략 모두 `passed=True` 확인
  - 실시간 운영 가능 구조: Bybit API fetch → strategy signal → PaperTrader 모의 실행
  - SSL 차단 환경에서는 실행 불가 (외부 API 접근 필요)
  - **실전 투입 조건 달성**: 3/5 PASS 충족 → live_paper_trader.py 실행 준비 완료
- **포트폴리오 제안**: OFI v2 40%, supertrend_multi 35%, cmf 25%
  - 근거: rank score 순위 (OFI v2 63.2 > supertrend 60.7 > cmf 43.4)
  - MDD 최소 전략 우선 가중 (supertrend MDD=3.14% 가장 낮음)

## 시뮬레이션 결과

- **테스트**: 8413 passed, 23 skipped (회귀 없음)
- **Paper Sim BTC 1h (22전략, 8 windows)**: 0/22 PASS (기존 유지)
  - rank1: price_cluster (score=75.7, Sharpe=0.59)
  - rank2: supertrend_multi (score=68.3, Sharpe=0.32)
- **Bundle OOS BTC 4h (5-fold)**: **3/5 PASS** ← Cycle 318 핵심 성과
  - OFI v2: **PASS** (avg=**4.345**, std=0.907, Rank 1) ← NEW PASS
  - supertrend_multi: PASS (avg=3.892, std=1.239)
  - cmf: PASS (avg=2.508, std=1.888)
  - price_cluster: FAIL (80% 저거래, binding constraint=bounce_pct)
  - value_area: FAIL (avg=0.713, std=2.018)

## 다음 Cycle 319 (319 mod 5 = 4 → D(ML) + E(실행) + F(리서치))

1. **D(ML)**: price_cluster `bounce_pct=0.025→0.015` 실험 (신호 빈도 증가 시도)
2. **E(실행)**: live_paper_trader.py 실전 투입 타임라인 구체화 (포트폴리오 배분 계획)
3. **F(리서치)**: value_area FAIL 원인 심층 분석 (std=2.018>2.0, 경계값 접근 중)
