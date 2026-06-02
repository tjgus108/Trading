# Current Cycle Briefing

_Cycle 260 — 2026-06-02_
_카테고리: A(품질) + C(데이터) + F(리서치)_

## 완료된 작업

### A(품질): MC 정밀도 향상 + 레짐 분석
- `src/backtest/engine.py`: MC_N_PERMUTATIONS 500→1000
  - 경계값 p-value 오분류 감소 (supertrend_multi w2: sharpe=3.23인데 mc_p=0.056으로 FAIL 사례)
- `scripts/paper_simulation.py`: window별 market_state 태그 추가
  - 종가 변화율로 bull(+5%)/bear(-5%)/sideways 분류
  - 다음 실행부터 JSON에 market_return, market_state 포함
- BTC 레짐-윈도우 매핑:
  - w1-w3 (Jul-Nov 2023): 횡보→완만 상승 → 전략 일부 PASS
  - w4-w7 (Oct 2023-Mar 2024): BTC ETF+반감기 강세 → **모든 전략 FAIL**
  - **핵심**: 비방향성 전략이 강세장 구간에서 집중 실패

### C(데이터): ETH GARCH OU 파라미터 최적화
- `scripts/generate_garch_csv.py` ETH 파라미터 변경:
  - ou_theta: 0.003 → **0.008** (강한 평균회귀)
  - ou_anchor_mult: 2.5 → **2.0** (anchor=1200×2.0=2400)
  - price_max_mult: 5.0 → **4.0** (cap=1200×4.0=4800)
- 결과: ETH max **11655 → 5955** (목표 6000 이하 달성!)
  - final: 3708 → 2433 (실제 ETH 2023 범위와 근접)
- ETH GARCH CSV 재생성 완료

### F(리서치): CMF 레짐 의존성 완전 분석
- Bundle OOS 5 fold → BTC 날짜 매핑:
  | Fold | OOS 기간 | 시장 | 결과 |
  |------|---------|------|------|
  | 0 | Jul-Sep 2023 | 횡보/약세 | FAIL (WFE=0) |
  | 1 | Oct-Dec 2023 | **강세 랠리** | **PASS** |
  | 2 | Jan-Mar 2024 | ETF 고변동성 | FAIL |
  | 3 | Feb-Apr 2024 | 반감기 피크 | FAIL |
  | 4 | Apr-May 2024 | 조정 | **PASS** |
- **CMF 패턴**: 지속적 방향성 + 저변동성에서 작동, 고변동성/횡보에서 FAIL
- OOS Sharpe std=1.888: fold간 변동 과다 = 레짐 민감성의 직접적 증거

## 시뮬레이션 결과 (Cycle 260)
- Paper Sim BTC 1h (실CSV): 0/22 PASS
  - Top: price_cluster(score=69.2), supertrend_multi(67.6), roc_ma_cross(66.3)
- Paper Sim ETH (GARCH OU): 0/22 PASS
  - Top: **momentum_quality** Sharpe=0.73 (score=75.8)
  - ETH 파라미터 변경으로 극단 가격 해소 → 이전 Sharpe 1.30에서 0.73으로 현실화
- Paper Sim SOL (GARCH OU): 0/22 PASS
  - Top: **momentum_quality** Sharpe=0.26 (score=75.0)
- Bundle OOS BTC 4h (실CSV): 0/5 PASS (CMF std=1.888>1.5 동일)

## 테스트: 8369 passed, 23 skipped (backtest+walk_forward 148 pass)

## 다음 Cycle 261 (261 mod 5 = 1 → B+D+F)
- B: CMF용 ATR 변동성 필터 → risk 모듈 연계 포지션 사이즈 조절 검토
- D: ETH momentum_quality PASS window 분석 (market_state 태그 활용)
  - Bull 구간에서만 작동하는지, 파라미터 조정 필요 여부
- F: BTC 레짐별 전략 배분 리서치 (강세/약세/횡보 맞춤 전략 조합)
