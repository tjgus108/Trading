# Trading Bot Status

_Last updated: 2026-04-22 (Cycle 179)_

## 현황 요약
- **전략 수**: ~355개 (신규 추가 동결)
- **PASS 전략**: 합성 22개 → ⚠️ **실제 데이터 0개** (Sharpe -2.84, PF 0.85 — 레짐 필터링 필수)
- **ML 2-class**: BTC 1000캔들 acc 63.5% → PASS (유일한 유효 경로)
- **ML 파이프라인**: ✅ 재학습+PFI+SHAP+ExtraTrees+XGBoost+PSI+MultiWindowEnsemble+RegimeAwareFeatureBuilder+DataFeed E2E+ADWIN 드리프트 감지 완비
- **Walk-Forward**: WFE > 0.5 + Trades >= 15 + MC p<0.05
- **테스트**: 7,400+ passed, 0 failed
- **리스크**: Kelly(quarter-cap+레짐+MDD+스무딩+stress) + BayesianKelly(β prior+fractional0.33) + VaR(CF+backtest) + DrawdownMonitor(4단계+cooldown) + VolTargeting + CircuitBreaker(일일제한)
- **실행**: TWAP + ML필터 + 레짐필터 + 포지션사이징 + CB + HealthChecker + Notifier + Telegram실연동 + BayesianKelly live 통합 + **RegimeDetector→paper_trader 통합** + **PerformanceMonitor→paper_trader 연결**
- **데이터**: 실데이터+GARCH합성+레짐캐시(동적TTL)+갭감지+DataFeed CB+FR/OI+0.055%+adaptive슬리피지+VPIN+WebSocket backoff+RegimeFeature E2E
- **드리프트 감지**: ADWINDriftDetector(delta=0.05) + DualGateADWINMonitor(피처+모델출력 이중게이트)
- **라이브**: live_paper_trader **100% 준비** (RegimeDetector통합+PerformanceMonitor통합+BayesianKelly통합+상태저장복원+에러복구개선)
- **OOS 인프라**: `scripts/run_bundle_oos.py` — 5-Bundle Rolling OOS 자동 실행 + 리포트 생성

## 최근 작업 (Cycle 179)
| 카테고리 | 상태 | 주요 변경 |
|---------|------|----------|
| D (ML) | ✅ | RegimeDetector→paper_trader 통합 (23 tests) |
| E (실행) | ✅ | 5-Bundle OOS 스크립트 + PerformanceMonitor 연결 (11 tests) |
| F (리서치) | ✅ | Paper Trading 자동화 + 봇 실패/성공 리서치 (RESEARCH_NOTES.md) |

## 주요 리스크/이슈
- ⚠️ 실데이터 PASS 전략 0개 — 레짐 스위칭 + ML이 유일한 돌파구
- 다음 우선: **실데이터 OOS 실행** (run_bundle_oos.py), Paper Trading 4주 테스트
- Paper Trading 리서치 결과: 4~8주 필수, 5% 급락 포함, Go/No-Go 자동 판정 설계 완료
