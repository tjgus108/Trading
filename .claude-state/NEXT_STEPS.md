# Next Steps

_Last updated: 2026-04-09_

## Status: **560 passed** | 전략 22종 | Phase G~L 완료

## 최근 작업 (2026-04-09) — 시장 레짐 자동 감지 추가

- `src/analysis/regime_detector.py` 신규: `SimpleRegimeDetector.detect()` (EMA50 기울기, bull/bear/sideways/unknown)
- `src/orchestrator.py`:
  - `from src.analysis.regime_detector import SimpleRegimeDetector` import 추가
  - `run_once()`: pipeline 실행 전 data fetch → regime 감지 → `logger.info("Market regime: %s", regime)`
  - `run_tournament()`: 토너먼트 시작 전 동일하게 regime 감지 로그
- `tests/test_regime_detector.py` 신규: 5개 테스트 (bull/bear/sideways/데이터부족/None) 전부 통과

## 이전 작업 (2026-04-09) — RSI Divergence 버그 수정

- `src/strategy/rsi_divergence.py`:
  - 버그: 임의 row 비교 → swing high/low pivot 확인 (`_is_swing_high`, `_is_swing_low`)
  - 버그: 첫 매칭 즉시 return → best divergence % 선택으로 변경 (가장 강한 신호 우선)
  - 추가: RSI zone 필터 (bearish ≥55, bullish ≤45) — 과잉 신호 억제
  - 추가: 최소 간격 `_MIN_GAP=3`, lookback `_LOOKBACK_MAX` 15→20 확장
- `tests/test_new_strategies.py`: 테스트 픽스처 개선 (swing pivot + RSI zone 조건 충족)
- 555 passed, 11 skipped. commit + push 완료.

## 이전 작업 (2026-04-09) — 토너먼트 상관관계 경고 + BacktestReport 연결

- `src/orchestrator.py`: `run_tournament()` 완료 후 `_check_top3_correlation()` 호출
  - 상위 3개 전략 win_rate 기반 신호 시뮬레이션 → SignalCorrelationTracker 사용
  - |r| ≥ 0.7 쌍 발견 시 `logger.warning(...)` 출력
- `src/backtest/report.py`: `BacktestReport.from_backtest_result()` classmethod 추가
  - BacktestEngine.BacktestResult → BacktestReport 직접 변환
- `tests/test_phase_j.py`: `test_from_backtest_result` 테스트 추가
- `tests/test_tournament.py`: 상관관계 체크 호출 테스트 2개 추가
- 36 passed. commit + push 완료.

## 이전 작업 (2026-04-09) — SuperTrend 토너먼트 포함 확인 + multiplier 2.5 조정

- 토너먼트 참여 확인: `_EXCLUDE_FROM_TOURNAMENT`에 supertrend 없음 (이미 포함됨)
- `src/strategy/supertrend.py`: multiplier 기본값 3.0 → 2.5 (신호 빈도 증가)
- `tests/test_supertrend.py`: multiplier 값 일치 업데이트
- 553 passed, 11 skipped. commit + push 완료.

## 이전 작업 (2026-04-09) — VWAPReversionStrategy 신규 추가

- `src/strategy/vwap_reversion.py` 신규: VWAPReversionStrategy (name="vwap_reversion")
  - BUY: close < vwap*0.995 AND rsi14 < 35, HIGH if rsi < 25
  - SELL: close > vwap*1.005 AND rsi14 > 65, HIGH if rsi > 75
  - 최소 50행 필요
- `src/orchestrator.py`: VWAPReversionStrategy import + STRATEGY_REGISTRY 등록
- `tests/test_vwap_reversion.py` 신규: 9개 테스트 전부 통과
- 전체 552 passed, 11 skipped. commit + push 완료.

## 이전 작업 (2026-04-09) — bb_squeeze squeeze percentile 완화

- `src/strategy/bb_squeeze.py`: `_SQUEEZE_PERCENTILE` 20 → 30 (신호 빈도 증가)
- 토너먼트 FAIL 원인: trades=11 < MIN_TRADES=15. percentile 완화로 squeeze 조건 더 자주 충족
- 테스트 543개 전부 통과. commit + push 완료.

## 이전 작업 (2026-04-08) — SuperTrend 전략 추가 (6 new tests)

- `src/strategy/supertrend.py` 신규: SuperTrendStrategy (ATR 기반 추세 전환, period=10, multiplier=3.0)
- `src/orchestrator.py`: SuperTrendStrategy import + STRATEGY_REGISTRY "supertrend" 등록
- `tests/test_supertrend.py` 신규: 6개 테스트 (이름, BUY/SELL/HOLD 신호, 데이터 부족, signal 필드)

