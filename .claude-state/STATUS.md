# Trading Bot Status

_Last updated: 2026-04-21 (Cycle 173)_

## 현황 요약
- **전략 수**: ~355개 (신규 추가 동결)
- **PASS 전략**: 합성 22개 → ⚠️ **실제 데이터 0개** (전략 약점, 엔진 정상)
- **ML 2-class**: BTC 1000캔들 acc 63.5% → PASS (유일한 유효 경로)
- **ML 파이프라인**: ✅ 재학습+PFI+예측+live+cal분리+SHAP선택+ExtraTrees+XGBoost+PSI드리프트+PSI-AccDrift통합+MultiWindowEnsemble+RegimeAwareFeatureBuilder 완비
- **Walk-Forward**: WFE > 0.5 + Trades >= 15 + MC p<0.05
- **테스트**: 7,354+ passed, 0 failed (risk 173, feed 118, health_check 23, notifier 20, exchange 98+, trainer 63+, FR/OI 49, kelly 93, feature_builder 29, drift 53, backtest 48, paper_trader 58, ml_pipeline 25, order_flow 61, websocket 63, regime_feature 34, var_backtest 5, ml_backtest_integration 11)
- **리스크**: Kelly(quarter-cap+레짐+MDD step-down+레짐스무딩+stress검증) + VaR(CF+backtest검증) + DrawdownMonitor(4단계+레짐cooldown) + VolTargeting + CircuitBreaker(일일제한)
- **실행**: TWAP + ML필터 + 레짐필터 + 레짐 포지션사이징 + CircuitBreaker + HealthChecker + Notifier + **Telegram실연동**
- **데이터**: 실데이터+GARCH합성+레짐캐시(동적TTL)+품질모니터링(갭감지)+DataFeed CB+FR/OI+수수료0.055%+adaptive슬리피지+VPIN강화+WebSocket backoff
- **라이브**: live_paper_trader **98% 준비** (레짐별성과추적+일별P&L+Telegram실연동+세션요약, 78개 테스트)

## 최근 작업 (Cycle 173)
| 카테고리 | 상태 | 주요 변경 |
|---------|------|----------|
| E (실행) | ✅ | live_paper_trader 레짐 성과 추적 + Telegram 실API 연동 |
| A (품질) | ✅ | RegimeFeature E2E 9개 + ML-Backtest 통합 11개 = 20개 테스트 |
| SIM | ✅ | detect_regime() 7 패턴 검증, 피처 축소 확인 (4~10 vs 17) |
| F (리서치) | ✅ | Bayesian Kelly (α=2,β=3), fractional 25~33%, 모니터링 3단계 |

## 완료된 대응 (Cycle 140~173)
- ✅ 슬리피지 0.1% / MIN_TRADES 15 / MC Permutation gate
- ✅ Regime Detection + 레짐 필터 (RANGING 차단)
- ✅ CircuitBreaker(일일거래제한) + DrawdownMonitor(4단계MDD+레짐cooldown) + 경계값 테스트
- ✅ Kelly Sizer: 레짐 조정 + quarter-cap(0.25) + MDD step-down + 레짐 스무딩(EMA) + stress 검증
- ✅ VaR/CVaR 검증 + Cornish-Fisher expansion + backtest validation (5% 초과율)
- ✅ ML: 재학습+예측+live+PFI+SHAP+ExtraTrees+XGBoost+MultiWindowEnsemble+RegimeAwareFeatureBuilder
- ✅ TWAP 검증 + 합성 데이터 GARCH 교체 + 품질 모니터링(갭 감지)
- ✅ LSTM 버그 수정 + Drift Detector (PHT+CUSUM+AccuracyDriftMonitor)
- ✅ DataFeed: 레짐 캐시(동적TTL) + Circuit Breaker + 갭 감지
- ✅ HealthChecker(4단계+재연결) + Notifier(3계층+Telegram실연동) + live_paper_trader 통합
- ✅ 수수료 현실화: Bybit taker 0.055% 기본값, adaptive_slippage 레짐별 가변
- ✅ PSI 드리프트 모니터 + AccuracyDriftMonitor 통합 (양방향)
- ✅ XGBoost + MultiWindowEnsemble 30/60/90일 다시간 stacking
- ✅ VPIN edge case 강화 + WebSocket exponential backoff + ConnectionMetrics
- ✅ Paper trader input validation + ML pipeline edge case 테스트
- ✅ RegimeAwareFeatureBuilder: 레짐별 동적 피처 선택 + E2E 통합 테스트
- ✅ live_paper_trader 레짐별 성과 추적 + 일별 P&L + 세션 요약

## 주요 리스크/이슈
- ⚠️ 실데이터 PASS 전략 0개 — ML 경로가 유일한 희망
- 다음 우선: **Bayesian Kelly 구현**, River ADWIN 통합, live 7일 운영
- 소자본 fractional Kelly 25~33% 적용 필요
- Alert fatigue 방지: Critical 세션당 3~5개 제한 준수
