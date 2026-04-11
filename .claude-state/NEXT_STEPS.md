# Next Steps

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

**Key Insights (Cycle 7 연구 반영):**
- **Look-ahead bias**: rolling/ewm은 현재 바 포함 → shift(1) 필수
- **Scaler fit 순서**: 전체 데이터 fit ❌ → train만 fit ✅
- **Walk-forward**: 시계열 순서 유지 + 각 구간별 독립 전처리

---

## Previous Cycles

[생략: Cycle 1-11 A,B,C 완료 기록]

## Next Pending Tasks

- Cycle 12: 다른 데이터 소스 견고성 (News/Sentiment/Onchain) 재검증
- Cycle 13: 모델 성능 검증 (Feature importance bias 확인)
