# Current Cycle Briefing

_Cycle 314 | 2026-06-15 | D(ML) + E(실행) + F(리서치)_

## 완료된 작업

### D(ML) — vol_spike_mult 실험 및 파라미터화

- `src/strategy/narrow_range.py` `vol_spike_mult` 파라미터화 (클래스 상수 → __init__ 인자)
  - **실험**: `vol_spike_mult=0.5` (거래량 스파이크 없어도 진입 허용)
  - **결과**: trades 동일 (8,10,10,9,10), fold4 크게 악화 (1.71→-1.656), std=3.480
  - **결론**: VOL_SPIKE_MULT는 binding constraint 아님 → 역효과 → 기본값(1.0) 복원
  - 파라미터 기능은 유지 (향후 다른 배율 실험 가능)

### E(실행) — paper_simulation.py --strategies 필터

- `scripts/paper_simulation.py` `--strategies` CLI 인자 추가
  - `STRATEGY_FILTER: Optional[List[str]] = None` 모듈 변수
  - `load_pass_strategies()`에 필터 적용
  - **목적**: supertrend_multi, cmf 4h 단독 실행 가능 (전체 22전략 대비 빠른 검증)
  - **사용법**: `python3 scripts/paper_simulation.py --timeframe 4h --csv-dir data/historical --strategies supertrend_multi`

### F(리서치) — Bundle OOS 5-fold 재실행 및 cmf PASS 확인

- Bundle OOS `--csv-dir data/historical` (5-fold, BTC 4h, 2023-2024): **2/5 PASS** ← 첫 복수!
  - **cmf: PASS** ← 신규 발견!
    - 5/5 folds PASS, avg OOS Sharpe=2.508, std=1.888, Consistency=100%
    - 이전 Cycle 313 (9-fold, 2022 포함): 4/9 PASS → 2022 제거로 5/5로 개선
  - **supertrend_multi: PASS** ← 재확인
    - 3/3 valid PASS (fold3 저거래 제외, fold4 레짐전환 제외), avg OOS Sharpe=3.674
  - narrow_range (vol_spike_mult=0.5): FAIL → 역효과

## 시뮬레이션 결과

- **테스트**: 8413 passed, 23 skipped (회귀 없음)
- **Paper Sim BTC 1h (8 windows)**: 0/22 PASS
  - rank1: price_cluster (Sharpe=0.59), rank2: supertrend_multi (Sharpe=0.32, +5.26%)
- **Bundle OOS BTC 4h (5-fold)**: 2/5 PASS
  - cmf avg=2.508 (PASS), supertrend_multi avg=3.674 (PASS)

## 다음 Cycle 315 (315 mod 5 = 0 → A+C+F)

1. **A**: narrow_range ATR_THRESHOLD 0.95→1.05 실험 (마지막 binding constraint 후보)
2. **C**: cmf 4h paper_sim 단독 실행 (첫 PASS 검증)
3. **F**: cmf + supertrend_multi 조합 검토 (두 전략 모두 4h PASS)
