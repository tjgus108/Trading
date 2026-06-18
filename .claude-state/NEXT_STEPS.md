# Next Steps

_Last updated: 2026-06-18 (Cycle 325 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 325

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 323 | C+B+F | 5/5 PASS 안정성 확인, combined_exclusion_ratio 경고 추가 |
| 324 | D+E+F | supertrend_multi_1h 그리드 추가, live_paper_trader 4h 지원, recommend_for_regime 통합 |
| 325 | A+C+F | value_area/supertrend_multi 1h 제외 확정, CSV 4h fallback 추가, 레짐 임계값 문제 발견 |

### 🎯 Cycle 326 작업 방향 (326 mod 5 = 1 → B(리스크) + D(ML) + F(리서치))

#### B(리스크): MarketRegimeDetector HIGH_VOL 임계값 재보정

- **현재 문제**: BTC 5-fold 분석에서 전 구간 ATR%=2.5-3.3% → 전부 HIGH_VOL 판정
  - BTC 정상 ATR% 범위가 2-4%이므로 임계값 2.5%는 너무 낮음
  - HIGH_VOL 판정 과다 → TREND_UP/DOWN 레짐 전략이 작동 안 함
- **확인 필요**: `src/strategy/regime.py` MarketRegimeDetector HIGH_VOL 임계값 현황
  - BTC 기준 HIGH_VOL: ATR%>4-5% 또는 VIX 등가 기준 재설정 검토
  - TREND_UP 판단 기준: EMA slope + 가격 변화율 조합 (현재 slope>0.002 & change>5%)
- **목표**: fold0(+132% but HIGH_VOL) → TREND_UP으로 재판정되어야 매핑 일치

#### D(ML): roc_ma_cross 1h PASS 경계값 분석

- **현재 상황**: Paper Sim rank2 (return=+0.38%, Sharpe=-0.35, 2/8 — 최고 consistency!)
  - FAIL 원인: Sharpe 평균이 음수, PF=1.12 < 1.5
  - 2/8 consistency가 price_cluster(1/8)보다 좋음 — 안정성 잠재력 있음
- **탐색 방향**: WalkForwardOptimizer로 roc_ma_cross 1h 파라미터 탐색
  - `walk_forward.py`에 `roc_ma_cross` 그리드 있는지 확인
  - 없다면 추가: `roc_period=[10,15,20]`, `ma_period=[20,30,40]` 정도
- **단, 합성 데이터 사용 금지**: BTC 1h CSV로만 검증

#### F(리서치): Bundle OOS 전략 로테이션 한계 분석

- **fold4 (2024-02-25~04-24) 이상**: supertrend_multi OOS=-1.538 (유일 FAIL fold)
  - 2024년 초 BTC ATH($73k) 후 조정 구간 — supertrend가 ATH에서 무너짐
  - fold4 제외 rule은 IS>2.0인데, fold4 IS=2.323>2.0 → 제외됨 ✓
  - OFI는 fold4 OOS=5.475 (최고) → ATH 구간에서 OFI가 supertrend를 대체
  - **레짐 스위칭 근거**: fold4 구간에서 OFI > supertrend → 2024년 Bull 레짐에서 OFI 우선
- **Cycle 325 레짐 분석 연장**: crypto 특화 레짐 감지기 논문 조사
  - 참고: "Regime-Switching Models for Crypto" (SSRN 2023-2024)
  - Hidden Markov Model(HMM) 기반 레짐 감지 vs EMA slope 기반 비교

### ⚠️ 주의 사항 (Cycle 326)
- **vwap_cross override 고정**: `{"min_oos_trades": 3, "is_negative_regime_max": -2.0, "bear_oos_max": 1.0}` 변경 금지
- **value_area override 고정**: `{"regime_transition_is_min": 2.0, "min_oos_trades": 5, "is_negative_regime_max": -1.4}` 변경 금지
- **STRATEGIES_TIMEFRAME_EXCLUDE 유지**: `"1h": {"value_area", "supertrend_multi"}` 변경 금지
- **새 전략 파일 생성 금지**: 355개 이상 추가 금지
- **합성 데이터 실험 금지**: 반드시 `--csv-dir data/historical` 사용

### 핵심 메트릭 (Cycle 325)
- 테스트: **8413 passed, 23 skipped** (회귀 없음)
- Paper Sim BTC 1h (8 windows, **20전략** — value_area/supertrend_multi 제외): **0/20 PASS**
  - rank1: price_cluster (return=+2.19%, Sharpe=0.34, 1/8)
  - rank2: roc_ma_cross (return=+0.38%, 2/8 consistency — 최고!)
  - rank3: positional_scaling (return=+1.97%, PF=1.18, 1/8)
- Bundle OOS BTC 4h (5-fold, --csv-dir data/historical): **5/5 PASS** (5사이클 연속 유지)
  - order_flow_imbalance_v2: PASS (avg=4.345, std=0.907, rank1)
  - supertrend_multi: PASS (avg=3.892, std=1.239, rank2)
  - value_area: PASS (avg=3.069, std=0.085, rank3)
  - vwap_cross: PASS (avg=3.047, std=1.437, rank4)
  - cmf: PASS (avg=2.508, std=1.888, rank5)

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: real CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows)
- ETH/SOL: synthetic CSV (data/historical/synthetic/)
- Bundle OOS: `--csv-dir data/historical` 필수 (합성 데이터 run은 리포트 덮어쓰기 방지됨)
- Paper simulation 1h: **20 전략** × 8 windows → 약 7분 소요 (BTC 단독)

