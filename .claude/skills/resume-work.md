---
name: resume-work
description: 이전 세션 상태를 복원하고 오늘의 작업 계획을 확인하는 스킬
---

# 작업 재개 프로토콜

이 스킬을 실행하면 현재 프로젝트 상태를 빠르게 파악하고 다음 할 일을 확인합니다.

## Step 1: 상태 파일 읽기

```
.claude-state/NEXT_STEPS.md   — 전체 Phase 완료 현황 + 남은 작업
.claude-state/BACKTEST_REPORT.md — 백테스트 결과 요약
```

## Step 2: 현재 상태 요약 출력

```
=== TRADING BOT 작업 재개 ===

[프로젝트 상태]
- 완료 Phase: A/B/C/D/E/F/G/H/I/J/K/L 전체 완료
- 전략 수: 20종 (STRATEGY_REGISTRY)
- 테스트: 537 passed, 11 skipped
- GitHub: https://github.com/tjgus108/Trading (main, e05a3cc)

[STRATEGY_REGISTRY — 20종]
기존(9): ema_cross, donchian_breakout, funding_rate, residual_mean_reversion,
         pair_trading, ml_rf, ml_lstm, rsi_divergence, bb_squeeze
Phase E(3): regime_adaptive, funding_carry, lob_maker
Phase F(3): heston_lstm, cross_exchange_arb, liquidation_cascade
Phase G(2): gex_signal, cme_basis
기타(3):  (specialist_agents는 전략이 아닌 앙상블 에이전트)

[신규 모듈 (Phase G~L)]
src/strategy/adaptive_selector.py  — rolling Sharpe 가중 실시간 전략 선택
src/strategy/multi_signal.py       — MultiStrategyAggregator (confidence 가중 투표)
src/risk/portfolio_optimizer.py    — Mean-Variance/Risk Parity/Equal Weight + VaR/CVaR
src/risk/drawdown_monitor.py       — MDD 초과 시 거래 자동 차단 (Orchestrator 연동)
src/risk/vol_targeting.py          — 목표 변동성 기반 포지션 사이즈 조정 (Pipeline 연동)
src/risk/kelly_sizer.py            — Half-Kelly + ATR 조정 (Pipeline H1 연동)
src/exchange/twap.py               — TWAP 분할 실행 (Pipeline H4 연동)
src/backtest/monte_carlo.py        — Block Bootstrap Monte Carlo 시뮬레이션
src/backtest/report.py             — BacktestReport (Sharpe/Calmar/MDD/win_rate)
src/analysis/strategy_correlation.py — 전략 신호 상관행렬
src/monitoring/anomaly_detector.py — Z-score/IQR/return spike 이상치 감지
src/monitoring/position_health.py  — HEALTHY/WARNING/CRITICAL 포지션 건강 판단
src/data/options_feed.py           — GEXFeed (Deribit) + CMEBasisFeed (Binance)
src/data/liquidation_feed.py       — LiquidationFetcher (청산 캐스케이드 예측)

[파이프라인 선택적 컴포넌트]
pipeline.kelly_sizer       = KellySizer()      # H1
pipeline.twap_executor     = TWAPExecutor()    # H4
pipeline.vol_targeting     = VolTargeting()    # I3
pipeline.specialist_ensemble = SpecialistEnsemble()  # F1
pipeline.llm_analyst       = LLMAnalyst()      # C2
pipeline.ensemble          = MultiLLMEnsemble() # D1

[유의사항]
- pytest 경로: ~/Library/Python/3.9/bin/pytest
- python 경로: /Library/Developer/CommandLineTools/usr/bin/python3 (3.9.6)
- Python 3.9 호환: X | None 금지 → Optional[X] 사용
- 권한 확인 없이 자율 진행 (사용자 명시 지시)
- 새 전략: BaseStrategy 상속 + STRATEGY_REGISTRY 등록 필수
```

## Step 3: 작업 시작

미완료 태스크가 있으면 즉시 작업을 시작하세요.
의존성 없는 태스크는 병렬 Agent로 실행하세요.

---

## 핵심 파일 위치

