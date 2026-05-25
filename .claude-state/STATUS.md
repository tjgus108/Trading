# Trading Bot Status

_Last updated: 2026-05-26 (Cycle 209)_

## 현황 요약
- **전략 수**: ~355개 (신규 추가 동결)
- **PASS 전략**: 합성 22개 → ⚠️ **실제 데이터 0개** (IS only, OOS 전부 FAIL)
- **가장 유망**: linear_channel_rev(SOL, Sharpe 1.65), frama(ETH, Sharpe 1.24)
- **ML 2-class**: BTC 1000캔들 acc 63.5% → PASS
- **ML 파이프라인**: ✅ 재학습+PFI+SHAP+ExtraTrees+XGBoost+PSI+MultiWindowEnsemble+RegimeAwareFeatureBuilder+DataFeed E2E+ADWIN 드리프트 감지+추론벤치마크+온체인피처stub 완비
- **Walk-Forward**: ✅ 7개 전략 factory + OOS Sharpe std 필터 + param stability CV + Sharpe-λ*CV penalty + fold time-decay 가중치
- **테스트**: 7,600+ passed, 0 failed
- **리스크**: **Kelly(rolling win_rate 동적추정+quarter-cap+레짐+MDD+스무딩+stress)** + BayesianKelly(β prior+fractional0.33) + VaR(CF+backtest+scipy_fallback검증) + DrawdownMonitor(4단계+cooldown+streak_grace직렬화수정) + VolTargeting(simple+EWMA) + CircuitBreaker(일일제한+급속하락감지+직렬화검증)
- **실행**: TWAP(엣지케이스30테스트) + ML필터 + 레짐필터 + PaperTrader(VolTargeting+KellySizer통합+TieredSlippage) + CB + HealthChecker + Notifier + Telegram실연동 + BayesianKelly live 통합 + RegimeDetector→paper_trader 통합 + PerformanceTracker(시간별PnL)
- **데이터**: 실데이터+GARCH합성+레짐캐시(동적TTL)+갭감지+DataFeed CB+FR/OI+0.055%+adaptive슬리피지+VPIN+**WebSocket(ConnectionHealthMonitor)**+RegimeFeature E2E
- **드리프트 감지**: ADWINDriftDetector(delta=0.05) + DualGateADWINMonitor(피처+모델출력 이중게이트)
- **라이브**: live_paper_trader **100% 준비**
- **OOS 인프라**: `scripts/run_bundle_oos.py` — 5-Bundle Rolling OOS 자동 실행 + 리포트 생성

## 최근 작업 (Cycle 209)
| 카테고리 | 상태 | 주요 변경 |
|---------|------|----------|
| C (데이터) | ✅ | 합성 seed 다양화(심볼 hash 기반), graceful import 확인 |
| B (리스크) | ✅ | VaR scipy fallback 검증 7t + streak grace 검증 7t + to_dict 버그 수정 |
| SIM | ✅ | 5전략 FAIL, narrow_range fold 1,6만 유의미(8 trades), value_area PF=999.99 artifact |
| F (리서치) | ✅ | IS→OOS R²<0.025, NR7+필터1개 PF=2.35, 파라미터 2개 전략 81조합 OOS+ |

## 주요 리스크/이슈
- ⚠️ 실데이터 PASS 전략 0개 — 기본값 전략 실데이터에서도 FAIL
- ✅ DataFeed Binance fallback 구현 완료 — 실데이터 확보 병목 해소
- ⚠️ 볼륨 단위 불일치 주의: Binance(base) vs Bybit(quote) (ccxt #25399)
- ⚠️ Paper→Live 갭: BTC 0.05%, 중형 0.2%, 소형 1.0% 슬리피지 반영 필수
- 다음 우선: 온체인 신호 통합(Exchange Netflow, DeFiLlama TVL, SOPR delta)
