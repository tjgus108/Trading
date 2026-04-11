# Next Steps

## Cycle 12 - Category B: Risk Management ✅ COMPLETED

**Task:** Correlation Throttle — 상관관계 급증 시 포지션 자동 축소

**Findings:** `src/risk/circuit_breaker.py`와 `src/analysis/strategy_correlation.py`에 이미 Correlation Throttle 로직이 구현되어 있었음.
테스트 헬퍼 `_make_tracker_with_high_corr()`의 버그 발견 및 수정.

**Bug Fixed:**
- `tests/test_circuit_breaker.py` `_make_tracker_with_high_corr()` (line 166-176): 모든 신호를 `Action.BUY`만 반복 → 분산=0 → Pearson 상관계수 NaN → throttle 미탐지.
  - 수정: 혼합 패턴 `[BUY, BUY, SELL, BUY, HOLD]` 사용으로 분산 확보 → r=1.0 정상 감지.

**Test Results:** 17/17 passed ✅ (기존 2 FAILED → 0 FAILED)

---

## Cycle 12 - Category D: ML & Signals ✅ COMPLETED

**Task:** 피처 누수 단위 테스트 추가 + 레이블 생성 버그 수정

**Bug Fixed:**
- `src/ml/features.py` `_compute_labels()` (line 154-163): 마지막 `forward_n` 행의 레이블이 NaN 대신 0(HOLD)으로 설정돼 `dropna()`를 통과하는 버그.
  - 수정: 초기값 `np.nan`으로 변경, `fwd_ret.isna()` 위치만 NaN 유지 → `build()` dropna()가 마지막 forward_n 행 제거

**Tests Added (`tests/test_phase_c_ml.py` +3):**
1. `test_future_price_change_does_not_affect_past_features` — 미래 행 수정 시 이전 피처 불변 검증
2. `test_labels_use_future_data_not_features` — 마지막 forward_n 행이 학습 X에서 제외되는지 검증 (버그 탐지 테스트)
3. `test_rolling_features_use_prior_bars_only` — 중간 행 극단값 삽입 시 이전 rolling 피처 불변 검증

**Test Results:** 28 passed, 7 skipped ✅ (기존 0 regressions)

---

## Cycle 11 - Category C: Data & Infrastructure ✅ COMPLETED

**Task:** FeatureBuilder 데이터 누출(leakage) 검증 및 수정

**Files Modified:**

1. `/home/user/Trading/src/ml/features.py` (lines 68-134)
   - **Look-ahead bias 고정**: 모든 rolling/EMA 계산에 shift(1) 추가
   - RSI z-score: `rsi_shifted = df["rsi14"].shift(1)` 기준으로 정규화
   - Volatility: `log_ret.shift(1).rolling(20).std()` 적용
   - EMA features: `close.shift(1)` 기준으로 계산
   - Volume MA: `volume.shift(1).rolling(20).mean()` 적용
   - Donchian: `high.shift(1)`, `low.shift(1)` 기준으로 계산
   - **효과**: 현재 바 데이터가 신호 계산에 포함되지 않음 → 실시간 거래 시 일관성 보장

2. `/home/user/Trading/src/ml/lstm_model.py` (lines 162-221)
   - **Scaler 누출 고정**: StandardScaler fit을 train 데이터에만 적용
   - **변경 순서**:
     1. 시퀀스 생성 (정규화 전): `seq_X_raw, seq_y = self._prepare_sequences(feat_df.values, y)`
     2. train/val/test 분할
     3. Scaler fit on train ONLY: `scaler.fit(train_flat)` 
     4. 각 구간 transform: `scaler.transform(seq_X_tr/val/te_raw)`
   - **효과**: 미래 통계(val/test mean/std)가 과거 학습에 누수되지 않음

3. `/home/user/Trading/tests/test_phase_c_ml.py` (line 116)
   - Added `test_no_lookahead_bias_in_features()`: shift(1) 적용 검증
   - Features가 유한값(inf/nan 없음)인지 확인

**Test Results:**
- test_phase_c_ml.py: 25 passed (신규 1개 포함) ✅
- Full test suite: 5849 passed ✅

---

## Next Pending Tasks

- Cycle 12: 다른 데이터 소스 견고성 (News/Sentiment/Onchain) 재검증
- Cycle 13: 모델 성능 검증 (Feature importance bias 확인)
- 옵션 2: MAR (Minimum Acceptable Return) 기반 평가 — Sortino 계산 시 MAR 파라미터 추가

---

## Cycle 13 - AnomalyDetector 강화 ✅ COMPLETED

**Task:** 크립토 특화 거래량 급증 감지 추가

**Files Modified:**
1. `/home/user/Trading/src/monitoring/anomaly_detector.py`
   - `__init__` line 56: `volume_surge_multiplier` 파라미터 추가 (default 3.0)
   - `detect()` lines 84-87: `_detect_volume_surge` 호출 추가
   - lines 163-189: `_detect_volume_surge()` 메서드 신규 추가
     - rolling mean 대비 3배 이상 → 이상치 (MEDIUM)
     - 4.5배 이상 → HIGH severity

2. `/home/user/Trading/tests/test_anomaly_detector.py` (신규)
   - 5개 테스트: 5 passed ✅

**Test Results:** 5/5 passed
