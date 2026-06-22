# Next Steps

_Last updated: 2026-06-22 (Cycle 346 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 346

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 344 | D+E+F | BundleOOSResult.avg_oos_mdd 필드화, SlipH% window진단, 슬리피지 무관 확인, 0/20 24연속 |
| 345 | A+C+F | WFO그리드 vol_regime_filter 버그수정, ema20_slope 동기화, ccxt타이밍버그수정, 0/20 25연속 |
| 346 | B+D+F | RANGING 스톱 바운드 추가, frama signal_thresh 파라미터화, 0/20 26연속 |

### 🎯 Cycle 347 작업 방향 (347 mod 5 = 2 → C(데이터) + E(실행) + F)

#### C(데이터): price_cluster vol_regime_filter 효과 검증 (D 연속)

- **배경**: Cycle 345 WFO 그리드 vol_regime_filter=True 추가 → 다음 paper_sim에서 효과 확인
  - price_cluster AvgTrades가 41에서 줄어드는지 (RANGING 진입 차단)
  - Sharpe std 1.10이 감소하는지 (W5/W6 분산 감소)
- **작업**:
  - paper_simulation.py 실행 후 price_cluster W5/W6 비교
  - vol_atr_trend_min 최적값 분석 (1.5 vs 2.0 vs 2.5 중 어느 값이 선택되는지)

#### E(실행): frama signal_thresh 효과 검증

- **배경**: Cycle 346 F(리서치)에서 frama signal_thresh 파라미터화
  - signal_thresh=[0.5, 1.0, 1.5] WFO 탐색 추가 (27조합)
  - 다음 시뮬에서 signal_thresh 최적값 확인
- **작업**:
  - paper_simulation.py 실행 후 frama OOS 결과 비교
  - signal_thresh=1.5 (엄격) vs 0.5 (완화) 중 어느 게 OOS에서 유리한지 분석

#### F(리서치): RANGING 리스크 바운드 효과 분석

- **배경**: Cycle 346 B(리스크)에서 RANGING stop 바운드 추가 (floor=1.5, ceiling=2.5)
  - paper_simulation.py에서 RANGING 레짐 감지 시 stoploss 변화 여부 확인
- **작업**:
  - RANGING 환경 손절 피격률 분석 (데이터 있으면)
  - adaptive_stop_multiplier RANGING 실제 반영 여부 점검

### ⚠️ 주의 사항 (Cycle 347)

- **max_hold_candles_override=48 유지**: paper_simulation.py engine에 고정
- **BUNDLE_STRATEGY_OVERRIDES 임계값 변경 금지**: 1h 연간화 기준 캘리브레이션됨
- **atr_multiplier_tp=3.5 유지**: Cycle 338 실험으로 확정
- **2단계 손실 스케일링 유지**: threshold=5 기준 2→75%, 5→50%
- **슬리피지 임계값 변경 금지**: Cycle 344 확인 → HIGH% < 1%, 동적 조정 불필요
- **PAPER_SIM_REGIME_FILTER**: `set()` (빈 집합) — 유지
- **새 전략 파일 생성 금지**: 355개 이상 추가 금지
- **합성 데이터 실험 금지**: 반드시 `--csv-dir data/historical` 사용

### 핵심 메트릭 (Cycle 346 확정)

| 지표 | Cycle 345 | Cycle 346 | 변화 |
|------|-----------|-----------|------|
| price_cluster Sharpe | 0.87 | **TBD** | — |
| price_cluster Consistency | 1/8 | **TBD** | — |
| roc_ma_cross Sharpe | 0.34 | **TBD** | — |
| roc_ma_cross Consistency | 2/8 | **TBD** | — |
| 1h PASS 수 | 0/20 (25연속) | **TBD** | — |
| Bundle OOS PASS | 5/5 | **5/5** | 유지 ✅ |
| Bundle OOS avg_mdd | cmf5.2/OFI3.4/ST2.2/VA1.9% | **cmf5.2/OFI3.4/ST2.2/VA2.7/VA1.9%** | 유지 |

### Cycle 346 코드 변경 요약

| 파일 | 변경 내용 |
|------|----------|
| `src/risk/manager.py` | `_REGIME_STOP_BOUNDS`에 RANGING 항목 추가 (floor=1.5, ceiling=2.5) |
| `src/strategy/frama.py` | `signal_thresh` 파라미터 추가 (gap_pct 진입 임계값 파라미터화) |
| `src/backtest/walk_forward.py` | frama 그리드에 `signal_thresh: [0.5, 1.0, 1.5]` 추가 (27조합) |

### E(실행) 슬리피지 진단 결과 (Cycle 344 확정)

| 지표 | BTC 1h 전체 평균 |
|------|----------------|
| LOW 레짐 비율 | 0% (모든 전략) |
| NORMAL 레짐 비율 | 92~100% |
| HIGH 레짐 비율 | 0~8% (최대 dema_cross 8.3%) |
| W5 vol=1.39% → 레짐 | NORMAL (0.5~3% 범위) |
| 동적 슬리피지 조정 필요성 | **없음** — HIGH%가 무시할 수준 |

### IS/OOS 레짐 진단 결과 (Cycle 340 신규, 유지)

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

### 핵심 메트릭 (Cycle 338: MAX_HOLD 분리 아키텍처, 유지)

| 구분 | max_hold_candles | 설정 위치 |
|------|-----------------|---------|
| 1h paper_sim | 48봉 (48시간) | `paper_simulation.py`: `max_hold_candles_override=48` |
| 4h Bundle OOS | 24봉 (96시간=4일) | `BacktestEngine` 기본값 `MAX_HOLD_CANDLES=24` |
| 기타(테스트 등) | 24봉 | `BacktestEngine` 기본값 |
