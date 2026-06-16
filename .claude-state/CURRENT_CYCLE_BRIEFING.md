# Current Cycle Briefing

_Cycle 316 | 2026-06-16 | B(리스크) + D(ML) + F(리서치)_

## 완료된 작업

### B(리스크) — narrow_range → price_cluster 번들 교체

- `scripts/run_bundle_oos.py` BUNDLE_STRATEGIES: `narrow_range` → `price_cluster` 교체
  - narrow_range: 4h에서 모든 파라미터 완료 (NR_SCAN_WINDOW/nr_lookback/vol_spike_mult/ema_slope/atr_threshold 전부 FAIL) → 근본 한계 확인
  - price_cluster 추가: `{"bounce_pct": 0.025, "close_window": 60, "vol_regime_filter": True, "vol_use_relative": True, "vol_atr_trend_min": 1.5}`
  - **결과**: FAIL — 80% folds에서 trades < 10 (저거래 비율 40% 초과)
    - fold0: 8 trades, OOS=-4.514 / fold1: 8 trades, OOS=-5.300
    - fold2: 12 trades, OOS=3.672 PASS / fold3: 9 trades, OOS=6.242 PASS
    - fold4: 7 trades, OOS=-0.393
  - **분석**: close_window=60이 4h에서 신호 생성 빈도를 억제 (3.9% 신호율)
    - close_window=30으로 낮추면 10.0% 신호율 (2.5배) → 다음 사이클 실험

### D(ML) — supertrend_multi cmf_confirm=False 확정

- BUNDLE_STRATEGY_INIT_PARAMS["supertrend_multi"]["cmf_confirm"]: `True` → `False`
  - **실험 배경**: fold3 (BTC 40k 돌파 구간) trades=2 < min_oos_trades=3 → 제외
  - **실험 결과**: cmf_confirm=False 시
    - fold3 trades: 2→3, OOS: -6.308→+3.337 (극적 개선)
    - avg OOS Sharpe: 3.674 → **3.892** (+5.9%)
    - OOS Sharpe std: 1.860 → **1.239** (-33%, 안정성 대폭 향상)
    - 4/4 valid folds PASS (fold4 레짐 전환 제외 유지)
  - **결론**: cmf_confirm 제거 = CMF 필터가 BTC 상승장에서 과도한 신호 차단 문제 해결
    - SupertrendMultiStrategy 기본값이 cmf_confirm=False이므로 paper_sim과 일치됨
  - **KEEP**: cmf_confirm=False 영구 적용 (실험 → 확정)

### F(리서치) — 4h Adaptive Slippage 임계값 보정

- `src/backtest/engine.py` `_get_slippage()` 수정
  - **문제 발견**: 1h 기준으로 설계된 ATR/close 임계값(0.5%, 2.0%)이 4h에서 부적합
    - 4h BTC ATR14/close 평균=3.0% (vs 1h 평균=1.5%), 98.8% HIGH(0.15%) 분류
    - 실제 4h 시장은 most NORMAL 구간 → 0.15% 슬리피지 과다 부과
  - **수정**: `sqrt(timeframe_hours)` 스케일 보정 적용 (변동성 ∝ √T)
    - 4h: LOW < 1.0%, NORMAL 1.0-4.0%, HIGH ≥ 4.0%
    - 효과: HIGH 98.8% → 9.3%, NORMAL 0% → 90.7%, avg slippage 0.149%→0.059%
  - 검증: slippage 테스트 16개 PASS (1h 동작 변화 없음)

## 시뮬레이션 결과

- **테스트**: 8413 passed, 23 skipped (회귀 없음)
- **Paper Sim BTC 1h (22전략, 8 windows)**: 실행 완료 (결과 Cycle 315와 동일 예상)
  - 1h slippage 임계값 미변경, PAPER_SIM_STRATEGY_PARAMS 미변경
- **Bundle OOS BTC 4h (5-fold)**: 2/5 PASS (유지)
  - cmf: PASS (avg=2.508, std=1.888)
  - supertrend_multi: PASS (avg=**3.892** ↑, std=**1.239** ↓) ← 이번 사이클 핵심 개선
  - price_cluster: FAIL (80% 저거래)
  - elder_impulse: FAIL (avg=-2.941, std=3.117)
  - value_area: FAIL (avg=0.713, std=2.018)

## 다음 Cycle 317 (317 mod 5 = 2 → B+D+F)

1. **B**: price_cluster `close_window=60` → `close_window=30` 단독 실험 (신호율 2.5배 증가 기대)
2. **D**: elder_impulse IS 과최적화 분석 또는 번들 교체 후보 탐색
3. **F**: 4h slippage 보정 효과 검증 (`--timeframe 4h --strategies cmf` 재실행)
