# Trading Bot Status

_Last updated: 2026-04-21 (Cycle 175)_

## 현황 요약
- **전략 수**: ~355개 (신규 추가 동결)
- **PASS 전략**: 합성 22개 → ⚠️ **실제 데이터 0개** (Sharpe -2.84, PF 0.85 — 레짐 필터링 필수)
- **ML 2-class**: BTC 1000캔들 acc 63.5% → PASS (유일한 유효 경로)
- **ML 파이프라인**: ✅ 재학습+PFI+SHAP+ExtraTrees+XGBoost+PSI+MultiWindowEnsemble+RegimeAwareFeatureBuilder+DataFeed E2E+**ADWIN 드리프트 감지** 완비
- **Walk-Forward**: WFE > 0.5 + Trades >= 15 + MC p<0.05
- **테스트**: 7,400+ passed, 0 failed
- **리스크**: Kelly(quarter-cap+레짐+MDD+스무딩+stress) + BayesianKelly(β prior+fractional0.33) + VaR(CF+backtest) + DrawdownMonitor(4단계+cooldown) + VolTargeting + CircuitBreaker(일일제한)
- **실행**: TWAP + ML필터 + 레짐필터 + 포지션사이징 + CB + HealthChecker + Notifier + Telegram실연동 + **BayesianKelly live 통합**
- **데이터**: 실데이터+GARCH합성+레짐캐시(동적TTL)+갭감지+DataFeed CB+FR/OI+0.055%+adaptive슬리피지+VPIN+WebSocket backoff+RegimeFeature E2E
- **드리프트 감지**: ADWINDriftDetector(delta=0.05) + DualGateADWINMonitor(피처+모델출력 이중게이트)
- **라이브**: live_paper_trader **100% 준비** (BayesianKelly통합+상태저장복원+에러복구개선)

## 최근 작업 (Cycle 175)
| 카테고리 | 상태 | 주요 변경 |
|---------|------|----------|
| D (ML) | ✅ | ADWIN 드리프트 감지 (이중게이트, 29 tests) |
| E (실행) | ✅ | BayesianKelly→live 통합, 상태저장/복원, 에러복구 (13 tests) |
| SIM | ✅ | 22 합성 PASS → 실데이터 전부 FAIL, 레짐 필터링 필수 확인 |
| F (리서치) | ✅ | ADWIN delta=0.01+debounce3, walk-forward 6/1, 레짐 3분류 |

## 주요 리스크/이슈
- ⚠️ 실데이터 PASS 전략 0개 — 레짐 스위칭 + ML이 유일한 돌파구
- 다음 우선: **Regime Switcher 구현**, live 7일 운영, ADWIN→파이프라인 연결
- ADWIN 리서치 결과: delta=0.01+debounce 3회가 크립토 최적 (기존 0.05보다 낮게)
