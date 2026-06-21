# Next Steps

_Last updated: 2026-06-21 (Cycle 339 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 339

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 337 | B+D+F | max_hold_candles_override=48(1h전용), OFI buy_thresh복원, 5/5 Bundle PASS 유지, 0/20 17연속 |
| 338 | C+B+F | TP=2.5 역효과 확인(TP=3.5 확정), 2단계 손실스케일링 추가, 윈도우별 레짐 분석, 0/20 18연속 |
| 339 | D+E+F | 레짐필터 역효과(roc_ma_cross Sharpe -0.75 급락→롤백), 슬리피지 임계값 2→3%(price_cluster+0.03), 0/20 19연속 |

### 🎯 Cycle 340 작업 방향 (340 mod 5 = 0 → A(품질) + C(데이터) + F(리서치))

#### A(품질): 레짐 필터 방향 전환 + 테스트 커버리지

- **배경**: Cycle 339 D(ML) 레짐 필터 역효과 확인
  - 개별 봉 TREND_UP 필터: BUY 신호 ~70% 차단 → trades 57→18 → Sharpe +0.32→-0.43
  - **근본 원인**: 윈도우 수준 TREND_UP% 상관관계 ≠ 개별 봉 수준 필터링 효과
  - 슬리피지 임계값 2%→3% 변경: price_cluster +0.03, frama +0.05 — 미미하지만 긍정적
- **작업 방향**:
  - PAPER_SIM_REGIME_FILTER는 이미 빈 집합으로 롤백됨 (Cycle 339 말미)
  - 레짐 필터 대신 IS/OOS 구간 레짐 **매칭** 방식 검토 (같은 레짐 구간에서만 IS→OOS 전이)
  - price_cluster 1/8 consistency 원인 분석: W6/W8에서만 PASS — 왜 이 구간만?
  - 테스트 커버리지: `tests/test_regime.py` 있는지 확인, 없으면 기존 파일에 추가

#### C(데이터): BTC 히스토리 데이터 확장 검토

- **배경**: 현재 BTC CSV는 2023-01~2024-05 (12000행). 더 긴 기간 데이터가 있으면 윈도우 수 증가
- **작업**:
  - `data/historical/binance/BTCUSDT/` 폴더 확인 (1h.csv만 있는지, 4h.csv 있는지)
  - 4h Bundle OOS는 12000행 1h → resample 3000행 4h = 2023-01~2024-05. 더 긴 기간 필요한지?
  - 데이터 추가 수집이 불가능하면 (SSL 차단) 현재 데이터 최대 활용 방안 검토

#### F(리서치): 레짐 필터 효과 심층 분석

- **배경**: TREND_UP 필터가 roc_ma_cross W3-W8에서 얼마나 신호를 줄였는지 검증 필요
- **작업**:
  - `--verbose-windows` 옵션으로 roc_ma_cross 8개 윈도우 Sharpe/Trades 상세 확인
  - trades가 0으로 떨어진 윈도우: 레짐 필터 과도 → PAPER_SIM_REGIME_FILTER 해제 고려
  - trades가 줄었지만 Sharpe 개선: 필터 효과 입증 → 다른 전략(frama, lob_maker)에도 확장 검토
  - 비교: Cycle 338 roc_ma_cross 전 윈도우 Sharpe vs 339 필터 후 윈도우 Sharpe

### ⚠️ 주의 사항 (Cycle 340)

- **max_hold_candles_override=48 유지**: `paper_simulation.py` engine에 고정, 절대 제거 금지
  - Bundle OOS engine에는 전달 안 함 (RollingOOSValidator → BacktestEngine 기본값 24 유지)
- **BUNDLE_STRATEGY_OVERRIDES 임계값 변경 금지**: 1h 연간화 기준 캘리브레이션됨
- **atr_multiplier_tp=3.5 유지**: Cycle 338 실험으로 확정.
- **2단계 손실 스케일링 유지**: threshold=5 기준 2→75%, 5→50%.
- **order_flow_imbalance_v2 현재 상태**: `{"trend_span": 20}` ← Cycle 337 D(ML) 복원
- **슬리피지 임계값 변경 금지**: Cycle 339 E(실행) 수정. `atr_ratio < 0.03 * tf_scale` (1h 기준 3%)
- **PAPER_SIM_REGIME_FILTER**: `set()` (빈 집합) — Cycle 339 D(ML) 역효과 확인. 개별 봉 필터링 방식 포기
- **새 전략 파일 생성 금지**: 355개 이상 추가 금지
- **합성 데이터 실험 금지**: 반드시 `--csv-dir data/historical` 사용

### 핵심 메트릭 (Cycle 339 확정)

| 지표 | Cycle 338 | Cycle 339 | 변화 |
|------|-----------|-----------|------|
| roc_ma_cross Sharpe | 0.32 | **-0.43** | -0.75 ↓↓ (레짐필터 역효과→롤백) |
| roc_ma_cross Trades | ~57 | 18 | -68% (필터로 신호 차단) |
| price_cluster Sharpe | 0.84 | **0.87** | +0.03 ↑ (슬리피지 개선 효과) |
| frama Sharpe | 0.19 | **0.24** | +0.05 ↑ |
| 1h PASS 수 | 0/20 (18연속) | **0/20 (19연속)** | — |
| Bundle OOS PASS | 5/5 | **5/5** | 유지 ✅ |

> ⚠️ PAPER_SIM_REGIME_FILTER 빈 집합으로 롤백됨. 슬리피지 임계값 0.03은 유지.

### 핵심 메트릭 (Cycle 338: MAX_HOLD 분리 아키텍처, 유지)

| 구분 | max_hold_candles | 설정 위치 |
|------|-----------------|---------|
| 1h paper_sim | 48봉 (48시간) | `paper_simulation.py`: `max_hold_candles_override=48` |
| 4h Bundle OOS | 24봉 (96시간=4일) | `BacktestEngine` 기본값 `MAX_HOLD_CANDLES=24` |
| 기타(테스트 등) | 24봉 | `BacktestEngine` 기본값 |

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: real CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows, 갭 없음)
- ETH/SOL: synthetic CSV (data/historical/synthetic/) — NaN 없음, OHLC 정상
- Bundle OOS: `--csv-dir data/historical` 필수 (합성 데이터 run은 리포트 덮어쓰기 방지됨)
- Paper simulation 1h: **20 전략** × 8 windows → 약 13분 소요 (BTC only)

