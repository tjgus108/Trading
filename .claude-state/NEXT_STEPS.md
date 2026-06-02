# Next Steps

_Last updated: 2026-06-02 (Cycle 260 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 251~260

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 256 | B+D+F | atr_tp 3.0→3.5, mom_quality_score 피처, **SOL 8/22 PASS** |
| 257 | B+D+F | HIGH conf 1.5→1.2, REGIME 피처, **ETH 5/22 PASS** |
| 258 | C+B+F | ETH/SOL GARCH CSV, HIGH conf 1.2→1.35 |
| 259 | D+E+F | **GARCH OU 평균회귀**, `--symbols`/`--csv-dir` 옵션, Bundle OOS CSV |
| 260 | A+C+F | MC 1000 perms, ETH GARCH max→5955, market_state 태그, CMF 레짐 분석 |

### 🎯 Cycle 261 작업 방향 (261 mod 5 = 1 → B(리스크) + D(ML) + F(리서치))

#### B(리스크): CMF 변동성 필터 추가 검토
- Cycle 260 분석: CMF는 고변동성/횡보 구간에서 실패
- 검토 방향: ATR 기반 변동성 필터 (변동성 높을 때 신호 억제)
- 단, 전략 파일 수정 금지 → risk 모듈에서 포지션 사이즈 조절로 구현 검토
- `src/risk/volatility_filter.py` 또는 DrawdownMonitor의 get_size_multiplier 연계

#### D(ML): momentum_quality 성과 개선 방향 탐색
- ETH momentum_quality: score=75.8점, Sharpe=0.73, PF=1.17 — near-PASS
- SOL momentum_quality: score=75.0점, Sharpe=0.26 — 상승 필요
- 분석 방향: ETH에서 momentum_quality가 PASS하는 1/8 window 파악
  - 해당 window의 시장 특성 분석 (bull/sideways?)
  - market_state 태그 (Cycle 260 추가)를 활용하여 다음 실행 시 확인

#### F(리서치): BTC window 레짐 개선
- w4-w7 (Oct 2023-Mar 2024): 강세장 구간 → 모든 전략 FAIL
- 방향성 트렌드 추종 전략이 없는 것이 핵심 문제
- QUALITY_AUDIT.csv에서 trend-following 전략 성과 확인
- 레짐별 전략 배분 검토 (bull → trend, bear → mean-reversion)

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: 실 binance CSV 사용 가능 (data/historical/binance/BTCUSDT/1h.csv)
- ETH/SOL: GARCH OU CSV 사용 (ETH: 680-5955, SOL: 12-247)
- Bundle OOS: `--csv-dir data/historical` 필수 (미지정 시 합성 데이터로 9 fold)

### 핵심 메트릭 (Cycle 260)
- 테스트: 8369 passed, 23 skipped (변경 없음)
- Paper Sim BTC: 0/22 (top: price_cluster 69.2점, supertrend_multi 67.6점)
- Paper Sim ETH: 0/22 (top: momentum_quality 75.8점, Sharpe=0.73)
- Paper Sim SOL: 0/22 (top: momentum_quality 75.0점, Sharpe=0.26)
- Bundle OOS BTC 4h (실CSV): 0/5 PASS (CMF std=1.888 > 1.5, 동일)
- ETH GARCH: max=11655 → **5955** (Cycle 260 개선)

### 주요 코드 변경 이력 (Cycle 260)
1. `src/backtest/engine.py` — MC_N_PERMUTATIONS 500→1000
2. `scripts/paper_simulation.py` — market_state/market_return 태그 추가
3. `scripts/generate_garch_csv.py` — ETH ou_theta=0.008, anchor=2.0x, max=4.0x
