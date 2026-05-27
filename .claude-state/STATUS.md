# Trading Bot Status

_Last updated: 2026-05-28 (Cycle 228)_

## 현황 요약
- **전략 수**: ~355개 (신규 추가 동결)
- **PASS 전략**: 합성 22개 → ⚠️ **실제 데이터 0개** (IS only, OOS 전부 FAIL)
- **가장 유망**: linear_channel_rev(SOL, Sharpe 1.65), frama(ETH, Sharpe 1.24), narrow_range(PF=1.61, 신호 빈도 개선), value_area(SharpeStd 안정화)
- **ML 2-class**: BTC 1000캔들 acc 63.5% → PASS
- **ML 파이프라인**: ✅ 재학습+PFI+SHAP+ExtraTrees+XGBoost+PSI+MultiWindowEnsemble+RegimeAwareFeatureBuilder+DataFeed E2E+ADWIN 드리프트 감지+추론벤치마크+온체인피처stub+EWMA early warning+**should_retrain_by_ewma+get_model_health** 완비
- **Walk-Forward**: ✅ 7개 전략 factory + OOS Sharpe std 필터 + param stability CV + Sharpe-λ*CV penalty + fold time-decay 가중치 + WFE/fold_pass_rate/is_robust + 파라미터5개↑경고
- **테스트**: 7,800+ passed (기존 flaky 45건 제외)
- **리스크**: **Kelly(rolling win_rate+quarter-cap+레짐+MDD+스무딩+stress)** + BayesianKelly + VaR(CF+backtest+scipy_fallback+소표본경고) + DrawdownMonitor(4단계+cooldown+streak_grace+trailing_stop_signal) + VolTargeting(simple+EWMA) + CircuitBreaker(일일제한+급속하락+config확장+**15분윈도우FlashCrash**) + **RiskManager CF-VaR 통합+trailing_stop 통합+orchestrator 주입 완료**
- **실행**: TWAP(34테스트+**unfilled_qty누적재시도**) + ML필터 + 레짐필터 + PaperTrader(VolTargeting+KellySizer+TieredSlippage+save_state/load_state+**load_state스키마검증**) + CB + HealthChecker + Notifier + Telegram + BayesianKelly live + RegimeDetector + PerformanceTracker(시간별+주간/월간PnL) + **orchestrator CF-VaR/DrawdownMonitor/PortfolioOptimizer 주입**
- **데이터**: 실데이터+GARCH합성+BlockBootstrap합성+레짐캐시(동적TTL+레짐별 차등만료)+갭감지+DataFeed CB+FR/OI+0.055%+adaptive슬리피지+VPIN(극단불균형감지)+WebSocket(ConnectionHealthMonitor)+RegimeFeature E2E+중복타임스탬프제거+스테일캐시자동무효화
- **드리프트 감지**: ADWINDriftDetector(delta=0.05) + DualGateADWINMonitor(피처+모델출력 이중게이트+EWMA accuracy+**should_retrain+model_health**)
- **라이브**: live_paper_trader **100% 준비** (graceful shutdown+상태복원 포함)
- **OOS 인프라**: run_bundle_oos.py — 5-Bundle Rolling OOS + **Rank Score** 리포트
- **SIM 랭킹**: Composite Rank Score (6지표 가중합산) — paper_simulation + **bundle_oos** 양쪽 적용

## 최근 작업 (Cycle 228)
| 카테고리 | 상태 | 주요 변경 |
|---------|------|----------|
| E (실행) | ✅ | PaperTrader load_state 스키마검증 + TWAP unfilled_qty 누적 재시도 |
| A (품질) | ✅ | MLSignalGenerator regime_aware 추론 통합 테스트 3개 추가 (74 passed) |
| SIM | ✅ | 0/22 PASS 유지 (합성 데이터 mc_p_value 편향), 상위 3 전략 안정성 확인 |
| F (리서치) | ✅ | TWAP MEV 봇 위험, Paper→Live $570만 슬리피지 사례, MC test 편향 대안 |

## 주요 리스크/이슈
- ⚠️ 실데이터 PASS 전략 0개
- ✅ RiskManager CF-VaR 체인 완성 + orchestrator 주입 완료
- ✅ Flash Crash 15분 윈도우 보호 추가
- ✅ value_area SharpeStd 안정화 + narrow_range 신호 빈도 개선
- ✅ circuit_breaker.py 강화 버전 → orchestrator FullCircuitBreakerAdapter 주입 완료
- ⚠️ 볼륨 단위 불일치: Binance(base) vs Bybit(quote)
- ⚠️ Paper→Live 갭: BTC 0.05%, 중형 0.2%, 소형 1.0% 슬리피지
- ⚠️ MC permutation test 합성데이터 편향 의심 (narrow_range 기본항목 PASS → MC FAIL)
- ✅ RegimeGuardedStrategy 래퍼 구현 완료 (src/strategy/base.py)
- ✅ MLSignalGenerator RegimeAwareFeatureBuilder 학습-추론 연결 완료
- 🆕 다음: WFO plateau check 추가, 실데이터 검증 파이프라인, value_area va_mult=0.6 효과 검증
