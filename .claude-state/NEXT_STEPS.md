# Next Steps

_Last updated: 2026-06-22 (Cycle 343 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 343

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 341 | B+D+F | W5 구조적 FAIL 확인, IS→OOS 상관관계 정량화, loss_scale 추적 추가, 0/20 21연속 |
| 342 | B+D+F | loss_scale 집계 paper_sim 연결, IS/OOS Pearson 추가, 0/20 22연속 |
| 343 | C+B+F | BTC CSV 품질확인, RANGING kill 1.5→1.2, avg_oos_mdd 추가, 0/20 23연속 |

### 🎯 Cycle 344 작업 방향 (344 mod 5 = 4 → D(ML) + E(실행) + F)

#### D(ML): avg_oos_mdd Bundle OOS 노출 + mean-reversion ML 신호 실험

- **배경**: Cycle 343에서 `avg_oos_mdd` 필드 WalkForwardResult에 추가 완료
  - Bundle OOS (`run_bundle_oos.py`) 출력에 `avg_oos_mdd` 노출 필요
- **작업**:
  - `scripts/run_bundle_oos.py` 리포트에 `avg_oos_mdd` 컬럼 추가
  - mean-reversion ML 신호 실험: price_cluster 전략에 RandomForest 신호 필터 추가 검토
    - 피처: ATR, RSI, CMF, rolling_vol → BUY/HOLD 분류 (라벨: 다음 N봉 수익 > 0)
    - 단, 합성 데이터에서만 검증하지 말 것 (실제 BTC CSV 사용 필수)

#### E(실행): W5 저변동성 구간 슬리피지 레짐 분포 확인

- **배경**: W5(vol=0.0139, RANGING)가 worst 창 (avg_sharpe=-2.994, loss_scale_full=9.3)
  - 저변동성에서 고정 슬리피지 모델이 PF를 과대 침식 가능성
- **작업**:
  - `src/backtest/engine.py`의 슬리피지 계산 로직 확인
  - W5 구간의 `slippage_regime` 분포 (low/normal/high) 추출
  - 변동성 기반 동적 슬리피지 조정 가능성 평가

#### F(리서치): 4h Bundle OOS 전략이 1h RANGING에서 실패하는 구조적 이유

- **배경**: Bundle OOS 5/5 PASS 전략들이 Paper Sim에서 모두 FAIL
  - 동일 전략이 4h에서는 통과, 1h에서는 FAIL → timeframe 의존성 분석 필요
- **작업**:
  - `cmf`, `order_flow_imbalance_v2` 등 4h PASS 전략의 1h paper_sim Sharpe 확인
  - RANGING 구간에서 4h vs 1h 신호 생성 빈도 비교
  - hold 기간(4h×24봉=4일 vs 1h×48봉=2일) 차이가 PF에 미치는 영향

### ⚠️ 주의 사항 (Cycle 344)

- **max_hold_candles_override=48 유지**: paper_simulation.py engine에 고정
- **BUNDLE_STRATEGY_OVERRIDES 임계값 변경 금지**: 1h 연간화 기준 캘리브레이션됨
- **atr_multiplier_tp=3.5 유지**: Cycle 338 실험으로 확정
- **2단계 손실 스케일링 유지**: threshold=5 기준 2→75%, 5→50%
- **슬리피지 임계값 변경 금지**: `atr_ratio < 0.03 * tf_scale`
- **PAPER_SIM_REGIME_FILTER**: `set()` (빈 집합) — 유지
- **새 전략 파일 생성 금지**: 355개 이상 추가 금지
- **합성 데이터 실험 금지**: 반드시 `--csv-dir data/historical` 사용

### 핵심 메트릭 (Cycle 343 확정)

| 지표 | Cycle 342 | Cycle 343 | 변화 |
|------|-----------|-----------|------|
| price_cluster Sharpe | 0.87 | **0.87** | 유지 |
| price_cluster Consistency | 1/8 | **1/8** | 유지 |
| roc_ma_cross Sharpe | 0.34 | **0.34** | 유지 |
| roc_ma_cross Consistency | 2/8 | **2/8** | 유지 |
| 1h PASS 수 | 0/20 (22연속) | **0/20 (23연속)** | — |
| Bundle OOS PASS | 5/5 | **5/5** | 유지 ✅ |

### Cycle 343 코드 변경 요약

| 파일 | 변경 내용 |
|------|----------|
| `src/risk/drawdown_monitor.py` | RANGING cooldown 1.0→1.2, kill_multiplier 1.5→1.2 |
| `src/backtest/walk_forward.py` | WindowResult.oos_mdd 추가, WalkForwardResult.avg_oos_mdd 추가 |

### IS/OOS 레짐 진단 결과 (Cycle 340 신규)

| Window | IS end-state | OOS dominant | mkt | price_cluster | roc_ma_cross |
|--------|-------------|--------------|-----|---------------|--------------|
| W1 | TREND_UP | TREND_UP | bull | -1.43 FAIL | 4.04 PASS |
| W2 | TREND_UP | RANGING | bull | 0.11 FAIL | 3.84 PASS |
| W3 | RANGING | RANGING | bear | 0.00 FAIL | -0.04 FAIL |
| W4 | RANGING | RANGING | bear | -0.41 FAIL | -2.01 FAIL |
| W5 | RANGING | RANGING | sideways | 0.99 FAIL | -3.77 FAIL |
| W6 | RANGING | RANGING | sideways | **3.78 PASS** | -0.28 FAIL |
| W7 | RANGING | RANGING | bull | -0.08 FAIL | -1.12 FAIL |
| W8 | TREND_UP | RANGING | bull | 0.21 FAIL | -2.05 FAIL |

- price_cluster 최적 환경: RANGING+RANGING+sideways (W6)
- roc_ma_cross 최적 환경: IS=TREND_UP + bull market momentum (W1, W2)

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: real CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows, 갭 없음)
- ETH/SOL: synthetic CSV (data/historical/synthetic/) — NaN 없음, OHLC 정상
- Bundle OOS: `--csv-dir data/historical` 필수 (합성 데이터 run은 리포트 덮어쓰기 방지됨)
- Paper simulation 1h: **20 전략** × 8 windows → 약 6분 소요 (BTC only)

