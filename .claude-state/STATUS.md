# Trading Bot Status

_Last updated: 2026-04-15 (Cycle 122)_

## 현황 요약
- **전략 수**: ~355개 (신규 추가 동결)
- **PASS 전략**: 22개 (실전 데이터 기준)
- **ML 피처**: 17개 + 앙상블 가중치 동적 계산 추가
- **Walk-Forward**: 리포팅 강화 (split_info, class_distribution, ensemble_weight)
- **리스크**: DrawdownMonitor 에스컬레이션 버그 수정 완료

## 최근 작업 (Cycle 122)
| 카테고리 | 상태 | 주요 변경 |
|---------|------|----------|
| B (리스크) | ✅ | DrawdownMonitor 에스컬레이션 버그 2건 수정, 회귀 테스트 3개 |
| D (ML) | ✅ | 앙상블 가중치 최적화, WF 리포팅 강화, 테스트 7개 |
| SIM | ✅ | dema_cross, acceleration_band, roc_ma_cross RSI 필터 추가 |
| F (리서치) | ✅ | 실패 4건/성공 3건 조사, Regime Detection 트렌드 |

## 실전 데이터 PASS 기준
- Sharpe ≥ 1.0, PF ≥ 1.5, Trades ≥ 15, MDD ≤ 20%

## 주요 리스크/이슈
- PASS 전략 22개 중 실제 수익: engulfing_zone(+5.42%), relative_volume(+4.95%) 2개만
- 나머지 20개 실전 데이터에서 FAIL — 과최적화 가능성
- Regime Detection 미구현 — 고변동성 시장에서 봇 크래시 증폭 위험
