# Trading Bot Status

_Last updated: 2026-05-21 (Cycle 186)_

## 현황 요약
- **전략 수**: ~355개 (신규 추가 동결)
- **PASS 전략**: 합성 22개 → ⚠️ **실제 데이터 0개** (IS only, OOS 전부 FAIL)
- **가장 유망**: linear_channel_rev(SOL, Sharpe 1.65), frama(ETH, Sharpe 1.24)
- **ML 2-class**: BTC 1000캔들 acc 63.5% → PASS
- **ML 파이프라인**: ✅ 재학습+PFI+SHAP+ExtraTrees+XGBoost+PSI+MultiWindowEnsemble+RegimeAwareFeatureBuilder+DataFeed E2E+ADWIN 드리프트 감지 완비
- **Walk-Forward**: ✅ 7개 전략 factory params 주입 완료 (Cycle 185-186), OOS Sharpe std 필터, param stability CV 리서치 완료
- **테스트**: 7,400+ passed, 0 failed
- **리스크**: Kelly(quarter-cap+레짐+MDD+스무딩+stress) + BayesianKelly(β prior+fractional0.33) + VaR(CF+backtest) + DrawdownMonitor(4단계+cooldown) + VolTargeting + CircuitBreaker(일일제한)
- **실행**: TWAP + ML필터 + 레짐필터 + 포지션사이징 + CB + HealthChecker + Notifier + Telegram실연동 + BayesianKelly live 통합 + RegimeDetector→paper_trader 통합 + PerformanceMonitor→paper_trader 연결
- **데이터**: 실데이터+GARCH합성+레짐캐시(동적TTL)+갭감지+DataFeed CB+FR/OI+0.055%+adaptive슬리피지+VPIN+WebSocket backoff+RegimeFeature E2E
- **드리프트 감지**: ADWINDriftDetector(delta=0.05) + DualGateADWINMonitor(피처+모델출력 이중게이트)
- **라이브**: live_paper_trader **100% 준비**
- **OOS 인프라**: `scripts/run_bundle_oos.py` — 5-Bundle Rolling OOS 자동 실행 + 리포트 생성

## 최근 작업 (Cycle 186)
| 카테고리 | 상태 | 주요 변경 |
|---------|------|----------|
| A (품질) | ✅ | 5개 전략 params kwargs 확장 + walk_forward factory 5개 추가 |
| C (데이터) | ✅ | SSL verify/proxy 설정 + 캐시 키 정규화(symbol.upper()) |
| F (리서치) | ✅ | param stability CV 방법론 + 2026 Q2 시장전망 + 봇 실패패턴 |
| SIM | ✅ | factory 수정 후 OOS 재검증: 0/5 PASS — 합성 데이터 한계 확인 |

## 주요 리스크/이슈
- ⚠️ 실데이터 PASS 전략 0개 — 합성 데이터에서는 IS 자체가 음수, 실데이터 확보가 최우선
- ⚠️ Bybit API SSL 차단 → 합성 데이터만 사용 중
- 다음 우선: factory 수정된 상태로 OOS 재실행, fold별 param stability 측정
