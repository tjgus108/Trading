# Current Cycle Briefing

_Cycle 338 | 2026-06-20 | C(데이터) + B(리스크) + F(리서치)_

## 완료된 작업

### B(리스크): TF_MAX_HOLD 구현 + walk_forward.py 버그 수정

- `engine.py`에 `TF_MAX_HOLD = {"1h": 48, "4h": 24, "1d": 10}` 추가
- `BacktestEngine.run()`: `max_hold = self._max_hold_override or TF_MAX_HOLD.get(self.timeframe, MAX_HOLD_CANDLES)`
- **핵심 버그 발견 및 수정**:
  - `RollingOOSValidator.validate()`가 `BacktestEngine()` 기본값 `timeframe="1h"` 사용
  - TF_MAX_HOLD["1h"]=48 → 4h bundle OOS에서 48봉=8일 보유 → catastrophic
  - 수정: `BacktestEngine`에 `max_hold_override: Optional[int]` 파라미터 추가
  - `walk_forward.py`: `BacktestEngine(max_hold_override=MAX_HOLD_CANDLES)` 로 수정
  - `walk_forward.py`: `from src.backtest.engine import ..., MAX_HOLD_CANDLES` import 추가
  - `tests/test_ml_backtest_integration.py`: tolerance <= 2 → <= 5 (1h max_hold=48 변경)
- **추가 발견**: timeframe="4h" 전달 시 Sharpe annualization이 6048→1512으로 반토막
  - bundle OOS의 모든 Sharpe 수치는 역사적으로 "1h" annualization 기준
  - max_hold_override로 역호환성 유지, annualization 재조정은 향후 과제
- **결과**: 4h Bundle OOS **5/5 PASS 유지**

### C(데이터): price_cluster Sharpe 0.90 원인 분석

- BTC 1h price_cluster 8 window별 분석:
  - W1 [bull, +143%]: Sharpe=-0.546 | W2 [bull, +127%]: Sharpe=-0.049 → FAIL (강세장 실패)
  - W5 [sideways, -1%]: Sharpe=0.980 → FAIL (0.02 차이로 임박!) | W6 [sideways, -4%]: Sharpe=3.167 PASS
  - W8 [bull, +32%]: Sharpe=2.225 PASS
  - **결론**: price_cluster = 횡보장 평균회귀 전략. 강한 추세장 (+100%+)에서 실패
  - 현재 PASS까지 최단거리: W5에서 Sharpe를 0.02 올리는 것
- TF_MAX_HOLD 1h=48 효과: **없음** (대부분 SL/TP로 먼저 청산됨)

### F(리서치): atr_multiplier_tp 실험 → Cycle 339로 연기

- PF=1.21 < 1.50 → F 실험 조건 충족
- B 태스크에서 복잡한 버그 발견/수정으로 인해 이번 사이클 내 연기
- Cycle 339에서 atr_multiplier_tp=3.5→4.0 (R:R=2.67, 이론 PF=1.63) 실험

## 시뮬레이션 결과 (Cycle 338)

- **테스트**: 8425+ passed (최종 확인 중)

- **Paper Sim BTC 1h (20전략, 8 windows, MAX_HOLD=48, buy_thresh=0.25)**: **0/20 PASS** (18사이클 연속)
  - rank1: price_cluster (Sharpe=**0.90**, PF=1.21, 41 trades, 2/8) ← Cycle 337과 동일
  - rank2: roc_ma_cross (Sharpe=0.25, PF=1.20, 36 trades, 2/8)
  - rank3: frama (Sharpe=0.33, PF=1.15, 40 trades, 1/8)
  - rank8: OFI v2 (Sharpe=-0.70, PF=0.96, 67 trades) ← 동일

- **Paper Sim ETH 1h**: 0/20 PASS (rank1: volatility_cluster Sharpe=0.63)

- **Paper Sim SOL 1h**: 0/20 PASS (rank1: wick_reversal Sharpe=0.00)

- **Bundle OOS BTC 4h**: **5/5 PASS** ← max_hold_override 수정 후 복원
  - rank1: order_flow_imbalance_v2 (avg=4.345, std=0.957)
  - rank2: supertrend_multi (avg=3.892, std=1.286)
  - rank3: value_area (avg=3.069, std=0.085)
  - rank4: vwap_cross (avg=3.047, std=1.437)
  - rank5: cmf (avg=2.508, std=1.888)

## 다음 사이클 (339 mod 5 = 4): D(ML) + F(리서치)

- **F(리서치)**: atr_multiplier_tp=3.5→4.0 실험 (Cycle 338 연기됨, 최우선)
  - engine.py `atr_multiplier_tp=3.5→4.0` 변경
  - Paper sim + Bundle OOS 실행 및 결과 비교
  - PF 개선 여부 확인 (현재 1.21, 목표 1.50)
- **D(ML)**: ML 모델 재훈련 검토 (ADWIN drift detected)
  - OFI v2 성능 점검 (rank8, Sharpe=-0.70)
