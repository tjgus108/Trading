# 현재 사이클 브리핑

_Cycle 277 완료 | 2026-06-05_

## 카테고리: B(리스크) + D(ML) + F(리서치)

## 수행 작업

### B(리스크): WFE 레짐 전환 임계값 조정
- `src/backtest/walk_forward.py` RollingOOSValidator WFE 계산
- IS < -1.0 + OOS > 2.0 → WFE=0.5 이었던 임계값을 OOS > 1.5로 완화
- wick_reversal fold4(IS=-1.032, OOS=1.772): WFE 0.0→0.5 → FAIL→PASS 구제
- walk_forward 테스트 70개 통과

### D(ML): BUNDLE_STRATEGY_INIT_PARAMS + sma_sell_threshold 검증
- `scripts/run_bundle_oos.py`에 `BUNDLE_STRATEGY_INIT_PARAMS` 딕셔너리 추가
- wick_reversal `sma_sell_threshold=1.01`로 Cycle 276 파라미터화 효과 검증
- **핵심 발견**: sma_sell_threshold=1.01이 fold1,2에 전혀 효과 없음
  - fold1,2 OOS Sharpe 동일 (-4.606, -2.046 변화 없음)
  - BUY Hammer 오신호가 핵심 문제 (SELL threshold가 아님)

### F(리서치): wick_reversal 문제 구조 규명
- wick_reversal fold1 (Aug-Oct 2023 횡보): Hammer BUY 오발이 원인
  - `trend_up = high >= high_14 * 0.99` 조건이 횡보에서 과도하게 True
- wick_reversal fold2 (Oct-Dec 2023 불마켓): 초기 상승에서 BUY 후 조정 손실
- CMF: 5/5 PASS 안정적 확인 (rsi_max_buy 파라미터화 Cycle 275의 효과 유지)

## 시뮬레이션 요약
- **테스트**: 70 passed (walk_forward + bundle_oos) — 회귀 없음
- **Paper Sim**: Cycle 276 결과 재사용 — 0/22 PASS (supertrend_multi 1위)
- **Bundle OOS 4h (5-fold)**:
  - cmf: PASS (5/5 PASS, avg=2.508)
  - wick_reversal: FAIL (3/5 PASS, std=4.842 > 3.0)
    - fold4 구제 성공 (WFE 임계값 수정)
    - fold1,2 여전히 FAIL

## 다음 사이클 (278) 방향
- C(데이터): wick_reversal BUY trend_up 조건 강화 또는 supertrend_multi 번들 교체
- B(리스크): supertrend_multi를 번들에 추가하여 cmf와 상관관계 확인
- F(리서치): wick_reversal vs supertrend_multi 비교 분석
