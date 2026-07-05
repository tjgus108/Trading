# Current Cycle Briefing

_Last updated: 2026-07-05 (Cycle 397 완료)_

## 현재 상태

- **완료된 사이클**: 397
- **다음 사이클**: 398 (398 mod 5 = 3 → C+B+F)
- **1h paper_sim PASS**: 1/19 (roc_ma_cross — Sh=1.81, PF=2.02, Consist=4/8)
- **frama**: Sh=0.24, PF=1.12, Trades=40 → 다음 개선 타겟 (atr_period dead param 확정됨)
- **price_cluster**: Sh=1.06, Consist=2/8 → 최적화 완전 종료
- **dema_cross**: Sh=0.85, PF=1.38 → 탐색 완전 종료
- **Bundle OOS**: 5/5 PASS (최신)
- **전체 테스트 수**: 8532개 (+6)

## Cycle 397 주요 결과

### B(리스크): DrawdownMonitor 미커버 케이스 6개 추가

- `tests/test_drawdown_monitor.py`: transition_cushion_multiplier 경계값 3개
  - regime_confidence=0 (최솟값) → 0.5x 축소
  - regime_confidence == threshold(0.70) → 1.0 (< 조건 불성립)
  - regime_confidence=1.0 (최댓값) → 1.0
- `tests/test_drawdown_monitor.py`: should_liquidate_all 3개
  - MDD 15.5% (LIQUIDATE 레벨) → True
  - MDD 21% (FULL_HALT 레벨) → True
  - MDD 11% (BLOCK_ENTRY 레벨) → False (청산 미발동)

### F(리서치): frama 신호 로직 분석 — 중요 발견

- **핵심 발견**: `frama.py`에서 `atr_contracting` 변수는 계산만 되고 BUY/SELL 조건에 미사용
  - `atr_str` 로그 문자열에만 사용 → ATR 수축 필터 = dead code
  - 따라서 `atr_period` 파라미터가 신호 생성에 완전히 무효과
  - Cycle363/371 에서 atr_period 실험이 "효과 없음"이었던 이유 설명됨
- **약한신호 RSI 조건**: gap<1%일 때 RSI<40(BUY)/RSI>60(SELL) 하드코딩
  - BTC 1h RANGING(47.3%)에서 RSI가 40-60 구간에 머물면 신호 차단
  - 다음 방향: weak_rsi_buy_max 파라미터화로 완화 검토

### D(ML): frama WFO 그리드 atr_period DEAD PARAM 정리

- `src/backtest/walk_forward.py`: DEFAULT_GRIDS["frama"] 업데이트
  - atr_period=[10,14,18] → 주석 처리 (dead param)
  - F(리서치) 분석 결과 + 탐색 종료 사유 문서화
  - WFO combos: 27 → 9 (3x 속도 향상 가능)
  - 다음 개선 방향(weak_rsi_buy_max 파라미터화) 주석 추가

## 시뮬레이션 현황 (Cycle 396 생성, Cycle 397 분석)

| 전략 | Sharpe | PF | Trades | Consist | Pass |
|------|--------|-----|--------|---------|------|
| roc_ma_cross | 1.81 | 2.02 | 14 | 4/8 | **PASS** |
| price_cluster | 1.06 | 1.32 | 35 | 2/8 | FAIL |
| dema_cross | 0.85 | 1.38 | 26 | 2/8 | FAIL |
| frama | 0.24 | 1.12 | 40 | 1/8 | FAIL (다음 타겟) |
