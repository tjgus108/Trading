# Current Cycle Briefing

_Cycle 330 | 2026-06-19 | A(품질) + C(데이터) + F(리서치)_

## 완료된 작업

### A(품질): roc_ma_cross ROC_MIN_ABS 0.3%→0.1% 실험 및 즉시 되돌림

- `src/strategy/roc_ma_cross.py` v4 → v5:
  - `_ROC_MIN_ABS = 0.3 → 0.1` 실험 후 Paper Sim 결과 확인
  - roc_ma_cross Sharpe: -0.41 → -0.74 (악화), trades: 42
  - **즉시 되돌림**: `_ROC_MIN_ABS = 0.3` 복원
  - docstring에 실험 결과 및 결론 기록 (오신호 증가 확인)
- **결론**: ROC 필터는 오신호 방어선 — 완화 시 신호 품질 저하. EMA50이 주 차단요인이지만 ROC 필터도 필요

### C(데이터): detect_series() 버그 수정 검증 테스트 3개 추가

- `tests/test_walk_forward.py` 끝에 3개 테스트 추가:
  1. `test_detect_series_returns_trend_up_on_uptrend()`:
     - 강한 상승 추세 데이터 (daily drift=+0.3%)에서 TREND_UP 30%+ 반환 검증
     - dtype=object 보장 확인 (pandas 3.x StringDtype 추론 방지)
     - Cycle 329 버그 수정 회귀 방지 테스트
  2. `test_annotate_regime_adds_column()`:
     - `_annotate_regime()` 반환 df에 `_regime_trend_up` bool 컬럼 존재 검증
     - 원본 df 불변 확인 (in-place 수정 방지)
     - 상승 추세 데이터에서 True 비율 30%+ 확인
  3. `test_regime_filter_true_blocks_buy_on_ranging()`:
     - `_RegimeFilterStrategy`: `_regime_trend_up=False` → BUY → HOLD 변환 검증
     - `_regime_trend_up=True` → BUY 통과 검증
     - "레짐 필터" reasoning 포함 확인

### F(리서치): Paper Sim 0/20 PASS 수수료 근본 원인 정량 분석

- 기존 Paper Sim 데이터로 수수료 impact 추정:
  - 비용 구조: fee 0.055%/leg + slippage 0.05%/leg = 왕복 0.21%
  - price_cluster (45 trades): 수수료 9.45% → gross return ≈ +11.64% (+2.19% + 9.45%)
  - positional_scaling (36 trades): 수수료 7.56% → gross ≈ +9.53%
  - roc_ma_cross (42 trades): 수수료 8.82% → gross ≈ +7.96%
  - volume_breakout (78 trades): 수수료 16.38% → gross ≈ +14.33%
- **결론**: 가설 B 확인 — 수수료가 0/20 PASS 주범
  - 가설 A (데이터 불리) 기각: gross return 양수 → 알파는 존재함
  - Bundle OOS 4h PASS 이유: 거래수 5~17/fold → 낮은 수수료 부담 (1.05%~3.57%)
- **Cycle 331 방향**: 1h 신호 선택성 강화 (거래수 절반 → 수수료 절반)

## 시뮬레이션 결과

- **테스트**: 8416 passed, 23 skipped (+3 신규, 회귀 없음)
- **Paper Sim BTC 1h**: 0/20 PASS (10사이클 연속 전멸)
  - rank1: price_cluster (+2.19%, Sharpe=0.34, 1/8)
  - rank2: positional_scaling (+1.97%, Sharpe=0.00, 1/8)
  - rank4: roc_ma_cross (-1.02%, Sharpe=-0.74, 2/8) ← 실험값, 복원 완료
- **Bundle OOS BTC 4h**: 5/5 PASS (10사이클 연속!)
  - rank1: order_flow_imbalance_v2 (avg OOS Sharpe=4.345, std=0.907)
  - rank2: supertrend_multi (avg=3.892, std=1.239)
  - rank3: value_area (avg=3.069, std=0.085) ← std 최저 안정
  - rank4: vwap_cross (avg=3.047, std=1.437)
  - rank5: cmf (avg=2.508, std=1.888)

## 다음 사이클 (331 mod 5 = 1): B(리스크) + D(ML) + F(리서치)

- **B(리스크)**: 1h 고빈도 전략 수수료 burden 감소 — min_hold_bars 파라미터 추가 검토
- **D(ML)**: price_cluster WFO 최적화 (거래수 20~25/window 목표, PF≥1.5)
- **F(리서치)**: fee=0 시뮬레이션 실행 (paper_simulation.py에 --fee-rate 인자 추가)
