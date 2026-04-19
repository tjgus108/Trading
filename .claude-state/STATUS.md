# Trading Bot Status

_Last updated: 2026-04-19 (Cycle 154)_

## 현황 요약
- **전략 수**: ~355개 (신규 추가 동결)
- **PASS 전략**: 합성 22개 → ⚠️ **실제 데이터 0개** (전략 약점, 엔진 정상)
- **ML 2-class**: BTC 1000캔들 acc 63.5% → PASS (유일한 유효 경로)
- **ML 파이프라인**: ✅ 자동 재학습 + PFI 분석 + 예측 + live 연동 완비
- **Walk-Forward**: WFE > 0.5 + Trades >= 15 + MC p<0.05
- **테스트**: 6700+ passed (risk 54, feed 93 포함)
- **리스크**: Kelly(레짐조정) + VaR + DrawdownMonitor(레짐연동) + VolTargeting + CircuitBreaker(경계값 검증 완료)
- **실행**: TWAP + ML필터 + 레짐필터 + 레짐 포지션사이징 + CircuitBreaker
- **데이터**: 실데이터+GARCH합성+레짐캐시+품질모니터링+DataFeed CircuitBreaker 완비

## 최근 작업 (Cycle 154)
| 카테고리 | 상태 | 주요 변경 |
|---------|------|----------|
| C (데이터) | ✅ | DataFeed Circuit Breaker 패턴 (3-state 자동복구), 13개 테스트 |
| B (리스크) | ✅ | CircuitBreaker 경계값 테스트 22개 추가 (54 total PASS) |
| F (리서치) | ✅ | 장기 생존 봇 패턴, Funding Rate+OI 피처, RF+XGBoost 앙상블 방향 |

## 완료된 대응 (Cycle 140~154)
- ✅ 슬리피지 0.1% / MIN_TRADES 15 / MC Permutation gate
- ✅ Regime Detection + 레짐 필터 (RANGING 차단)
- ✅ CircuitBreaker + DrawdownMonitor (HIGH_VOL 2% 한도) + 경계값 테스트 완비
- ✅ Kelly Sizer 레짐 조정 + 레짐 기반 포지션 사이징
- ✅ VaR/CVaR 검증 + DataFeed 레짐 캐시
- ✅ ML 재학습 + 예측 + live 연동 + PFI 분석
- ✅ TWAP 검증 + 합성 데이터 GARCH 교체 + 품질 모니터링
- ✅ LSTM 버그 수정 + Drift Detector (PHT+CUSUM+AccuracyDriftMonitor)
- ✅ Triple Barrier + CPCV 구현 + AccuracyDriftMonitor live 연동
- ✅ DataFeed Circuit Breaker (cascading failure 방지)

## 주요 리스크/이슈
- ⚠️ 실데이터 PASS 전략 0개 — ML 경로가 유일한 희망
- 리서치 권장: MDD 기준 20%→10% 강화, Funding Rate+OI 피처 추가
- 다음: ML 피처 확장 (Funding Rate, OI), XGBoost 앙상블, live 검증 7일
