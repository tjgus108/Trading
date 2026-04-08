# Next Steps

_Last updated: 2026-04-08_

## Status: **541 passed / 1 failed** | 전략 17종 | Phase A~L 완료

### 테스트 현황
- 541 passed, 1 failed (pair_trading spread extreme low), 6 skipped
- 실패 테스트: `tests/test_phase_a_strategies.py::TestPairTradingStrategy::test_buy_when_spread_extreme_low`

---

## 전략 목록 (17종)

| # | name | 전략 | 파일 |
|---|---|---|---|
| 1 | ema_cross | EMA20/50 크로스 | ema_cross.py |
| 2 | donchian_breakout | 20바 Donchian 돌파 | donchian_breakout.py |
| 3 | funding_rate | 펀딩비 역추세 | funding_rate.py |
| 4 | residual_mean_reversion | BTC-neutral 잔차 z-score | residual_mean_reversion.py |
| 5 | pair_trading | BTC-ETH 스프레드 | pair_trading.py |
| 6 | ml_rf | RandomForest ML | ml_strategy.py |
| 7 | ml_lstm | LSTM ML (PyTorch/numpy) | lstm_strategy.py |
| 8 | rsi_divergence | RSI 다이버전스 | rsi_divergence.py |
| 9 | bb_squeeze | Bollinger Band Squeeze | bb_squeeze.py |
| 10 | funding_carry | Funding Cash-and-Carry | funding_carry.py |
| 11 | regime_adaptive | HMM 레짐 적응형 RF | regime_adaptive.py |
| 12 | lob_maker | LOB OFI 마켓메이킹 | lob_strategy.py |
| 13 | heston_lstm | Heston-LSTM 하이브리드 | heston_lstm_strategy.py |
| 14 | cross_exchange_arb | DEX/CEX 차익 | cross_exchange_arb.py |
| 15 | liquidation_cascade | 청산 캐스케이드 | liquidation_cascade.py |
| 16 | gex_signal | GEX 감마 노출 | gex_strategy.py |
| 17 | cme_basis | CME 베이시스 스프레드 | cme_basis_strategy.py |

---

## 완료된 Phase 요약

### 인프라 (Phase 1~5)
- [x] BotOrchestrator, TradingPipeline, BacktestEngine
- [x] RiskManager + CircuitBreaker
- [x] Strategy Tournament (병렬 백테스트 → Sharpe 순위)
- [x] PositionTracker, DailyPnL, MultiBot
- [x] Dashboard, Telegram 알림, CandleScheduler

### Phase A — 신규 전략 3종
- [x] FundingRate, ResidualMeanReversion, PairTrading

### Phase B — 알파 소스 확장
- [x] SentimentFetcher, OnchainFetcher, NewsMonitor, MarketContext

### Phase C — ML/LLM 고도화
- [x] RandomForest, LSTM, LLMAnalyst, Auto-tournament

### Phase D — 인프라 고도화
- [x] MultiLLMEnsemble, WebSocketFeed, WalkForwardOptimizer
- [x] RSI Divergence, BB Squeeze, OrderFlow, LSTM Strategy

### Phase E — 전략 고도화
- [x] E1: HMM Regime-Adaptive (hmmlearn)
- [x] E2: Funding Cash-and-Carry
- [x] E3: LOB OFI Market Making

### Phase F — 고급 모델/인프라
- [x] F1: LLM 멀티에이전트 (SpecialistEnsemble)
- [x] F2: Heston-LSTM 하이브리드
- [x] F3: DEX/CEX 차익 인프라

### Phase G — 포트폴리오 & 데이터
- [x] G1: SpecialistEnsemble 파이프라인 연결
- [x] G2: GEX + CME Basis 전략
- [x] G3: 멀티에셋 포트폴리오 최적화기
- [x] G4: DataFeed 캐싱 + 통합 테스트

### Phase H — 고급 리스크 & 적응형 선택
- [x] H1: KellySizer 파이프라인 통합
- [x] H2: AdaptiveStrategySelector
- [x] H3: VaR95/CVaR95
- [x] H4: TWAPExecutor 파이프라인 통합

### Phase I — 복수 전략 & 리스크 모니터링
- [x] I1: MultiStrategyAggregator
- [x] I2: DrawdownMonitor
- [x] I3: VolTargeting

### Phase J — 백테스트 강화 & 분석
- [x] J1: Monte Carlo Block Bootstrap
- [x] J2: BacktestReport (Sharpe/Calmar/MDD/win_rate)
- [x] J3: SignalCorrelationTracker

### Phase K — 이상치 감지 & 포지션 건강
- [x] K1: AnomalyDetector (Z-score/IQR/return spike)
- [x] K2: PositionHealthMonitor

### Phase L — 통합 배선
- [x] Orchestrator: DrawdownMonitor 자동 체크
- [x] Pipeline: VolTargeting 선택적 연결

---

## 다음 작업 후보 (미착수)

### Phase M — 안정화 & 버그 수정
- [ ] pair_trading 테스트 실패 수정 (spread extreme low)
- [ ] 전체 테스트 그린 달성

### Phase N — 라이브 준비
- [ ] 환경별 설정 분리 (dev/staging/prod)
- [ ] API 키 로테이션 & 보안 강화
- [ ] 로깅 표준화 (structured logging)
- [ ] 모니터링/알러팅 시스템 (Prometheus/Grafana 연동)
- [ ] Graceful shutdown & 재시작 복구

### Phase O — 성능 최적화
- [ ] 전략 실행 프로파일링 & 병목 제거
- [ ] 데이터 파이프라인 비동기화 (asyncio)
- [ ] 백테스트 병렬화 (multiprocessing)

### Phase P — 전략 추가 후보
- [ ] Orderbook Heatmap 전략
- [ ] Whale Alert 기반 전략
- [ ] Options IV Surface 전략
- [ ] Volume Profile / VWAP 전략

---

## 실행 명령어
```bash
# 데모
python3 main.py --demo --tournament --dashboard

# 풀 스택
python3 main.py --live --websocket --ensemble --walk-forward --loop --dashboard

# ML 학습
python3 scripts/train_ml.py --demo --model rf
python3 scripts/train_ml.py --demo --model lstm

# 테스트
python3 -m pytest tests/ -q

# 의존성
pip install numpy pandas ccxt python-dotenv scikit-learn
pip install hmmlearn    # E1 HMM
pip install websockets  # D2 WebSocket
pip install torch       # LSTM PyTorch (optional)
```
