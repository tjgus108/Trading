# Current Cycle Briefing

_Cycle 271 완료 | 2026-06-04_

## 이번 사이클 요약

**카테고리**: B(리스크) + D(ML) + F(리서치)

### 완료된 작업

| # | 파일 | 변경 내용 | 결과 |
|---|------|---------|------|
| 1 | `src/strategy/wick_reversal.py` | EMA 방향 필터 추가 후 롤백 | 역효과 확인 (avg 1.200→-0.416), 복원 |
| 2 | `src/backtest/walk_forward.py` | avg_wfe 윈소라이즈 (±3.0 클리핑) | avg_wfe 집계 지표 강인화 |
| 3 | `src/backtest/walk_forward.py` | DEFAULT_GRIDS cmf_1h 추가 | 미래 1h cmf WFO 기반 제공 |

### Bundle OOS 결과 (Cycle 271 — Cycle 270 동일)

| Strategy | Folds PASS | Avg Sharpe | std | Overall |
|----------|-----------|-----------|-----|---------|
| **cmf** | **5/5** | 2.508 | 1.888 | **✅ PASS** |
| wick_reversal | 1/5 | -0.416 | 6.995 | ❌ FAIL (EMA filter applied) |
| wick_reversal (reverted) | ~3/5 | ~1.200 | ~4.842 | ❌ FAIL (std > 3.0) |

> **Note**: wick_reversal EMA filter를 추가했으나 결과가 악화되어 즉시 롤백

### EMA 필터 실패 원인

- fold1 (Aug-Oct 2023, bull run): EMA20>EMA50 → Hammer 허용 → 5 trades 모두 실패 (Sharpe=-9.992)
- EMA 방향 필터는 wick_reversal의 근본 문제(저거래 폴드 + 레짐 민감성)를 해결 못함
- 올바른 접근: **ADX < 25 필터** (트렌드 강도가 낮을 때만 reversal 신호 허용)

### 다음 사이클 (272) 방향

- **B(리스크)**: ADX < 25 필터 추가 (wick_reversal 레인지 마켓 한정)
  - enrich_indicators()에 adx14 컬럼 추가 필요
  - fold1 Aug-Oct 2023: ADX > 25 예상 → Hammer 차단
- **D(ML)**: paper_simulation.py에 PAPER_SIM_STRATEGY_PARAMS 추가 (cmf 1h: period=60)
- **F(리서치)**: ADX 효과 fold별 사전 분석

### 테스트 상태

- **8369 passed, 23 skipped** (413s) — 회귀 없음
- **70 walk_forward tests passed** (129s) — avg_wfe 변경 후 정상
