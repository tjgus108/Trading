# Trading Bot Status

_Last updated: 2026-04-17 (Cycle 138)_

## 현황 요약
- **전략 수**: ~355개 (신규 추가 동결)
- **PASS 전략**: 22개 (합성 데이터 기준) → ⚠️ **실제 데이터에서 0개 PASS** (심각한 오버피팅)
- **실제 수익 전략**: 0개 (실전 walk-forward 결과, 이전 2개도 합성 데이터 기반)
- **ML 피처**: 17개 + 앙상블 recency decay + DSR 과최적화 필터
- **Walk-Forward**: WFE > 0.5 + Trades >= 50 필터 적용 완료
- **테스트**: 6598+ passed / 33 failed / 0 collection errors (3개 수정)
- **리스크**: Kelly Bayesian + VaR parametric + DrawdownMonitor 쿨다운/연속손실 + Volatility Targeting
- **실행**: TWAP+DrawdownMonitor 연동, Volatility Targeting 포지션 사이징 완비

## 최근 작업 (Cycle 138)
| 카테고리 | 상태 | 주요 변경 |
|---------|------|----------|
| E (실행) | ✅ | Volatility Targeting 도입, TWAP+DrawdownMonitor 연동 |
| A (품질) | ✅ | Collection error 3개 수정, 호환성 검증 |
| SIM | ⚠️ | 22개 PASS 전략 실제 데이터에서 전부 실패 (오버피팅) |
| F (리서치) | ✅ | 운영 실패 3건, 알파 감쇠 관리, 배포 체크리스트 |

## 실전 데이터 PASS 기준
- Sharpe ≥ 1.0, PF ≥ 1.5, Trades ≥ 50, MDD ≤ 20%, WFE > 0.5

## ⚠️ 긴급 이슈: 전략 오버피팅
- **22개 PASS 전략이 실제 거래소 데이터(Bybit)에서 전부 손실**
- BTC -7.25%, ETH -4.61%, SOL -5.92% (평균)
- 합성 데이터 기반 백테스트와 실전 간 심각한 괴리
- 다음 단계: 전략 신호 생성 로직 전면 재검토, 실제 데이터 기반 전략 재설계 필요

## 주요 리스크/이슈
- ⚠️ PASS 전략 전체 오버피팅 — 실제 데이터 기반 재설계 필요
- Regime Detection 미구현 — 리서치 3회 완료, 최우선 과제
- 테스트 33개 실패 중 (collection error는 해결)
- 전략 간 상관관계 모니터링 부재
- 알파 감쇠 모니터링(Rolling Sharpe) 미구현
