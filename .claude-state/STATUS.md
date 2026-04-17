# Trading Bot Status

_Last updated: 2026-04-17 (Cycle 139)_

## 현황 요약
- **전략 수**: ~355개 (신규 추가 동결)
- **PASS 전략**: 합성 22개 → ⚠️ **실제 데이터 0개** (오버피팅, 근본 원인 분석 완료)
- **실제 수익 전략**: 0개 — 합성 데이터 기반 전략 전면 재검토 필요
- **ML 피처**: 17개 + 앙상블 recency decay + DSR 필터
- **Walk-Forward**: WFE > 0.5 + Trades >= 50 (50→15 하향 검토 중)
- **테스트**: 6598+ passed / 33 failed / 0 collection errors
- **리스크**: Kelly + VaR + DrawdownMonitor + VolTargeting + Rolling Sharpe 모니터
- **실행**: TWAP+DrawdownMonitor 연동, VolTargeting 완비
- **데이터**: 실제 거래소 데이터 다운로드+검증 유틸리티 완비

## 최근 작업 (Cycle 139)
| 카테고리 | 상태 | 주요 변경 |
|---------|------|----------|
| C (데이터) | ✅ | data_utils.py (실데이터 다운로드+검증), feed.py 자동 재연결 |
| B (리스크) | ✅ | Rolling Sharpe 모니터, CircuitBreaker 3% 일일 한도 |
| SIM | ✅ | 오버피팅 근본 원인 5개 분석 (슬리피지/합성데이터/파라미터) |
| F (리서치) | ✅ | 합성 데이터 실패 메커니즘, 로버스트니스 검증 방법론 |

## 실전 데이터 PASS 기준
- Sharpe ≥ 1.0, PF ≥ 1.5, Trades ≥ 50 (15로 하향 검토), MDD ≤ 20%, WFE > 0.5

## ⚠️ 긴급 이슈: 오버피팅 근본 원인 (Cycle 139 분석 결과)
1. **슬리피지 괴리**: 0.05% (코드) vs 0.2-1.0% (실전) — 4-20x
2. **합성 데이터 비현실성**: 첨도 0.51 vs 3-5, stylized facts 미보존
3. **신호 파라미터 과적합**: ATR 조건이 실제 데이터에서 0% 충족
4. **WFA 미적용**: 500-candle 합성 테스트만으로 PASS 판정
5. **다중 비교 문제**: 355개 전략 동시 테스트 → 우연 통과 ~57개 예상

## 대응 방향
- 합성 데이터 → GARCH(1,1)+Student-t 또는 실제 데이터로 교체
- Monte Carlo Permutation gate 추가 (p < 0.05)
- OOS 기간 1개월 → 3개월 확장 + regime 다양성 요건
- 슬리피지 0.05% → 0.2% 상향
- MIN_TRADES 50 → 15 하향 + WFA 필수

## 주요 리스크/이슈
- ⚠️ 전략 전체 오버피팅 — 실데이터 기반 재설계 최우선
- Regime Detection 미구현 — 설계안 준비됨
- 테스트 33개 실패 중
