# Trading Bot Status

_Last updated: 2026-05-29 (Cycle 239)_

## 현황 요약
- **전략 수**: ~355개 (신규 추가 동결)
- **PASS 전략**: 합성 22개 → ⚠️ **실제 데이터 0개** (MC test 합성데이터 한계)
- **가장 유망**: momentum_quality(Sharpe 7.67), price_action_momentum(Sharpe 6.98), supertrend_multi(Sharpe 6.57)
- **ML 2-class**: BTC 1000캔들 acc 63.5% → PASS
- **ML 파이프라인**: ✅ 재학습+PFI+SHAP+ExtraTrees+XGBoost+PSI+MultiWindowEnsemble+RegimeAwareFeatureBuilder+DataFeed E2E+ADWIN 드리프트 감지+추론벤치마크+온체인피처stub+EWMA early warning+should_retrain_by_ewma+get_model_health+compare_feature_importance+VPIN피처 완비
- **Walk-Forward**: ✅ 7개 전략 factory + OOS Sharpe std 필터 + param stability CV + Sharpe-λ*CV penalty + fold time-decay 가중치 + WFE/fold_pass_rate/is_robust + Sharpe IC 파라미터 선택 + regime fold weighting
- **테스트**: 8,240+ passed (Cycle 239 +42개)
- **리스크**: **Kelly(rolling win_rate+quarter-cap+레짐+MDD+스무딩+stress+동적fraction+**vol_scaling**)** + BayesianKelly + VaR(CF+backtest+scipy_fallback+소표본경고) + DrawdownMonitor(4단계+cooldown+streak_grace+trailing_stop_signal+**mdd_kill_switch**) + VolTargeting(simple+EWMA) + CircuitBreaker(일일제한+급속하락+config확장+15분윈도우FlashCrash) + RiskManager CF-VaR 통합+trailing_stop 통합+orchestrator 주입 완료
- **실행**: TWAP(80테스트+unfilled_qty누적재시도+orderbook동적슬라이스+volume-weighted slices+엣지케이스검증) + ML필터 + 레짐필터 + PaperTrader(VolTargeting+KellySizer+TieredSlippage+save_state/load_state+load_state스키마검증+get_execution_summary) + CB + HealthChecker(get_uptime_pct+엣지케이스8개보강) + Notifier + Telegram + BayesianKelly live + RegimeDetector + PerformanceTracker(시간별+주간/월간PnL+rolling_sharpe_30d)
- **데이터**: 실데이터+GARCH합성+BlockBootstrap합성(block_size기본24)+레짐캐시(동적TTL+레짐별 차등만료)+갭감지+DataFeed CB(**get_cache_stats**)+FR/OI+0.055%+adaptive슬리피지+VPIN(극단불균형감지)+WebSocket(ConnectionHealthMonitor+동적타임아웃+validate_timeout+MAX_BACKOFF=60s+**reconnect_gaps**)+RegimeFeature E2E+중복타임스탬프제거+스테일캐시자동무효화+get_order_book_depth(5초TTL)+OFICalculator(극단감지)+TTL일관성검증
- **백테스트**: MC permutation test block sign randomization 버그 수정 + --regime-weights CLI + perturbation_check(ROBUST/MODERATE/FRAGILE) + **--perturbation-check CLI**
- **드리프트 감지**: ADWINDriftDetector(delta=0.05) + DualGateADWINMonitor(피처+모델출력 이중게이트+EWMA accuracy+should_retrain+model_health)
- **라이브**: live_paper_trader **100% 준비** (graceful shutdown+상태복원 포함)
- **OOS 인프라**: run_bundle_oos.py — 5-Bundle Rolling OOS + Rank Score 리포트
- **SIM 랭킹**: Composite Rank Score (6지표 가중합산) — paper_simulation + bundle_oos 양쪽 적용

## 최근 작업 (Cycle 239)
| 카테고리 | 상태 | 주요 변경 |
|---------|------|----------|
| C (데이터) | ✅ | WebSocket reconnect_gaps + DataFeed get_cache_stats (14 tests) |
| B (리스크) | ✅ | MDD kill switch + KellySizer vol_scaling (17 tests) |
| SIM | ✅ | perturbation_check 통합 + --perturbation-check CLI (11 tests) |
| F (리서치) | ✅ | 슬리피지 실패 4건, 5-layer kill switch, GAN 합성(TimeGAN/SFAG/Diffusion) |

## 주요 리스크/이슈
- ⚠️ 실데이터 PASS 전략 0개 (MC test on GBM은 구조적 한계 — 실데이터 필요)
- ✅ MDD kill switch 구현 (should_kill_strategy + get_kill_switch_status)
- ✅ KellySizer volatility scaling 구현 (target_vol/realized_vol, 2x cap)
- ✅ perturbation_check() paper_simulation 연동 완료
- ⚠️ 볼륨 단위 불일치: Binance(base) vs Bybit(quote)
- ⚠️ Paper→Live 갭: BTC 0.05%, 중형 0.2%, 소형 1.0% 슬리피지
- 🆕 리서치: 오더북 깊이 기반 포지션 사이즈 제한, GAN 합성은 실데이터 PASS 후 검토
