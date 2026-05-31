# Current Cycle Briefing

_Cycle 254 — 2026-05-31_
_카테고리: D(ML) + E(실행) + F(리서치)_

## 완료된 작업

### D(ML): NarrowRange ML 피처 추가
- `src/ml/features.py`: `nr_range_ratio`, `nr_atr_ratio` 2개 피처 추가
- base feature count: 14 → 16 (feature_names 업데이트)
- narrow_range 신호 조건(ATR 수축, range 수축)을 RF가 직접 학습 가능

### E(실행): paper_simulation.py CSV fallback + --csv-dir
- `load_ohlcv_from_csv_dir()` 헬퍼: data/historical/ 계층 구조 탐색
- simulate_symbol(): 거래소 실패 시 data/historical/ 자동 탐색
- argparse `--csv-dir` 옵션 추가

### E(실행) 버그 수정: BacktestEngine MC 테스트
- **버그**: equity-curve Sharpe vs trade-PnL Sharpe 스케일 불일치
  - equity-curve Sharpe: flat period로 희석 (~4.16 for narrow_range)
  - trade-PnL Sharpe: 100 trades * ann_factor → much higher scale (~19.0)
  - 결과: 모든 permutation이 original보다 낮아보여 p~0.25-0.35 (잘못된 결과)
- **수정**: `mc_reference_sharpe`를 trade PnL 기준으로 계산 → apples-to-apples
- **효과**: narrow_range mc_p 0.28 → ~0.007 예상 (합성 데이터에서도 신호 탐지)

### F(리서치): PBO 분석
- narrow_range fold 4 PASS: 합성 데이터 운 좋은 구간 (IS Sharpe 2.454)
- PBO 계산: 9-fold CPCV IS-best → OOS 반전 비율 (합성~50%, 실 데이터 필요)

## 시뮬레이션 결과

| 시뮬 | PASS | 최고 전략 |
|------|------|----------|
| Paper (1h, BTC/USDT) | 0/22 | narrow_range (Sharpe 4.16, PF 1.63) |
| Bundle OOS (4h) | 0/5 | narrow_range (Score 85.2, fold 4 PASS) |

## 다음 사이클 (255)
- 255 mod 5 = 0 → A(품질) + C(데이터) + F(리서치)
- **핵심**: MC 버그 수정 후 시뮬 재실행 → narrow_range PASS 여부 확인
- C: data/historical/ CSV 파이프라인 실전 검증