### BUNDLE_STRATEGY_INIT_PARAMS 현재 설정 (Cycle 340 변경 없음)
- `vwap_cross: {}` ← 기본 파라미터
- `supertrend_multi: {atr_threshold=0.5, atr_threshold_max=1.5, ema_filter=True, confidence_filter=True, rsi_ob_filter=True, rsi_ob_threshold=80, trend_confirm_bars=2, cmf_confirm=False}` ← 고정
- `order_flow_imbalance_v2: {"trend_span": 20}` ← 최적 확정 (delta_window=10 기본값)

### BUNDLE_STRATEGY_OVERRIDES 현재 설정 (Cycle 330 변경 없음)
- `cmf: {"min_wfe": 0.4, "sharpe_decay_max": 0.40}`
- `supertrend_multi: {"min_oos_trades": 3, "max_oos_sharpe_std": 3.0, "regime_transition_is_min": 2.0}`
- `order_flow_imbalance_v2: {"regime_transition_is_min": 2.0, "min_oos_trades": 3}`
- `vwap_cross: {"min_oos_trades": 3, "is_negative_regime_max": -2.0, "bear_oos_max": 1.0}` ← 고정
- `value_area: {"regime_transition_is_min": 2.0, "min_oos_trades": 5, "is_negative_regime_max": -1.4}` ← 유지

### PAPER_SIM_STRATEGY_PARAMS 현재 설정 (Cycle 340 변경 없음)
- `value_area: {"vol_filter_mult": 0.5}` (1h paper_sim에서 제외됨)
- `wick_reversal: {"min_volatility": 0.001, "vol_mult": 0.6}`
- `relative_volume: {"rvol_buy_sell": 1.2}`
- `momentum_quality: {"quality_score_buy_threshold": 0.8, "consistency_buy_threshold": 0.3}`
- `order_flow_imbalance_v2: {"trend_span": 20}` ← Cycle 337 D(ML) 복원
- `cmf: {"buy_thresh": 0.10}`

### PAPER_SIM_REGIME_FILTER 현재 설정 (Cycle 339 롤백 유지)
- `set()` ← 빈 집합 (레짐 필터 비활성화)
- 이유: 개별 봉 수준 TREND_UP 필터 → roc_ma_cross trades 57→18, Sharpe +0.32→-0.43 역효과 확인

### 핵심 메트릭 (Cycle 338: MAX_HOLD 분리 아키텍처, 유지)

| 구분 | max_hold_candles | 설정 위치 |
|------|-----------------|---------|
| 1h paper_sim | 48봉 (48시간) | `paper_simulation.py`: `max_hold_candles_override=48` |
| 4h Bundle OOS | 24봉 (96시간=4일) | `BacktestEngine` 기본값 `MAX_HOLD_CANDLES=24` |
| 기타(테스트 등) | 24봉 | `BacktestEngine` 기본값 |
