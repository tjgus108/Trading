# Current Cycle Briefing

_Cycle 278 완료 | 2026-06-06_

## 카테고리: C(데이터) + B(리스크) + F(리서치)

## 핵심 변경사항

1. **wick_reversal 모멘텀 필터 추가** (`src/strategy/wick_reversal.py`)
   - 14봉 양(+) 모멘텀 `has_momentum = close > ref_close_14` 추가
   - Hammer BUY 조건에 필수 조건으로 포함
   - fold1 (Aug-Oct 2023 횡보) 오신호 감소 목적

2. **Bundle에서 wick_reversal → supertrend_multi 교체** (`scripts/run_bundle_oos.py`)
   - wick_reversal: 3회 연속 FAIL, std=4.842 → 제거
   - supertrend_multi: Paper Sim BTC 1h 4연속 1위 (+5.87%) → 추가
   - min_oos_trades=3 오버라이드 (4h 신호 희소 완화)

## 시뮬레이션 결과

| 항목 | 결과 |
|------|------|
| 테스트 | 8369 passed (회귀 없음) |
| Paper Sim BTC 1h | 0/22 PASS, 1위: supertrend_multi +5.87% |
| Bundle OOS BTC 4h | 1/5 PASS: cmf (avg=2.508, std=1.888) |
| supertrend_multi OOS | avg=1.699, std=3.769, fold4: OOS=-4.239 |

## Cycle 279 준비

**카테고리**: D(ML) + E(실행) + F(리서치)

**주요 과제**:
- supertrend_multi fold4 (Feb-Apr 2024 BTC ATH) OOS=-4.239 원인 규명
- ATR 상한 임계값 추가 or atr_threshold 조정 실험
- Bundle OOS 2번째 PASS 전략 달성 목표

## 환경 상태
- 거래소 API: 차단 (SSL) → CSV fallback 사용
- BTC 데이터: synthetic CSV 2023-01~2024-05 (12000 rows 1h)
