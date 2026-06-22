# Next Steps

_Last updated: 2026-06-22 (Cycle 346 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 346

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 344 | D+E+F | avg_oos_mdd Bundle OOS 노출, Slip_High% per-window 추가, 4h/1h 구조 분석, 0/20 24연속 |
| 345 | A+C+F | avg_oos_mdd 테스트 5개, cumulative→rolling VWAP 교체, min_hold_bars=4 실험, 0/20 25연속 |
| 346 | B+D | per-strategy min_hold_bars, roc_ma_cross ROC0.5% (+0.15 Sharpe), 0/20 26연속 |

### 🎯 Cycle 347 작업 방향 (347 mod 5 = 2 → C(데이터) + E(실행))

#### C(데이터): price_cluster 창 진단 — 왜 W6만 PASS인가

- **배경**: price_cluster Sharpe=0.87, Consistency=1/8 (W6만 PASS: RANGING+RANGING+sideways)
  - W1(bull), W2-W5(RANGING), W7-W8(bull) 모두 FAIL
  - 독특하게 sideways 전용 전략 같은 패턴 — RANGING 구간 중에서도 sideways만 성공
- **작업**:
  - `src/strategy/price_cluster.py` 코드 분석: 어떤 조건에서 신호 생성?
  - W6 특성 파악: IS 데이터 레짐 + OOS 시장 조건 (sideways 정의 확인)
  - 시장 환경별 신호 빈도 분석: 왜 W6만 41→36 trades에서 3.78 Sharpe 가능?
  - 단독 실험 원칙: 1가지 변경만

#### E(실행): roc_ma_cross W6/W7 MC 통계 문제 해결 탐색

- **배경**: W6 Sharpe=1.20(달성)이나 `mc_p_value 0.259 > 0.1` (통계 미달)
  - W7: Sharpe=0.98 (0.02 미달)
  - 둘 다 해결되면 roc_ma_cross 4/8 PASS 가능성
- **작업**:
  - MC p-value 임계값 분석: W6 trades=30 → p-value=0.259의 의미
  - 거래 수 증가 방향 탐색: roc_period 변경 또는 ma_period 변경
  - W7 Sharpe 0.02 gap: 무엇이 차단하는지 분석 (W7: RANGING+bull)
  - 단독 실험 원칙: 1가지 변경만

### ⚠️ 주의 사항 (Cycle 347)

- **max_hold_candles_override=48 유지**: paper_simulation.py engine에 고정
- **BUNDLE_STRATEGY_OVERRIDES 임계값 변경 금지**: 1h 연간화 기준 캘리브레이션됨
- **atr_multiplier_tp=3.5 유지**: Cycle 338 실험으로 확정
- **2단계 손실 스케일링 유지**: threshold=5 기준 2→75%, 5→50%
- **슬리피지 임계값 변경 금지**: `atr_ratio < 0.03 * tf_scale`
- **PAPER_SIM_REGIME_FILTER**: `set()` (빈 집합) — 유지
- **새 전략 파일 생성 금지**: 355개 이상 추가 금지
- **합성 데이터 실험 금지**: 반드시 `--csv-dir data/historical` 사용

### 핵심 메트릭 (Cycle 346 확정)

| 지표 | Cycle 345 | Cycle 346 | 변화 |
|------|-----------|-----------|------|
| roc_ma_cross Sharpe | 0.34(global MHB0) / 0.99(MHB4) | **1.14** (per-strat MHB4 + ROC0.5%) | +0.15 |
| roc_ma_cross Consistency | 2/8 | **2/8** | 유지 |
| price_cluster Sharpe | 0.87 | **0.87** | 유지 |
| price_cluster Consistency | 1/8 | **1/8** | 유지 |
| 1h PASS 수 | 0/20 (25연속) | **0/20 (26연속)** | — |
| Bundle OOS PASS | 5/5 | **5/5** | 유지 ✅ |
| 테스트 수 | 8432 | **8432** | 변화 없음 |

### Cycle 346 코드 변경 요약

| 파일 | 변경 내용 |
|------|----------|
| `scripts/paper_simulation.py` | `PAPER_SIM_MIN_HOLD_BARS` 딕셔너리 추가, `simulate_symbol` 시그니처+루프 수정, `run_simulation` per-strategy engine 생성 |
| `src/strategy/roc_ma_cross.py` | `_ROC_MIN_ABS` 0.3 → 0.5% |

### Cycle 346 B+D 실험 결과

#### D(ML): per-strategy min_hold_bars 구현
- `PAPER_SIM_MIN_HOLD_BARS = {"roc_ma_cross": 4}` → 기본 engine과 별도 engine 생성
- 초기값: roc_ma_cross=4, Sharpe=0.99 검증 ✅
- price_cluster 영향 없음 검증 ✅

#### B(리스크): roc_ma_cross ROC 임계값 실험
| _ROC_MIN_ABS | Sharpe | PF | Trades | Consistency |
|---|---|---|---|---|
| 0.3% (baseline) | 0.99 | 1.34 | 34 | 2/8 |
| 0.5% (Cycle 346) | **1.14** | **1.37** | 33 | 2/8 |

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
- BTC: real CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows)
- ETH/SOL: synthetic CSV (data/historical/synthetic/) — NaN 없음, OHLC 정상
- Bundle OOS: `--csv-dir data/historical` 필수 (합성 데이터 run은 리포트 덮어쓰기 방지됨)
- Paper simulation 1h: **20 전략** × 8 windows × 3 symbols → 약 12분 소요 (순차적)

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

### PAPER_SIM_MIN_HOLD_BARS 현재 설정 (Cycle 346 D(ML) 신규)
- `roc_ma_cross: 4` ← per-strategy min_hold_bars

### PAPER_SIM_REGIME_FILTER 현재 설정 (Cycle 339 롤백 유지)
- `set()` ← 빈 집합 (레짐 필터 비활성화)
- 이유: 개별 봉 수준 TREND_UP 필터 → roc_ma_cross trades 57→18, Sharpe +0.32→-0.43 역효과 확인

### 핵심 메트릭 (Cycle 338: MAX_HOLD 분리 아키텍처, 유지)

| 구분 | max_hold_candles | 설정 위치 |
|------|-----------------|---------|
| 1h paper_sim | 48봉 (48시간) | `paper_simulation.py`: `max_hold_candles_override=48` |
| 4h Bundle OOS | 24봉 (96시간=4일) | `BacktestEngine` 기본값 `MAX_HOLD_CANDLES=24` |
| 기타(테스트 등) | 24봉 | `BacktestEngine` 기본값 |