### BUNDLE_STRATEGY_INIT_PARAMS 현재 설정 (Cycle 339 변경 없음)
- `vwap_cross: {}` ← 기본 파라미터
- `supertrend_multi: {atr_threshold=0.5, atr_threshold_max=1.5, ema_filter=True, confidence_filter=True, rsi_ob_filter=True, rsi_ob_threshold=80, trend_confirm_bars=2, cmf_confirm=False}` ← 고정
- `order_flow_imbalance_v2: {"trend_span": 20}` ← 최적 확정 (delta_window=10 기본값)

### BUNDLE_STRATEGY_OVERRIDES 현재 설정 (Cycle 330 변경 없음)
- `cmf: {"min_wfe": 0.4, "sharpe_decay_max": 0.40}`
- `supertrend_multi: {"min_oos_trades": 3, "max_oos_sharpe_std": 3.0, "regime_transition_is_min": 2.0}`
- `order_flow_imbalance_v2: {"regime_transition_is_min": 2.0, "min_oos_trades": 3}`
- `vwap_cross: {"min_oos_trades": 3, "is_negative_regime_max": -2.0, "bear_oos_max": 1.0}` ← 고정
- `value_area: {"regime_transition_is_min": 2.0, "min_oos_trades": 5, "is_negative_regime_max": -1.4}` ← 유지

### PAPER_SIM_STRATEGY_PARAMS 현재 설정 (Cycle 339 변경 없음)
- `value_area: {"vol_filter_mult": 0.5}` (1h paper_sim에서 제외됨)
- `wick_reversal: {"min_volatility": 0.001, "vol_mult": 0.6}`
- `relative_volume: {"rvol_buy_sell": 1.2}`
- `momentum_quality: {"quality_score_buy_threshold": 0.8, "consistency_buy_threshold": 0.3}`
- `order_flow_imbalance_v2: {"trend_span": 20}` ← Cycle 337 D(ML) 복원
- `cmf: {"buy_thresh": 0.10}`

### PAPER_SIM_REGIME_FILTER 현재 설정 (Cycle 339 신규)
- `{"roc_ma_cross"}` ← TREND_UP 레짐에서만 BUY 허용 (TREND_DOWN/RANGING/HIGH_VOL 차단)
- 근거: PASS W1(TREND_UP=45.5%), W2(41.0%) vs FAIL W3~W8(21~32%)
- Cycle 340 검증 후 확장(frama 등) 또는 철수 결정

### 윈도우별 성능 분석 (Cycle 338 F(리서치) 결과, TP=3.5 기준)

| Window | Market | price_cluster | roc_ma_cross |
|--------|--------|---------------|--------------|
| W1 | bull | Sharpe=-0.55 ❌ | Sharpe=4.39 ✅ |
| W2 | bull | Sharpe=-0.05 ❌ | Sharpe=3.51 ✅ |
| W3 | bear | Sharpe=-0.12 ❌ | Sharpe=0.20 ❌ |
| W4 | bear | Sharpe=0.62 ❌ | Sharpe=-0.45 ❌ |
| W5 | sideways | Sharpe=0.98 ❌ | Sharpe=-3.91 ❌ |
| W6 | sideways | Sharpe=3.17 ✅ | Sharpe=0.28 ❌ |
| W7 | bull | Sharpe=0.94 ❌ | Sharpe=0.26 ❌ |
| W8 | bull | Sharpe=2.23 ✅ | Sharpe=-2.25 ❌ |

- 레짐 의존성: price_cluster ↔ late sideways/bull | roc_ma_cross ↔ early strong bull only
- roc_ma_cross W5 -3.91: 횡보장 whipsaw → TREND_UP 필터 적용 (Cycle 339 D(ML)) 효과 Cycle 340 확인