| 파일 | 역할 |
|---|---|
| src/orchestrator.py | BotOrchestrator + STRATEGY_REGISTRY (20종) + DrawdownMonitor |
| src/pipeline/runner.py | TradingPipeline (data→context→alpha→risk→exec) + Kelly/TWAP/Vol |
| src/strategy/base.py | BaseStrategy ABC |
| src/strategy/adaptive_selector.py | rolling Sharpe 가중 전략 선택기 |
| src/strategy/multi_signal.py | MultiStrategyAggregator (복수 전략 합의) |
| src/alpha/context.py | MarketContext (B1~B3 통합) |
| src/alpha/ensemble.py | MultiLLMEnsemble (Claude + GPT-4o) |
| src/alpha/llm_analyst.py | LLMAnalyst (단일, 하위호환) |
| src/alpha/specialist_agents.py | F1: Technical/Sentiment/Onchain 3개 전문 에이전트 |
| src/risk/portfolio_optimizer.py | Mean-Variance/Risk Parity/Equal Weight + VaR/CVaR |
| src/risk/kelly_sizer.py | Half-Kelly + ATR 조정 포지션 사이저 |
| src/risk/drawdown_monitor.py | MDD 실시간 추적 + 긴급 정지 |
| src/risk/vol_targeting.py | 목표 변동성 기반 포지션 사이즈 |
| src/backtest/monte_carlo.py | Block Bootstrap Monte Carlo |
| src/backtest/report.py | BacktestReport (Sharpe/Calmar/MDD) |
| src/backtest/walk_forward.py | WalkForwardOptimizer (D3) |
| src/analysis/strategy_correlation.py | 전략 신호 상관행렬 |
| src/monitoring/anomaly_detector.py | 이상치 실시간 감지 |
| src/monitoring/position_health.py | 포지션 건강 상태 |
| src/data/feed.py | DataFeed + TTL 캐싱 (G4) |
| src/data/websocket_feed.py | BinanceWebSocketFeed (D2) |
| src/data/order_flow.py | OFI + VPINCalculator |
| src/data/options_feed.py | GEXFeed + CMEBasisFeed |
| src/data/dex_feed.py | DEX 가격 피드 (CoinGecko fallback) |
| src/exchange/twap.py | TWAP 분할 실행기 |
| src/ml/trainer.py | WalkForwardTrainer (RF) |
| src/ml/lstm_model.py | LSTMSignalGenerator (PyTorch/numpy) |
| src/ml/hmm_model.py | HMMRegimeDetector (E1) |
| src/ml/heston_model.py | HestonVolatilityModel (F2, numpy only) |
| scripts/train_ml.py | ML 학습 CLI (rf/lstm) |
| README.md | 전체 사용 매뉴얼 |

## 실행 명령어

```bash
# 테스트
~/Library/Python/3.9/bin/pytest tests/ -q

# 데모 (API 키 없이)
python3 main.py --demo --tournament --dashboard

# 전체 기능
python3 main.py --websocket --ensemble --walk-forward --loop --dashboard

# ML 학습
python3 scripts/train_ml.py --demo --model rf
python3 scripts/train_ml.py --demo --model lstm

# 의존성
pip install hmmlearn scikit-learn websockets torch openai anthropic
```

## Phase 전체 완료 이력

| Phase | 내용 | 테스트 |
|---|---|---|
| 인프라 | BotOrchestrator, BacktestEngine, RiskManager, Dashboard, Telegram | ✅ |
| A | FundingRate, ResidualMeanReversion, PairTrading | ✅ |
| B | SentimentFetcher, OnchainFetcher, NewsMonitor, MarketContext | ✅ |
| C | FeatureBuilder, WalkForwardTrainer, MLRFStrategy, LLMAnalyst, auto-tournament | ✅ |
| D | MultiLLMEnsemble, BinanceWebSocket, WalkForwardOptimizer, LSTM, OrderFlow | ✅ |
| E1 | HMM Regime-Adaptive (Sharpe 1.8~2.5) | ✅ |
| E2 | Funding Carry Cash-and-Carry (Sharpe 2.0~5.0) | ✅ |
| E3 | LOB OFI + VPIN Market Making (Sharpe 1.5~3.0) | ✅ |
| F1 | LLM 멀티에이전트 — SpecialistEnsemble (Technical/Sentiment/Onchain) | ✅ |
| F2 | Heston-LSTM 하이브리드 (Sharpe 1.8~2.1) | ✅ |
| F3 | DEX/CEX 차익 — CrossExchangeArbStrategy | ✅ |
| G1 | SpecialistEnsemble 파이프라인 배선 + funding rate auto-inject | ✅ |
| G2 | GEXStrategy + CMEBasisStrategy (gex_signal, cme_basis) | ✅ |
| G3 | PortfolioOptimizer (mean_variance / risk_parity / equal_weight) | ✅ |
| G4 | DataFeed TTL 캐싱 + 통합 테스트 4개 | ✅ |
| H1 | KellySizer 파이프라인 통합 | ✅ |
| H2 | AdaptiveStrategySelector (rolling Sharpe 가중치) | ✅ |
| H3 | VaR95 / CVaR95 PortfolioOptimizer 추가 | ✅ |
| H4 | TWAPExecutor 파이프라인 통합 | ✅ |
| I1 | MultiStrategyAggregator (confidence 가중 투표) | ✅ |
| I2 | DrawdownMonitor (MDD 초과 자동 차단) | ✅ |
| I3 | VolTargeting (목표 변동성 포지션 조정) | ✅ |
| J1 | MonteCarlo Block Bootstrap | ✅ |
| J2 | BacktestReport (Sharpe/Calmar/MDD/win_rate) | ✅ |
| J3 | SignalCorrelationTracker | ✅ |
| K1 | AnomalyDetector (Z-score/IQR/return spike) | ✅ |
| K2 | PositionHealthMonitor (HEALTHY/WARNING/CRITICAL) | ✅ |
| L | DrawdownMonitor→Orchestrator, VolTargeting→Pipeline 배선 | ✅ |
| **합계** | **537 passed, 11 skipped** | ✅ |
