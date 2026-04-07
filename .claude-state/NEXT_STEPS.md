# Next Steps

_Last updated: 2026-04-08_

## Status: Phase A + B + C + D 전체 완료 — 245 passed, 5 skipped

---

## 완료된 모든 Phase

### 인프라 (Phase 1~5)
- [x] BotOrchestrator, TradingPipeline, BacktestEngine
- [x] RiskManager + CircuitBreaker (hard-coded, LLM 개입 없음)
- [x] Strategy Tournament (병렬 백테스트 → Sharpe 순위)
- [x] PositionTracker, DailyPnL, MultiBot (심볼별 스레드)
- [x] Dashboard (stdlib HTTP, 30s auto-refresh)
- [x] Telegram 알림, CandleScheduler

### Phase A — 신규 전략 3종
- [x] A1. FundingRateStrategy: 펀딩비 역추세 (Sharpe 1.66~3.5)
- [x] A2. ResidualMeanReversionStrategy: BTC-neutral rolling OLS z-score
- [x] A3. PairTradingStrategy: BTC-ETH Engle-Granger 공적분

### Phase B — 알파 소스 확장
- [x] B1. SentimentFetcher: Fear&Greed + 펀딩비/OI
- [x] B2. OnchainFetcher: blockchain.com + Glassnode
- [x] B3. NewsMonitor: CryptoPanic HIGH/MEDIUM/LOW 분류
- [x] MarketContext: B1~B3 통합, confidence 자동 조정, HIGH → 진입 차단

### Phase C — ML/LLM 고도화
- [x] C1. FeatureBuilder + WalkForwardTrainer + MLRFStrategy (RandomForest)
- [x] C2. LLMAnalyst: Claude API 분석 (주문 금지)
- [x] C3. Auto-tournament: 72사이클마다 전략 자동 재평가

### Phase D — 인프라 고도화
- [x] D1. MultiLLMEnsemble: Claude + GPT-4o 합의 신호, 충돌 시 HOLD
- [x] D2. BinanceWebSocketFeed: 실시간 캔들, 자동 재연결, REST fallback
- [x] D3. WalkForwardOptimizer: IS/OOS 파라미터 최적화, 과최적화 감지
- [x] LSTM: PyTorch 2-layer + numpy fallback (torch 없어도 동작)

---

## STRATEGY_REGISTRY (6종)
| 이름 | 전략 |
|---|---|
| ema_cross | EMA20/50 크로스 |
| donchian_breakout | 20바 Donchian 돌파 |
| funding_rate | 펀딩비 역추세 |
| residual_mean_reversion | BTC-neutral 잔차 z-score |
| pair_trading | BTC-ETH 스프레드 |
| ml_rf | RandomForest ML |

---

## 전체 실행 명령어
```bash
# 데모 (API 키 없이 전체 체험)
python3 main.py --demo --tournament --dashboard

# WebSocket + 앙상블 + Walk-Forward 최적화 후 루프
python3 main.py --websocket --ensemble --walk-forward --loop --dashboard

# 실거래 (API 키 필요, backtest gate 자동)
python3 main.py --live --tournament --loop --dashboard

# 선택적 기능
pip install websockets    # D2 WebSocket
pip install torch         # LSTM PyTorch
pip install scikit-learn  # ML RandomForest
pip install openai        # D1 GPT-4o 앙상블
```

## 선택적 의존성 (없어도 동작)
| 패키지 | 기능 |
|---|---|
| scikit-learn | RandomForest 학습 |
| torch | LSTM (없으면 numpy fallback) |
| websockets | Binance WebSocket (없으면 REST) |
| openai | GPT-4o 앙상블 (없으면 Claude 단독) |
| anthropic | Claude 분석/앙상블 (없으면 mock) |
