# Trading Bot Status

_Last updated: 2026-04-16 (Cycle 135)_

## 현황 요약
- **전략 수**: ~355개 (신규 추가 동결)
- **PASS 전략**: 22개 (실전 데이터 기준, Trades>=15 → 50 상향 검토 중)
- **실제 수익 전략**: 2개 (engulfing_zone +5.42%, relative_volume +4.95%)
- **ML 피처**: 17개 + 앙상블 가중치 시간 감쇠(recency decay) 추가
- **Walk-Forward**: 리포팅 강화 완료, WFE > 0.5 기준 도입 검토
- **테스트**: 6598+ passed / 33 failed / 3 collection errors
- **리스크**: Kelly Bayesian shrinkage + VaR parametric 보정
- **실행**: Telegram/connector 재시도 로직 + exponential backoff 완비

## 최근 작업 (Cycle 135)
| 카테고리 | 상태 | 주요 변경 |
|---------|------|----------|
| D (ML) | ✅ | RF 피처 중요도 영속화, 앙상블 recency decay, CCV 버그 수정 |
| E (실행) | ✅ | Telegram/connector exponential backoff, _retry 래퍼 |
| SIM | ✅ | 결과 JSON/CSV 저장, √impact 슬리피지 모델 |
| F (리서치) | ✅ | DSR/PBO/CPCV 과최적화 탐지, WFE>0.5 + Trades>=50 권장 |

## 실전 데이터 PASS 기준
- Sharpe ≥ 1.0, PF ≥ 1.5, Trades ≥ 15 (→50 상향 검토), MDD ≤ 20%

## 주요 리스크/이슈
- PASS 22개 중 실제 수익 2개만 — DSR/PBO 기반 과최적화 필터 도입 필요
- Regime Detection 미구현 — 리서치 2회 완료, 구현 설계 준비됨
- 테스트 33개 실패 중 — 다음 품질 사이클에서 수정
- Trades>=15 기준 통계적으로 불충분 — 50회 상향 필요
