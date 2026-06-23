# Next Steps

_Last updated: 2026-06-23 (Cycle 347 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 347

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 345 | A+C+F | ema20_slope 동기화 버그 수정, price_cluster WFO 그리드 수정, 0/20 25연속 |
| 346 | B+D+F | RANGING 매크로 중립 판별(DrawdownMonitor), narrow_range grid 0.0005 추가, 0/20 26연속 |
| 347 | B+D+F | RANGING 매크로 manager.py 실전 연동(evaluate→set_ranging_macro_neutral), 0/20 27연속 |

### 🎯 Cycle 348 작업 방향 (348 mod 5 = 3 → C(데이터) + B(리스크) + F(리서치))

#### C(데이터): ETH/SOL 합성 데이터 슬리피지 레짐 이상 진단

- **배경**: Cycle 347 F에서 ETH 합성 데이터 dema_cross High% = 94.9% 발견 (BTC: 8.3%)
- **작업**:
  - `data/historical/synthetic/ETHUSDT/1h.csv` High/Low/Close 스프레드 비율 분석
  - adaptive_slippage 계산 로직이 High 레짐으로 분류하는 조건 확인
  - 필요시 합성 데이터 생성 스크립트의 HL 범위 보정

#### B(리스크): paper_simulation.py ↔ DrawdownMonitor 연결 여부 확인

- **배경**: Cycle 347 B에서 manager.py evaluate()에 RANGING 매크로 연동 완료
  - 그러나 paper_simulation.py가 RiskManager+DrawdownMonitor를 사용하는지 미확인
- **작업**:
  - paper_simulation.py에서 RiskManager 생성 여부 확인
  - DrawdownMonitor가 연결되지 않으면: 연결 추가 or 별도 ema50_slope 계산 필요 여부 문서화

#### F(리서치): 4h paper_sim 타당성 분석

- **배경**: 27연속 1h 0/20 FAIL, 4h Bundle OOS 5/5 PASS → 4h 전환 타당성 평가
- **작업**:
  - `data/historical/binance/BTCUSDT/4h.csv` 존재 여부 확인
  - paper_simulation.py `--timeframe 4h` 지원 여부 확인 (현재 1h 고정인지)
  - 4h resample 가능하면 소규모 테스트 실행, 결과로 4h 전환 결정

### ⚠️ 주의 사항 (Cycle 348)

- **max_hold_candles_override=48 유지**: paper_simulation.py engine에 고정
- **BUNDLE_STRATEGY_OVERRIDES 임계값 변경 금지**: 1h 연간화 기준 캘리브레이션됨
- **atr_multiplier_tp=3.5 유지**: Cycle 338 실험으로 확정
- **2단계 손실 스케일링 유지**: threshold=5 기준 2→75%, 5→50%
- **슬리피지 임계값 변경 금지**: Cycle 344 확인 → HIGH% < 1%, 동적 조정 불필요
- **PAPER_SIM_REGIME_FILTER**: `set()` (빈 집합) — 유지
- **새 전략 파일 생성 금지**: 355개 이상 추가 금지
- **합성 데이터 실험 금지**: 반드시 `--csv-dir data/historical` 사용

### 핵심 메트릭 (Cycle 347 확정)

| 지표 | Cycle 346 | Cycle 347 | 변화 |
|------|-----------|-----------|------|
| price_cluster Sharpe | 0.87 | **0.87** | 유지 |
| price_cluster Consistency | 1/8 | **1/8** | 유지 |
| roc_ma_cross Sharpe | 0.34 | **0.34** | 유지 |
| roc_ma_cross Consistency | 2/8 | **2/8** | 유지 |
| 1h PASS 수 | 0/20 (26연속) | **0/20 (27연속)** | — |
| Bundle OOS PASS | 5/5 | **5/5** | 유지 ✅ |
| Bundle OOS OFI Sharpe | 4.345 | **4.345** | 유지 |

### Cycle 347 코드 변경 요약

| 파일 | 변경 내용 |
|------|----------|
| `src/risk/manager.py` | evaluate()에 RANGING 레짐 시 ema50_slope→set_ranging_macro_neutral() 자동 연동 추가 |
| `tests/test_risk_manager.py` | _make_candle_df_with_ema_slope() 헬퍼 + TestRangingMacroNeutralManagerIntegration 4개 테스트 추가 |

### Cycle 346 코드 변경 요약 (참고)

| 파일 | 변경 내용 |
|------|----------|
| `src/risk/drawdown_monitor.py` | RANGING 매크로 중립 판별 추가 (set_ranging_macro_neutral, 클래스 상수 2개, _ranging_macro_neutral 상태) |
| `src/backtest/walk_forward.py` | narrow_range DEFAULT_GRIDS ema_slope_min_buy [0.0,0.001,0.002]→[0.0,0.0005,0.001] |
| `tests/test_risk.py` | RANGING 매크로 중립 판별 테스트 4개 추가 |

### F(리서치) BTC 1h 레짐별 특성 (Cycle 346 확정)

| 레짐 | 캔들 비율 | avg return/봉 | ema50 slope mean | 중립(<0.0005) 비율 |
|------|---------|------------|----------------|----------------|
| TREND_UP | 31.3% | +0.0250% | +0.001391 | 14.4% |
| TREND_DOWN | 21.4% | +0.0377% | -0.001266 | 18.9% |
| RANGING | 47.3% | +0.0217% | +0.000110 | 45.1% |

**핵심 결론**: RANGING에서만 neutral macro 비율 45.1% 확보 → mean-reversion 조건 충족

### EMA slope 차단 비율 분석 (Cycle 346 D(ML) 확정)

| ema_slope_min_buy 임계값 | 전체 BUY pass | RANGING BUY pass | 판단 |
|------------------------|-------------|----------------|------|
| 0.0 (필터 없음) | 54.7% | 50.8% | 기본값 |
| 0.0005 | 44.3% | 38.2% | ✅ 중간 균형점 |
| 0.001 | 34.5% | 27.1% | ⚠️ RANGING 과도 차단 |
| 0.002 | ~25% | ~20% | ❌ 지나치게 엄격 (제거됨) |

### E(실행) 슬리피지 진단 결과 (Cycle 344 확정)

| 지표 | BTC 1h 전체 평균 |
|------|----------------|
| HIGH 레짐 비율 | 0~8% (최대 dema_cross 8.3%) |
| 동적 슬리피지 조정 필요성 | **없음** |

### Bundle OOS avg_oos_mdd (Cycle 346 확정, 변화 없음)

| 전략 | avg_oos_mdd |
|------|-------------|
| cmf | 5.2% |
| order_flow_imbalance_v2 | 3.4% (Cycle346: 일부 fold 재계산) |
| supertrend_multi | 2.2% |
| vwap_cross | 2.7% |
| value_area | 1.9% |

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

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: real CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows, 갭 없음)
- ETH/SOL: synthetic CSV (data/historical/synthetic/) — NaN 없음, OHLC 정상
- Bundle OOS: `--csv-dir data/historical` 필수 (합성 데이터 run은 리포트 덮어쓰기 방지됨)
- Paper simulation 1h: **20 전략** × 8 windows → 약 6분 소요 (BTC only)
