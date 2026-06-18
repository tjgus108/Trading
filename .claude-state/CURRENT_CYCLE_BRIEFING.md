# Current Cycle Briefing

_Cycle 328 | 2026-06-18 | C(데이터) + B(리스크) + F(리서치)_

## 완료된 작업

### C(데이터): adx_threshold=22.0 효과 검증

- BTC 1h CSV 5개 시간 구간 비교 (adx_threshold=25.0 vs 22.0, lookback=200):
  - Early 2023: TREND_UP +8.5% (26.5→35.0%), RANGING -10.5% ← 최대 효과
  - Q4 2023 bull: 변화 없음 (0.0%) — HIGH_VOL 이미 0%로 vol_multiplier=2.0 효과
  - Early 2024 (최근): +0.5% 미미
- **결론**: adx_threshold=22.0 변경 유효, 향후 시장에서 진가 발휘 예상

### B(리스크): regime_filter 옵션 추가

1. `src/strategy/regime.py` `MarketRegimeDetector.detect_series()` 신규 추가:
   - 전체 DataFrame 벡터화 레짐 계산 (O(n) 효율)
   - iloc[-2] 기준 미래 데이터 누출 방지
2. `src/backtest/walk_forward.py` regime_filter 옵션:
   - `_RegimeFilterStrategy` 래퍼: _regime_trend_up=False인 봉의 BUY → HOLD 변환
   - `_annotate_regime()`: IS/OOS DF에 _regime_trend_up 컬럼 추가
   - `WalkForwardOptimizer(regime_filter=True)` 지원
   - 테스트 104개 통과 (회귀 없음)

### F(리서치): roc_ma_cross 필터 영향 분석

- BTC 1h 전체 (12000 bars), potential BUY = 404개:
  - RSI<70 차단: **0% (완전 무의미)** — 크로스 시점 RSI>=70 없음
  - EMA50 차단: 29.7%
  - EMA200 차단: 33.7%
  - 모든 필터 제거해도: 8.4 signals/window (목표 30+/window 미달)
- **핵심 결론**: ROC_MIN_ABS=0.3%가 1h에서 너무 높음 → Cycle 329에서 0.1% 하향 실험

## 시뮬레이션 결과

- Paper Sim BTC 1h: **0/20 PASS** | rank1=price_cluster (+2.19%), rank2=positional_scaling (+1.97%)
- Bundle OOS BTC 4h: **5/5 PASS** (8사이클 연속) | rank1=OFI (4.345), rank2=supertrend (3.892)

## 다음 사이클 (329 mod 5 = 4): D(ML) + E(실행) + F(리서치)

- D(ML): roc_ma_cross RSI 필터 제거 + ROC_MIN_ABS 0.3→0.1% 실험
- E(실행): regime_filter=True positional_scaling WFO 실험 (1/8→2/8+ PASS 목표)
- F(리서치): roc_ma_cross 1h vs 4h 타임프레임 비교 분석
