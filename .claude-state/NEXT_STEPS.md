# Next Steps

_Last updated: 2026-06-20 (Cycle 336 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 336

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 334 | D+E+F | delta_window=5 실험→FAIL(avg=2.962,std=3.570), live_paper_trader CSV fallback 검증 |
| 335 | A+C+F | 청산이유 추적(sl/tp/max_hold), BTC CSV 갭 없음 확인, OFI imbalance_threshold 탐색 완료 |
| 336 | B+D+F | MAX_HOLD=48 실험(Sharpe 전 전략 개선), OFI buy_thresh=0.30(BTC개선/ETH악화), 0/20 PASS 16연속 |

### 🎯 Cycle 337 작업 방향 (337 mod 5 = 2 → B(리스크) + D(ML) + F(리서치))

#### B(리스크): MAX_HOLD_CANDLES=48 실제 적용

- **배경**: Cycle 336 실험 확인 — MAX_HOLD=48 시 전 전략 Sharpe/PF 개선
  - price_cluster: max_hold% 12%→3%, Sharpe +0.498, PF +0.100
  - roc_ma_cross: max_hold% 18%→5%, Sharpe +0.665, MDD -6.4%p
  - 설정 위치: `src/backtest/engine.py` line 27 `MAX_HOLD_CANDLES = 24`
- **작업**: `engine.py` `MAX_HOLD_CANDLES = 24` → `48` 변경 후 Paper Sim 전체 재실행
  - Paper Sim 재실행으로 전체 전략에서 PASS 수 변화 확인
  - MDD 악화 여부 감시 (≤20% 기준 유지 필수)
  - 테스트 실행 (`pytest tests/ -x -q`)으로 회귀 없음 확인
- **기대**: 0/20 PASS → 1~3 PASS 가능성 (PF 개선 흐름 전략 대상)
- **금지**: 전략 파일 수정 금지, MDD > 20% 초과 시 즉시 복원

#### D(ML): OFI v2 buy_thresh=0.30 결과 평가 및 결정

- **배경**: Cycle 336 결과 — BTC 개선(Sharpe -0.83→-0.64), ETH 악화(rank15, Sharpe=-2.40)
  - 복합 결과로 단순 유지/복원 결정 어려움
  - 주의: Cycle 300에서도 buy_thresh=0.30 시도 → 역효과 후 복원 전례 있음
- **작업**: 유지 여부 결정을 위한 추가 분석
  - ETH 악화 원인 분석 (`order_flow_imbalance_v2.py` ETH 신호 패턴 확인)
  - BTC-only 기준에서는 유지, ETH/SOL 포함 멀티심볼 기준에서는 복원 고려
  - 결론이 복원이면: `{"trend_span": 20}`으로 되돌리기
- **주의**: Bundle OOS `BUNDLE_STRATEGY_INIT_PARAMS` 변경 금지 (4h 최적 유지)

#### F(리서치): 1h PASS 불가 구조적 원인 분석

- **배경**: 16사이클 연속 0/20 PASS — 단순 파라미터 조정의 한계 도달
- **작업**: SL/TP 비율 재검토
  - 현재: SL=5%, TP=2% → 2.5:1 손절 우세 → 높은 WR 필요 (현재 37-40% WR로 부족)
  - 대안 탐색: SL=2%, TP=4% (1:2 리스크리워드) or SL=3%, TP=6% (1:2)
  - `src/backtest/engine.py`에서 SL_PCT, TP_PCT 파라미터 위치 확인
  - **주의**: 실험 전 전략별 평균 승률 확인 필수 (현재 37~40%)

### ⚠️ 주의 사항 (Cycle 337)
- **order_flow_imbalance_v2 현재 상태**: `{"trend_span": 20, "buy_thresh": 0.30, "sell_thresh": -0.30}` ← Cycle 336 변경
  - **Bundle OOS 파라미터 변경 금지**: 5/5 PASS 유지
  - ETH 악화 분석 후 복원 여부 결정
- **vwap_cross override 고정**: `{"min_oos_trades": 3, "is_negative_regime_max": -2.0, "bear_oos_max": 1.0}` 변경 금지
- **value_area override 고정**: `{"regime_transition_is_min": 2.0, "min_oos_trades": 5, "is_negative_regime_max": -1.4}` 변경 금지
- **STRATEGIES_TIMEFRAME_EXCLUDE 유지**: `"1h": {"value_area", "supertrend_multi"}` 변경 금지
- **새 전략 파일 생성 금지**: 355개 이상 추가 금지
- **합성 데이터 실험 금지**: 반드시 `--csv-dir data/historical` 사용
- **ROC_MIN_ABS 추가 하향 실험 금지**: 이미 0.1% 역효과 확인

### ⚠️ 주의 사항 (Cycle 331, 유지)
- **vwap_cross override 고정**: `{"min_oos_trades": 3, "is_negative_regime_max": -2.0, "bear_oos_max": 1.0}` 변경 금지
- **value_area override 고정**: `{"regime_transition_is_min": 2.0, "min_oos_trades": 5, "is_negative_regime_max": -1.4}` 변경 금지
- **STRATEGIES_TIMEFRAME_EXCLUDE 유지**: `"1h": {"value_area", "supertrend_multi"}` 변경 금지
- **새 전략 파일 생성 금지**: 355개 이상 추가 금지
- **합성 데이터 실험 금지**: 반드시 `--csv-dir data/historical` 사용
- **roc_ma_cross 현재 상태**: v5 (RSI 필터 제거, ROC_MIN_ABS=0.3%)

### 핵심 메트릭 (Cycle 336 B: MAX_HOLD 실험)
- MAX_HOLD=24 vs 48 close_reason 분포 (BTC 1h 실데이터):

| 전략 | MAX_HOLD | trades | sl% | tp% | max_hold% | Sharpe | PF | MDD |
|------|----------|--------|-----|-----|-----------|--------|-----|-----|
| price_cluster | 24 | 368 | 61% | 27% | 12% | 0.239 | 1.061 | 30.7% |
| price_cluster | 48 | 336 | 63% | 34% | 3% | 0.737 | 1.161 | 31.2% |
| roc_ma_cross | 24 | 309 | 59% | 23% | 18% | -0.168 | 0.995 | 23.1% |
| roc_ma_cross | 48 | 284 | 64% | 31% | 5% | 0.497 | 1.115 | 16.7% |
| positional_scaling | 24 | 314 | 62% | 21% | 17% | -0.688 | 0.895 | 36.0% |
| positional_scaling | 48 | 288 | 68% | 28% | 4% | -0.393 | 0.946 | 31.5% |

- **결론**: MAX_HOLD=48이 전 전략에서 Sharpe/PF 개선 (max_hold% 급감: 12-18% → 3-5%)
  - price_cluster: Sharpe +0.498, PF +0.100, MDD +0.5%p (허용 범위)
  - roc_ma_cross: Sharpe +0.665, PF +0.120, MDD -6.4%p (개선)
  - positional_scaling: Sharpe +0.295, PF +0.051, MDD -4.5%p (개선)
  - **주의**: 세 전략 모두 여전히 FAIL (PF<1.5, Sharpe 부족, MDD>20%)
  - MAX_HOLD=48 권장 — Cycle 337에서 engine.py 상수 변경 가능
- **미변경**: engine.py MAX_HOLD_CANDLES 아직 24 유지 (추가 검토 후 Cycle 337 B에서 결정)

### 핵심 메트릭 (Cycle 336)
- 테스트: **8425 passed, 23 skipped** (회귀 없음)
- Paper Sim BTC 1h (8 windows, **20전략**, buy_thresh=0.30): **0/20 PASS** (16사이클 연속)
  - rank1: price_cluster (Sharpe=0.34, Return=+2.19%, PF=1.11, 1/8)
  - rank2: roc_ma_cross (Sharpe=-0.41, PF=1.10, 2/8)
  - rank3: positional_scaling (Sharpe=0.00, PF=1.18, 1/8)
  - OFI rank5: Sharpe=-0.64, PF=1.04, 70 trades (이전 rank10, Sharpe=-0.83 대비 개선)
  - 주요 FAIL 원인: profit_factor < 1.5 (전체), MAX_HOLD 강제청산 구조적 원인
- Bundle OOS BTC 4h: **5/5 PASS** ← 유지
  - rank1: order_flow_imbalance_v2 (avg=4.345, std=0.907)
  - rank2: supertrend_multi (avg=3.892, std=1.239)
  - rank3: value_area (avg=3.069, std=0.085)
  - rank4: vwap_cross (avg=3.047, std=1.437)
  - rank5: cmf (avg=2.508, std=1.888)

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: real CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows, 갭 없음)
- ETH/SOL: synthetic CSV (data/historical/synthetic/) — NaN 없음, OHLC 정상
- Bundle OOS: `--csv-dir data/historical` 필수 (합성 데이터 run은 리포트 덮어쓰기 방지됨)
- Paper simulation 1h: **20 전략** × 8 windows → 약 13분 소요

