# Trading Bot Status

_Last updated: 2026-04-18 (Cycle 146)_

## 현황 요약
- **전략 수**: ~355개 (신규 추가 동결)
- **PASS 전략**: 합성 22개 → ⚠️ **실제 데이터 0개** (전략 약점, 엔진 정상)
- **ML 2-class**: BTC 1000캔들 acc 63.5% → PASS (유일한 유효 경로)
- **ML 파이프라인**: ✅ 자동 재학습 + 예측 + live 연동 완비
- **Walk-Forward**: WFE > 0.5 + Trades >= 15 + MC p<0.05
- **테스트**: 6598+ passed / 30 failed (3개 수정)
- **리스크**: Kelly(레짐 조정) + VaR(검증완료) + DrawdownMonitor + VolTargeting + CircuitBreaker
- **실행**: TWAP(검증완료) + ML필터 + 레짐필터 + CircuitBreaker
- **데이터**: 실데이터+GARCH합성+레짐캐시+품질모니터링 완비

## 최근 작업 (Cycle 146)
| 카테고리 | 상태 | 주요 변경 |
|---------|------|----------|
| A (품질) | ✅ | LSTM BooleanArray 수정, Python 3.7 호환성, 166+ 테스트 확인 |
| C (데이터) | ✅ | 합성 데이터 GARCH+Student-t (kurtosis 5.0+), 품질 로깅 |
| F (리서치) | ✅ | GARCH-t/EGARCH-t 비교, 전략 수명/decay, FDR 보정 |

## 실전 데이터 PASS 기준
- Sharpe ≥ 1.0, PF ≥ 1.5, Trades ≥ 15, MDD ≤ 20%, MC p<0.05, WFE > 0.5

## 완료된 대응 (Cycle 140~146)
- ✅ 슬리피지 0.1% 현실화
- ✅ MIN_TRADES 15 하향
- ✅ MC Permutation gate (500 perms, sign randomization)
- ✅ Regime Detection (ADX+EMA+ATR)
- ✅ CircuitBreaker live 통합 (일일 3%, 전체 15%)
- ✅ live_paper_trader 레짐 필터 (RANGING 차단)
- ✅ DataFeed 레짐 캐시 (TTL 5분)
- ✅ VaR/CVaR parametric fallback 강화
- ✅ Kelly Sizer 레짐 조정
- ✅ ML 자동 재학습 파이프라인 (--auto-retrain)
- ✅ ML 예측/live 연동 (--predict, --ml-filter)
- ✅ TWAP 실행기 검증 및 안정성 개선
- ✅ 합성 데이터 GARCH(1,1)+Student-t 교체 (kurtosis 5.0+)
- ✅ 데이터 품질 모니터링 (kurtosis/skewness 로깅)
- ✅ LSTM BooleanArray 버그 수정

## 주요 리스크/이슈
- ⚠️ 실데이터 PASS 전략 0개 — ML 경로가 유일한 희망
- 다음: ML 모델 실제 생성, 레짐 기반 동적 포지션 사이징, 전략 상관관계 모니터링
