# Trading Bot Status

_Last updated: 2026-04-17 (Cycle 137)_

## 현황 요약
- **전략 수**: ~355개 (신규 추가 동결)
- **PASS 전략**: 22개 (Trades>=50 + WFE>0.5 기준 적용됨)
- **실제 수익 전략**: 2개 (engulfing_zone +5.42%, relative_volume +4.95%)
- **ML 피처**: 17개 + 앙상블 recency decay + DSR 과최적화 필터
- **Walk-Forward**: WFE > 0.5 필터 적용 완료
- **테스트**: 6598+ passed / 33 failed / 3 collection errors
- **리스크**: Kelly Bayesian shrinkage + VaR parametric + DrawdownMonitor 쿨다운/연속손실 감지
- **실행**: Telegram/connector exponential backoff 완비

## 최근 작업 (Cycle 137)
| 카테고리 | 상태 | 주요 변경 |
|---------|------|----------|
| B (리스크) | ✅ | DrawdownMonitor 연속손실 감지+쿨다운, 테스트 60/60 |
| D (ML) | ✅ | MIN_TRADES 50, WFE>0.5 필터, DSR 함수 구현 |
| SIM | ✅ | roc_ma_cross/volatility_cluster 파라미터 튜닝 |
| F (리서치) | ✅ | 실패 사례 3건, Volatility Targeting/상관관계 제한 권고 |

## 실전 데이터 PASS 기준
- Sharpe ≥ 1.0, PF ≥ 1.5, Trades ≥ 50, MDD ≤ 20%, WFE > 0.5

## 주요 리스크/이슈
- PASS 22개 중 실제 수익 2개만 — DSR 필터 적용됨, 재평가 필요
- Regime Detection 미구현 — 리서치 3회 완료, 최우선 구현 과제
- 테스트 33개 실패 중 — 다음 품질 사이클에서 수정
- Volatility Targeting 미도입 — 리서치에서 강력 권고
- 전략 간 상관관계 모니터링 부재 — 군집 매도 리스크
