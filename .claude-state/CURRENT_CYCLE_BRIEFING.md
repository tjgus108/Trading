# Current Cycle Briefing

_Cycle 341 | 2026-06-21 | B(리스크) + D(ML) + F(리서치)_

## 완료된 작업

### B(리스크): price_cluster W5 구조적 FAIL 확인 + 손실 스케일링 추적 추가

분석:
- W5 OOS (2023-11-27~2024-01-26): volatility=0.054 (낮은 변동성)
- CLT=0 시 Sharpe=1.458, PF=1.314 → FAIL (PF<1.5)
- CLT=5(현재) 시 Sharpe=1.298, PF=1.281 → FAIL
- CLT=7 시 Sharpe=1.382, PF=1.299 → FAIL
- **결론**: W5 FAIL은 구조적 — 낮은 변동성에서 price_cluster가 PF≥1.5 달성 불가. 손실 스케일링이 결정 요인 아님
- W6 PASS는 CLT 무관하게 유지 (더 높은 volatility=0.104)

코드 개선 (`src/backtest/engine.py`):
- `BacktestResult`에 `loss_scale_half_count`, `loss_scale_full_count` 필드 추가
- `run()`에서 75%/50% 스케일 적용 횟수 추적 → 손실 스케일링 영향도 정량화 가능

### D(ML): IS end-state→OOS 상관관계 정량화 + is_sharpe 컬럼 추가

roc_ma_cross 8개 윈도우 분석:

| Window | IS_end | IS_Sharpe | OOS_Sharpe | Result |
|--------|--------|-----------|------------|--------|
| W1 | TREND_UP | -0.49 | 4.69 | PASS |
| W2 | TREND_UP | -0.20 | 3.41 | PASS |
| W3 | RANGING | -0.16 | 0.10 | FAIL (PF) |
| W4 | RANGING | -0.58 | -0.71 | FAIL |
| W5 | RANGING | +0.19 | -2.98 | FAIL |
| W6 | RANGING | -0.06 | 1.25 | FAIL (PF=1.30) |
| W7 | RANGING | -0.27 | -0.16 | FAIL |
| W8 | TREND_UP | -0.41 | -1.59 | FAIL (OOS=RANGING) |

- **핵심 패턴**: IS=RANGING이면 OOS FAIL 확실. IS=TREND_UP이지만 OOS=RANGING이면 FAIL (W8)
- IS 음수 Sharpe + IS_end=TREND_UP → OOS 강한 양전 (W1, W2)

코드 개선 (`scripts/paper_simulation.py`):
- `window_results`에 `is_sharpe` 필드 추가 (VERBOSE_WINDOWS 활성화 시 계산)
- verbose-windows 테이블에 `IS_Sh` 컬럼 추가

### F(리서치): TREND_UP 비율 분석 (ADX=22 vs 18)

BTC 1h CSV 전구간 (12000 행):
- ADX=22: TREND_UP=31.3%, RANGING=47.3%, TREND_DOWN=21.4%
- ADX=18: TREND_UP=34.3%, RANGING=41.6%, TREND_DOWN=24.1% (+3.0% TREND_UP)
- ADX=20: TREND_UP=32.9%, RANGING=44.4%

**결론**: ADX 임계값 완화로 TREND_UP +3% 획득 가능하나 구조적 RANGING 지배(41~47%) 유지. 임계값 변경만으로는 roc_ma_cross 문제 해결 불가 → 현재 ADX=22 유지

## 시뮬레이션 결과 (이번 사이클)

- Paper Sim BTC 1h: **0/20 PASS** (21사이클 연속)
  - rank1: price_cluster (Sharpe=0.87, 1/8) ← 유지
  - rank2: roc_ma_cross (Sharpe=0.34, 2/8) ← 유지
- Bundle OOS BTC 4h: **5/5 PASS** ✅ (cmf, order_flow_imbalance_v2, supertrend_multi, vwap_cross, value_area)

## 테스트

- pytest backtest engine: **56 passed** (회귀 없음, loss_scale 추적 추가 후)
