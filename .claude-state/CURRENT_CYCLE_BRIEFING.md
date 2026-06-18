# Current Cycle Briefing

_Cycle 326 | 2026-06-18 | B(리스크) + D(ML) + F(리서치)_

## 완료된 작업

### B(리스크): MarketRegimeDetector HIGH_VOL 임계값 재보정

- `src/strategy/regime.py` `MarketRegimeDetector.__init__` vol_multiplier 1.5→2.0
  - 기존: 현재 ATR이 20-bar 평균의 1.5배 초과 시 HIGH_VOL
  - 변경: 2.0배 초과 시에만 HIGH_VOL (BTC 정상 ATR% 2-4% 감안)
  - 효과: TREND_UP/DOWN 판정 빈도 증가, HIGH_VOL 과다 판정 해소
- 테스트: test_market_regime.py 32개 모두 통과 (회귀 없음)

### D(ML): roc_ma_cross 1h WFO 그리드 추가

- `src/strategy/roc_ma_cross.py`: `roc_period`, `ma_period` 생성자 파라미터 추가
  - 기존: `_ROC_PERIOD=12`, `_MA_PERIOD=3` 모듈 상수 고정
  - 변경: `ROCMACrossStrategy(roc_period=12, ma_period=3)` 기본값 유지, WFO 탐색 가능
  - `_min_rows = max(roc_period + ma_period, 20)` 동적 계산
- `src/backtest/walk_forward.py`:
  - `DEFAULT_GRIDS["roc_ma_cross"]` 추가: `roc_period=[10,12,15]`, `ma_period=[3,5,7]`
  - `optimize_roc_ma_cross()` 함수 추가
- 테스트: test_roc_ma_cross.py 전체 통과

### F(리서치): HMM vs EMA slope 레짐 감지 비교

- SSRN 2023-2024 논문 기반 HMM 접근 평가:
  - BTC 2-state/3-state HMM 피팅 우수, 전환 확률 행렬이 추세 지속성 캡처
  - 단점: EM 수렴 불안정, forward-looking 바이어스 → 실시간 부적합
- **결론**: 현재 EMA slope + ADX 기반 + vol_multiplier 강화가 최선
  - HMM은 오프라인 fold 사후 분석용으로 검토 가능 (구현 보류)
  - adx_threshold 25→22 완화로 TREND 감지 민감도 향상도 차선책 (Cycle 327 검토)

## 시뮬레이션 결과 (Cycle 326)

### Paper Sim BTC 1h (8 windows, 20전략)
- **0/20 PASS** (Cycle 325와 동일)
- rank1: price_cluster (return=+2.19%, Sharpe=0.34, 1/8)
- rank2: roc_ma_cross (return=+0.38%, -0.35 Sharpe, **2/8** consistency — 최고!)
- rank3: positional_scaling (return=+1.97%, PF=1.18, 1/8)
- roc_ma_cross FAIL 원인: Sharpe=-0.35 < 1.0, PF=1.12 < 1.5

### Bundle OOS BTC 4h (5-fold, --csv-dir data/historical)
- **5/5 PASS** (6사이클 연속 유지)
- order_flow_imbalance_v2: PASS (avg=4.345, std=0.907, rank1)
- supertrend_multi: PASS (avg=3.892, std=1.239, rank2)
- value_area: PASS (avg=3.069, std=0.085, rank3)
- vwap_cross: PASS (avg=3.047, std=1.437, rank4)
- cmf: PASS (avg=2.508, std=1.888, rank5)

## 현재 시스템 상태

- 테스트: **8413 passed, 23 skipped** (회귀 없음)
- Paper Sim: 0/20 PASS (1h, 8 windows) — rank1 price_cluster
- Bundle OOS: **5/5 PASS** (6사이클 연속)
- 코드 변경: regime.py + roc_ma_cross.py + walk_forward.py (회귀 없음)

## 다음 사이클 (327) 핵심 작업

- **C(데이터)** + **B(리스크)** + **F**: 327 mod 5 = 2 → B+D+F
  - B: adx_threshold 25→22 완화 실험 (TREND 감지 민감도) 또는 regime 로직 정밀 분석
  - D: roc_ma_cross WFO 실행 (새 그리드 사용) — 파라미터 탐색
  - F: positional_scaling 1/8 PASS 분석 (PASS 구간 패턴 파악)
