# Next Steps

_Last updated: 2026-06-17 (Cycle 321 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 321

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 319 | D+E+F | bounce_pct=0.015 실험(저거래 80%→60%), Bundle PASS 가중치 live_paper_trader |
| 320 | A+C+F | value_area overrides 추가(avg 0.713→2.016, std 2.018→1.825), price_cluster 교체 결정 |
| 321 | B+D+F | price_cluster→vwap_cross 교체, is_negative_regime_max 추가, **Bundle 3→4/5 PASS** |

### 🎯 Cycle 322 작업 방향 (322 mod 5 = 2 → B(리스크) + D(ML) + F(리서치))

#### B(리스크): vwap_cross fold1 해결 또는 vwap_band 교체 검토

- **Cycle 321 B 결론**: vwap_cross fold1 binding
  - fold1(2023-08-29~2023-10-27): IS=-2.29, OOS=-0.91, FAIL
  - 2023-08~10 BTC 25k→26k 횡보: VWAP20/50 bidirectional crossing → 가짜 신호
  - fold0(2023-01~03): 저거래(< 3) — BTC 회복기에 VWAP 크로스 너무 희소
- **B 작업 (둘 중 하나 선택)**:
  1. **Option A**: vwap_cross 추가 override 검토
     - fold1: IS=-2.29 < -1.4, OOS=-0.91 (|OOS|=0.91 > 0.5) → is_negative_regime_max로 제외 불가
     - `is_negative_regime_max=-2.0` + |OOS| threshold를 0.5→1.0으로 변경 가능?
       - 하지만 이는 walk_forward.py 로직 변경 (|OOS|<0.5 → <1.0) → 다른 전략에 영향
       - 위험: value_area fold 제외 조건도 완화됨
     - **더 안전**: `BUNDLE_STRATEGY_OVERRIDES["vwap_cross"]["is_negative_regime_max"] = -2.0`
       AND `BUNDLE_STRATEGY_OVERRIDES["vwap_cross"]["bear_oos_max"] = 1.0` (새 파라미터)
       - 전략별 OOS threshold를 별도 설정 가능하게 해야 함
  2. **Option B**: vwap_band 교체 실험
     - vwap_band: VWAP + std 밴드 내 mean reversion → 횡보장 적합
     - 4h 신호 빈도: mean reversion이 cross보다 더 잦을 가능성
     - 단, 추세장(fold3 OOS=4.59, fold4 OOS=1.75 in vwap_cross) 약할 수 있음
  3. **추천**: Option A 시도 → FAIL 시 Option B 전환
     - 이유: vwap_cross fold2~4는 매우 양호(OOS 2.80, 4.59, 1.75) — fold1만 해결하면 PASS

#### D(ML): value_area 2-active-fold 안정성 모니터링

- **Cycle 321 D 결론**: value_area PASS (avg=3.069, std=0.085)
  - active folds: [1, 2] only (fold0=bear_regime, fold3,4=regime_transition)
  - std=0.085 (excellent) but 2 folds는 통계적으로 취약
- **D 작업**:
  1. value_area active fold 개수 확인: 2개는 샘플 부족 위험
     - fold1(OOS=3.01): WFE=0.5 — 최소값 경계 (min_wfe=0.5)
     - OOS/IS 데이터 범위가 늘어나면 fold 구성 변경 가능
  2. value_area 1h paper sim 성능 재확인: rank21(-12.60%, Sharpe=-3.08)
     - 1h에서 value_area가 최하위 → 4h 전용 전략 특성 확인
     - PAPER_SIM_STRATEGY_PARAMS에서 value_area vol_filter_mult=0.5 유지 여부 판단
  3. fold1(2023-03~08 OOS): IS=-1.91, OOS=3.01 — 하락장 IS에서 OOS 강세 구조 유지 확인

#### F(리서치): vwap_band vs vwap_cross 비교 분석

- vwap_band 전략 파라미터 확인 (`src/strategy/vwap_band.py`)
- 4h 신호 빈도 추정: band 이탈/재진입 빈도 계산
- 번들 내 다른 전략과 상관관계 체크 (value_area가 유사 로직인지 확인)
- vwap_cross fold0 저거래 원인: 2023-01~03 BTC 회복기에 VWAP20/50 크로스 왜 없었는지

### ⚠️ 주의 사항 (Cycle 322)
- **is_negative_regime_max=-1.4 (value_area)**: 변경 금지 — Cycle 321 D 효과 확인
- **active fold 40% 초과 제외 시 FAIL**: vwap_cross에 추가 override 시 bear+regime_transition 합산 40% 초과 주의
- **vwap_cross fold0 저거래 원인**: BTC 2023-01~03 회복 → VWAP20/50 방향성 확립 전 크로스 희소
- **단독 실험 원칙**: vwap_cross override 추가 시 파라미터 하나씩
- **cmf_confirm=False**: 변경 금지 — Cycle 316 D 확정
- **close_window=60**: 변경 금지 — (price_cluster 제거로 무관하나 walk_forward 기준 유지)

### 핵심 메트릭 (Cycle 321)
- 테스트: **8413 passed, 23 skipped** (회귀 없음)
- Paper Sim BTC 1h (8 windows, 22전략): **0/22 PASS** (기존 유지)
  - rank1: supertrend_multi (score=73.5, Sharpe=0.32, trades=48)
  - rank2: price_cluster (score=69.7, Sharpe=0.34, default params)
  - vwap_cross: 1h 미등록 (OFI v2 rank11, value_area rank21)
- Bundle OOS BTC 4h (5-fold, --csv-dir data/historical): **4/5 PASS** ← +1!
  - order_flow_imbalance_v2: **PASS** (avg=4.345, std=0.907, rank1) ← 유지
  - supertrend_multi: PASS (avg=3.892, std=1.239, rank2) ← 유지
  - value_area: **PASS** (avg=3.069, std=0.085, rank3) ← **NEW!** (3→4 기여)
  - cmf: PASS (avg=2.508, std=1.888, rank4) ← 유지
  - vwap_cross: FAIL (avg=2.057, std=2.302) ← fold0 저거래, fold1 OOS=-0.91

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: real CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows)
- ETH/SOL: synthetic CSV (data/historical/synthetic/)
- Bundle OOS: `--csv-dir data/historical` 필수 (합성 데이터 run은 리포트 덮어쓰기 방지됨)
- Paper simulation 1h: 22 전략 × 8 windows → 약 8분 소요 (BTC 단독)

