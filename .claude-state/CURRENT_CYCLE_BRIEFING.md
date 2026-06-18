# Current Cycle Briefing

_Cycle 327 | 2026-06-18 | B(리스크) + D(ML) + F(리서치)_

## 완료된 작업

### B(리스크): adx_threshold 25.0→22.0 완화

- `src/strategy/regime.py` `MarketRegimeDetector.__init__` adx_threshold 25.0→22.0
  - Wilder 기준(25.0) → 완화(22.0)로 TREND 감지 민감도 향상
  - TREND_UP/DOWN 판정 빈도 증가 기대 (ADX 22-25 구간 신호 캡처)
  - 도큐스트링 업데이트: "ADX > 25" → "ADX > 22"
- 테스트: test_market_regime.py + test_walk_forward.py 85개 통과 (회귀 없음)

### D(ML): roc_ma_cross WFO 실행 → ma_period=7 역효과 확인

- BTC 1h CSV 5-fold WFO 결과:
  - best params 도출: roc_period=12, ma_period=7
  - avg OOS Sharpe +0.072 (개선: -0.35→+0.07), WFE=0.0377 (낮음)
  - 핵심 문제: avg 33 trades/8 windows = 4.1 trades/window → 통계적 신뢰도 부족
- paper_simulation 적용 결과:
  - ma_period=7: roc_ma_cross rank2→rank6 (Sharpe -0.35→-0.69) — 역효과
  - 즉시 되돌림 (paper_simulation.py 변경 없음)
- **결론**: EMA50 + RSI 이중 필터가 1h 신호를 과도 차단 → 필터 완화가 핵심 과제

### F(리서치): positional_scaling 1/8 PASS 분석

- positional_scaling 전략 분석 (rank2, +1.97%, Sharpe=0.00, 1/8):
  - 조건: EMA20>EMA50>EMA100 + close±ATR*0.3 + 양봉
  - **1/8 PASS 원인**: 레짐 필터 없음 → 횡보(2023 Q1-Q2)/하락(2022) 구간 BUY 진입
  - PASS 윈도우: 2023 Q4 불마켓에서만 EMA alignment 지속 유효
  - 개선 제안: MarketRegimeDetector(adx_threshold=22.0) TREND_UP 필터 추가

## 시뮬레이션 결과 (Cycle 327)

### Paper Sim BTC 1h (8 windows, 20전략)
- **0/20 PASS** (Cycle 326과 동일)
- rank1: price_cluster (return=+2.19%, Sharpe=0.34, 1/8)
- rank2: positional_scaling (return=+1.97%, Sharpe=0.00, 1/8)
- rank6: roc_ma_cross (return=-1.10%, Sharpe=-0.69, 1/8) ← ma_period=7 역효과

### Bundle OOS BTC 4h (5-fold, --csv-dir data/historical)
- **5/5 PASS** (7사이클 연속 유지)
- order_flow_imbalance_v2: PASS (avg=4.345, std=0.907, rank1)
- supertrend_multi: PASS (avg=3.892, std=1.239, rank2)
- value_area: PASS (avg=3.069, std=0.085, rank3)
- vwap_cross: PASS (avg=3.047, std=1.437, rank4)
- cmf: PASS (avg=2.508, std=1.888, rank5)

## 현재 시스템 상태

- 테스트: **8409 passed, 17 skipped** (회귀 없음)
- Paper Sim: 0/20 PASS (1h, 8 windows) — rank1 price_cluster
- Bundle OOS: **5/5 PASS** (7사이클 연속)
- 코드 변경: regime.py adx_threshold 25→22 (회귀 없음)

## 다음 사이클 (328) 핵심 작업

- **Cycle 328** = 328 mod 5 = 3 → C(데이터) + B(리스크) + F(리서치)
  - C: adx_threshold=22.0 효과 검증 (TREND_UP 빈도 측정)
  - B: positional_scaling 레짐 필터 실험 (TREND_UP 조건 추가)
  - F: roc_ma_cross EMA/RSI 필터 완화 방향 분석 (trades 4.1→10+/window 목표)