### Cycle 325 추가 코드 변경 요약
- `scripts/paper_simulation.py`: `STRATEGIES_TIMEFRAME_EXCLUDE` 추가 (A품질)
  - `"1h": {"value_area", "supertrend_multi"}` — 4h 전용 전략 1h 제외
- `scripts/live_paper_trader.py`: `fetch_latest_candles()` CSV 4h fallback 추가 (C데이터)
  - exchange 실패 시 data/historical CSV fallback, 1h→4h resample, 실거래소 우선 정렬

### BUNDLE_STRATEGY_INIT_PARAMS 현재 설정 (Cycle 325 변경 없음)
- `vwap_cross: {}` ← 기본 파라미터
- `supertrend_multi: {atr_threshold=0.5, atr_threshold_max=1.5, ema_filter=True, confidence_filter=True, rsi_ob_filter=True, rsi_ob_threshold=80, trend_confirm_bars=2, cmf_confirm=False}` ← 고정
- `order_flow_imbalance_v2: {"trend_span": 20}` ← 유지

### BUNDLE_STRATEGY_OVERRIDES 현재 설정 (Cycle 325 변경 없음)
- `cmf: {"min_wfe": 0.4, "sharpe_decay_max": 0.40}`
- `supertrend_multi: {"min_oos_trades": 3, "max_oos_sharpe_std": 3.0, "regime_transition_is_min": 2.0}`
- `order_flow_imbalance_v2: {"regime_transition_is_min": 2.0, "min_oos_trades": 3}`
- `vwap_cross: {"min_oos_trades": 3, "is_negative_regime_max": -2.0, "bear_oos_max": 1.0}` ← 고정
- `value_area: {"regime_transition_is_min": 2.0, "min_oos_trades": 5, "is_negative_regime_max": -1.4}` ← 유지

### PAPER_SIM_STRATEGY_PARAMS 현재 설정 (Cycle 325 변경 없음)
- `value_area: {"vol_filter_mult": 0.5}` (1h paper_sim에서 제외됨)
- `wick_reversal: {"min_volatility": 0.001, "vol_mult": 0.6}`
- `relative_volume: {"rvol_buy_sell": 1.2}`
- `momentum_quality: {"quality_score_buy_threshold": 0.8, "consistency_buy_threshold": 0.3}`
- `order_flow_imbalance_v2: {"trend_span": 20}`
- `cmf: {"buy_thresh": 0.10}`