### BUNDLE_STRATEGY_INIT_PARAMS 현재 설정 (Cycle 321 완료 후)
- `vwap_cross: {}` ← 기본 파라미터 (Cycle 321 B: price_cluster 교체)
- `supertrend_multi: {atr_threshold=0.5, atr_threshold_max=1.5, ema_filter=True, confidence_filter=True, rsi_ob_filter=True, rsi_ob_threshold=80, trend_confirm_bars=2, cmf_confirm=False}` ← 고정
- `order_flow_imbalance_v2: {"trend_span": 20}` ← 유지

### BUNDLE_STRATEGY_OVERRIDES 현재 설정 (Cycle 321 완료 후)
- `cmf: {"min_wfe": 0.4, "sharpe_decay_max": 0.40}`
- `supertrend_multi: {"min_oos_trades": 3, "max_oos_sharpe_std": 3.0, "regime_transition_is_min": 2.0}`
- `order_flow_imbalance_v2: {"regime_transition_is_min": 2.0, "min_oos_trades": 3}`
- `vwap_cross: {"min_oos_trades": 3}` ← **NEW** Cycle 321 B
- `value_area: {"regime_transition_is_min": 2.0, "min_oos_trades": 5, "is_negative_regime_max": -1.4}` ← **UPDATED** Cycle 321 D

### PAPER_SIM_STRATEGY_PARAMS 현재 설정 (Cycle 321 변경 후)
- `value_area: {"vol_filter_mult": 0.5}`
- `wick_reversal: {"min_volatility": 0.001, "vol_mult": 0.6}`
- `relative_volume: {"rvol_buy_sell": 1.2}`
- `momentum_quality: {"quality_score_buy_threshold": 0.8, "consistency_buy_threshold": 0.3}`
- ~~`price_cluster: {...}`~~ ← **REMOVED** Cycle 321 B (번들 교체, default 파라미터로 복원)
- `order_flow_imbalance_v2: {"trend_span": 20}`
- `cmf: {"buy_thresh": 0.10}`
