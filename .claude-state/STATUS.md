# Trading Bot Status

_Last updated: 2026-05-21 (Cycle 188)_

## 현황 요약
- **전략 수**: ~355개 (신규 추가 동결)
- **PASS 전략**: 합성 22개 → ⚠️ **실제 데이터 0개** (IS only, OOS 전부 FAIL)
- **가장 유망**: linear_channel_rev(SOL, Sharpe 1.65), frama(ETH, Sharpe 1.24)
- **ML 2-class**: BTC 1000캔들 acc 63.5% → PASS
- **ML 파이프라인**: ✅ 재학습+PFI+SHAP+ExtraTrees+XGBoost+PSI+MultiWindowEnsemble+RegimeAwareFeatureBuilder+DataFeed E2E+ADWIN 드리프트 감지 완비
- **Walk-Forward**: ✅ 7개 전략 factory params 주입 + OOS Sharpe std 필터 + param stability CV 측정 + Sharpe-λ*CV penalty 구현
- **테스트**: 7,400+ passed, 0 failed
- **리스크**: Kelly(quarter-cap+레짐+MDD+스무딩+stress) + BayesianKelly(β prior+fractional0.33) + VaR(CF+backtest) + DrawdownMonitor(4단계+cooldown) + VolTargeting + CircuitBreaker(일일제한+급속하락감지)
- **실행**: TWAP + ML필터 + 레짐필터 + 포지션사이징 + CB + HealthChecker + Notifier + Telegram실연동 + BayesianKelly live 통합 + RegimeDetector→paper_trader 통합 + PerformanceMonitor→paper_trader 연결
- **데이터**: 실데이터+GARCH합성+레짐캐시(동적TTL)+갭감지+DataFeed CB+FR/OI+0.055%+adaptive슬리피지+VPIN+WebSocket backoff+RegimeFeature E2E
- **드리프트 감지**: ADWINDriftDetector(delta=0.05) + DualGateADWINMonitor(피처+모델출력 이중게이트)
- **라이브**: live_paper_trader **100% 준비**
- **OOS 인프라**: `scripts/run_bundle_oos.py` — 5-Bundle Rolling OOS 자동 실행 + 리포트 생성

## 최근 작업 (Cycle 188)
| 카테고리 | 상태 | 주요 변경 |
|---------|------|----------|
| E (실행) | ✅ | DataFeed Binance fallback 구현 (connector+feed+mock 완료) |
| A (품질) | ✅ | 7,605 테스트 전부 pass + 2건 수정 |
| F (리서치) | ✅ | 실데이터 전환 체크리스트 + 볼륨 단위 차이 확인 |
| SIM | ✅ | Binance 실데이터 EMA Cross: IS -0.44, OOS -0.25 (기본값 FAIL) |

## 주요 리스크/이슈
- ⚠️ 실데이터 PASS 전략 0개 — 기본값 전략 실데이터에서도 FAIL
- ✅ DataFeed Binance fallback 구현 완료 — 실데이터 확보 병목 해소
- ⚠️ 볼륨 단위 불일치 주의: Binance(base) vs Bybit(quote) (ccxt #25399)
- 다음 우선: Binance 실데이터 + WF 파라미터 최적화 → OOS 재검증
