# 오늘의 에이전트 작업 계획

_작성일: 2026-04-08_

---

## 현재 상태 요약

Phase A~D 전체 구현 완료. 245 tests passed.
- 전략 6종 (ema_cross, donchian_breakout, funding_rate, residual_mean_reversion, pair_trading, ml_rf)
- B: 감성/온체인/뉴스 MarketContext
- C: RandomForest, LSTM, LLMAnalyst, C3 auto-tournament
- D: MultiLLMEnsemble, WebSocketFeed, WalkForwardOptimizer

---

## 오늘 에이전트별 할 일

### strategy-researcher-agent (Sonnet)
**태스크: RSI Divergence + BB Squeeze 전략 구현**
- `src/strategy/rsi_divergence.py` 구현
  - 원리: 가격 신고점인데 RSI 저점 → Bearish Divergence (SELL)
  - 가격 신저점인데 RSI 고점 → Bullish Divergence (BUY)
  - lookback: 5~20봉
- `src/strategy/bb_squeeze.py` 구현
  - 원리: Bollinger Band 폭이 좁아지면(Squeeze) 변동성 폭발 임박
  - BB width < 20% percentile → 대기, Keltner Channel 내부 → Squeeze ON
  - Squeeze 해제 방향으로 진입
- STRATEGY_REGISTRY 등록
- 테스트 파일 작성
- **완료 파일**: src/strategy/rsi_divergence.py, src/strategy/bb_squeeze.py

### backtest-agent (Haiku)
**태스크: 전략 6종 + 신규 2종 백테스트 결과 보고**
- MockExchangeConnector로 BTC/USDT 1h 1000캔들 시뮬레이션
- 각 전략 BacktestEngine.run() 실행
- PASS/FAIL 판정 + Sharpe/MDD/PF 수치 보고
- 결과를 `.claude-state/BACKTEST_REPORT.md`에 저장

### reviewer (Haiku)
**태스크: Phase D 신규 파일 코드 리뷰**
- `src/alpha/ensemble.py` — 앙상블 합의 로직 검토
- `src/data/websocket_feed.py` — 재연결/스레드 안전성 검토
- `src/backtest/walk_forward.py` — 과최적화 방지 로직 검토
- `src/ml/lstm_model.py` — numpy fallback 정확도 검토
- 결과: `.claude-state/REVIEW_REPORT.md`에 저장

### ml-agent (Sonnet)
**태스크: ML 학습 스크립트 + LSTM 통합**
- `scripts/train_ml.py` 작성
  - argparse: --symbol, --timeframe, --model (rf|lstm), --limit
  - MockConnector로 데이터 fetch → FeatureBuilder → WalkForwardTrainer
  - 학습 후 models/ 자동 저장
  - LSTM 분기 처리 (torch 없으면 numpy fallback)
- `src/strategy/lstm_strategy.py` 작성
  - MLRFStrategy 패턴으로 LSTMSignalGenerator 래핑
  - STRATEGY_REGISTRY에 "ml_lstm"으로 등록
- 테스트 작성

### data-agent (Haiku)
**태스크: Order Flow Imbalance 실시간 감지**
- `src/data/order_flow.py` 작성
  - Binance REST로 orderbook depth 조회 (무료)
  - bid_volume vs ask_volume 불균형 계산
  - OFI score [-3, +3] 반환
  - MarketContext에 통합 가능한 인터페이스
- `src/data/feed.py`에 `fetch_order_flow()` 추가 (선택)
- 테스트 작성

---

## 병렬 실행 우선순위

| 우선순위 | 에이전트 | 예상 소요 | 의존성 |
|---|---|---|---|
| 1 | strategy-researcher-agent | 높음 | 없음 |
| 1 | reviewer | 중간 | 없음 |
| 1 | ml-agent | 높음 | 없음 |
| 1 | data-agent | 중간 | 없음 |
| 2 | backtest-agent | 중간 | strategy-researcher 완료 후 |

---

## 완료 기준

- [ ] rsi_divergence.py + bb_squeeze.py 구현 + 테스트
- [ ] STRATEGY_REGISTRY 8종으로 확장
- [ ] BACKTEST_REPORT.md 생성
- [ ] REVIEW_REPORT.md 생성
- [ ] scripts/train_ml.py 작동
- [ ] lstm_strategy.py 구현
- [ ] order_flow.py 구현
- [ ] 전체 테스트 통과

완료 후 NEXT_STEPS.md 업데이트.
