# Current Cycle Briefing

_Cycle 315 | 2026-06-16 | A(품질) + C(데이터) + F(리서치)_

## 완료된 작업

### A(품질) — narrow_range ATR_THRESHOLD 파라미터화 및 1.05 실험

- `src/strategy/narrow_range.py` `atr_threshold` 파라미터화 완료
  - `__init__`에 `atr_threshold: float = 0.95` 추가, `self._atr_threshold` 사용
  - **실험**: `atr_threshold=1.05` (ATR 필터 거의 폐기 수준으로 완화)
  - **결과**: trades 크게 증가 (8-10 → 13-21), BUT avg OOS Sharpe=-2.118, std=3.889
    - IS Sharpe 80% 음수 (4/5 folds) — 전략 자체 불안정
    - PASS: fold0(1.981), fold4(2.128) / FAIL: fold1(-5.622), fold2(-3.625), fold3(-5.451)
  - **결론**: ATR 완화 → 오신호 폭발 → 역효과 → 기본값(0.95) 복원
  - **인사이트**: narrow_range 4h 모든 파라미터 실험 완료 → 근본 한계 → 번들 교체 검토 필요
    - 실험 이력: NR_SCAN_WINDOW, nr_lookback, vol_spike_mult, ema_slope, atr_threshold 전부 FAIL

### C(데이터) — cmf 4h paper_simulation BTC-특이성 확인

- `python3 scripts/paper_simulation.py --timeframe 4h --csv-dir data/historical --strategies cmf`
  - BTC 4h: 1/8 PASS, avg Sharpe=0.74 → FAIL (consistency 12.5%)
  - ETH 4h: 0/8, avg Sharpe=-4.26 → FAIL
  - SOL 4h: 0/8, avg Sharpe=-7.47 → FAIL
  - **결론**: cmf는 BTC 전용 전략 확인 — Bundle OOS(5/5 PASS)는 BTC 2023-2024에 특화
  - Slippage "HIGH" 99.4% → 실전 환경에서 슬리피지 영향 주의 필요

### F(리서치) — narrow_range 번들 교체 및 실전 투입 검토

- narrow_range 번들 교체 후보 정리:
  - price_cluster: paper_sim rank1 (Sharpe=0.59, 3/8, return=+4.50%) → 4h 평가 필요
  - roc_ma_cross: paper_sim rank4 (Sharpe=-0.35, 2/8, return=+0.38%) → 상대적으로 안정
  - positional_scaling: paper_sim rank3 (return=+1.97%) → Sharpe=0.00 (중립)
- cmf + supertrend_multi 2개 PASS 전략 실전 투입 조건 검토 완료
  - cmf: BTC 단독 배포만 고려 (다자산 배포 금지 확인)
  - supertrend_multi: 다자산 배포 가능성 더 높음 (3/3 valid PASS)

## 시뮬레이션 결과

- **테스트**: 8413 passed, 23 skipped (회귀 없음)
- **Paper Sim BTC 1h (22전략, 8 windows)**: 0/22 PASS
  - rank1: price_cluster (Sharpe=0.59, 3/8, return=+4.50%)
  - rank2: supertrend_multi (Sharpe=0.32, 2/8, return=+5.26%) ← 수익률 1위
  - narrow_range: rank9 (Sharpe=-0.42, 0/8, PF=0.99)
- **Paper Sim 4h cmf 단독**: 0/1 PASS (BTC=1/8, ETH=0/8, SOL=0/8)
- **Bundle OOS BTC 4h (5-fold)**: 2/5 PASS (Cycle 314 동일)
  - cmf: 5/5 PASS (avg=2.508, std=1.888)
  - supertrend_multi: 3/3 valid PASS (avg=3.674, std=1.860)
  - narrow_range (1.05 실험): FAIL (avg=-2.118, std=3.889) → 복원

## 다음 Cycle 316 (316 mod 5 = 1 → B+D+F)

1. **B**: narrow_range → price_cluster 번들 교체 실험 (4h Bundle OOS 평가)
2. **D**: supertrend_multi fold3 저거래 원인 파악 (cmf_confirm=False 임시 실험)
3. **F**: cmf BTC 슬리피지 분석 및 실전 배포 준비 검토
