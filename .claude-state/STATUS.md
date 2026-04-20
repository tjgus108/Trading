# Trading Bot Status

_Last updated: 2026-04-21 (Cycle 174)_

## 현황 요약
- **전략 수**: ~355개 (신규 추가 동결)
- **PASS 전략**: 합성 22개 → ⚠️ **실제 데이터 0개** (77% 거래수 미달, 레짐 스위칭으로 해결 가능)
- **ML 2-class**: BTC 1000캔들 acc 63.5% → PASS (유일한 유효 경로)
- **ML 파이프라인**: ✅ 재학습+PFI+SHAP+ExtraTrees+XGBoost+PSI+MultiWindowEnsemble+RegimeAwareFeatureBuilder+**DataFeed E2E 연결** 완비
- **Walk-Forward**: WFE > 0.5 + Trades >= 15 + MC p<0.05
- **테스트**: 7,400+ passed, 0 failed
- **리스크**: Kelly(quarter-cap+레짐+MDD+스무딩+stress) + **BayesianKelly(β prior+fractional0.33)** + VaR(CF+backtest) + DrawdownMonitor(4단계+cooldown) + VolTargeting + CircuitBreaker(일일제한)
- **실행**: TWAP + ML필터 + 레짐필터 + 포지션사이징 + CB + HealthChecker + Notifier + **Telegram실연동**
- **데이터**: 실데이터+GARCH합성+레짐캐시(동적TTL)+갭감지+DataFeed CB+FR/OI+0.055%+adaptive슬리피지+VPIN+WebSocket backoff+**RegimeFeature E2E**
- **라이브**: live_paper_trader **99% 준비** (레짐성과추적+일별P&L+Telegram+BayesianKelly+DataFeed E2E)

## 최근 작업 (Cycle 174)
| 카테고리 | 상태 | 주요 변경 |
|---------|------|----------|
| B (리스크) | ✅ | BayesianKellyPositionSizer (α=2,β=3, fractional 0.33, warmup 50) |
| C (데이터) | ✅ | DataFeed→RegimeFeature E2E 파이프라인 (fetch_with_regime) |
| SIM | ✅ | 133 backtest PASS, 레짐 스위칭 4~5x 거래수 증가 가능성 |
| F (리서치) | ✅ | ADWIN delta=0.05~0.1, 이중게이트, Telegram 즉시/큐 분리 |

## 주요 리스크/이슈
- ⚠️ 실데이터 PASS 전략 0개 — 레짐 스위칭 + ML이 돌파구
- 다음 우선: **River ADWIN 통합**, live 7일 운영, 레짐 기반 전략 로테이션
- Bayesian Kelly 50거래 warmup 후 자동 활성화 대기
