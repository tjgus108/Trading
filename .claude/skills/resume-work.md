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
- 완료 Phase: A/B/C/D/E/F 전체 완료
- 전략 수: 15종 (STRATEGY_REGISTRY)
- 테스트: 356 passed, 11 skipped

[STRATEGY_REGISTRY — 15종]
기존(9): ema_cross, donchian_breakout, funding_rate, residual_mean_reversion,
         pair_trading, ml_rf, ml_lstm, rsi_divergence, bb_squeeze
Phase E(3): regime_adaptive, funding_carry, lob_maker
Phase F(3): heston_lstm, specialist_agents(F1 — 전략 외), cross_exchange_arb

[남은 작업]
- 없음. 모든 Phase 완료.
- 추가 방향: 실제 Binance API 데이터로 백테스트 재검증
- 추가 방향: ML 모델 학습 (scripts/train_ml.py --model rf)

[유의사항]
- pytest 경로: ~/Library/Python/3.9/bin/pytest
- python 경로: /Library/Developer/CommandLineTools/usr/bin/python3 (3.9.6)
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
| src/orchestrator.py | BotOrchestrator + STRATEGY_REGISTRY (15종) |
| src/pipeline/runner.py | TradingPipeline (data→context→alpha→risk→exec) |
| src/strategy/base.py | BaseStrategy ABC |
| src/alpha/context.py | MarketContext (B1~B3 통합) |
| src/alpha/ensemble.py | MultiLLMEnsemble (Claude + GPT-4o) |
| src/alpha/llm_analyst.py | LLMAnalyst (단일, 하위호환) |
| src/alpha/specialist_agents.py | F1: Technical/Sentiment/Onchain 3개 전문 에이전트 |
| src/data/websocket_feed.py | BinanceWebSocketFeed (D2) |
| src/data/order_flow.py | OFI + VPINCalculator |
| src/data/dex_feed.py | DEX 가격 피드 (CoinGecko fallback) |
| src/backtest/walk_forward.py | WalkForwardOptimizer (D3) |
| src/ml/trainer.py | WalkForwardTrainer (RF) |
| src/ml/lstm_model.py | LSTMSignalGenerator (PyTorch/numpy) |
| src/ml/hmm_model.py | HMMRegimeDetector (E1) |
| src/ml/heston_model.py | HestonVolatilityModel (F2, numpy only) |
| src/strategy/regime_adaptive.py | E1: HMM 레짐 적응형 |
| src/strategy/funding_carry.py | E2: Funding Cash-and-Carry |
| src/strategy/lob_strategy.py | E3: LOB OFI + VPIN |
| src/strategy/heston_lstm_strategy.py | F2: Heston-LSTM 하이브리드 |
| src/strategy/cross_exchange_arb.py | F3: CEX vs DEX 차익 |
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
```

## Phase 전체 완료 이력

| Phase | 내용 | 테스트 |
|---|---|---|
| 인프라 | BotOrchestrator, BacktestEngine, RiskManager, Dashboard, Telegram | ✅ |
| A | FundingRate, ResidualMeanReversion, PairTrading | ✅ |
| B | SentimentFetcher, OnchainFetcher, NewsMonitor, MarketContext | ✅ |
| C | FeatureBuilder, WalkForwardTrainer, MLRFStrategy, LLMAnalyst, auto-tournament | ✅ |
| D | MultiLLMEnsemble, BinanceWebSocket, WalkForwardOptimizer, LSTM, OrderFlow | ✅ |
| E1 | HMM Regime-Adaptive (Sharpe 1.8~2.5) | ✅ 8 passed |
| E2 | Funding Carry Cash-and-Carry (Sharpe 2.0~5.0) | ✅ 9 passed |
| E3 | LOB OFI + VPIN Market Making (Sharpe 1.5~3.0) | ✅ 8 passed |
| F1 | LLM 멀티에이전트 분리 — SpecialistEnsemble (Technical/Sentiment/Onchain) | ✅ 15 passed |
| F2 | Heston-LSTM 하이브리드 (Sharpe 1.8~2.1, Springer 2026) | ✅ 11 passed |
| F3 | DEX/CEX 차익 — CrossExchangeArbStrategy (CoinGecko fallback) | ✅ 11 passed |
| **합계** | **356 passed, 11 skipped** | ✅ |
