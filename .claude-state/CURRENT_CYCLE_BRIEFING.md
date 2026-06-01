# Current Cycle Briefing

_Cycle 259 — 2026-06-01_
_카테고리: D(ML) + E(실행) + F(리서치)_

## 완료된 작업

### D(ML): GARCH CSV OU 평균회귀 추가
- `scripts/generate_garch_csv.py` 개선:
  - Ornstein-Uhlenbeck 평균회귀: `ou_correction = ou_theta * (log(anchor) - log(price))`
  - ETH: ou_theta=0.003, anchor=3000(=1200×2.5), price_max_mult=5.0
  - SOL: ou_theta=0.004, anchor=75(=15×5.0), price_max_mult=20.0
  - 2차 안전장치: 가격 한계 초과 시 강제 드리프트 반전
- 개선 결과:
  - ETH: 1196→3708, max=11655 (이전 1193→42518, max=63478) ✓
  - SOL: 15→99, max=247 — 2023 실제 범위 재현 ✓

### E(실행): roc_ma_cross SOL 분석
- BacktestEngine R:R = 3.5/1.5 = 2.33:1 확인
- PF=1.43 for ~38% win_rate, PF=1.5 for ~39.2% — 차이 1.2% (합성 데이터 범위 내)
- 결론: 실거래소 데이터 검증 전 파라미터 변경 보류

### F(리서치): 인프라 개선
- `scripts/run_bundle_oos.py`: `load_csv_and_resample()` + `--csv-dir` 인자
  - 1h CSV → target timeframe 리샘플링 지원
- `scripts/paper_simulation.py`: `--symbols` 인자 추가 (병렬 실행)

## 시뮬레이션 결과 (Cycle 259)
- Paper Sim BTC 1h (CSV): 0/22 PASS
  - Top: price_cluster(sharpe=0.40), supertrend_multi(0.43)
- Paper Sim ETH (OU-GARCH): **0/22 PASS**
  - momentum_quality **Sharpe 1.30**, volatility_cluster 1.31 (OU 개선 효과 확인)
  - 미PASS 원인: 8-window consistency 50% 미달
- Paper Sim SOL (OU-GARCH): **0/22 PASS**
  - top: htf_ema Sharpe 0.51 (SOL 범위 안정화되었으나 전략 성과 낮음)
- Bundle OOS BTC 4h (실CSV): 0/5 PASS
  - CMF: score=93.6, OOS Sharpe=2.508, std=1.888>1.5 (FAIL)
  - wick_reversal: 0거래 (저빈도 전략, min_oos_trades=10 미달)

## 테스트: 8369 passed, 23 skipped

## 다음 Cycle 260 (260 mod 5 = 0 → A+C+F)
- A: ETH 8-window 실패 패턴 분석 (momentum_quality sharpe 1.30이 어느 window에서 실패?)
- C: GARCH ou_theta/anchor_mult 미세조정 (ETH max < 6000 목표)
- F: CMF Bundle OOS 실패 fold 레짐 분석