### BUNDLE_STRATEGY_INIT_PARAMS 현재 설정 (Cycle 336 변경 없음)
- `vwap_cross: {}` ← 기본 파라미터
- `supertrend_multi: {atr_threshold=0.5, atr_threshold_max=1.5, ema_filter=True, confidence_filter=True, rsi_ob_filter=True, rsi_ob_threshold=80, trend_confirm_bars=2, cmf_confirm=False}` ← 고정
- `order_flow_imbalance_v2: {"trend_span": 20}` ← 최적 확정 (delta_window=10 기본값)

### BUNDLE_STRATEGY_OVERRIDES 현재 설정 (Cycle 330 변경 없음)
- `cmf: {"min_wfe": 0.4, "sharpe_decay_max": 0.40}`
- `supertrend_multi: {"min_oos_trades": 3, "max_oos_sharpe_std": 3.0, "regime_transition_is_min": 2.0}`
- `order_flow_imbalance_v2: {"regime_transition_is_min": 2.0, "min_oos_trades": 3}`
- `vwap_cross: {"min_oos_trades": 3, "is_negative_regime_max": -2.0, "bear_oos_max": 1.0}` ← 고정
- `value_area: {"regime_transition_is_min": 2.0, "min_oos_trades": 5, "is_negative_regime_max": -1.4}` ← 유지

### PAPER_SIM_STRATEGY_PARAMS 현재 설정 (Cycle 336 변경)
- `value_area: {"vol_filter_mult": 0.5}` (1h paper_sim에서 제외됨)
- `wick_reversal: {"min_volatility": 0.001, "vol_mult": 0.6}`
- `relative_volume: {"rvol_buy_sell": 1.2}`
- `momentum_quality: {"quality_score_buy_threshold": 0.8, "consistency_buy_threshold": 0.3}`
- `order_flow_imbalance_v2: {"trend_span": 20, "buy_thresh": 0.30, "sell_thresh": -0.30}` ← Cycle 336 D(ML) 변경
- `cmf: {"buy_thresh": 0.10}`
