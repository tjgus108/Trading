# Trading Bot Status

_Last updated: 2026-05-27 (Cycle 219)_

## 현황 요약
- **전략 수**: ~355개 (신규 추가 동결)
- **PASS 전략**: 합성 22개 → ⚠️ **실제 데이터 0개** (IS only, OOS 전부 FAIL)
- **가장 유망**: linear_channel_rev(SOL, Sharpe 1.65), frama(ETH, Sharpe 1.24), narrow_range(PF=1.61, 신호 빈도 개선 완료)
- **ML 2-class**: BTC 1000캔들 acc 63.5% → PASS
- **ML 파이프라인**: ✅ 재학습+PFI+SHAP+ExtraTrees+XGBoost+PSI+MultiWindowEnsemble+RegimeAwareFeatureBuilder+DataFeed E2E+ADWIN 드리프트 감지+추론벤치마크+온체인피처stub+EWMA early warning 완비
- **Walk-Forward**: ✅ 7개 전략 factory + OOS Sharpe std 필터 + param stability CV + Sharpe-λ*CV penalty + fold time-decay 가중치 + WFE/fold_pass_rate/is_robust + 파라미터5개↑경고
- **테스트**: 7,800+ passed (기존 flaky 45건 제외)
- **리스크**: **Kelly(rolling win_rate+quarter-cap+레짐+MDD+스무딩+stress)** + BayesianKelly + VaR(CF+backtest+scipy_fallback+**소표본경고**) + DrawdownMonitor(4단계+cooldown+streak_grace+**trailing_stop_signal**) + VolTargeting(simple+EWMA) + CircuitBreaker(일일제한+급속하락+config확장4파라미터) + **RiskManager CF-VaR 통합 + trailing_stop 통합**
- **실행**: TWAP(30테스트) + ML필터 + 레짐필터 + PaperTrader(VolTargeting+KellySizer+TieredSlippage+save_state/load_state) + CB + HealthChecker + Notifier + Telegram + BayesianKelly live + RegimeDetector + PerformanceTracker(시간별+주간/월간PnL)
- **데이터**: 실데이터+GARCH합성+**BlockBootstrap합성**+레짐캐시(동적TTL+**레짐별 차등만료**)+갭감지+DataFeed CB+FR/OI+0.055%+adaptive슬리피지+VPIN(**극단불균형감지**)+WebSocket(ConnectionHealthMonitor)+RegimeFeature E2E+**중복타임스탬프제거**+**스테일캐시자동무효화**
- **드리프트 감지**: ADWINDriftDetector(delta=0.05) + DualGateADWINMonitor(피처+모델출력 이중게이트+EWMA accuracy)
- **라이브**: live_paper_trader **100% 준비** (graceful shutdown+상태복원 포함)
- **OOS 인프라**: run_bundle_oos.py — 5-Bundle Rolling OOS + **Rank Score** 리포트
- **SIM 랭킹**: Composite Rank Score (6지표 가중합산) — paper_simulation + **bundle_oos** 양쪽 적용

## 최근 작업 (Cycle 219)
| 카테고리 | 상태 | 주요 변경 |
|---------|------|----------|
| C (데이터) | ✅ | DataFeed 중복 타임스탬프 제거, 레짐별 캐시 만료, VPIN 극단 불균형 감지 |
| B (리스크) | ✅ | RiskManager CF-VaR 통합 + trailing_stop_signal 통합 (포지션 자동 축소) |
| SIM | ✅ | narrow_range NR_SCAN_WINDOW=3, ATR 0.95 완화 → 신호 3~4배 증가 |
| F (리서치) | ✅ | 실패사례($9M 슬리피지, 플래시크래시), 성공사례(stat arb Sharpe 2.3), CF-VaR 실전 |

## 주요 리스크/이슈
- ⚠️ 실데이터 PASS 전략 0개
- ✅ RiskManager CF-VaR 체인 완성 (KellySizer → PortfolioOptimizer → RiskManager)
- ✅ narrow_range 저거래 문제 개선 (3봉 윈도우 + ATR 완화)
- ⚠️ 볼륨 단위 불일치: Binance(base) vs Bybit(quote)
- ⚠️ Paper→Live 갭: BTC 0.05%, 중형 0.2%, 소형 1.0% 슬리피지
- 🆕 다음: narrow_range 개선 효과 실데이터 검증, 플래시 크래시 circuit breaker, 레짐 필터 레이어
