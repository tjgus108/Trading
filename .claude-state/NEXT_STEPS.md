# Next Steps

_Last updated: 2026-04-08_

## Status: Phase A~F 전체 완료 — 전략 15종 | CircuitBreaker 상태 추적 활성화 + 전략 IndexError 방어 완료

## 최근 작업 (2026-04-08)
- CircuitBreaker.reset_daily(): `_consecutive_losses` 초기화 추가
- RiskManager.reset_daily(): CircuitBreaker에 위임하는 메서드 추가
- PipelineResult: `pnl: float = 0.0` 필드 추가
- BotOrchestrator: `_last_run_date` + 자정 감지 → reset_daily() 호출, circuit_breaker.record_trade_result() 연동
- rsi_divergence.py: `df is None` 체크 + 데이터 부족 시 entry_price=0.0 반환
- regime_adaptive.py: `df is None` 체크, 체크를 generate() 맨 앞으로 이동
- pair_trading.py: BTC df + ETH df 최소 30행 체크 추가
- tests/test_risk_manager.py: 신규 생성 (14개 테스트)
- tests/test_new_strategies.py: 데이터 부족 HOLD 테스트 + reset_daily 테스트 추가

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
- [x] rsi_divergence, bb_squeeze, OrderFlowFetcher, scripts/train_ml.py
- [x] 코드 리뷰: eval→ast.literal_eval, torch.load, best_state unbound 수정
- [x] README.md 사용 매뉴얼 작성 (13섹션)

---

## STRATEGY_REGISTRY (현재 9종 → Phase E 완료 후 12종)
| 이름 | 전략 | 상태 |
|---|---|---|
| ema_cross | EMA20/50 크로스 | ✅ |
| donchian_breakout | 20바 Donchian 돌파 | ✅ |
| funding_rate | 펀딩비 역추세 | ✅ |
| residual_mean_reversion | BTC-neutral 잔차 z-score | ✅ |
| pair_trading | BTC-ETH 스프레드 | ✅ |
| ml_rf | RandomForest ML | ✅ |
| ml_lstm | LSTM ML (PyTorch / numpy fallback) | ✅ |
| rsi_divergence | RSI 다이버전스 | ✅ |
| bb_squeeze | Bollinger Band Squeeze 돌파 | ✅ |
| regime_adaptive | HMM 레짐 적응형 RF | ✅ E1 완료 |
| funding_carry | Funding Rate Cash-and-Carry | ✅ E2 완료 |
| lob_maker | LOB OFI 마켓메이킹 | 🔨 E3 구현 중 |

---

## Phase E — 전략 고도화 (리서치 기반, 2026-04-08 착수)

### E1. HMM Regime-Adaptive Strategy (Sharpe 1.8~2.5)
- **근거**: Preprints.org 2026.03, IDS2025 — 약세장 단독 Sharpe 2.24 실증
- **방법**: hmmlearn 2-state HMM(bull/bear) → 레짐별 RF 전문가 분리 훈련
- **파일**: `src/strategy/regime_adaptive.py`, `src/ml/hmm_model.py`
- **의존성**: `pip install hmmlearn` (없으면 볼린저 기반 fallback)

### E2. Funding Rate Cash-and-Carry (Sharpe 2.0~5.0)
- **근거**: ScienceDirect 2025 — 스팟 롱 + 퍼프 숏으로 펀딩비 수집 (시장중립)
- **방법**: 펀딩비 > threshold → 스팟 매수 + 선물 숏, 펀딩비 지급 시 청산
- **파일**: `src/strategy/funding_carry.py` (신규)
- **특징**: 기존 funding_rate.py와 달리 방향성 없음, 순수 차익거래

### E3. OFI LOB Market Making (Sharpe 1.5~3.0)
- **근거**: arxiv 2506.05764, EFMA 2025 — OFI AUC>0.55 예측력 실증
- **방법**: Binance depth WebSocket → VPIN 계산 → OFI 신호 → 마켓메이킹
- **파일**: `src/data/order_flow.py` (VPIN 추가), `src/strategy/lob_strategy.py`
- **특징**: 현재 order_flow.py stub 완성

---

## Phase F — 인프라 고도화 (장기)

### F1. LLM 멀티에이전트 분리 (FLAG-Trader 패턴)
- `src/alpha/llm_analyst.py` → 3개 전문 에이전트로 분리
  - TechnicalAnalystAgent (TA 신호 해석)
  - SentimentAnalystAgent (Fear&Greed, 뉴스)
  - OnchainAnalystAgent (온체인 지표)
- 합의 점수 기반 최종 신호

### F2. Heston-LSTM 하이브리드 ✅ 완료 (2026-04-08)
- `src/ml/heston_model.py`: Heston 확률 변동성 파라미터 추정 (numpy only)
- `src/strategy/heston_lstm_strategy.py`: LSTM + Heston fallback 전략
- `tests/test_heston_lstm.py`: 10개 테스트
- STRATEGY_REGISTRY: "heston_lstm" 등록
- **근거**: Springer Nature 2026.02 — Sharpe 2.1, MDD 4.2% 실증

### F3. DEX/CEX 차익 인프라 ✅ 완료 (2026-04-08)
- `src/data/dex_feed.py`: CoinGecko fallback DEX 가격 피드, 60초 캐시, mock 지원
- `src/strategy/cross_exchange_arb.py`: CEX vs DEX 스프레드 기반 차익 전략
- `tests/test_cross_exchange_arb.py`: 11개 테스트 (mock 주입, HTTP 없음)
- STRATEGY_REGISTRY: "cross_exchange_arb" 등록
- **패턴**: Hummingbot XEMM 참조, BUY_DEX/SELL_DEX 방향성 신호

---

## 전체 실행 명령어
```bash
# 데모
python3 main.py --demo --tournament --dashboard

# 풀 스택
python3 main.py --live --websocket --ensemble --walk-forward --loop --dashboard

# ML 학습
python3 scripts/train_ml.py --demo --model rf
python3 scripts/train_ml.py --demo --model lstm

# 의존성
pip install hmmlearn    # E1 HMM
pip install websockets  # D2 WebSocket
pip install torch       # LSTM PyTorch
pip install scikit-learn
pip install openai
pip install anthropic
```
