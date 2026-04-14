# Trading Bot Status

_Last updated: 2026-04-14 (Cycle 121)_

## 현황 요약
- **전략 수**: ~355개 (신규 추가 동결)
- **PASS 전략**: 22개 (실전 데이터 기준)
- **ML 피처**: 17개 (macd_hist, bb_position 추가)
- **Walk-Forward**: 분할 로직 개선 완료
- **슬리피지 추적**: bps 단위 정밀 추적 적용

## 최근 작업 (Cycle 121)
| 카테고리 | 상태 | 주요 변경 |
|---------|------|----------|
| D (ML) | ✅ | 피처 2개 추가, walk-forward 분할 개선 |
| E (실행) | ✅ | 슬리피지 bps 추적, connector 개선 |
| SIM | ✅ | linear_channel_rev v4, price_action_momentum v2 |
| F (리서치) | ✅ | 실패/성공 5건 조사, 교훈 정리 |

## 실전 데이터 PASS 기준
- Sharpe ≥ 1.0, PF ≥ 1.5, Trades ≥ 15, MDD ≤ 20%

## 주요 리스크/이슈
- PASS 전략 22개 중 실제 수익: engulfing_zone(+5.42%), relative_volume(+4.95%) 2개만
- 나머지 20개 실전 데이터에서 FAIL — 과최적화 가능성
