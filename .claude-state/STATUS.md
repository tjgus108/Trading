# Trading Bot Status

_Last updated: 2026-05-26 (Cycle 213)_

## 현황 요약
- **전략 수**: ~355개 (신규 추가 동결)
- **PASS 전략**: 합성 22개 → ⚠️ **실제 데이터 0개** (IS only, OOS 전부 FAIL)
- **가장 유망**: linear_channel_rev(SOL, Sharpe 1.65), frama(ETH, Sharpe 1.24)
- **ML 2-class**: BTC 1000캔들 acc 63.5% → PASS
- **ML 파이프라인**: ✅ 재학습+PFI+SHAP+ExtraTrees+XGBoost+PSI+MultiWindowEnsemble+RegimeAwareFeatureBuilder+DataFeed E2E+ADWIN 드리프트 감지+추론벤치마크+온체인피처stub 완비
- **Walk-Forward**: ✅ 7개 전략 factory + OOS Sharpe std 필터 + param stability CV + Sharpe-λ*CV penalty + fold time-decay 가중치 + WFE/fold_pass_rate/is_robust + 파라미터5개↑경고
- **테스트**: 7,600+ passed, 0 failed
- **리스크**: **Kelly(rolling win_rate 동적추정+quarter-cap+레짐+MDD+스무딩+stress)** + BayesianKelly(β prior+fractional0.33) + VaR(CF+backtest+scipy_fallback검증) + DrawdownMonitor(4단계+cooldown+streak_grace직렬화수정) + VolTargeting(simple+EWMA) + CircuitBreaker(일일제한+급속하락감지+직렬화검증)
- **실행**: TWAP(엣지케이스30테스트) + ML필터 + 레짐필터 + PaperTrader(VolTargeting+KellySizer통합+TieredSlippage+**save_state/load_state**) + CB + HealthChecker + Notifier + Telegram실연동 + BayesianKelly live 통합 + RegimeDetector→paper_trader 통합 + PerformanceTracker(시간별+**주간/월간PnL**)
- **데이터**: 실데이터+GARCH합성+레짐캐시(동적TTL)+갭감지+DataFeed CB+FR/OI+0.055%+adaptive슬리피지+VPIN+**WebSocket(ConnectionHealthMonitor)**+RegimeFeature E2E
- **드리프트 감지**: ADWINDriftDetector(delta=0.05) + DualGateADWINMonitor(피처+모델출력 이중게이트)
- **라이브**: live_paper_trader **100% 준비** (graceful shutdown+상태복원 포함)
- **OOS 인프라**: `scripts/run_bundle_oos.py` — 5-Bundle Rolling OOS 자동 실행 + 리포트 생성
- **SIM 랭킹**: Composite Rank Score (6지표 가중합산) + percentile + sharpe_std

## 최근 작업 (Cycle 213)
| 카테고리 | 상태 | 주요 변경 |
|---------|------|----------|
| E (실행) | ✅ | PerformanceTracker 주간/월간 + PaperTrader save/load state + graceful shutdown |
| A (품질) | ✅ | volume_breakout v3 (추세필터→confidence), price_cluster v3 (threshold 수정) |
| SIM | ✅ | Composite Rank Score 6지표 가중합산 + sharpe_std + percentile 라벨 |
| F (리서치) | ✅ | 실패/성공사례 리서치 + Block Bootstrap/CPCV 극복방안 도출 |

## 주요 리스크/이슈
- ⚠️ 실데이터 PASS 전략 0개 — 기본값 전략 실데이터에서도 FAIL
- ✅ DataFeed Binance fallback 구현 완료 — 실데이터 확보 병목 해소
- ⚠️ 볼륨 단위 불일치 주의: Binance(base) vs Bybit(quote) (ccxt #25399)
- ⚠️ Paper→Live 갭: BTC 0.05%, 중형 0.2%, 소형 1.0% 슬리피지 반영 필수
- 🆕 리서치 권고: GBM→Block Bootstrap 교체, CPCV 도입 검토
- 다음 우선: Block Bootstrap 합성데이터 생성기 구현 + 소수 전략 재검증
