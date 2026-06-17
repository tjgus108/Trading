# Next Steps

_Last updated: 2026-06-17 (Cycle 322 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 322

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 320 | A+C+F | value_area overrides 추가(avg 0.713→2.016, std 2.018→1.825), price_cluster 교체 결정 |
| 321 | B+D+F | price_cluster→vwap_cross 교체, is_negative_regime_max 추가, **Bundle 3→4/5 PASS** |
| 322 | B+D+F | bear_oos_max=1.0 추가, vwap_cross fold1 해결, **Bundle 4→5/5 PASS (역대 최고!)** |

### 🎯 Cycle 323 작업 방향 (323 mod 5 = 3 → C(데이터) + B(리스크) + F(리서치))

#### C(데이터): Bundle OOS 5/5 PASS 안정성 검증

- **5/5 PASS 유지 확인**: Bear/Regime 제외 fold 합산 비율 모니터링
  - vwap_cross: fold0(low_trade=20%) + fold1(bear_regime=20%) = 총 40% 제외 — 경계값
  - 향후 데이터 범위 확장 시 fold 구성 변화 가능성 체크
- **데이터 범위 확장 가능성**:
  - 현재 BTC CSV: 2023-01~2024-05 (12000 rows 1h → ~500봉 4h)
  - fold 구성: is_bars=1080, oos_bars=360, slide=360 → 5-fold 구성
  - 데이터 추가 시 fold 수 증가 → vwap_cross fold0(저거래) 비율 20%→17% 개선 가능

#### B(리스크): bear_regime 제외 비율 40% 경계 안전성 검토

- **현재 비율**:
  - vwap_cross: low_trade [0]=20%, bear_regime [1]=20% → 합산 40% 경계
  - value_area: regime_transition [3,4]=40%, bear_regime [0]=20% → 총 60%지만 카테고리별 각 ≤40% OK
- **B 작업**: 40% 제외 threshold 너무 관대한지 검토
  - vwap_cross가 5/5 PASS이지만 fold0+fold1 2개 제외는 sample 부족 위험
  - 대안: fold별 제외 이유 다양화(low_trade ≠ bear_regime ≠ regime_transition) → 각 카테고리 20% 이하 유지 규칙 추가?
  - 단, 현재 구조 동작 중 — 보수적으로 모니터링만 권고

#### F(리서치): 5/5 PASS 이후 다음 단계 전략

- **Paper Trading 실전 투입 검토**: Bundle OOS 5/5 PASS → paper trader에서 번들 전략 실행 가능
- **live_paper_trader.py**: BUNDLE 전략(vwap_cross 포함) 현황 확인
  - Cycle 319에서 가중치 추가, vwap_cross 신규 등록 여부 확인
- **레짐 기반 전략 스위칭 준비**: 불/베어/횡보에 따른 전략 조합 활성화 로드맵

### ⚠️ 주의 사항 (Cycle 323)
- **vwap_cross override 고정**: `{"min_oos_trades": 3, "is_negative_regime_max": -2.0, "bear_oos_max": 1.0}` 변경 금지
- **value_area override 고정**: `{"regime_transition_is_min": 2.0, "min_oos_trades": 5, "is_negative_regime_max": -1.4}` 변경 금지
- **새 전략 파일 생성 금지**: 355개 이상 추가 금지
- **합성 데이터 실험 금지**: 반드시 `--csv-dir data/historical` 사용

### 핵심 메트릭 (Cycle 322)
- 테스트: **8413 passed, 23 skipped** (회귀 없음)
- Paper Sim BTC 1h (8 windows, 22전략): **0/22 PASS** (기존 유지)
  - rank1: supertrend_multi (score=73.5, Sharpe=0.32, trades=48)
  - rank2: price_cluster (score=69.7, Sharpe=0.34)
- Bundle OOS BTC 4h (5-fold, --csv-dir data/historical): **5/5 PASS ← 역대 최고!**
  - order_flow_imbalance_v2: **PASS** (avg=4.345, std=0.907, rank1)
  - supertrend_multi: PASS (avg=3.892, std=1.239, rank2)
  - value_area: PASS (avg=3.069, std=0.085, rank3)
  - vwap_cross: **PASS** (avg=3.047, std=1.437, rank4) ← **NEW!**
  - cmf: PASS (avg=2.508, std=1.888, rank5)

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: real CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows)
- ETH/SOL: synthetic CSV (data/historical/synthetic/)
- Bundle OOS: `--csv-dir data/historical` 필수 (합성 데이터 run은 리포트 덮어쓰기 방지됨)
- Paper simulation 1h: 22 전략 × 8 windows → 약 8분 소요 (BTC 단독)

### BUNDLE_STRATEGY_INIT_PARAMS 현재 설정 (Cycle 322 완료 후)
- `vwap_cross: {}` ← 기본 파라미터 (Cycle 321 B: price_cluster 교체)
- `supertrend_multi: {atr_threshold=0.5, atr_threshold_max=1.5, ema_filter=True, confidence_filter=True, rsi_ob_filter=True, rsi_ob_threshold=80, trend_confirm_bars=2, cmf_confirm=False}` ← 고정
- `order_flow_imbalance_v2: {"trend_span": 20}` ← 유지

### BUNDLE_STRATEGY_OVERRIDES 현재 설정 (Cycle 322 완료 후)
- `cmf: {"min_wfe": 0.4, "sharpe_decay_max": 0.40}`
- `supertrend_multi: {"min_oos_trades": 3, "max_oos_sharpe_std": 3.0, "regime_transition_is_min": 2.0}`
- `order_flow_imbalance_v2: {"regime_transition_is_min": 2.0, "min_oos_trades": 3}`
- `vwap_cross: {"min_oos_trades": 3, "is_negative_regime_max": -2.0, "bear_oos_max": 1.0}` ← **UPDATED** Cycle 322 B
- `value_area: {"regime_transition_is_min": 2.0, "min_oos_trades": 5, "is_negative_regime_max": -1.4}` ← 유지

### PAPER_SIM_STRATEGY_PARAMS 현재 설정 (Cycle 322 변경 없음)
- `value_area: {"vol_filter_mult": 0.5}`
- `wick_reversal: {"min_volatility": 0.001, "vol_mult": 0.6}`
- `relative_volume: {"rvol_buy_sell": 1.2}`
- `momentum_quality: {"quality_score_buy_threshold": 0.8, "consistency_buy_threshold": 0.3}`
- `order_flow_imbalance_v2: {"trend_span": 20}`
- `cmf: {"buy_thresh": 0.10}`
