# Current Cycle Briefing

_Cycle 323 | 2026-06-17 | C(데이터) + B(리스크) + F(리서치)_

## 완료된 작업

### C(데이터) — Bundle OOS 5/5 PASS 안정성 검증

- Bundle OOS 재실행: **5/5 PASS 유지** (수치 동일 — 데이터 변동 없음)
- vwap_cross fold 구성: fold0(저거래=2<3) + fold1(bear_regime) = 40% 제외, active=[2,3,4] 안정 확인
- BTC 1h.csv: 12000 rows, 4h 환산 약 500봉, 5-fold 구성 유지

### B(리스크) — combined_exclusion_ratio 경고 추가 + connector.py 버그 수정

1. `src/backtest/walk_forward.py` `RollingOOSValidator.validate()`:
   - 카테고리별(low_trade + regime_transition + bear_regime) 합산 제외 비율 ≥40% → WARNING 로그
   - PASS/FAIL 기준은 변경 없음 (카테고리별 40% 독립 체크 유지)
   - vwap_cross 합산=40%, value_area 합산=60% — 경고 발생, 모니터링 확인

2. `src/exchange/connector.py` ccxt 경쟁 조건 버그 수정:
   - 모듈 임포트 시 `_CcxtNotSupported = ccxt.NotSupported` 사전 계산
   - `except (ccxt.NotSupported, ...)` → `except (_CcxtNotSupported, ...)` 교체
   - ccxt=None 상태에서 AttributeError 발생 방지 (pip 병렬 설치 경쟁 조건)

### F(리서치) — live_paper_trader Bundle 전략 5개로 확장

- `scripts/live_paper_trader.py` BUNDLE_PASS_PRIORITY: 3개→5개
  - 추가: value_area(rank3), vwap_cross(rank4)
- BUNDLE_PASS_WEIGHTS: OFI=0.30, ST=0.28, VA=0.16, VWAP=0.14, CMF=0.12 (rank score 비례)

## 시뮬레이션 결과

| 지표 | 결과 |
|------|------|
| 테스트 | 8413 passed, 23 skipped (회귀 없음) |
| Paper Sim (1h, 22전략) | **0/22 PASS** (기존 유지) |
| Paper Sim rank1 | supertrend_multi (return=+5.26%, Sharpe=0.32) |
| Bundle OOS (4h, 5-fold) | **5/5 PASS** (유지) |
| Bundle rank1 | OFI v2 (avg=4.345, std=0.907) |
| vwap_cross | PASS (avg=3.047, std=1.437) — 유지 |
| value_area | PASS (avg=3.069, std=0.085) — 유지 |

## 다음 사이클 (324) 핵심 과제

1. **D(ML)**: supertrend_multi 1h 파라미터 개선 (1h Sharpe=0.32 → PASS 기준 1.0 목표)
2. **E(실행)**: live_paper_trader 4h 타임프레임 지원 추가 검토 (bundle 전략은 4h OOS PASS)
3. **F(리서치)**: 레짐 기반 전략 스위칭 로드맵 구체화
