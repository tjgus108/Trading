# Trading Bot Status

_Last updated: 2026-05-29 (Cycle 233)_

## 현황 요약
- **전략 수**: ~355개 (신규 추가 동결)
- **PASS 전략**: 합성 22개 → ⚠️ **실제 데이터 0개** (IS only, OOS 전부 FAIL)
- **가장 유망**: momentum_quality(Sharpe 6.71 BTC), price_action_momentum(Sharpe 5.16 SOL), supertrend_multi(Sharpe 4.84 ETH)
- **ML 2-class**: BTC 1000캔들 acc 63.5% → PASS
- **ML 파이프라인**: ✅ 재학습+PFI+SHAP+ExtraTrees+XGBoost+PSI+MultiWindowEnsemble+RegimeAwareFeatureBuilder+DataFeed E2E+ADWIN 드리프트 감지+추론벤치마크+온체인피처stub+EWMA early warning+**should_retrain_by_ewma+get_model_health+bid_ask_depth_imbalance피처+compare_feature_importance+VPIN피처** 완비
- **Walk-Forward**: ✅ 7개 전략 factory + OOS Sharpe std 필터 + param stability CV + Sharpe-λ*CV penalty + fold time-decay 가중치 + WFE/fold_pass_rate/is_robust + 파라미터5개↑경고 + **Sharpe IC 파라미터 선택**
- **테스트**: 8,150+ passed (Cycle 233 +30개)
- **리스크**: **Kelly(rolling win_rate+quarter-cap+레짐+MDD+스무딩+stress+**동적fraction**)** + BayesianKelly + VaR(CF+backtest+scipy_fallback+소표본경고) + DrawdownMonitor(4단계+cooldown+streak_grace+trailing_stop_signal) + VolTargeting(simple+EWMA) + CircuitBreaker(일일제한+급속하락+config확장+**15분윈도우FlashCrash**) + **RiskManager CF-VaR 통합+trailing_stop 통합+orchestrator 주입 완료**
- **실행**: TWAP(76테스트+**unfilled_qty누적재시도+orderbook동적슬라이스**) + ML필터 + 레짐필터 + PaperTrader(VolTargeting+KellySizer+TieredSlippage+save_state/load_state+**load_state스키마검증+get_execution_summary**) + CB + HealthChecker(**get_uptime_pct**) + Notifier + Telegram + BayesianKelly live + RegimeDetector + PerformanceTracker(시간별+주간/월간PnL) + **orchestrator CF-VaR/DrawdownMonitor/PortfolioOptimizer 주입**
- **데이터**: 실데이터+GARCH합성+BlockBootstrap합성+레짐캐시(동적TTL+레짐별 차등만료)+갭감지+DataFeed CB+FR/OI+0.055%+adaptive슬리피지+VPIN(극단불균형감지)+WebSocket(ConnectionHealthMonitor+**동적타임아웃+validate_timeout**)+RegimeFeature E2E+중복타임스탬프제거+스테일캐시자동무효화+**get_order_book_depth(5초TTL)+OFICalculator(극단감지)+TTL일관성검증**
- **드리프트 감지**: ADWINDriftDetector(delta=0.05) + DualGateADWINMonitor(피처+모델출력 이중게이트+EWMA accuracy+**should_retrain+model_health**)
- **라이브**: live_paper_trader **100% 준비** (graceful shutdown+상태복원 포함)
- **OOS 인프라**: run_bundle_oos.py — 5-Bundle Rolling OOS + **Rank Score** 리포트
- **SIM 랭킹**: Composite Rank Score (6지표 가중합산) — paper_simulation + **bundle_oos** 양쪽 적용

## 최근 작업 (Cycle 233)
| 카테고리 | 상태 | 주요 변경 |
|---------|------|----------|
| E (실행) | ✅ | PaperTrader get_execution_summary() + HealthChecker get_uptime_pct() (12 tests) |
| A (품질) | ✅ | KellySizer/VPIN/SharpeIC 엣지케이스 테스트 18개 추가 |
| SIM | ✅ | 0/66 PASS (합성), Top: momentum_quality Sharpe 6.71 |
| F (리서치) | ✅ | Flash Crash 분석, Kelly-VIX Hybrid, RegimeFolio, WF fold 레짐 구성 |

## 주요 리스크/이슈
- ⚠️ 실데이터 PASS 전략 0개
- ✅ RiskManager CF-VaR 체인 완성 + orchestrator 주입 완료
- ✅ Flash Crash 15분 윈도우 보호 추가
- ✅ PaperTrader 실행 품질 모니터링 (get_execution_summary)
- ⚠️ 볼륨 단위 불일치: Binance(base) vs Bybit(quote)
- ⚠️ Paper→Live 갭: BTC 0.05%, 중형 0.2%, 소형 1.0% 슬리피지
- ⚠️ MC permutation test 합성데이터 편향 (alpha 부재 → 전략 무차별 FAIL)
- 🆕 리서치 권장: Kelly-VIX Hybrid, fold별 레짐 구성 기록, 파라미터 섭동 테스트
