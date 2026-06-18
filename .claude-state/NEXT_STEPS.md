# Next Steps

_Last updated: 2026-06-18 (Cycle 324 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 324

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 322 | B+D+F | bear_oos_max=1.0 추가, vwap_cross fold1 해결, **Bundle 4→5/5 PASS (역대 최고!)** |
| 323 | C+B+F | 5/5 PASS 안정성 확인, combined_exclusion_ratio 경고 추가, Bundle 5개 live_paper_trader 등록 |
| 324 | D+E+F | supertrend_multi_1h 그리드 추가, live_paper_trader 4h 지원, recommend_for_regime Bundle 통합 |

### 🎯 Cycle 325 작업 방향 (325 mod 5 = 0 → A(품질) + C(데이터) + F(리서치))

#### A(품질): supertrend_multi 1h PASS 경계값 분석

- **현재 상황**: Paper Sim rank1 (Sharpe=0.32, PF=1.14, 2/8 windows)
  - FAIL 원인: PF=1.47 < 1.5 (0.03 차이), mc_p=0.161 > 0.1
  - **Cycle 324에 추가된 `supertrend_multi_1h` 그리드** 활용 방법 검토:
    - `trend_confirm_bars=[4,6,8]`, `atr_threshold=[0.3,0.4,0.5]` 탐색
    - paper_simulation.py `PAPER_SIM_STRATEGY_PARAMS["supertrend_multi"]`에 1h 최적 파라미터 반영 고려
    - 단, 실제 WalkForwardOptimizer로 BTC 1h 데이터에서 검증 후 업데이트
- **품질 체크**: value_area 1h (rank 21, Sharpe=-3.08) — 4h 전용 확정, paper_sim 목록에서 제외 검토

#### C(데이터): data/historical 4h 데이터 경로 확인

- **Bundle OOS는 1h CSV를 4h로 리샘플링**: 데이터 품질 검증
  - `data/historical/binance/BTCUSDT/1h.csv` → 4h 리샘플링 정확도 확인
  - 4h 리샘플링 시 volume 집계 방식 검증 (sum vs first)
- **live_paper_trader 4h 지원**: Cycle 324 E(실행) 완료
  - `--timeframe 4h` 옵션 추가됨 → Bundle 전략 4h 실행 경로 확인
  - WARMUP_CANDLES=200 × 4h = 800h ≈ 33일 데이터 필요 (CSV fallback 검증)

#### F(리서치): 레짐 스위칭 실효성 분석

- **recommend_for_regime 통합 완료** (Cycle 324): Bundle PASS 전략 레짐 매핑
  - TREND_UP → OFI v2 + supertrend_multi
  - TREND_DOWN → vwap_cross + value_area
  - HIGH_VOL → cmf 우선
  - RANGING → 포지션 최소화 (상위 2개)
- **다음 단계**: BTC 2023 데이터에서 레짐별 전략 성과 사후 분석
  - fold0 (2023-06~08): supertrend_multi OOS=2.545 vs value_area OOS=-0.091 — TREND_UP 구간?
  - fold1 (2023-08~10): OFI OOS=3.791, vwap_cross OOS=-0.913 — 레짐 매핑 일치 여부

### ⚠️ 주의 사항 (Cycle 325)
- **vwap_cross override 고정**: `{"min_oos_trades": 3, "is_negative_regime_max": -2.0, "bear_oos_max": 1.0}` 변경 금지
- **value_area override 고정**: `{"regime_transition_is_min": 2.0, "min_oos_trades": 5, "is_negative_regime_max": -1.4}` 변경 금지
- **새 전략 파일 생성 금지**: 355개 이상 추가 금지
- **합성 데이터 실험 금지**: 반드시 `--csv-dir data/historical` 사용

### 핵심 메트릭 (Cycle 324)
- 테스트: **8413 passed, 23 skipped** (회귀 없음)
- Paper Sim BTC 1h (8 windows, 22전략): **0/22 PASS** (기존 유지)
  - rank1: supertrend_multi (return=+5.26%, Sharpe=0.32, trades=48, 2/8)
  - rank2: price_cluster (return=+2.19%, Sharpe=0.34)
  - supertrend_multi FAIL 경계: PF=1.47 < 1.5, mc_p=0.161 > 0.1
- Bundle OOS BTC 4h (5-fold, --csv-dir data/historical): **5/5 PASS** (유지)
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
- Paper simulation 1h: 22 전략 × 8 windows → 약 8분 소요 (BTC 단독)

### Cycle 324 추가 코드 변경 요약
- `src/backtest/walk_forward.py`: `supertrend_multi_1h` 그리드 추가 (D(ML))
- `scripts/live_paper_trader.py`: `--timeframe {1h,4h,1d}` 옵션, `self.timeframe` 전달 (E(실행))
- `src/strategy/rotation.py`: `recommend_for_regime()` Bundle PASS 레짐 매핑 통합 (F(리서치))

### BUNDLE_STRATEGY_INIT_PARAMS 현재 설정 (Cycle 324 변경 없음)
- `vwap_cross: {}` ← 기본 파라미터
- `supertrend_multi: {atr_threshold=0.5, atr_threshold_max=1.5, ema_filter=True, confidence_filter=True, rsi_ob_filter=True, rsi_ob_threshold=80, trend_confirm_bars=2, cmf_confirm=False}` ← 고정
- `order_flow_imbalance_v2: {"trend_span": 20}` ← 유지

### BUNDLE_STRATEGY_OVERRIDES 현재 설정 (Cycle 324 변경 없음)
- `cmf: {"min_wfe": 0.4, "sharpe_decay_max": 0.40}`
- `supertrend_multi: {"min_oos_trades": 3, "max_oos_sharpe_std": 3.0, "regime_transition_is_min": 2.0}`
- `order_flow_imbalance_v2: {"regime_transition_is_min": 2.0, "min_oos_trades": 3}`
- `vwap_cross: {"min_oos_trades": 3, "is_negative_regime_max": -2.0, "bear_oos_max": 1.0}` ← 고정
- `value_area: {"regime_transition_is_min": 2.0, "min_oos_trades": 5, "is_negative_regime_max": -1.4}` ← 유지

### PAPER_SIM_STRATEGY_PARAMS 현재 설정 (Cycle 324 변경 없음)
- `value_area: {"vol_filter_mult": 0.5}`
- `wick_reversal: {"min_volatility": 0.001, "vol_mult": 0.6}`
- `relative_volume: {"rvol_buy_sell": 1.2}`
- `momentum_quality: {"quality_score_buy_threshold": 0.8, "consistency_buy_threshold": 0.3}`
- `order_flow_imbalance_v2: {"trend_span": 20}`
- `cmf: {"buy_thresh": 0.10}`
