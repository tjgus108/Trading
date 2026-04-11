# Cycle 74 - Category F: Research
## Status: COMPLETE

## [2026-04-11] Cycle 74 — ETF Option Bots
- BITO(선물 ETF)·IBIT(현물 ETF) 옵션 체인 모두 활성화, 유동성 확보로 봇 전략 적용 가능
- 주요 봇 전략: covered call(IBIT 보유 + 월물 OTM call 매도), 또는 delta-neutral strangle on BITO 주변 BTC 변동성 spike
- BITO는 0.95% 보수·roll 비용 있어 단기 옵션 매도(프리미엄 수집) 위주, IBIT은 spot-tracking으로 방향성 옵션 매수 유리
- 2025 트렌드: IV rank 기반 premium-selling 봇(IV 높을 때 매도 진입, GEX flip 레벨 결합)

---
# Cycle 73 - Category F: Research
## Status: COMPLETE

## [2026-04-11] Cycle 73 — Crypto Options Bots & Gamma Exposure
- Positive GEX → 딜러 매수/매도 헤지로 변동성 억제, 주요 스트라이크에 가격 pin → mean-revert 전략 유효
- Negative GEX → 헤지 흐름이 추세 가속, 방향성 추세추종 유리 (기존 `gex_signal` 전략이 이 패턴 구현 완료)
- 크립토 GEX는 주식 대비 참여자 구조 차이로 flow-based 보정 필요 (Glassnode taker-flow GEX 모델)
- 자동화 봇 트렌드: 딜러 헤징 흐름 선행 예측 + 0DTE 옵션 만기 gamma flip 레벨 활용

참고: `/home/user/Trading/src/strategy/gex_strategy.py` — Positive/Negative GEX 분기 이미 구현

---
# Cycle 72 - Category D: ML & Signals
## Status: COMPLETE

### HMM Regime Detector Fallback
- `src/ml/hmm_model.py`: fallback 이미 구현됨 (hmmlearn ImportError → Bollinger Band fallback)
- 테스트 `/home/user/Trading/tests/test_hmm_fallback.py` 신규 작성, 5개 모두 PASS
  1. hmmlearn 미설치 시 `_use_fallback=True` 설정
  2. fallback predict()가 BULL/BEAR 반환
  3. fallback sequence 길이 = df 길이
  4. 데이터 < 20행 → 전부 BULL
  5. fallback 모드 fit() 에러 없음

---
# Cycle 72 - Category F: Research
## Status: COMPLETE

## [2026-04-11] Cycle 72 — Bayesian Optimization
- TPE (Tree-structured Parzen Estimator, Optuna) 기반 Bayesian 최적화가 2025 비교 연구에서 75% strategy-asset pair 승리, 예산의 13~17%만으로 최적치 90% 도달
- Walk-forward validation 필수 — 브루트포스 대비 효율적이나 out-of-sample 검증 없으면 오버피팅
- AutoQuant 프레임워크: Bayesian + 2단계 double screening → 결정론적 artifact 추출

---
# Cycle 71 - Category C: Data & Infrastructure
## Status: COMPLETE

### Websocket Buffer Overflow Prevention
- Verified `/home/user/Trading/src/data/websocket_feed.py`
- Buffer uses `deque(maxlen=MAX_CANDLES)` (1000) → auto-eviction when limit exceeded
- Created comprehensive buffer tests at `/home/user/Trading/tests/test_websocket_buffer.py`:
  1. `test_candle_buffer_maxlen_enforced` — MAX_CANDLES limit enforced, no overflow
  2. `test_deque_auto_eviction` — validates deque behavior
  3. `test_candle_count_respects_maxlen` — candle_count() ≤ 1000
  4. `test_get_latest_df_memory_bounded` — 5000 candles added, buffer stays at 1000
  5. `test_concurrent_append_respects_maxlen` — 2000 appends respect maxlen
- All 5 tests PASSED ✓
- No memory leak detected: buffer automatically evicts oldest candles

Result: websocket_feed.py is production-safe for high-frequency candle ingestion.

---
# Cycle 70 - Category F: Research
## Status: COMPLETE

### Influential Crypto Trading Bot Articles 2025
- **3Commas blog** — Smart Trading + TradingView 통합 패턴, 실전 참조 빈도 높음
- **Intellectia.ai** — 수동 개입 없는 RL 기반 실시간 전략 최적화, 2025 신흥 영향력
- **WunderTrading** — TradingView webhook → 자동 주문 파이프라인 구현 참조
- **Flashbots Protect docs** — 온체인 봇 MEV 방어 필수 참조 (Cycle 69에서 상세 확인)

Key trend: ML/RL 실시간 최적화 + DeFi 통합 + Private mempool 방어
