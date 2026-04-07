# Next Steps

_Last updated: 2026-04-08_

## Status: Phase A + B + C 완료 — 테스트 204 passed, 5 skipped

---

## 완료된 작업 (전체)

### 인프라 (Phase 1~5)
- [x] BotOrchestrator, TradingPipeline, BacktestEngine
- [x] RiskManager + CircuitBreaker
- [x] Strategy Tournament (병렬 백테스트 → Sharpe 순위)
- [x] PositionTracker, DailyPnL, MultiBot
- [x] Dashboard (stdlib HTTP, 30s auto-refresh)
- [x] Telegram 알림, CandleScheduler

### Phase A — 신규 전략 3종
- [x] A1. FundingRateStrategy: 펀딩비 역추세 (Sharpe 1.66~3.5)
- [x] A2. ResidualMeanReversionStrategy: BTC-neutral rolling OLS z-score (Sharpe 2.3)
- [x] A3. PairTradingStrategy: BTC-ETH Engle-Granger 공적분 (Sharpe 2.45)
- [x] STRATEGY_REGISTRY 등록 (tournament 자동 참여)

### Phase B — 알파 소스 확장
- [x] B1. SentimentFetcher: Fear&Greed (alternative.me) + 펀딩비/OI (Binance)
- [x] B2. OnchainFetcher: blockchain.com + Glassnode (exchange flow/whale/NVT)
- [x] B3. NewsMonitor: CryptoPanic, HIGH/MEDIUM/LOW 키워드 분류, HIGH 콜백
- [x] MarketContext + MarketContextBuilder: B1~B3 통합, 신호 confidence 조정
- [x] TradingPipeline: MarketContext 통합 (context_score, news_risk 필드)
- [x] HIGH 뉴스 → 신규 진입 자동 차단, 포지션 축소 권고

### Phase C — ML/LLM 고도화
- [x] C1. FeatureBuilder: 15개 피처 (수익률/모멘텀/변동성/추세/볼륨/Donchian/VWAP)
- [x] C1. MLSignalGenerator: RandomForest, pkl 로드, predict()
- [x] C1. WalkForwardTrainer: 60/20/20 시계열 분할, test acc > 55%
- [x] C1. MLRFStrategy: BaseStrategy 호환, STRATEGY_REGISTRY 등록 ("ml_rf")
- [x] C2. LLMAnalyst: Claude API (Haiku/Sonnet 라우팅), 분석만 (주문 금지)
- [x] C3. Auto-tournament: 72사이클마다 전략 자동 재평가

---

## 현재 STRATEGY_REGISTRY (6종)
| 이름 | 전략 | 특이사항 |
|---|---|---|
| ema_cross | EMA20/50 크로스 | 기본 |
| donchian_breakout | 20바 돌파 | 기본 |
| funding_rate | 펀딩비 역추세 | update_funding_rate() 주입 필요 |
| residual_mean_reversion | BTC-neutral 잔차 z-score | set_btc_data() 주입 권장 |
| pair_trading | BTC-ETH 스프레드 | set_eth_data() 주입 필수 |
| ml_rf | RandomForest | models/ pkl 자동 로드 |

---

## 남은 Phase D (장기)
- [ ] D1. 멀티 LLM 앙상블 (Claude + GPT-4o 합의 진입)
- [ ] D2. WebSocket 실시간 피드 (REST → Binance WebSocket)
- [ ] D3. Walk-Forward 최적화 (파라미터 자동 튜닝)
- [ ] ML 고도화: LSTM 시계열 패턴 학습

## ML 모델 학습 방법
```bash
# scikit-learn 설치 필요
pip install scikit-learn

# 학습 스크립트 (Python REPL)
from src.data.feed import DataFeed
from src.exchange.mock_connector import MockExchangeConnector
from src.ml.trainer import WalkForwardTrainer

conn = MockExchangeConnector("BTC/USDT")
conn.connect()
feed = DataFeed(conn)
summary = feed.fetch("BTC/USDT", "1h", limit=1000)

trainer = WalkForwardTrainer(symbol="BTC/USDT")
result = trainer.train(summary.df)
print(result.summary())
if result.passed:
    trainer.save()  # models/rf_btcusdt_<date>.pkl
```

## 사용법
```bash
# 데모 (API 키 불필요)
python3 main.py --demo

# 토너먼트 (6전략 병렬 백테스트 → 자동 선택)
python3 main.py --tournament --demo

# 토너먼트 + 루프 + 대시보드
python3 main.py --tournament --loop --dashboard --demo

# 실거래 (API 키 필요, backtest gate 자동 실행)
python3 main.py --live --loop --dashboard
```
