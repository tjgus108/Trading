# Next Steps

_Last updated: 2026-06-21 (Cycle 340 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 340

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 338 | C+B+F | TP=2.5 역효과 확인(TP=3.5 확정), 2단계 손실스케일링, 윈도우별 레짐 분석, 0/20 18연속 |
| 339 | D+E+F | 레짐필터 역효과(roc_ma_cross -0.43→롤백), 슬리피지 임계값 2→3%, 0/20 19연속 |
| 340 | A+C+F | IS/OOS 레짐 진단 추가, roc_ma_cross 필터 롤백 확인(+0.34↑), 0/20 20연속 |

### 🎯 Cycle 341 작업 방향 (341 mod 5 = 1 → B(리스크) + D(ML) + F(리서치))

#### B(리스크): price_cluster W5 근접 PASS 분석 및 리스크 조정

- **배경**: Cycle 340 F(리서치) 결과: price_cluster W5(RANGING+RANGING, mkt=sideways, Sharpe=0.99)
  - 0.01 차이로 FAIL. PF도 아슬아슬 FAIL. 리스크 파라미터 조정으로 해결 가능할 수도.
  - W5 구간(Nov 2023 ~Jan 2024): 횡보장 — price_cluster 최적 환경
- **작업 방향**:
  - W5 구간 price_cluster 상세 분석: PF FAIL 원인 파악
  - kelly_sizer 또는 position sizing 미세 조정 (손실 스케일링 threshold 튜닝)
  - DrawdownMonitor의 W5 구간 영향 분석

#### D(ML): roc_ma_cross W1/W2 PASS 패턴 활용 검토

- **배경**: roc_ma_cross는 IS=TREND_UP인 구간에서만 PASS (W1: IS끝 TREND_UP + OOS=TREND_UP)
  - 현재 2/8 consistency → PASS 기준(50%) 미달
  - IS끝 레짐이 TREND_UP일 때만 전략 활성화 → paper_simulation 레벨에서 검토
- **주의**: 이전 Cycle 339에서 개별봉 레짐 필터 역효과 확인 → 봉 수준 필터 금지
  - 윈도우 수준 필터 고려: IS가 TREND_UP으로 끝나는 경우만 OOS 결과 카운트
  - 단, 이는 실제 배포에서 구현이 복잡 — 검토만 수행
- **작업**:
  - verbose-windows 활용해 roc_ma_cross W3~W8의 상세 fail reason 파악
  - IS end-state와 strategy 성과 상관관계 정량화

#### F(리서치): RANGING 지배 문제와 대응 전략 리서치

- **배경**: 분석 결과 OOS dominant regime이 RANGING인 경우가 8개 윈도우 중 6개 이상
  - MarketRegimeDetector가 TREND_UP을 너무 보수적으로 감지 (ADX>22 필요)
  - BTC 1h봉에서 TREND_UP 비율이 낮음 → roc_ma_cross는 구조적으로 불리
- **작업**:
  - detect_series()로 전체 BTC CSV TREND_UP 비율 계산
  - ADX 임계값 완화(22→18) 시 TREND_UP 비율 변화 측정
  - RANGING 지배 환경에서 효과적인 전략 특성 분석 (price_cluster 참고)

### ⚠️ 주의 사항 (Cycle 341)

- **max_hold_candles_override=48 유지**: paper_simulation.py engine에 고정
- **BUNDLE_STRATEGY_OVERRIDES 임계값 변경 금지**: 1h 연간화 기준 캘리브레이션됨
- **atr_multiplier_tp=3.5 유지**: Cycle 338 실험으로 확정
- **2단계 손실 스케일링 유지**: threshold=5 기준 2→75%, 5→50%
- **슬리피지 임계값 변경 금지**: `atr_ratio < 0.03 * tf_scale`
- **PAPER_SIM_REGIME_FILTER**: `set()` (빈 집합) — 유지
- **새 전략 파일 생성 금지**: 355개 이상 추가 금지
- **합성 데이터 실험 금지**: 반드시 `--csv-dir data/historical` 사용

### 핵심 메트릭 (Cycle 340 확정)

| 지표 | Cycle 339 | Cycle 340 | 변화 |
|------|-----------|-----------|------|
| roc_ma_cross Sharpe | -0.43 | **+0.34** | +0.77 ↑↑ (레짐필터 롤백 효과 확인) |
| roc_ma_cross Trades | 18 | 36 | +100% (신호 복구) |
| roc_ma_cross Consistency | 0/8 | **2/8** | 개선 ↑ |
| price_cluster Sharpe | 0.87 | **0.87** | 유지 |
| price_cluster Consistency | 1/8 | **1/8** | 유지 |
| 1h PASS 수 | 0/20 (19연속) | **0/20 (20연속)** | — |
| Bundle OOS PASS | 5/5 | **5/5** | 유지 ✅ |

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
- 근본 문제: 8개 윈도우 중 IS=TREND_UP인 구간은 W1, W2, W8뿐 → roc_ma_cross에 불리한 데이터 구조

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
- 윈도우 수준 레짐 매칭 방식은 Cycle 341 D(ML)에서 검토 예정
