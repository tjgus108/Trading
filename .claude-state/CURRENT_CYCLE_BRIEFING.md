# 현재 사이클 브리핑

_Cycle 276 완료 | 2026-06-05_

## 카테고리: B(리스크) + D(ML) + F(리서치)

## 수행 작업

### B(리스크): DrawdownStatus 완전성 개선
- `DrawdownStatus` 데이터클래스에 `sharpe_decay_multiplier: float = 1.0` 추가
- `update()` 반환 시 `_sharpe_decay_mult` 상태 포함
- 호출자 코드가 별도 메서드 호출 없이 status에서 직접 sharpe decay 상태 확인 가능

### D(ML): wick_reversal sma_sell_threshold 파라미터화
- `WickReversalStrategy.__init__`에 `sma_sell_threshold: float = 1.03` 추가
- Shooting Star 조건: `close < sma20 * 1.03` → `close < sma20 * self.sma_sell_threshold`
- WFO 그리드: `sma_sell_threshold: [1.01, 1.02, 1.03]`
- 목적: fold6(2023-06~08) OOS=-12.365 원인인 추세장 SELL 오신호 차단

### F(리서치): Bundle OOS 9-fold 분석
- 9-fold 구조(2022 포함)로 CMF가 이전 5-fold PASS → 현재 FAIL
- wick_reversal 5/9 folds PASS이나 fold6 극단값(-12.365)으로 std=6.085 초과
- 핵심 취약 구간: 2023-06~08 여름 불마켓 (wick_reversal SELL 오신호 집중)

## 시뮬레이션 요약
- **테스트**: 8369 passed, 23 skipped
- **Paper Sim BTC 1h**: 0/22 PASS (top: supertrend_multi +5.87%)
- **Bundle OOS 4h**: 0/5 PASS (wick_reversal avg=1.289 best, cmf avg=-0.805)

## 다음 사이클 (277)
- sma_sell_threshold 그리드 효과 검증 (fold6 개선 여부)
- CMF 9-fold 구조 분석 및 대응 방안 결정
