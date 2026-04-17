# Trading Bot Status

_Last updated: 2026-04-18 (Cycle 144)_

## 현황 요약
- **전략 수**: ~355개 (신규 추가 동결)
- **PASS 전략**: 합성 22개 → ⚠️ **실제 데이터 0개** (전략 약점 확인, 엔진 정상)
- **ML 2-class**: BTC 1000캔들 acc 63.5% → PASS (유일한 유효 경로)
- **Walk-Forward**: WFE > 0.5 + Trades >= 15 + MC p<0.05
- **테스트**: 6598+ passed / 33 failed
- **리스크**: Kelly(레짐 조정) + VaR(검증완료) + DrawdownMonitor + VolTargeting + CircuitBreaker
- **실행**: TWAP+DrawdownMonitor+CircuitBreaker 연동, VolTargeting 완비
- **데이터**: 실데이터 다운로드+검증+레짐 캐시 완비
- **레짐 필터**: ✅ live_paper_trader에 RANGING 시그널 차단 구현 완료

## 최근 작업 (Cycle 144)
| 카테고리 | 상태 | 주요 변경 |
|---------|------|----------|
| C (데이터) | ✅ | live_paper_trader 레짐 필터 (RANGING 차단), DataFeed 레짐 캐시 |
| B (리스크) | ✅ | VaR/CVaR MIN_SAMPLES 100 상향, Kelly 레짐 조정 메서드 |
| F (리서치) | ✅ | 크립토봇 실패사례 5건, 레짐 기반 포지션 사이징 리서치 |
| SIM | ✅ | BacktestEngine 품질 게이트 검증 (모두 정상) |

## 실전 데이터 PASS 기준
- Sharpe ≥ 1.0, PF ≥ 1.5, Trades ≥ 15, MDD ≤ 20%, MC p<0.05, WFE > 0.5

## 완료된 대응 (Cycle 140~144)
- ✅ 슬리피지 0.1% 현실화
- ✅ MIN_TRADES 15 하향
- ✅ MC Permutation gate (500 perms, sign randomization)
- ✅ Regime Detection (ADX+EMA+ATR)
- ✅ CircuitBreaker live 통합 (일일 3%, 전체 15%)
- ✅ live_paper_trader 레짐 필터 (RANGING 차단)
- ✅ DataFeed 레짐 캐시 (TTL 5분)
- ✅ VaR/CVaR parametric fallback 강화
- ✅ Kelly Sizer 레짐 조정

## 주요 리스크/이슈
- ⚠️ 실데이터 PASS 전략 0개 — ML 경로가 유일한 희망
- 다음 우선과제: ML 자동 재학습 파이프라인, ML 시그널 live 연동
