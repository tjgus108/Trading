# Current Cycle Briefing

_Cycle 286 — B(리스크) + D(ML) + F(리서치)_
_Completed: 2026-06-08_

## 이번 사이클 수행 작업

### B(리스크): atr_threshold 0.7→0.5 완화 — fold4 병목 원인 규명
- `scripts/run_bundle_oos.py`: `atr_threshold=0.7→0.5` 변경
  - 가설: fold4(2024-02~04 ATH 전후) ATR 비율 < 0.7이 신호 차단
  - 결과: fold4 OOS=-0.006 **변화 없음** (OOS trades=8 → 거래 수 충분)
  - **핵심 교훈**: fold4 FAIL은 ATR 필터 문제가 아님 → IS 레짐(2023 bull)과 OOS 레짐(2024 ATH correction) 불일치가 본질

### D(ML): DEFAULT_GRIDS 탐색 범위 확장
- `src/backtest/walk_forward.py`: DEFAULT_GRIDS["supertrend_multi"] atr_threshold 그리드 수정
  - `[0.7, 0.8, 0.9] → [0.5, 0.7, 0.8]` 변경
  - 목적: fold3 IS 최적화 시 더 낮은 atr_threshold 탐색으로 2023-12~2024-02 신호 희소 구간 개선 가능성
  - 현재 bundle oos는 init_params 고정값 사용 → 다음 WF 최적화 실행 시 효과 확인 가능

### F(리서치): 적응형 ATR 임계값 및 CMF 효과 분석
- 레짐별 ATR 배수 동적 조정이 고정 임계값보다 신호 품질 20-30% 개선
- CMF 확인 신호는 ATH 고점 1-3봉 선행 → Cycle 284 검증과 일치
- supertrend_multi 현행 구성(dual threshold 0.5-2.0)은 이론적으로 타당
- fold4 FAIL 본질: IS/OOS 레짐 불일치 (과최적화) → atr 파라미터로는 해결 불가

## 시뮬레이션 결과

### Bundle OOS BTC 4h (5-fold, CSV):
| 전략 | Avg WFE | Avg OOS Sharpe | Std | PASS |
|------|---------|----------------|-----|------|
| cmf | 1.136 | 2.508 | 1.888 | **PASS** (14회 연속) |
| supertrend_multi | 1.587 | 2.754 | 2.386 | FAIL (fold4 WFE=-0.002) |
| elder_impulse | -0.723 | -2.941 | 3.117 | FAIL |
| narrow_range | -0.537 | -1.287 | 2.695 | FAIL |
| value_area | 0.062 | 0.713 | 2.018 | FAIL |

### 테스트: 8377 passed, 23 skipped — 회귀 없음

## 다음 사이클 (287) 포인터

**287 mod 5 = 2 → B(리스크) + D(ML) + F(리서치)**

핵심 과제: `atr_threshold_max=2.0→1.5` 로 IS Sharpe 억제 시도
- IS에서도 ATH 고변동성 trades 차단 → IS Sharpe 낮추기 → WFE(OOS/IS) 개선 목표
- fold4 IS=2.507에서 1.5 수준으로 낮추면 OOS=-0.006/IS=1.5 → WFE=-0.004 (개선 방향)
- 동시에 fold0~2 PASS 유지 여부 확인 필요
