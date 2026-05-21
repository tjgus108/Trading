# Trading Bot Status

_Last updated: 2026-05-22 (Cycle 192)_

## 현황 요약
- **전략 수**: ~355개 (신규 추가 동결)
- **PASS 전략**: 합성 22개 → ⚠️ **실제 데이터 0개** (IS only, OOS 전부 FAIL)
- **가장 유망**: linear_channel_rev(SOL, Sharpe 1.65), frama(ETH, Sharpe 1.24)
- **ML 2-class**: BTC 1000캔들 acc 63.5% → PASS
- **ML 파이프라인**: ✅ 재학습+PFI+SHAP+ExtraTrees+XGBoost+PSI+MultiWindowEnsemble+RegimeAwareFeatureBuilder+DataFeed E2E+ADWIN 드리프트 감지 완비
- **Walk-Forward**: ✅ 7개 전략 factory + OOS Sharpe std 필터 + param stability CV + Sharpe-λ*CV penalty + fold time-decay 가중치
- **테스트**: 7,600+ passed, 0 failed
- **리스크**: Kelly(quarter-cap+레짐+MDD+스무딩+stress) + BayesianKelly(β prior+fractional0.33) + VaR(CF+backtest) + DrawdownMonitor(4단계+cooldown) + VolTargeting(simple+EWMA) + CircuitBreaker(일일제한+급속하락감지+직렬화검증)
- **실행**: TWAP(엣지케이스30테스트) + ML필터 + 레짐필터 + **PaperTrader(VolTargeting연동)** + CB + HealthChecker + Notifier + Telegram실연동 + BayesianKelly live 통합 + RegimeDetector→paper_trader 통합 + PerformanceTracker(시간별PnL)
- **데이터**: 실데이터+GARCH합성+레짐캐시(동적TTL)+갭감지+DataFeed CB+FR/OI+0.055%+adaptive슬리피지+VPIN+WebSocket backoff+RegimeFeature E2E
- **드리프트 감지**: ADWINDriftDetector(delta=0.05) + DualGateADWINMonitor(피처+모델출력 이중게이트)
- **라이브**: live_paper_trader **100% 준비**
- **OOS 인프라**: `scripts/run_bundle_oos.py` — 5-Bundle Rolling OOS 자동 실행 + 리포트 생성

## 최근 작업 (Cycle 192)
| 카테고리 | 상태 | 주요 변경 |
|---------|------|----------|
| E (실행) | ✅ | PaperTrader VolTargeting 연동 (변동성 높으면 자동 사이즈 축소) |
| A (품질) | ✅ | TWAP 엣지 케이스 30개 + CircuitBreaker 직렬화 라운드트립 5개 테스트 |
| F (리서치) | ✅ | 실행 품질: EWMA λ=0.94 기관 표준, 73% 봇 6개월 내 실패, Paper→Live 갭 분석 |

## 주요 리스크/이슈
- ⚠️ 실데이터 PASS 전략 0개 — 기본값 전략 실데이터에서도 FAIL
- ✅ DataFeed Binance fallback 구현 완료 — 실데이터 확보 병목 해소
- ⚠️ 볼륨 단위 불일치 주의: Binance(base) vs Bybit(quote) (ccxt #25399)
- ⚠️ Paper→Live 갭: BTC 0.05%, 중형 0.2%, 소형 1.0% 슬리피지 반영 필수
- 다음 우선: Binance 실데이터 + WF 파라미터 최적화 → OOS 재검증
