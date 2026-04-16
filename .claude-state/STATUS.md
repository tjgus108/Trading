# Trading Bot Status

_Last updated: 2026-04-16 (Cycle 134)_

## 현황 요약
- **전략 수**: ~355개 (신규 추가 동결)
- **PASS 전략**: 22개 (실전 데이터 기준)
- **실제 수익 전략**: 2개 (engulfing_zone +5.42%, relative_volume +4.95%)
- **ML 피처**: 17개 + 앙상블 가중치 동적 계산
- **Walk-Forward**: 리포팅 강화 완료
- **테스트**: 6598 passed / 33 failed / 3 collection errors
- **리스크**: KellySizer Bayesian shrinkage + VaR/CVaR parametric 보정 추가

## 최근 작업 (Cycle 134)
| 카테고리 | 상태 | 주요 변경 |
|---------|------|----------|
| C (데이터) | ✅ | VPIN zero-volume 버그 수정, DataFeed LRU 캐시 퇴거 |
| B (리스크) | ✅ | KellySizer Bayesian shrinkage, VaR/CVaR parametric 보정 |
| SIM | ✅ | paper_simulation 에러 카운트/exit code, paper_connector 가격 검증 |
| F (리서치) | ✅ | Regime Detection HMM/GMM deep dive, 적용 방안 설계 |

## 실전 데이터 PASS 기준
- Sharpe ≥ 1.0, PF ≥ 1.5, Trades ≥ 15, MDD ≤ 20%

## 주요 리스크/이슈
- PASS 전략 22개 중 실제 수익: engulfing_zone, relative_volume 2개만
- 나머지 20개 실전 데이터에서 FAIL — 과최적화 확인
- Regime Detection 미구현 — 리서치 2회 완료, 구현 설계 준비됨 (HMM k=2~3, GMM 크립토용)
- 테스트 33개 여전히 실패 중 — 다음 품질 사이클에서 수정 필요