## 이전 작업 (2026-04-08) — bb_squeeze 완화 + MIN_TRADES 조정 (537 tests)

- `src/backtest/engine.py`: MIN_TRADES 30 → 15 (고품질 저빈도 전략 허용)
- `src/strategy/bb_squeeze.py`: squeeze release 시 price inside bands에도 mid 기준 BUY/SELL MEDIUM 신호 추가 (신호 빈도 대폭 증가)

## 이전 작업 (2026-04-08) — Phase G~L 완료 (537 tests)

### Phase H — 고급 리스크 & 적응형 전략 선택
- H1: KellySizer 파이프라인 통합 (거래 이력 10건 이상 시 position_size 재계산)
- H2: `src/strategy/adaptive_selector.py`: AdaptiveStrategySelector (rolling Sharpe 가중치, 14개 테스트)
- H3: PortfolioOptimizer VaR95/CVaR95 추가 (Expected Shortfall, 4개 테스트)
- H4: TWAPExecutor 파이프라인 통합 (대형 주문 분할 실행)

### Phase I — 복수 전략 & 리스크 모니터링
- I1: `src/strategy/multi_signal.py`: MultiStrategyAggregator (confidence 가중 투표, 10개 테스트)
- I2: `src/risk/drawdown_monitor.py`: DrawdownMonitor (peak 추적, MDD 초과 차단, 8개 테스트)
- I3: `src/risk/vol_targeting.py`: VolTargeting (목표 변동성 기반 사이즈 조정, 7개 테스트)

### Phase J — 백테스트 강화 & 분석
- J1: `src/backtest/monte_carlo.py`: MonteCarlo Block Bootstrap (8개 테스트)
- J2: `src/backtest/report.py`: BacktestReport (Sharpe/Calmar/MDD/win_rate, 9개 테스트)
- J3: `src/analysis/strategy_correlation.py`: SignalCorrelationTracker (9개 테스트)

### Phase K — 이상치 감지 & 포지션 건강
- K1: `src/monitoring/anomaly_detector.py`: AnomalyDetector (Z-score/IQR/return spike, 8개 테스트)
- K2: `src/monitoring/position_health.py`: PositionHealthMonitor (HEALTHY/WARNING/CRITICAL, 8개 테스트)

### Phase L — 통합 배선
- Orchestrator: DrawdownMonitor 자동 체크 (MDD 초과 → BLOCKED)
- Pipeline: VolTargeting 선택적 연결 (Kelly 이후 적용)

## 이전 작업 (2026-04-08) — Phase G 완료 (454 tests)

### G1 — SpecialistEnsemble 파이프라인 연결
- `src/pipeline/runner.py`: specialist_ensemble attr + 충돌 감지 HOLD 로직
- `src/orchestrator.py`: funding rate auto-inject, attach_specialist() 공개 메서드

### G2 — GEX Signal + CME Basis Spread 전략
- `src/data/options_feed.py` 신규: GEXFeed, CMEBasisFeed, mock() 지원
- `src/strategy/gex_strategy.py` 신규: GEXStrategy (name="gex_signal")
- `src/strategy/cme_basis_strategy.py` 신규: CMEBasisStrategy (name="cme_basis")
- `tests/test_gex_cme.py` 신규: 14개 테스트

### G3 — 멀티에셋 포트폴리오 최적화기
- `src/risk/portfolio_optimizer.py` 신규: mean_variance / risk_parity / equal_weight (scipy 금지, numpy only)
- `tests/test_portfolio_optimizer.py` 신규: 12개 테스트

### G4 — DataFeed 캐싱 + 통합 테스트
- `src/data/feed.py`: cache_ttl + _fetch_fresh() + invalidate_cache()
- `tests/integration/test_full_pipeline.py` 신규: 4개 통합 테스트

### 수정사항
- Python 3.9 type hint 호환 (`Optional[X]` 사용)
- RiskResult 테스트 mock 누락 필드 추가

## 이전 작업 (2026-04-08) — G4 DataFeed 캐싱 + 통합 테스트
- `src/data/feed.py`: `import time` 추가, `__init__`에 `cache_ttl` 파라미터 + `_cache` dict 추가
- `fetch()` → 캐시 히트/미스 로직으로 교체, 기존 로직은 `_fetch_fresh()`로 이름 변경
- `invalidate_cache(symbol, timeframe)` 메서드 추가 (전체/부분 무효화)
- `tests/integration/test_full_pipeline.py` 신규 생성: 4개 통합 테스트 (EMA 백테스트, 캐시, 토너먼트, walk-forward)

## 이전 작업 (2026-04-08)
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

## STRATEGY_REGISTRY (현재 19종)
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
| vwap_reversion | VWAP 이탈 + RSI 회귀 (약세장용) | ✅ |

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
