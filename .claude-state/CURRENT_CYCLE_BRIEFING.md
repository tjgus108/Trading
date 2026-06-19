# Current Cycle Briefing

_Cycle 329 | 2026-06-19 | D(ML) + E(실행) + F(리서치)_

## 완료된 작업

### D(ML): roc_ma_cross RSI 필터 제거

- `src/strategy/roc_ma_cross.py` v3 → v4:
  - BUY 조건에서 `rsi_val < 70` 제거 (Cycle 328 분석: BTC 1h에서 차단 0건)
  - SELL 조건에서 `rsi_val > 30` 대칭 제거
  - ROC_MIN_ABS=0.3% 유지
- Paper Sim 결과: rank3 (return=+0.09%, Sharpe=-0.41, 2/8) ← Cycle 328 대비 미세 악화
  - RSI 제거 효과: BUY 신호 증가 없음 (BUY에선 원래 0% 차단), SELL 미세 영향 있었던 듯
  - 2/8 consistency 유지 → ROC_MIN_ABS 0.1% 하향은 Cycle 330으로 이연

### E(실행): detect_series() pandas 3.x 버그 수정 (핵심 발견)

- **발견**: `pd.Series(regimes, dtype=str)` → pandas 3.x에서 벡터화 enum 비교 실패
  - `series == MarketRegime.TREND_UP` 항상 0 반환 (TREND_UP=0.0%)
  - Cycle 328에서 추가된 regime_filter=True가 실질적으로 ALL BUY 차단했음
- **수정**: `pd.Series(regimes, index=df.index, dtype=object)` → 비교 정상화
  - 수정 후 TREND_UP coverage: 31.3% (window별 정상 분포)
- **positional_scaling 비교 결과** (수정 후):
  - No-filter: 1/8 PASS (W3: Sharpe=2.793), avg=-0.491
  - Regime-filter: 1/8 PASS (W3: Sharpe=2.331), avg=-0.633
  - **결론**: EMA alignment이 이미 강한 방향 필터 → regime_filter 추가 효과 제한적

### F(리서치): roc_ma_cross 1h vs 4h 신호 빈도 분석

- BTC 1h 실제 CSV 분석 (1500 bars/window, 8 windows):
  - cross_above: 57/window
  - ROC>0.3% + EMA50 통과: 35.5 signals/window
  - ROC>0.1% + EMA50 통과: 37.1 signals/window (ROC 완화 효과 제한적)
- 4h 시뮬 분석 (1h→4h 리샘플, 600 bars/fold, 5 folds):
  - cross_above: 23.2/fold, ROC>0.3%+EMA50: 14.6 signals/fold
- **결론**: 1h가 4h보다 신호 2.4배 많음 → 4h 이동이 신호 빈도 해결책 아님
  - 진짜 병목: EMA50 필터(29.7% 차단) > ROC_MIN_ABS(11.4% 차단)
  - ROC_MIN_ABS 0.1% 하향의 실제 기대 효과: +6.5 signals/window (37.1 vs 35.5)

## 시뮬레이션 결과

- **테스트**: 8413 passed, 23 skipped (회귀 없음)
- **Paper Sim BTC 1h**: 0/20 PASS (9사이클 연속 전멸)
  - rank1: price_cluster (+2.19%, Sharpe=0.34, 1/8)
  - rank2: positional_scaling (+1.97%, Sharpe=0.00, 1/8)
  - rank3: roc_ma_cross (+0.09%, Sharpe=-0.41, 2/8)
- **Bundle OOS BTC 4h**: 5/5 PASS (9사이클 연속!)
  - rank1: order_flow_imbalance_v2 (avg OOS Sharpe=4.345, std=0.907)
  - rank2: supertrend_multi (avg=3.892, std=1.239)
  - rank3: value_area (avg=3.069, std=0.085) ← std 최저 안정
  - rank4: vwap_cross (avg=3.047, std=1.437)
  - rank5: cmf (avg=2.508, std=1.888)

## 다음 사이클 (330 mod 5 = 0): A(품질) + C(데이터) + F(리서치)

- **A(품질)**: roc_ma_cross ROC_MIN_ABS 0.3%→0.1% 실험 (PF 1.5+ 유지 확인 필수)
- **C(데이터)**: detect_series() 버그 수정 후 regime_filter WFO 실제 동작 검증 테스트 추가
- **F(리서치)**: Paper Sim 0/20 PASS 근본 원인 분석 (수수료 0 시뮬로 비용 효과 분리)
