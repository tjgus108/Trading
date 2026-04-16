# Trading Bot Status

_Last updated: 2026-04-16 (Cycle 133)_

## 현황 요약
- **전략 수**: ~355개 (신규 추가 동결)
- **PASS 전략**: 22개 (실전 데이터 기준)
- **실제 수익 전략**: 2개 (engulfing_zone +5.42%, relative_volume +4.95%)
- **ML 피처**: 17개 + 앙상블 가중치 동적 계산
- **Walk-Forward**: 리포팅 강화 완료
- **테스트**: 6598 passed / 33 failed / 3 collection errors (대폭 개선)

## 최근 작업 (Cycle 133)
| 카테고리 | 상태 | 주요 변경 |
|---------|------|----------|
| E (실행) | ✅ | TWAP side 검증 + 에러 분리, 비대칭 슬리피지 모델 |
| A (품질) | ✅ | 389→3 collection errors, 6598 tests passing, Python 3.7 호환 |
| SIM | ✅ | paper_simulation 합성데이터 indicator 누락 수정, balance 정확도 개선 |
| F (리서치) | ✅ | 과최적화 실패 사례, Regime Detection 트렌드, 구조적 엣지 성공 사례 |

## 실전 데이터 PASS 기준
- Sharpe ≥ 1.0, PF ≥ 1.5, Trades ≥ 15, MDD ≤ 20%

## 주요 리스크/이슈
- PASS 전략 22개 중 실제 수익: engulfing_zone, relative_volume 2개만
- 나머지 20개 실전 데이터에서 FAIL — 과최적화 확인 (리서치로 재확인)
- Regime Detection 미구현 — 2025-2026 업계 표준 트렌드이나 아직 미적용
- 테스트 33개 여전히 실패 중 — 다음 품질 사이클에서 추가 수정 필요
