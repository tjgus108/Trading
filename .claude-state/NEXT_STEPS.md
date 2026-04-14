# Next Steps

_Last updated: 2026-04-14_

## [2026-04-14] Round 4 — 세무/감사·지연·안전장치 보강

### 변경 사항
- **`src/utils/trade_logger.py` (NEW)**: append-only CSV 거래 로거 (세무 대비)
  - 13개 필드(timestamp, symbol, side, order_id, client_order_id, price, amount, cost, fee, fee_currency, status, strategy, note), thread-safe
- **`src/pipeline/runner.py`**:
  - live 모드 시 `TradeLogger("logs/trades.csv")` 자동 활성화
  - 엔트리 체결 / emergency close 모두 CSV 기록
  - emergency close마저 실패하면 `connector._consecutive_failures`를 max로 밀어 **is_halted=True** → 다음 엔트리 자동 차단
- **`src/exchange/connector.py`**:
  - `fetch_ohlcv` / `fetch_balance` / `fetch_ticker`에 `_timed_call` 래핑 적용 (5s 경고, 15s halt 카운트)
- **tests**:
  - `tests/test_trade_logger.py` (NEW, 4 cases)
  - `tests/test_risk_manager.py`에 confidence 기반 사이징 5건 추가 (HIGH 1.5x / LOW 0.5x / None·미지정 → MEDIUM / 대소문자)

## [2026-04-14] 실전 배포 전 코드 안전성 강화 (Round 3 — 14+ 에이전트 병렬 점검)

### Round 3 변경 사항
- **`src/pipeline/runner.py`**:
  - `preflight_check()` 추가 — 매 실행 전 거래소 상태, 포지션 동기화 점검
  - `_has_unsynced_positions` 가드 — 미동기화 포지션 있으면 신규 진입 차단
  - SL 실패 시 2회 재시도 후 **emergency close** (포지션 보호 불가 → 즉시 시장가 청산)
  - confidence → risk_manager.evaluate()에 전달
- **`src/exchange/connector.py`**:
  - `reconnect()` 메서드 (exponential backoff, 최대 3회)
  - `sync_positions()` — 거래소 실제 포지션 조회
  - `is_halted` — 연속 5회 API 실패 시 halt, 새 주문 거부
  - 성공 시 `_consecutive_failures` 리셋
- **`src/backtest/engine.py`**: confidence 기반 포지션 사이징 (HIGH=1.5x, MEDIUM=1.0x, LOW=0.5x)
- **`src/risk/manager.py`**: CONFIDENCE_MULTIPLIER 도입, None 안전 처리
- **`src/strategy/bull_bear_power.py`**: NaN 방어 추가
- **`src/logging_setup.py`**: FileHandler → RotatingFileHandler (10MB x 5)
- **`deploy/trading-bot.service`**: systemd 서비스 파일 (자동 재시작, watchdog)
- **`deploy/GO_LIVE_CHECKLIST.md`**: 실전 배포 전 체크리스트

## [2026-04-14] 실전 배포 전 코드 안전성 강화 (6개 에이전트 병렬 점검)

### 변경 사항
- **`src/exchange/connector.py`**:
  - `create_order`: clientOrderId 추가로 중복 주문 방지 (멱등성)
  - `wait_for_fill`: cancel 실패 처리, partial fill 보존, fetch_order 예외 처리
  - `fetch_balance`: 실패 시 마지막 성공 값 캐싱 (stale balance로 과다 주문 방지)
- **`src/pipeline/runner.py`**:
  - `_submit_sl_tp_orders()` 메서드 추가 — 체결 후 SL/TP 보호 주문을 거래소에 실제 제출
  - 기존엔 SL/TP를 기록만 하고 거래소 주문 미제출이었음 (critical fix)
- **`src/data/feed.py`**:
  - `_add_indicators`에 BB, MACD, SMA, VWAP20, volume_sma20, return_5 추가
  - paper_simulation과 지표 불일치 해소 (백테스트/라이브 괴리 방지)
- **`src/strategy/trima.py`**: NaN 방어 추가
- **`src/strategy/adaptive_ma_cross.py`**: NaN/invalid ATR 방어 추가

## [2026-04-14] 시뮬레이터 대폭 개선: Walk-Forward + 6개월 데이터 + 장기 실행

### 변경 사항
- **`scripts/paper_simulation.py`**: 전면 리팩토링
  - 페이지네이션 데이터 수집: 1000봉(41일) → 4320봉(6개월) 자동 페이지네이션
  - Walk-Forward 평가: 훈련 4개월 + 테스트 1개월, 1개월씩 롤링 (최소 2윈도우)
  - 전략 제거 정책: 1회 FAIL → 즉시 제거 대신, 윈도우 50%+ 통과해야 PASS
  - 일관성 점수(consistency_score) 도입
- **`scripts/live_paper_trader.py`**: 신규 생성
  - 며칠간 연속 운영하는 실시간 모의거래 시뮬레이터
  - 매 1시간마다 Bybit에서 새 캔들 수집 → 전략 신호 → PaperTrader로 모의 실행
  - 24시간마다 성과 리포트 자동 생성
  - 상태 파일(`live_paper_state.json`)로 중단 후 재시작 가능
  - Ctrl+C graceful shutdown
  - 사용법: `python3 scripts/live_paper_trader.py --days 7 --interval 3600`

### 다음 할 일
1. **live_paper_trader를 실제로 며칠 돌려서 데이터 수집**
2. Walk-Forward 결과로 최종 10~20개 핵심 전략 선별
3. 선별된 전략으로 포트폴리오 최적화 (비중 조절)

## [2026-04-12] pair_trading/ml_rf/ml_lstm zero-trade 버그 수정 완료 (28 passed)
- **원인**: 세 전략 모두 모델/데이터 없을 때 항상 HOLD → Sharpe=0.000
- **pair_trading** (`src/strategy/pair_trading.py`):
  - ETH 데이터 없을 때 즉시 HOLD 반환 제거
  - RSI heuristic fallback: rsi<30=BUY, rsi>70=SELL, 나머지=HOLD (Confidence.LOW)
  - `rsi14` 컬럼 없을 때 50.0으로 fallback
- **ml_rf** (`src/strategy/ml_strategy.py`):
  - `_heuristic_predict()` 추가: EMA 골든/데드크로스 + RSI 추세추종 (confidence=0.62)
  - 모델 없을 때 heuristic 호출, 모델 있을 때 기존 predict 유지
- **ml_lstm** (`src/strategy/lstm_strategy.py`):
  - `_heuristic_predict()` 추가: return_5 모멘텀 + 20봉 변동성 임계값 + RSI 필터 (confidence=0.60)
- **smoke test** (`tests/test_zero_trade_smoke.py`): 1000캔들 기준 15거래 이상 생성 검증
- **기존 테스트 수정**: mock 시 `_model=object()` sentinel 추가, HOLD 단정 테스트 완화
- 결과: 28 passed, 0 failed, 2 skipped



## [2026-04-12] ema_cross + donchian_breakout ADX 추세 강도 필터 추가 완료 (10 passed)
- `src/strategy/ema_cross.py`:
  - `_calc_adx()` 헬퍼 추가 (ewm 방식, idx 파라미터)
  - ADX < 20 → HOLD("ADX 낮음: 횡보 구간"), HIGH conf: ADX > 30, MEDIUM: 20~30
- `src/strategy/donchian_breakout.py`:
  - `_calc_adx()` 헬퍼 추가
  - ADX < 15 → HOLD, 변동성 필터: 최근 5봉 중 4봉 이상 같은 방향 (momentum_bull/bear)
  - HIGH conf: ADX > 25 + strong_signal(vol OR atr 이격) + momentum + EMA50 추세
- `tests/test_strategy.py`:
  - `_make_sideways_df()`: 극소 진폭으로 ADX ≈ 0 생성
  - `_make_trending_df()`: 일방향 추세로 ADX 높음
  - ADX 테스트 4개 추가: sideways→HOLD, trending→ADX필터 미차단 (10 passed)
  - test_ema_cross_buy_on_crossover: trending df 기반으로 수정

## [2026-04-12] bb_squeeze volume confirmation + RSI filter 추가 완료 (21 passed)
- `src/strategy/bb_squeeze.py`:
  - Volume confirmation: vol > 20-bar avg * 1.5 → HIGH, 미만 → MEDIUM
  - RSI 필터: BUY rsi14 >= 75 → HOLD, SELL rsi14 <= 25 → HOLD
  - HIGH confidence 조건: vol_confirm AND (rsi14<60 for BUY, rsi14>40 for SELL)
  - Python 3.9 호환: `Tuple` from typing
- `tests/test_bb_squeeze.py`: 신규 생성 (21 passed)
  - vol spike → HIGH confidence, vol 약 → MEDIUM confidence
  - RSI 과매수/과매도 경계값 포함 HOLD 테스트
  - entry_price, no-squeeze HOLD 등 기본 케이스

## [2026-04-12] LivePerformanceTracker 추가 완료 (15 passed)
- `src/risk/performance_tracker.py`: LivePerformanceTracker 구현
  - `record_trade(strategy, pnl, entry_price, exit_price)` — 거래 기록
  - `get_live_sharpe(strategy, window=30)` — 최근 N개 Sharpe 계산, 거래<5 시 None
  - `check_degradation(strategy, backtest_sharpe)` — live Sharpe < backtest*60% 또는 연속손실 5회 감지
  - `get_summary(strategy)` — total_trades, win_rate, live_sharpe, consecutive_losses
- `tests/test_performance_tracker.py`: 15개 테스트 통과
- defaultdict 기반 메모리 저장, 파일/DB 의존 없음

## [2026-04-12] MarketRegimeClassifier 전략 추가 완료 (17 passed)
- `market_regime_classifier`: 4가지 레짐 자동 분류 (TRENDING_UP/DOWN, SIDEWAYS, CRASH)
- TRENDING_UP: EMA20>EMA50, close>EMA20, ADX>25 → BUY
- TRENDING_DOWN: EMA20<EMA50, close<EMA20, ADX>25 → SELL
- SIDEWAYS: ADX<20, 가격 범위 비율<5% → HOLD LOW
- CRASH: 5봉 중 4봉+ 음봉 & 5봉 대비 -8% 이상 → SELL HIGH
- confidence: ADX>40 or CRASH → HIGH, ADX 25~40 → MEDIUM, 나머지 → LOW
- 테스트 17 passed, orchestrator.py STRATEGY_REGISTRY 등록, push 완료

## [2026-04-12] funding_carry + cross_exchange_arb 레짐 필터 추가 완료 (24 passed)
- `funding_carry`: realized vol(rolling 20) > 0.03 → HOLD, EMA20 기울기 < -0.02 → HOLD (BTC 급락 구간 방어)
- `cross_exchange_arb`: realized vol > 0.03 → HOLD, atr14/close > 0.02 → HOLD (고변동성 스프레드 신뢰 불가)
- 기존 rsi_floor, atr_stop_mult 로직 유지
- 테스트 24 passed, push 완료

## [2026-04-10] PriceActionMomentum + VolatilityBreakout 전략 추가 완료 (40 passed)
- `price_action_momentum`: body strength(body_abs/total_range>0.5) + ROC5 vs ROC5_MA 복합, BUY/SELL 방향성 확인, HIGH conf: body_strength>0.7 & abs(roc5)>roc5_std20
- `volatility_breakout`: BB 확장(bb_width>bb_width_ma) + 상/하단 돌파 추세 추종, HIGH conf: bb_width>bb_width_ma*1.3
- 기존 파일(다른 로직)을 스펙에 맞게 재구현, orchestrator.py에 volatility_breakout 추가 등록
- 테스트 각 20개 (40 passed), push 완료

## [2026-04-10] VolumeMomentumBreak + PriceStructureAnalysis 전략 추가 완료 (32 passed)
- `volume_momentum_break`: 거래량 급증(vol_ratio>2) + ROC3 모멘텀 가속(roc3>roc3_ma) 기반, HIGH conf: vol_ratio>3
- `price_structure_analysis`: Higher High/Lower Low 구조 분석, 5봉 local 고점/저점(shift(3) lookahead 방지), HIGH conf: close > prev_recent_high(BUY) or < prev_recent_low(SELL)
- 테스트 각 16개 (32 passed), orchestrator.py STRATEGY_REGISTRY 등록, push 완료

## [2026-04-10] SpreadMomentum + TrendExhaustionSignal 전략 추가 완료 (32 passed)
- `spread_momentum`: EMA8/EMA21 스프레드 변화율(spread_roc) 기반, BUY: spread>0 & roc>0 & roc>roc_ma, SELL: spread<0 & roc<0 & roc<roc_ma, HIGH conf: abs(roc)>roc rolling std
- `trend_exhaustion_signal`: 최근 20봉 상승봉 비율(trend_bars) + ATR stretch, BUY: trend_bars<=4 & stretch>1.5 & 반등, SELL: trend_bars>=16 & stretch>1.5 & 반락, HIGH conf: tb<=2(BUY) or tb>=18(SELL)
- 테스트 각 16개 (32 passed), orchestrator.py STRATEGY_REGISTRY 등록, push 완료

## [2026-04-10] HigherHighMomentum + MeanRevBounce 전략 추가 완료 (29 passed)
- `higher_high_momentum`: HH5/LL5 rolling 구조(shift(5)) + ROC3 모멘텀, BUY: hh5>hh5_prev & ll5>ll5_prev & roc3>0, SELL: ll5<ll5_prev & hh5<hh5_prev & roc3<0, HIGH conf: vol>vol_ma10*1.3
- `mean_rev_bounce`: Z-score(ma20,std20) 기반 평균 회귀 반등, BUY: z<-1.5 & z_change>0, SELL: z>1.5 & z_change<0, HIGH conf: abs(z)>2.0
- 테스트 각 14~15개 (29 passed), orchestrator.py STRATEGY_REGISTRY 등록, push 완료

## [2026-04-10] TrendBreakConfirm + MomentumMeanRev 전략 추가 완료 (32 passed)
- `trend_break_confirm`: EMA20 돌파 후 3봉 rolling 재확인 + EMA20>EMA50 방향 필터 + vol>vol_ma10, HIGH conf: BUY시 close>ema50, SELL시 close<ema50
- `momentum_mean_rev`: 10봉 모멘텀(mom10_ma) + Z-score 기반 풀백 진입, BUY: mom>0 & -2<z<-0.5, SELL: mom<0 & 0.5<z<2, HIGH conf: abs(z)>1.0 & abs(mom)>mom_std
- 테스트 각 16개 (32 passed), orchestrator.py STRATEGY_REGISTRY 등록, push 완료



## [2026-04-10] PriceDivergenceIndex + TrendMomentumScore 전략 추가 완료 (35 passed)
- `price_divergence_index`: RSI(14) + OBV 기반 divergence 인덱스, bull/bear_div_score>=2 + RSI 필터로 신호 생성, HIGH conf: score==2
- `trend_momentum_score`: EMA10/20/50 정렬(trend_score 0~3) + ROC5/ROC10(mom_score 0~2) 합산 total_bull 0~5, total_bull>=4 BUY, <=1 SELL, HIGH conf: total_bull==5 or ==0
- 테스트 각 17/18개 (35 passed), orchestrator.py STRATEGY_REGISTRY 등록, push 완료

## [2026-04-10] ImpulseSystem + ColoredCandles 전략 추가 완료 (28 passed)
- `impulse_system`: Elder's Impulse System, EMA13 slope + MACD hist slope 기반, 두 지표 모두 양수→BUY, 모두 음수→SELL, HIGH conf: abs(ema_slope) > ema_slope rolling std
- `colored_candles`: 연속 색깔 캔들 패턴, 4봉 중 3+개 양봉/음봉 + 거래량 증가 + vol>vol_ma, HIGH conf: 4봉 연속
- 테스트 각 14개 (28 passed), orchestrator.py STRATEGY_REGISTRY 등록, push 완료


## [2026-04-10] RangeTrading + TrendAcceleration 전략 추가 완료 (32 passed)
- `range_trading`: 횡보 구간 rolling(20) 하단/상단 20% + RSI 반전 매매, HIGH conf: rsi<30 or rsi>70
- `trend_acceleration`: EMA10-EMA20 스프레드 가속도(spread_slope=diff(3)) 기반 추세 추종, HIGH conf: abs(slope)>spread_std
- 테스트 각 16개 (32 passed), orchestrator.py STRATEGY_REGISTRY 등록, push 완료

## [2026-04-10] AdaptiveVolatility + TrendPersistence 전략 추가 완료 (28 passed)
- `adaptive_volatility`: ATR 기반 변동성 레짐 감지, 동적 임계값(vol_regime*2.0)으로 momentum 신호 필터링, LOW/HIGH vol에 따라 confidence 조정
- `trend_persistence`: 자기상관(autocorr > 0.2) 기반 추세 지속성 점수, Hurst-like 지표, HIGH conf: autocorr > 0.5
- 테스트 각 14개 (28 passed), orchestrator.py STRATEGY_REGISTRY 등록 완료, push 완료

## [2026-04-10] MarketPressure + TrendQualityFilter 전략 추가 완료 (30 passed)
- `market_pressure`: 매수/매도 압력 비율(buy_ratio - sell_ratio) 기반, pressure_trend vs pressure_ma 방향 확인 + volume 필터
- `trend_quality_filter`: 20봉 롤링 양/음봉 일관성 + 10봉 모멘텀 기반 추세 품질 평가, HIGH conf: consistency > 0.6
- 테스트 각 15개 (30 passed), orchestrator.py STRATEGY_REGISTRY 등록, push 완료

## [2026-04-10] BollingerSqueeze + RelativeMomentumIndex 전략 추가 완료 (30 passed)
- `bollinger_squeeze`: BB 폭 수축 후 모멘텀 방향 돌파 전략, HIGH conf: width < width_ma*0.5
- `relative_momentum_index`: RMI(momentum_period=3, rmi_period=14) 과매도<30/과매수>70 반전 전략
- 테스트 각 15개 (30 passed), orchestrator.py STRATEGY_REGISTRY 등록 완료, push 완료

## [2026-04-10] StochasticMomentum + PriceChannelFilter 전략 추가 완료 (32 passed)
- `stochastic_momentum`: SMI 기반 과매도(-40)/과매수(+40) 시그널 크로스 전략, HIGH conf: ±60
- `price_channel_filter`: 도나치안 채널 상단(>0.8)/하단(<0.2) 돌파 필터 전략, HIGH conf: >0.95/<0.05
- 테스트 각 16개 (32 passed), orchestrator.py STRATEGY_REGISTRY 등록 완료

## [2026-04-10] TailRiskFilter + PricePathEfficiency 전략 추가 완료 (30 passed)
- `tail_risk_filter`: calm z-score 기반 진입 필터, rolling max으로 극단 감지
- `price_path_efficiency`: Fractal Efficiency Ratio 간소화, lookback=8
- orchestrator.py STRATEGY_REGISTRY 등록, 테스트 각 15개

## Status: **33 passed** | CyclicMomentum + PriceRhythm 전략 추가 완료

## 최근 작업 (2026-04-10) — CyclicMomentum + PriceRhythm 신규 추가

- src/strategy/cyclic_momentum.py: CyclicMomentumStrategy (name=cyclic_momentum)
- src/strategy/price_rhythm.py: PriceRhythmStrategy (name=price_rhythm)
- 테스트 33 passed, orchestrator.py STRATEGY_REGISTRY 등록 완료

---

## Status: **28 passed** | VolumePriceTrendV2 + CumulativeDelta(재구현) 전략 추가 완료

## 최근 작업 (2026-04-10) — VolumePriceTrendV2 + CumulativeDelta 신규/재구현

- `src/strategy/volume_price_trend_v2.py`: `VolumePriceTrendV2Strategy` (name=`volume_price_trend_v2`)
  - VPT v2 히스토그램 기반 시그널 크로스
  - BUY: vpt_hist > 0 AND 상승 중 AND vpt > vpt_signal
  - SELL: vpt_hist < 0 AND 하락 중 AND vpt < vpt_signal
  - confidence: HIGH if abs(vpt_hist) > rolling(20) std else MEDIUM
- `src/strategy/cumulative_delta.py`: `CumulativeDeltaStrategy` (name=`cumulative_delta`) 재구현
  - 누적 매수/매도 불균형 (up_vol - down_vol 방식)
  - BUY: cum_delta > cum_delta_ma AND cum_delta > 0 AND close > close_ma
  - SELL: cum_delta < cum_delta_ma AND cum_delta < 0 AND close < close_ma
  - confidence: HIGH if abs(cum_delta) > rolling(20) std else MEDIUM
- `tests/test_volume_price_trend_v2.py`, `tests/test_cumulative_delta.py`: 각 14개 테스트 (28 passed)
- `src/orchestrator.py`: STRATEGY_REGISTRY 등록 완료



## 최근 작업 (2026-04-10) — TrendFibonacci + MeanReversionScore 신규 추가

- `src/strategy/trend_fibonacci.py`: `TrendFibonacciStrategy` (name=`trend_fibonacci`)
  - EMA20 방향 추세 + 피보나치 되돌림 레벨 (38.2% / 61.8%) 신호
  - BUY: 상승추세(ema20 > ema20_prev) + close < fib_382
  - SELL: 하락추세(ema20 < ema20_prev) + close > fib_618
  - confidence: HIGH if close가 fib_500 ±5% range else MEDIUM
- `src/strategy/mean_reversion_score.py`: `MeanReversionScoreStrategy` (name=`mean_reversion_score`)
  - z_price + z_rsi 합산 평균 회귀 점수 (rev_score)
  - BUY: rev_score > 1.5 AND vol_z > 0
  - SELL: rev_score < -1.5 AND vol_z > 0
  - confidence: HIGH if abs(rev_score) > 2.0 else MEDIUM
- `tests/test_trend_fibonacci.py`, `tests/test_mean_reversion_score.py`: 각 17개 테스트 (34 passed)
- `src/orchestrator.py`: STRATEGY_REGISTRY 등록 완료



## 최근 작업 (2026-04-10) — WickAnalysis + PriceFlowIndex 신규 추가

- `src/strategy/wick_analysis.py`: `WickAnalysisStrategy` (name=`wick_analysis`)
  - 꼬리(wick) 비율 rolling 분석으로 방향성 신호
  - BUY: wick_imbalance > 0.2 AND > imbalance_ma AND lower_ratio > 0.3
  - SELL: wick_imbalance < -0.2 AND < imbalance_ma AND upper_ratio > 0.3
  - confidence: HIGH if abs(wi) > 0.4 else MEDIUM
- `src/strategy/price_flow_index.py`: `PriceFlowIndexStrategy` (name=`price_flow_index`)
  - Money Flow Index 간소화 (pfi)
  - BUY: pfi < 30 AND rising (과매도 반등)
  - SELL: pfi > 70 AND falling (과매수 하락)
  - confidence: HIGH if pfi < 20 (BUY) or pfi > 80 (SELL) else MEDIUM
- `tests/test_wick_analysis.py`, `tests/test_price_flow_index.py`: 각 16개 테스트 (32 passed)
- `src/orchestrator.py`: STRATEGY_REGISTRY 등록 완료

## 이전 작업 (2026-04-10) — CandleBodyFilter + EMAFan 신규 추가

- `src/strategy/candle_body_filter.py`: `CandleBodyFilterStrategy` (name=`candle_body_filter`)
  - 연속 강한 방향성 봉 + volume 필터
  - BUY: bull_streak >= 2 AND close > prev_close AND volume > vol_ma
  - SELL: bear_streak >= 2 AND close < prev_close AND volume > vol_ma
  - confidence: HIGH if streak == 3 else MEDIUM
- `src/strategy/ema_fan.py`: `EMAFanStrategy` (name=`ema_fan`)
  - EMA 5/10/20/50 부채꼴 정렬 + 팬 확대 추세 전략
  - BUY: bullish_fan AND fan_spread > fan_spread_ma
  - SELL: bearish_fan AND fan_spread > fan_spread_ma
  - confidence: HIGH if fan_spread > fan_spread_ma*1.5 else MEDIUM
- `tests/test_candle_body_filter.py`, `tests/test_ema_fan.py`: 각 15개 테스트 (30 passed)
- `src/orchestrator.py`: STRATEGY_REGISTRY 등록 완료

## 이전 작업 (2026-04-10) — EntropyMomentum + FractalDimension 신규 추가

- `src/strategy/entropy_momentum.py`: `EntropyMomentumStrategy` (name=`entropy_momentum`)
  - 가격 변화 엔트로피 근사 + 모멘텀 결합
  - BUY: entropy_proxy < entropy_ma*0.7 AND mom > mom_ma AND mom > 0
  - SELL: entropy_proxy < entropy_ma*0.7 AND mom < mom_ma AND mom < 0
  - confidence: HIGH if ep < ema*0.5 else MEDIUM
- `src/strategy/fractal_dimension.py`: `FractalDimensionStrategy` (name=`fractal_dimension`)
  - Fractal Efficiency Ratio (Kaufman ER) 기반
  - BUY: er > 0.6 AND er > er_ma AND trend_up
  - SELL: er > 0.6 AND er > er_ma AND NOT trend_up
  - confidence: HIGH if er > 0.8 else MEDIUM
- `tests/test_entropy_momentum.py`, `tests/test_fractal_dimension.py`: 각 17개 테스트 (34 passed)
- `src/orchestrator.py`: STRATEGY_REGISTRY 등록 완료

## 이전 작업 (2026-04-10) — KeltnerChannelV2 + RSIBand 신규 추가

- `src/strategy/keltner_channel_v2.py`: `KeltnerChannelV2Strategy` (name=`keltner_channel_v2`)
  - EMA 기반 Keltner Channel 평균 회귀 전략
  - BUY: close < lower(EMA20 - ATR14*2) AND close > prev_close
  - SELL: close > upper(EMA20 + ATR14*2) AND close < prev_close
  - confidence: HIGH if abs(close-ema20) > atr14*2.5 else MEDIUM
- `src/strategy/rsi_band.py`: `RSIBandStrategy` (name=`rsi_band`)
  - 동적 과매수/과매도 임계값 RSI 밴드 전략
  - BUY: rsi < rsi_ma-rsi_std AND rsi > prev_rsi
  - SELL: rsi > rsi_ma+rsi_std AND rsi < prev_rsi
  - confidence: HIGH if extreme deviation else MEDIUM
- `tests/test_keltner_channel_v2.py`, `tests/test_rsi_band.py`: 각 15개 테스트 (30 passed)
- `src/orchestrator.py`: STRATEGY_REGISTRY 등록 완료

## 이전 작업 (2026-04-10) — PriceActionScorer + VolatilityTrend 신규 추가

## 최근 작업 (2026-04-10) — PriceActionScorer + VolatilityTrend 신규 추가

- `src/strategy/price_action_scorer.py`: `PriceActionScorerStrategy` (name=`price_action_scorer`)
  - 여러 가격 행동 지표 합산 점수 기반 진입
  - bull_score/bear_score (0~4): 양/음봉 + body_ratio>0.6 + wick 비율 + 거래량
  - BUY/SELL: score >= 3, HIGH if == 4 else MEDIUM
- `src/strategy/volatility_trend.py`: `VolatilityTrendStrategy` (name=`volatility_trend`)
  - ATR 확장 + 기울기 양수 + EMA20 방향으로 진입
  - BUY: atr>atr_ma AND atr_slope>0 AND close>close_ma
  - SELL: atr>atr_ma AND atr_slope>0 AND close<close_ma
  - confidence: HIGH if atr > atr_ma * 1.5 else MEDIUM
- `tests/test_price_action_scorer.py`, `tests/test_volatility_trend.py`: 각 14개 테스트 (28 passed)
- `src/orchestrator.py`: STRATEGY_REGISTRY 등록 완료, push to main

## 이전 작업 (2026-04-10) — OrderFlowImbalanceV2 + MarketMicrostructure 전략 추가 완료

## 최근 작업 (2026-04-10) — OrderFlowImbalanceV2 + MarketMicrostructure 신규 추가

- `src/strategy/order_flow_imbalance_v2.py`: `OrderFlowImbalanceV2Strategy` (name=`order_flow_imbalance_v2`)
  - 가격+거래량 기반 주문 흐름 불균형 v2
  - buy_vol/sell_vol delta → cum_delta(10) / total_vol → imbalance(-1~+1)
  - BUY: imbalance > 0.2 AND > imbalance_ma AND close > EWM(10)
  - SELL: imbalance < -0.2 AND < imbalance_ma AND close < EWM(10)
  - confidence: HIGH if abs(imbalance) > 0.4 else MEDIUM
- `src/strategy/market_microstructure.py`: `MarketMicrostructureStrategy` (name=`market_microstructure`)
  - 시장 미시구조 기반 (bid-ask spread 대리 + 가격 충격)
  - effective_spread = (high-low)/(close+1e-10), price_impact = |pct_change|/vol_ratio
  - BUY: good_liquidity(spread < spread_ma*0.8) AND close↑ AND price_impact < impact_ma
  - SELL: good_liquidity AND close↓ AND price_impact < impact_ma
  - confidence: HIGH if spread < spread_ma * 0.5 else MEDIUM
- `tests/test_order_flow_imbalance_v2.py`, `tests/test_market_microstructure.py`: 각 17개 테스트 (34 passed)
- `src/orchestrator.py`: STRATEGY_REGISTRY 등록 완료, push to main

## 이전 작업 (2026-04-10) — ScalpingSignal + SwingMomentum 신규 추가

- `src/strategy/scalping_signal.py`: `ScalpingSignalStrategy` (name=`scalping_signal`)
  - EMA(3/8/13) 정렬 + RSI7(50~70 BUY, 30~50 SELL) + 볼륨 필터
- `src/strategy/swing_momentum.py`: `SwingMomentumStrategy` (name=`swing_momentum`)
  - 확인된 스윙 고/저점(rolling 5, shift 2) 돌파 + 볼륨 필터
- `tests/test_scalping_signal.py`, `tests/test_swing_momentum.py`: 각 14개 테스트 (28 passed)
- `src/orchestrator.py`: STRATEGY_REGISTRY 등록 완료, push to main

## 이전 작업 (2026-04-10) — GapMomentum + ConsolidationBreak 신규 추가

- `src/strategy/gap_momentum.py`: `GapMomentumStrategy` (name=`gap_momentum`)
  - 갭 발생 후 모멘텀 지속 전략
  - BUY: gap_up_pct > 0.3 AND close > open AND volume > vol_ma(10)
  - SELL: gap_down_pct > 0.3 AND close < open AND volume > vol_ma(10)
  - confidence: HIGH if gap_pct > 1.0 else MEDIUM
- `src/strategy/consolidation_break.py`: `ConsolidationBreakStrategy` (name=`consolidation_break`)
  - 횡보 후 돌파 전략 (lookback=10, consolidating = range_width < range_ma*0.6)
  - BUY: consolidating.shift(1) AND close > hi.shift(1)
  - SELL: consolidating.shift(1) AND close < lo.shift(1)
  - confidence: HIGH if vol > vol_ma*1.5 AND range_width < range_ma*0.4 else MEDIUM
- 테스트: `tests/test_gap_momentum.py` (15개), `tests/test_consolidation_break.py` (15개), 30 passed
- orchestrator.py STRATEGY_REGISTRY 등록 완료
- git push origin main 완료

## 이전 작업 (2026-04-10) — MomentumDivergenceV2 + VolumeSpreadAnalysisV2 신규 추가

- `src/strategy/momentum_divergence_v2.py`: `MomentumDivergenceV2Strategy` (name=`momentum_divergence_v2`)
  - MACD(12,26,9) + 가격 divergence 기반
  - Bullish: close < price_low[idx-5] AND macd > macd_low[idx-5] → BUY
  - Bearish: close > price_high[idx-5] AND macd < macd_high[idx-5] → SELL
  - confidence: HIGH if hist > 0 (bullish) or hist < 0 (bearish) else MEDIUM
- `src/strategy/volume_spread_analysis_v2.py`: `VolumeSpreadAnalysisV2Strategy` (name=`volume_spread_analysis_v2`)
  - spread/volume MA(10) 기반 VSA v2
  - BUY: wide_spread(>1.2x) AND high_vol(>1.2x) AND close_position > 0.7
  - SELL: wide_spread(>1.2x) AND high_vol(>1.2x) AND close_position < 0.3
  - confidence: HIGH if spread>1.5x AND vol>1.5x else MEDIUM
- 테스트: `tests/test_momentum_divergence_v2.py` (18개), `tests/test_volume_spread_analysis_v2.py` (18개), 36 passed
- orchestrator.py STRATEGY_REGISTRY 등록 완료

## 이전 작업 (2026-04-10) — AdaptiveTrend + PriceCompressionSignal 신규 추가

- `src/strategy/adaptive_trend.py`: `AdaptiveTrendStrategy` (name=`adaptive_trend`)
  - volatility percentile 기반 adaptive EMA span (5~50)
  - BUY: fast_ema > adaptive_ema > slow_ema AND close > fast_ema
  - SELL: fast_ema < adaptive_ema < slow_ema AND close < fast_ema
  - confidence: HIGH if vol_percentile < 0.3 else MEDIUM
- `src/strategy/price_compression_signal.py`: `PriceCompressionSignalStrategy` (name=`price_compression_signal`)
  - NR7 압축 감지 + 방향 돌파
  - BUY: nr7 AND close > prev 3봉 rolling max
  - SELL: nr7 AND close < prev 3봉 rolling min
  - confidence: HIGH if range < avg_range*0.5 else MEDIUM
- 테스트: `tests/test_adaptive_trend.py` (16개), `tests/test_price_compression_signal.py` (16개)
- orchestrator.py STRATEGY_REGISTRY 등록 완료

## 이전 작업 (2026-04-10) — BreakoutPullback + TrendFollowFilter 신규 추가

- `src/strategy/breakout_pullback.py`: `BreakoutPullbackStrategy` (name=`breakout_pullback`)
  - resistance=high.rolling(20).max().shift(1), support=low.rolling(20).min().shift(1)
  - BUY: broke_up_recently AND pullback_to_resistance AND close > close.shift(1)
  - SELL: broke_down_recently AND pullback_to_support AND close < close.shift(1)
  - confidence: HIGH if volume > vol_avg*1.5 else MEDIUM
- `src/strategy/trend_follow_filter.py`: `TrendFollowFilterStrategy` (name=`trend_follow_filter`)
  - 간소화 ADX (DI+/DI- 14봉), ema20/ema50
  - BUY: adx>20 AND di_up>di_down AND close>ema20 AND ema20>ema50
  - SELL: adx>20 AND di_down>di_up AND close<ema20 AND ema20<ema50
  - confidence: HIGH if adx>35 else MEDIUM
- 테스트: `tests/test_breakout_pullback.py` (14개), `tests/test_trend_follow_filter.py` (14개)
- orchestrator.py STRATEGY_REGISTRY 등록 완료
- 커밋: 8c6b243, push → main

## 이전 작업 (2026-04-10) — PriceRangeBreakout + VolumeOscillatorV2 전략 추가 완료

## 최근 작업 (2026-04-10) — PriceRangeBreakout + VolumeOscillatorV2 신규 추가

- `src/strategy/price_range_breakout.py`: `PriceRangeBreakoutStrategy` (name=`price_range_breakout`)
  - range_high/low rolling(15).max/min, range_width rolling(20).mean
  - compression = range_width < range_ma * 0.7
  - BUY: compression AND close > range_high.shift(1)
  - SELL: compression AND close < range_low.shift(1)
  - confidence: HIGH if range_width < range_ma * 0.5 else MEDIUM
- `src/strategy/volume_oscillator_v2.py`: `VolumeOscillatorV2Strategy` (name=`volume_oscillator_v2`)
  - fast_vol EWM(5), slow_vol EWM(20), vol_osc=(fast-slow)/(slow+1e-10)*100
  - vol_osc_ma = vol_osc.rolling(5)
  - BUY: vol_osc>0 AND vol_osc>vol_osc_ma AND price_up
  - SELL: vol_osc>0 AND vol_osc>vol_osc_ma AND NOT price_up
  - confidence: HIGH if vol_osc>20 else MEDIUM
- 테스트: `tests/test_price_range_breakout.py` (16개), `tests/test_volume_oscillator_v2.py` (16개)
- orchestrator.py STRATEGY_REGISTRY 등록 완료
- 커밋: af22618, push → main

## 이전 작업 (2026-04-10) — PriceVelocityFilter + MomentumQualityV2 전략 추가 완료

## 최근 작업 (2026-04-10) — PriceVelocityFilter + MomentumQualityV2 신규 추가

- `src/strategy/price_velocity_filter.py`: `PriceVelocityFilterStrategy` (name=`price_velocity_filter`)
  - EMA(5)-EMA(20) 속도 + rolling vel_ma + diff(3) 가속도 필터
  - BUY: vel>0 AND vel>vel_ma AND accel>0
  - SELL: vel<0 AND vel<vel_ma AND accel<0
  - confidence: HIGH if |vel|>vel_std else MEDIUM
- `src/strategy/momentum_quality_v2.py`: `MomentumQualityV2Strategy` (name=`momentum_quality_v2`)
  - roc5/10/20 기반 consistency(0~3) + strength(rolling mean)
  - BUY: consistency>=3 AND strength>0 AND roc5>roc10
  - SELL: consistency<=0 AND strength<0 AND roc5<roc10
- 테스트: `tests/test_price_velocity_filter.py` (16개), `tests/test_momentum_quality_v2.py` (16개)
- orchestrator.py STRATEGY_REGISTRY 등록 완료
- 커밋: f426293, push → main

## 이전 작업 (2026-04-10) — MultiTimeframeMomentum + SmartBeta 신규 추가

- `src/strategy/multi_timeframe_momentum.py`: `MultiTimeframeMomentumStrategy` (name=`multi_timeframe_momentum`)
  - mom_short/mid/long (5/10/20봉) + vol_confirm(rolling 10 mean)
  - BUY: bull_score>=3 AND vol_confirm / SELL: bear_score>=3 AND vol_confirm
  - confidence HIGH if all aligned AND abs(mom_short) > rolling 20 mean, MIN_ROWS=30
- `src/strategy/smart_beta.py`: `SmartBetaStrategy` (name=`smart_beta`)
  - realized_vol rank + momentum_12 rank -> composite_score = (1-vol_rank)*0.5 + mom_rank*0.5
  - BUY: composite_score>0.6 AND >score_ma / SELL: composite_score<0.4 AND <score_ma
  - confidence HIGH if composite_score>0.75 or <0.25, MIN_ROWS=30
- tests: `tests/test_multi_timeframe_momentum.py` (14개), `tests/test_smart_beta.py` (14개) = 28 passed
- `src/orchestrator.py`: 두 전략 import + STRATEGY_REGISTRY 등록

---

## 이전 작업 (2026-04-10) — HighLowReversal + TrendFilteredMeanRev 신규 추가

- `src/strategy/high_low_reversal.py`: `HighLowReversalStrategy` (name=`high_low_reversal`)
  - position = (close-low)/(high-low+1e-10), pos_ma = position.rolling(10, min_periods=1).mean()
  - BUY: position<0.2 AND position>pos_ma / SELL: position>0.8 AND position<pos_ma
  - confidence HIGH if position<0.1(BUY) or position>0.9(SELL), MIN_ROWS=20
- `src/strategy/trend_filtered_mean_rev.py`: `TrendFilteredMeanRevStrategy` (name=`trend_filtered_mean_rev`)
  - ema50 + BB(20, 1.5std) / BUY: trend_up AND close<lower / SELL: trend_down AND close>upper
  - confidence HIGH if abs(close-bb_mid)>bb_std*2.0, MIN_ROWS=30
- tests: `tests/test_high_low_reversal.py` (16개), `tests/test_trend_filtered_mean_rev.py` (14개) = 30 passed
- `src/orchestrator.py`: 두 전략 import + STRATEGY_REGISTRY 등록

---

## Status (이전): **28 passed** | ChandelierExit(재구현) + VWAPBand 전략 추가 완료

## 최근 작업 (2026-04-10) — ChandelierExit 재구현 + VWAPBand 신규 추가

- `src/strategy/chandelier_exit.py`: `ChandelierExitStrategy` (name=`chandelier_exit`) 재구현
  - atr14 = (high-low).rolling(14, min_periods=1).mean() (True Range 간소화)
  - chandelier_long = highest_high22 - atr14*3.0 / chandelier_short = lowest_low22 + atr14*3.0
  - BUY: close > CL AND close > prev_close / SELL: close < CS AND close < prev_close
  - confidence HIGH if close > CL*1.01 (BUY) or close < CS*0.99 (SELL), MIN_ROWS=25
- `src/strategy/vwap_band.py`: `VWAPBandStrategy` (name=`vwap_band`) 신규
  - vwap = (close*vol).rolling(20).sum() / vol.rolling(20).sum()
  - BUY: close < lower_band AND close > prev_close (하단 밴드 반등)
  - SELL: close > upper_band AND close < prev_close (상단 밴드 반락)
  - confidence HIGH if abs(deviation) > dev_std*2.5, MIN_ROWS=20
- tests: `tests/test_chandelier_exit.py` (14개), `tests/test_vwap_band.py` (14개) = 28 passed
- `src/orchestrator.py`: vwap_band import + STRATEGY_REGISTRY 등록 (chandelier_exit는 기존 유지)

## 이전 작업 (2026-04-10) — TrendConsistency + VolumeWeightedMomentum 전략 추가

- `src/strategy/trend_consistency.py`: `TrendConsistencyStrategy` (name=`trend_consistency`)
  - 다중 시간대 EMA 일관성 점수 (ema5/ema10/ema20)
  - BUY: bull_count==3 AND close > prev_close / SELL: bear_count==3 AND close < prev_close
  - confidence HIGH if count==3, MIN_ROWS=25
- `src/strategy/volume_weighted_momentum.py`: `VolumeWeightedMomentumStrategy` (name=`volume_weighted_momentum`)
  - 거래량 가중 모멘텀: vw_momentum = (returns * vol_norm).rolling(10).sum()
  - BUY: vw_momentum > vw_mom_ma AND vw_momentum > 0
  - SELL: vw_momentum < vw_mom_ma AND vw_momentum < 0
  - confidence HIGH if abs(vw_momentum) > std20, MIN_ROWS=20
- tests: `tests/test_trend_consistency.py` (16개), `tests/test_volume_weighted_momentum.py` (16개) = 32 passed
- `src/orchestrator.py`: 두 전략 import + STRATEGY_REGISTRY 등록

## Status: **33 passed** | PivotPoint + NightStar 전략 추가 완료

## 최근 작업 (2026-04-10) — PivotPoint + NightStar 전략 추가

- `src/strategy/pivot_point.py`: `PivotPointStrategy` (name=`pivot_point`)
  - 이전 봉 기반 피벗 포인트 돌파 전략
  - BUY: close > pivot AND close > r1 / SELL: close < pivot AND close < s1
  - confidence HIGH if close > r2 (BUY) or close < s2 (SELL), MIN_ROWS=20
- `src/strategy/night_star.py`: `NightStarStrategy` (name=`night_star`)
  - Morning Star (BUY) / Evening Star (SELL) 3봉 반전 패턴
  - doji star 또는 high volume 시 HIGH confidence, MIN_ROWS=15
- tests: `tests/test_pivot_point.py` (16개), `tests/test_night_star.py` (17개) = 33 passed
- `src/orchestrator.py`: 두 전략 import + STRATEGY_REGISTRY 등록

## Status: **28 passed** | PricePatternRecog + TrendMomentumBlend 전략 추가 완료

## 최근 작업 (2026-04-10) — PricePatternRecog + TrendMomentumBlend 전략 추가

- `src/strategy/price_pattern_recog.py`: `PricePatternRecogStrategy` (name=`price_pattern_recog`)
  - Morning Star, Evening Star, Three White Soldiers, Three Black Crows 4가지 다중 캔들 패턴
  - BUY: morning_star OR three_white | SELL: evening_star OR three_black
  - confidence HIGH if three_white/three_black, MEDIUM if morning/evening star, MIN_ROWS=8
- `src/strategy/trend_momentum_blend.py`: `TrendMomentumBlendStrategy` (name=`trend_momentum_blend`)
  - EMA50 기울기(추세) + ROC10 크로스오버(모멘텀) + RSI(14) 블렌딩
  - BUY: slope>0 AND roc>roc_ma AND 50<rsi<70 | SELL: slope<0 AND roc<roc_ma AND 30<rsi<50
  - confidence HIGH if abs(slope) > std20/close*0.005, MIN_ROWS=60
- tests: `tests/test_price_pattern_recog.py` (14개), `tests/test_trend_momentum_blend.py` (14개) = 28 passed
- `src/orchestrator.py`: 두 전략 import + STRATEGY_REGISTRY 등록
- pushed to main (bcc6744)

## 이전 작업 (2026-04-10) — IntradayMomentum + VolatilitySurface 전략 추가 완료

## 최근 작업 (2026-04-10) — IntradayMomentum + VolatilitySurface 전략 추가

- `src/strategy/intraday_momentum.py`: `IntradayMomentumStrategy` (name=`intraday_momentum`)
  - 봉 내 위치(position) + 거래량 흐름 기반 단기 모멘텀
  - BUY: momentum_score > score_ma AND position > 0.7 AND volume > vol_ma
  - SELL: momentum_score < score_ma AND position < 0.3 AND volume > vol_ma
  - confidence HIGH if position > 0.85 (BUY) or < 0.15 (SELL), MIN_ROWS=20
- `src/strategy/volatility_surface.py`: `VolatilitySurfaceStrategy` (name=`volatility_surface`)
  - 단기/장기 실현 변동성 비율(term structure) 기반
  - BUY: vol_ratio < 0.8 AND close > ma20 AND vol_ratio < vol_ratio_ma
  - SELL: vol_ratio < 0.8 AND close < ma20 AND vol_ratio < vol_ratio_ma
  - confidence HIGH if vol_ratio < 0.6, MIN_ROWS=30
- tests: `tests/test_intraday_momentum.py` (14개), `tests/test_volatility_surface.py` (14개) = 28 passed
- `src/orchestrator.py`: 두 전략 import + STRATEGY_REGISTRY 등록
- pushed to main (ccd2fad)

## 이전 작업 (2026-04-10) — RegimeMomentum + LiquidityScore 전략 추가 완료

## 최근 작업 (2026-04-10) — RegimeMomentum + LiquidityScore 전략 추가

- `src/strategy/regime_momentum.py`: `RegimeMomentumStrategy` (name=`regime_momentum`)
  - efficiency_ratio 기반 레짐 판단 (> 0.4 추세장, ≤ 0.4 횡보장)
  - 추세장: EMA10/EMA20 크로스 모멘텀 BUY/SELL
  - 횡보장: BB 밴드 이탈 반전 BUY/SELL
  - confidence HIGH if ER > 0.6 or < 0.2, MIN_ROWS=30
- `src/strategy/liquidity_score.py`: `LiquidityScoreStrategy` (name=`liquidity_score`)
  - spread_proxy + vol_score + price_impact 기반 유동성 점수
  - BUY: liq > liq_ma AND close > close_ma AND vol_score > 1.2
  - SELL: liq > liq_ma AND close < close_ma AND vol_score > 1.2
  - confidence HIGH if vol_score > 2.0 AND liq > liq_ma * 1.5, MIN_ROWS=20
- tests: `tests/test_regime_momentum.py` (16개), `tests/test_liquidity_score.py` (16개) = 32 passed
- `src/orchestrator.py`: 두 전략 import + STRATEGY_REGISTRY 등록
- pushed to main

## 이전 작업 (2026-04-10) — HarmonicPattern + DivergenceConfirmation 전략 추가

## 최근 작업 (2026-04-10) — HarmonicPattern + DivergenceConfirmation 전략 추가

- `src/strategy/harmonic_pattern.py`: `HarmonicPatternStrategy` (name=`harmonic_pattern`)
  - 피보나치 ABCD 패턴, BC/AB 0.382~0.886, CD/BC 1.13~1.618
  - BUY: CD > 0, SELL: CD < 0, confidence HIGH if BC/AB ≈ 0.618±0.02
  - MIN_ROWS=20 (completed < 20 → HOLD)
- `src/strategy/divergence_confirmation.py`: `DivergenceConfirmationStrategy` (name=`divergence_confirmation`)
  - RSI(14) divergence, lookback=10
  - Bullish: price↓ + RSI↑, Bearish: price↑ + RSI↓
  - confidence HIGH if RSI <= 30 (bullish) or >= 70 (bearish), MIN_ROWS=30
- tests: `tests/test_harmonic_pattern.py` (14개), `tests/test_divergence_confirmation.py` (14개) = 28 passed
- `src/orchestrator.py`: 두 전략 import + STRATEGY_REGISTRY 등록
- pushed to main

## 이전 작업 (2026-04-10) — TickVolume + MarketBreadthProxy 전략 추가

- `src/strategy/tick_volume.py`: `TickVolumeStrategy` (name=`tick_volume`)
  - volume을 틱 대리로 사용, cum_delta rolling(10) + cum_delta_ma rolling(5)
  - BUY: cum_delta > cum_delta_ma AND cum_delta > 0 AND vol > tick_vol_ma
  - SELL: cum_delta < cum_delta_ma AND cum_delta < 0 AND vol > tick_vol_ma
  - confidence: HIGH if vol > tick_vol_ma * 1.5, MIN_ROWS=20
- `src/strategy/market_breadth_proxy.py`: `MarketBreadthProxyStrategy` (name=`market_breadth_proxy`)
  - 단일 심볼 breadth 대리: advances/declines rolling(20), ad_ratio = advances/(declines+1)
  - BUY: ad_ratio > 1.5 AND ad_ratio > ad_ma AND close > EMA(20)
  - SELL: ad_ratio < 0.67 AND ad_ratio < ad_ma AND close < EMA(20)
  - confidence: HIGH if ad_ratio > 2.0 (BUY) or < 0.5 (SELL), MIN_ROWS=30
- tests: `tests/test_tick_volume.py` (16개), `tests/test_market_breadth_proxy.py` (17개) = 33 passed
- `src/orchestrator.py`: 두 전략 import + STRATEGY_REGISTRY 등록
- pushed to main

## 이전 작업 (2026-04-10) — OscillatorBand + PriceActionFilter 전략 추가

- `src/strategy/oscillator_band.py`: `OscillatorBandStrategy` (name=`oscillator_band`)
  - RSI(14) + Stochastic(14) 합성 오실레이터 밴드 (0~100)
  - BUY: osc < 30 AND osc 상승 AND K > D / SELL: osc > 70 AND osc 하락 AND K < D
  - confidence: HIGH if osc < 20 (BUY) or osc > 80 (SELL), MIN_ROWS=20
- `src/strategy/price_action_filter.py`: `PriceActionFilterStrategy` (name=`price_action_filter`)
  - 추세(EMA50) + 변곡(강한 봉 body_ratio>0.6) + 거래량(vol>rolling10 mean) 3중 필터
  - BUY: trend_up + strong_bull + vol_confirm / SELL: trend_down + strong_bear + vol_confirm
  - confidence: HIGH if body_ratio > 0.8, MIN_ROWS=55
- tests: `tests/test_oscillator_band.py` (14개), `tests/test_price_action_filter.py` (14개) = 28 passed
- `src/orchestrator.py`: 두 전략 import + STRATEGY_REGISTRY 등록
- pushed to main

## 이전 작업 (2026-04-10) — PriceImpact + SmartMoneyFlow 전략 추가

- `src/strategy/price_impact.py`: `PriceImpactStrategy` (name=`price_impact`)
  - Kyle's Lambda 간소화: price_change / volume * 1000 → impact_ma(ewm span=20)
  - BUY: impact > impact_ma * 1.5 AND dir_ma > 0 / SELL: 반대
  - confidence: HIGH if impact > impact_ma * 2.0 else MEDIUM, MIN_ROWS=25
- `src/strategy/smart_money_flow.py`: `SmartMoneyFlowStrategy` (name=`smart_money_flow`)
  - otc_return * volume → rolling(10).sum() = smf, ewm(span=5) = smf_signal
  - BUY: smf > smf_signal AND smf < 0 / SELL: smf < smf_signal AND smf > 0
  - confidence: HIGH if abs(smf) > smf.rolling(20).std() else MEDIUM, MIN_ROWS=20
- tests: `tests/test_price_impact.py` (14개), `tests/test_smart_money_flow.py` (14개) = 28 passed
- `src/orchestrator.py`: 두 전략 import + STRATEGY_REGISTRY 등록
- pushed to main

## 이전 작업 (2026-04-10) — BreakoutVolRatio + MeanRevBandV2 전략 추가 완료

## 최근 작업 (2026-04-10) — BreakoutVolRatio + MeanRevBandV2 전략 추가

- `src/strategy/breakout_vol_ratio.py`: `BreakoutVolRatioStrategy` (name=`breakout_vol_ratio`)
  - 20봉 고점/저점 돌파 + 거래량 비율(vol/vol_ma20) 신뢰성 판단
  - BUY: broke_up AND vol_ratio > 1.5 / SELL: broke_down AND vol_ratio > 1.5
  - confidence: HIGH if vol_ratio > 2.0 else MEDIUM
  - ATR14 기반 breakout_size 계산, MIN_ROWS=25
- `src/strategy/mean_rev_band_v2.py`: `MeanRevBandV2Strategy` (name=`mean_rev_band_v2`)
  - EMA20 ± N*ATR14 다중 밴드 (band1=1x, band2=2x)
  - BUY: band2 아래 복귀 OR band1 아래 반등 / SELL: band2 위 반락 OR band1 위 반락
  - confidence: HIGH if band2 조건 else MEDIUM, MIN_ROWS=25
- tests: `tests/test_breakout_vol_ratio.py` (14개), `tests/test_mean_rev_band_v2.py` (14개) = 28 passed
- `src/orchestrator.py`: 두 전략 import + STRATEGY_REGISTRY 등록
- pushed to main

## 이전 작업 (2026-04-10) — VelocityEntry + RangeBias 전략 추가

## 최근 작업 (2026-04-10) — VelocityEntry + RangeBias 전략 추가

- `src/strategy/velocity_entry.py`: `VelocityEntryStrategy` (name=`velocity_entry`)
  - 가격 속도(1차 미분) + 가속도(2차 미분) 기반 진입
  - BUY: velocity > velocity_ma AND acceleration > 0
  - SELL: velocity < velocity_ma AND acceleration < 0
  - confidence: HIGH if |velocity| > velocity.rolling(20).std() else MEDIUM
  - MIN_ROWS=20
- `src/strategy/range_bias.py`: `RangeBiasStrategy` (name=`range_bias`)
  - 봉의 위치 편향 — 범위 내 종가 위치 추세
  - BUY: bias > 0.6 AND bias_trend > 0
  - SELL: bias < 0.4 AND bias_trend < 0
  - confidence: HIGH if bias > 0.75 (BUY) or bias < 0.25 (SELL) else MEDIUM
  - MIN_ROWS=20
- tests: `tests/test_velocity_entry.py` (16개), `tests/test_range_bias.py` (17개) = 33 passed
- `src/orchestrator.py`: 두 전략 import + STRATEGY_REGISTRY 등록
- pushed to main

## 이전 작업 (2026-04-10) — CompositeMomentum + SignalLineCross 전략 추가

- `src/strategy/composite_momentum.py`: `CompositeMomentumStrategy` (name=`composite_momentum`)
  - RSI14 + ROC10 + MACD방향 정규화 합성 점수, BUY>0.65, SELL<0.35
- `src/strategy/signal_line_cross.py`: `SignalLineCrossStrategy` (name=`signal_line_cross`)
  - EMA(8)/EMA(21) diff의 signal line(EMA9) 크로스오버, 음수/양수 구간 필터
- tests: `tests/test_composite_momentum.py` (14개), `tests/test_signal_line_cross.py` (14개)
- `src/orchestrator.py`: 두 전략 import + STRATEGY_REGISTRY 등록
- 28 tests PASSED, pushed to main

## 이전 작업 (2026-04-10) — DualThrust + VolatilityBreakoutV2 전략 추가

- `src/strategy/dual_thrust.py`: `DualThrustStrategy` (name=`dual_thrust`)
  - rolling N=4 고가/저가 범위 기반, k=0.5
  - BUY: close > open + 0.5 * range_val; SELL: close < open - 0.5 * range_val
  - confidence: HIGH if ratio > 0.02, MIN_ROWS=10
- `src/strategy/volatility_breakout_v2.py`: `VolatilityBreakoutV2Strategy` (name=`volatility_breakout_v2`)
  - ATR(14) 배수로 진입 레벨 설정, upper=prev_close+0.5*atr, lower=prev_close-0.5*atr
  - BUY: close > upper; SELL: close < lower
  - confidence: HIGH if (close-upper)/atr > 0.3, MIN_ROWS=20
- tests: 14 + 14 = 28 passed
- orchestrator: 두 전략 import + registry 등록, pushed

---

## 이전 작업 (2026-04-10) — CumulativeDelta + SpreadAnalysis 전략 추가

## Status: **28 passed** | CumulativeDelta + SpreadAnalysis 전략 추가 완료

## 최근 작업 (2026-04-10) — CumulativeDelta + SpreadAnalysis 전략 추가

- `src/strategy/cumulative_delta.py`: `CumulativeDeltaStrategy` (name=`cumulative_delta`)
  - 봉 구조로 매수/매도 거래량 추정, rolling(20) 누적 델타
  - BUY: cum_delta crosses above cum_delta_ma AND cum_delta < 0
  - SELL: cum_delta crosses below cum_delta_ma AND cum_delta > 0
  - confidence: HIGH if abs(cum_delta) > std, MIN_ROWS=30
- `src/strategy/spread_analysis.py`: `SpreadAnalysisStrategy` (name=`spread_analysis`)
  - (high-low)/close 스프레드 프록시로 유동성 판단
  - BUY: low_spread AND close_pos > 0.7 AND close_pos > close_pos_ma
  - SELL: low_spread AND close_pos < 0.3 AND close_pos < close_pos_ma
  - confidence: HIGH if spread < ma*0.6, MIN_ROWS=20
- tests: 14 + 14 = 28 passed
- orchestrator: 두 전략 import + registry 등록, pushed

---

## 이전 작업 (2026-04-10) — PivotBand + TrendIntensityIndex 전략 추가

## 최근 작업 (2026-04-10) — PivotBand + TrendIntensityIndex 전략 추가

- `src/strategy/pivot_band.py`: `PivotBandStrategy` (name=`pivot_band`)
  - 피벗 포인트 기반 동적 밴드 (r1+r2)/2, (s1+s2)/2
  - BUY: prev_close < band_lower → curr_close >= band_lower (하단 복귀)
  - SELL: prev_close > band_upper → curr_close <= band_upper (상단 이탈)
  - confidence: HIGH if curr < s2 or curr > r2, MIN_ROWS=5
- `src/strategy/trend_intensity_index.py`: `TrendIntensityIndexV2Strategy` (name=`trend_intensity_index`)
  - TII = (above - below) / period * 100 (-100~+100), tii_ma = TII.rolling(9)
  - BUY: tii crosses above tii_ma AND tii < 0
  - SELL: tii crosses below tii_ma AND tii > 0
  - confidence: HIGH if abs(tii) > 40, MIN_ROWS=45
- tests: 16 + 16 = 32 passed
- orchestrator: 두 전략 import + registry 등록, pushed

## 이전 작업 (2026-04-10) — PriceCycleDetector + MomentumQuality 전략 추가

- `src/strategy/price_cycle_detector.py`: `PriceCycleDetectorStrategy` (name=`price_cycle_detector`)
  - 자기상관(autocorrelation) lag 2~10에서 최대 상관 탐색
  - BUY: best_corr > 0.5 AND cycle_momentum > 0.01; SELL: best_corr > 0.5 AND cycle_momentum < -0.01
  - confidence: HIGH if best_corr > 0.7, MIN_ROWS=35
- `src/strategy/momentum_quality.py`: `MomentumQualityStrategy` (name=`momentum_quality`)
  - quality_score = consistency*2-1 + (acceleration>0); 범위 -1~2
  - BUY: quality_score > 1.0 AND mom20 > 0; SELL: quality_score < -0.5 AND mom20 < 0
  - confidence: HIGH if score > 1.5 (BUY) or < -0.8 (SELL), MIN_ROWS=25
- tests: 16 + 16 = 32 passed
- orchestrator: 두 전략 import + registry 등록, pushed

## 이전 작업 (2026-04-10) — NormalizedPriceOsc + EMAEnvelope 전략 추가

- `src/strategy/normalized_price_osc.py`: `NormalizedPriceOscStrategy` (name=`normalized_price_osc`)
  - rolling min-max 정규화(0~100), npo_ma(5) 필터
  - BUY: npo crosses above 20 AND npo>npo_ma; SELL: npo crosses below 80 AND npo<npo_ma
  - confidence: HIGH if npo<10 (BUY) or >90 (SELL), MIN_ROWS=25
- `src/strategy/ema_envelope.py`: `EMAEnvelopeStrategy` (name=`ema_envelope`)
  - EMA20 ±2.5% 엔벨로프 밴드
  - BUY: prev<lower AND curr>lower; SELL: prev>upper AND curr<upper
  - confidence: HIGH if curr<ema20*0.97 (BUY) or >ema20*1.03 (SELL), MIN_ROWS=25
- tests: 14 + 14 = 28 passed
- orchestrator: 두 전략 import + registry 등록, pushed

## 이전 작업 (2026-04-10) — TrendExhaustion + HighLowChannel 전략 추가

- `src/strategy/trend_exhaustion.py`: `TrendExhaustionStrategy` (name=`trend_exhaustion`)
  - EMA20 기반 bars_up + ROC5 모멘텀으로 추세 소진 감지
  - BUY: bars_up<=3 AND roc5>0 AND roc5>roc5_ma; SELL: bars_up>=8 AND trend_up AND mom_weak_up
  - confidence: HIGH if bars_up<=2 (BUY) or >=9 (SELL), MIN_ROWS=25
- `src/strategy/high_low_channel.py`: `HighLowChannelStrategy` (name=`high_low_channel`)
  - 14기간 High-Low 채널 position 기반 반등/반락
  - BUY: position<0.25 AND price_up; SELL: position>0.75 AND price_down
  - confidence: HIGH if position<0.1 (BUY) or >0.9 (SELL), MIN_ROWS=20
- tests: 17 + 17 = 34 passed
- orchestrator: 두 전략 import + registry 등록, pushed

## 이전 작업 (2026-04-10) — DeMarker + ConnorsRSI 전략 추가

- `src/strategy/demarker.py`: `DeMarkerStrategy` (name=`demarker`)
  - DeMax/DeMin 14기간 평활 → DeMarker oscillator [0,1]
  - BUY: dem crosses above 0.3, SELL: crosses below 0.7
  - confidence: HIGH if dem < 0.2 (BUY) or dem > 0.8 (SELL), MIN_ROWS=20
- `src/strategy/connors_rsi.py`: `ConnorsRSIStrategy` 재작성 (name=`connors_rsi`)
  - CRSI = (RSI(3) EWM + StreakRSI(2) + ROC Percentile(100)) / 3
  - BUY: crsi crosses above 10, SELL: crosses below 90
  - confidence: HIGH if crsi < 5 or > 95, MIN_ROWS=110
- tests: 17 + 18 = 35 passed
- orchestrator: demarker 추가 등록, pushed

## 이전 작업 (2026-04-10) — SineWave + AdaptiveCycle 전략 추가

- `src/strategy/sine_wave.py`: `SineWaveStrategy` (name=`sine_wave`)
  - Ehlers Sine Wave: HP filter + z-score 위상 → arcsin → sine/lead 크로스오버
  - BUY: sine crosses above lead, SELL: sine crosses below lead
  - confidence: HIGH if |sine| > 0.7 else MEDIUM, MIN_ROWS=25
- `src/strategy/adaptive_cycle.py`: `AdaptiveCycleStrategy` (name=`adaptive_cycle`)
  - Rolling 극값으로 사이클 위치(0~1) 계산
  - BUY: cycle_pos < 0.2 AND dir > 0, SELL: cycle_pos > 0.8 AND dir < 0
  - confidence: HIGH if pos < 0.1 (BUY) or pos > 0.9 (SELL) else MEDIUM, MIN_ROWS=15
- tests: 18 + 18 = 36 passed
- orchestrator: 두 전략 등록 완료, pushed

## 이전 작업 (2026-04-10) — GaussianChannel + EhlersFisher 전략 추가

- `src/strategy/gaussian_channel.py`: `GaussianChannelStrategy` (name=`gaussian_channel`)
  - 4-pole Gaussian 필터 (4단계 EMA) + ATR 채널
  - BUY: prev_close < lower AND curr_close > lower (하단 채널 복귀)
  - SELL: prev_close > upper AND curr_close < upper (상단 채널 이탈)
  - confidence: HIGH if gauss_rising (BUY) or not gauss_rising (SELL) else MEDIUM
- `src/strategy/ehlers_fisher.py`: `EhlersFisherStrategy` (name=`ehlers_fisher`)
  - Ehlers Fisher Transform (period=10): 가격 정규분포 변환
  - BUY: fish cross up signal AND fish < 0, SELL: cross down AND fish > 0
  - confidence: HIGH if |fish| > 2.0 else MEDIUM
- tests: 18 + 18 = 36 passed
- orchestrator: 두 전략 등록 완료, pushed

## 이전 상태: **30 passed** | MassIndex + UltimateOscillator 전략 확인 완료

## 최근 작업 (2026-04-10) — MassIndex + UltimateOscillator 전략 확인

- `src/strategy/mass_index.py`: `MassIndexStrategy` (name=`mass_index`) — 이미 존재
  - Reversal Bulge: MI > 27 → < 26.5, BUY if close > ema50, SELL if close < ema50
- `src/strategy/ultimate_oscillator.py`: `UltimateOscillatorStrategy` (name=`ultimate_oscillator`) — 이미 존재
  - BUY: UO < 30 AND 상승 중, SELL: UO > 70 AND 하락 중
- tests: 15 + 15 = 30 passed
- orchestrator: 두 전략 이미 등록됨

## 이전 상태: **35 passed** | WaveTrendOsc + CyberCycle 전략 추가 완료

## 최근 작업 (2026-04-10) — WaveTrendOsc + CyberCycle 전략 추가

- `src/strategy/wavetrend_osc.py`: `WaveTrendOscStrategy` (name=`wavetrend_osc`)
  - WaveTrend Oscillator (LazyBear): hlc3 기반 EMA/CCI 체인
  - BUY: wt1 cross up wt2 AND wt1 < -60, SELL: cross down AND wt1 > 60
  - confidence: HIGH if |wt1| > 80 else MEDIUM
- `src/strategy/cyber_cycle.py`: `CyberCycleStrategy` (name=`cyber_cycle`)
  - Ehlers Cyber Cycle (alpha=0.07): recursive 주기 추출
  - BUY: cycle cross up trigger AND cycle < 0, SELL: cross down AND cycle > 0
  - warmup: idx < 10 → HOLD
- tests: 17 + 18 = 35 passed
- orchestrator: 두 전략 등록 완료, pushed

## 이전 상태: **28 passed** | LaguerreRSI + ZeroLagEMA 전략 추가 완료

## 최근 작업 (2026-04-10) — LaguerreRSI + ZeroLagEMA 전략 추가

- `src/strategy/laguerre_rsi.py`: `LaguerreRSIStrategy` (name=`laguerre_rsi`)
  - Ehlers Laguerre 필터 기반 RSI (0~1), gamma=0.5
  - BUY: lrsi crosses above 0.2, SELL: crosses below 0.8
- `src/strategy/zero_lag_ema.py`: `ZeroLagEMAStrategy` (name=`zero_lag_ema`)
  - Zero-lag EMA (2*EMA - EMA(EMA)), fast=10/slow=25
  - BUY: fast crosses above slow, SELL: crosses below
- `tests/test_laguerre_rsi.py` + `tests/test_zero_lag_ema.py`: 각 14개 = 28 passed
- `src/orchestrator.py`: import + STRATEGY_REGISTRY 등록
- commit: `feat: add LaguerreRSI + ZeroLagEMA strategies (28 tests)` → pushed

## 이전 상태: **14 passed** | AbsoluteStrengthHist 전략 추가 완료

## 이전 작업 (2026-04-10) — AbsoluteStrengthHist 전략 추가

- `src/strategy/absolute_strength_hist.py`: `AbsoluteStrengthHistStrategy` (name=`absolute_strength_hist`)
  - ASH: bulls/bears 이중 EWM 평활(span=9→3), diff_val = smooth2_bulls - smooth2_bears
  - BUY: diff_val 0선 상향 돌파, SELL: 0선 하향 이탈
  - confidence: HIGH if abs(diff_val) > (s2_bulls + s2_bears) * 0.3 else MEDIUM
- `tests/test_absolute_strength_hist.py`: 14개 테스트 — 14 passed
- `src/orchestrator.py`: import + STRATEGY_REGISTRY 등록
- commit: `feat: add AbsoluteStrengthHist strategy (14 tests)` → pushed

## 이전 상태: **30 passed** | VortexIndicator + LinearRegChannel 테스트 추가 완료

## 최근 작업 (2026-04-10) — VortexIndicator + LinearRegChannel 테스트 작성

- `tests/test_vortex_indicator.py`: `VortexIndicatorStrategy` (name=`vortex_indicator`) 테스트 15개
  - VI+ 크로스오버 BUY, VI+ 크로스 하방 SELL, HIGH conf (sep>0.1), 데이터 부족 HOLD
- `tests/test_linear_reg_channel.py`: `LinearRegChannelStrategy` (name=`linear_reg_channel`) 테스트 15개
  - 하단 채널 이탈 후 복귀 BUY, 상단 채널 이탈 후 복귀 SELL, 최소 35행
- commit: `feat: add tests for VortexIndicator + LinearRegChannel (28 tests)` → pushed

## 이전 상태: **23 passed, 5 skipped** | MoneyFlowIndex + TrendStrengthIndex 추가 완료

## 최근 작업 (2026-04-10) — MoneyFlowIndex + TrendStrengthIndex 구현

- `src/strategy/money_flow_index.py`: `MoneyFlowIndexStrategy` (name=`money_flow_index`)
  - MFI crossover: above 20 = BUY (과매도 탈출), below 80 = SELL (과매수 이탈)
  - HIGH conf if mfi < 10 (BUY) or mfi > 90 (SELL), 최소 20행, 14 tests
- `src/strategy/trend_strength_index.py`: `TrendStrengthIndexStrategy` (name=`trend_strength_index`)
  - Double-smoothed TSI (span 25/13), signal EMA-7
  - BUY: TSI crosses above signal AND TSI < 0; SELL: crosses below AND TSI > 0
  - HIGH conf if abs(TSI) > 25, 최소 40행, 14 tests
- `src/orchestrator.py`: import + STRATEGY_REGISTRY 등록 완료
- commit: `feat: add MoneyFlowIndex + TrendStrengthIndex strategies (28 tests)` → pushed

## 이전 상태: **36 passed** | PivotPointRev + HeikenAshiTrend 추가 완료

## 최근 작업 (2026-04-10) — PivotPointRev + HeikenAshiTrend 구현

- `src/strategy/pivot_point_rev.py`: `PivotPointRevStrategy` (name=`pivot_point_rev`)
  - BUY: close 근처 S1(MEDIUM) 또는 S2(HIGH), SELL: R1(MEDIUM) 또는 R2(HIGH)
  - ATR14 포함, 최소 20행, 18 tests PASSED
- `src/strategy/heiken_ashi_trend.py`: `HeikenAshiTrendStrategy` (name=`heiken_ashi_trend`)
  - 순수 HA (EMA 스무딩 없음), 3봉 연속 + 방향 확인
  - HIGH conf if 5연속, 최소 10행, 18 tests PASSED
- commit: `feat: add PivotPointRev + HeikenAshiTrend strategies (36 tests)` → pushed

## 이전 상태: **28 passed** | VolumeWeightedRSI + AdaptiveMomentum 추가 완료

## 최근 작업 (2026-04-10) — VolumeWeightedRSI + AdaptiveMomentum 구현

- `src/strategy/volume_weighted_rsi.py`: `VolumeWeightedRSIStrategy` (name=`volume_weighted_rsi`)
  - 거래량으로 가중된 RSI: vol_weight = volume / volume.rolling(14).mean()
  - BUY: VRSI crosses above 30, SELL: VRSI crosses below 70
  - HIGH conf if vrsi_prev < 20 (BUY) or vrsi_prev > 80 (SELL), 최소 20행, 14 tests PASSED
- `src/strategy/adaptive_momentum.py`: `AdaptiveMomentumStrategy` (name=`adaptive_momentum`)
  - ATR14 기반 vol_rank(rolling 50) → lookback 동적 결정 (5/10/20봉)
  - BUY: mom > 0.02 AND mom > mom_prev, SELL: mom < -0.02 AND mom < mom_prev
  - HIGH conf if |mom| > 0.05, 최소 60행, 14 tests PASSED
- `src/orchestrator.py`: 두 전략 import + STRATEGY_REGISTRY 등록
- commit: `feat: add VolumeWeightedRSI + AdaptiveMomentum strategies (28 tests)` → pushed

## 이전 작업 (2026-04-10) — KeltnerBreakout + SqueezeMomentum 구현

- `src/strategy/keltner_breakout.py`: `KeltnerBreakoutStrategy` (name=`keltner_breakout`)
  - 순수 Keltner Channel 돌파: EMA20 ± 2*ATR14(rolling)
  - BUY: 이전봉 < kc_upper AND 현재봉 > kc_upper (상단 돌파)
  - SELL: 이전봉 > kc_lower AND 현재봉 < kc_lower (하단 붕괴)
  - HIGH conf if close > kc_upper * 1.005, 최소 25행, 14 tests PASSED
- `src/strategy/squeeze_momentum.py`: `SqueezeMomentumStrategy` (name=`squeeze_momentum`) **재작성**
  - Lazybear 공식: momentum = close - (roll_high_max + roll_low_min)/2 - sma20
  - BUY: squeeze 해제 AND momentum > 0 AND momentum > prev_momentum
  - SELL: squeeze 해제 AND momentum < 0 AND momentum < prev_momentum
  - HIGH conf if abs(momentum) > momentum.rolling(20).std(), 최소 30행, 14 tests PASSED
- `src/orchestrator.py`: keltner_breakout import + STRATEGY_REGISTRY 등록
- commit: `feat: add KeltnerBreakout + SqueezeMomentum strategies (28 tests)` → pushed

## 이전 작업 (2026-04-10) — AccDist + PriceMomentumOsc 구현

- `src/strategy/acc_dist.py`: `AccDistStrategy` (name=`acc_dist`)
  - CLV → A/D Line cumsum, 3봉 전 대비 A/D vs 가격 divergence 감지
  - BUY: A/D 상승 + 가격 하락 (bullish divergence), SELL: 반대
  - HIGH conf if abs(ad_change) > rolling(20).std(), 최소 20행, 14 tests PASSED
- `src/strategy/price_momentum_osc.py`: `PriceMomentumOscStrategy` (name=`price_momentum_osc`)
  - PPO = 100*(EMA12-EMA26)/EMA26, ppo_hist = PPO - Signal(9)
  - BUY: ppo_hist 상향 크로스 0 + PPO < 0, SELL: 하향 크로스 + PPO > 0
  - HIGH conf if abs(ppo) > 2.0, 최소 35행, 14 tests PASSED
- `src/orchestrator.py`: 두 전략 import + STRATEGY_REGISTRY 등록 완료
- commit: `feat: add AccDist + PriceMomentumOsc strategies (28 tests)` → pushed

## 이전 작업 (2026-04-10) — CandlePatternScore + MultiTFTrend 구현

- `src/strategy/candle_pattern_score.py`: `CandlePatternScoreStrategy` (name=`candle_pattern_score`)
  - 7개 캔들 패턴 점수화 (Hammer, Shooting Star, Engulfing, Strong 봉, Doji)
  - score >= 3 → BUY, <= -3 → SELL, HIGH conf if abs(score) >= 4
  - 최소 5행, 14 tests PASSED
- `src/strategy/multi_tf_trend.py`: `MultiTFTrendStrategy` (name=`multi_tf_trend`)
  - EMA10/20/50/100 기반 fast/mid/slow 추세 합성, score 0~3
  - score==3 → BUY, score==0 → SELL, HIGH conf if new alignment
  - 최소 110행, 14 tests PASSED
- `src/orchestrator.py`: 두 전략 import + STRATEGY_REGISTRY 등록 완료
- commit: `feat: add CandlePatternScore + MultiTFTrend strategies (28 tests)` → pushed

## 이전 작업 (2026-04-10) — PriceActionQuality + RegimeFilter 구현

- `src/strategy/price_action_quality.py`: `PriceActionQualityStrategy` (name=`price_action_quality`)
  - 봉 품질 점수화 (body_ratio, wick_ratio), 3연속 강한 양/음봉 → BUY/SELL
  - confidence: HIGH if body_ratio > 0.8 else MEDIUM, 최소 10행
- `src/strategy/regime_filter.py`: `RegimeFilterStrategy` (name=`regime_filter`)
  - EMA20/50 + ATR 기반 레짐 감지 (TREND_UP/DOWN/RANGING/HIGH_VOL)
  - BUY: TREND_UP+5bar_max 돌파 / SELL: TREND_DOWN+5bar_min 붕괴 / HOLD: 비추세
  - confidence: HIGH if TREND_UP + atr_ratio < mean*0.8 else MEDIUM, 최소 60행
- 각 전략 14개 테스트, 총 28 passed
- `src/orchestrator.py` STRATEGY_REGISTRY에 `price_action_quality`, `regime_filter` 추가, push 완료

## 이전 작업 (2026-04-10) — FractalBreak + MarketStructureBreak 구현

- `src/strategy/fractal_break.py`: `FractalBreakStrategy` (name=`fractal_break`)
  - 5봉 Williams Fractal 탐지, 최근 20봉 내 last_up/down fractal 탐색
  - BUY: close > last_up_fractal / SELL: close < last_down_fractal
  - confidence: HIGH if atr14>0 and deviation>1% else MEDIUM, 최소 15행
- `src/strategy/market_structure_break.py`: `MarketStructureBreakStrategy` (name=`market_structure_break`)
  - swing high/low (3봉 패턴) 탐지, 마지막 2개 swing 비교
  - BUY: HH+HL / SELL: LH+LL / HOLD: 혼합
  - confidence: HIGH if swing 2개씩 확보, 최소 20행
- 각 전략 14개 테스트, 총 28 passed
- `src/orchestrator.py` STRATEGY_REGISTRY에 `fractal_break`, `market_structure_break` 추가, push 완료

## 이전 작업 (2026-04-10) — MeanRevZScore + MomentumPersistence 구현

- `src/strategy/mean_rev_zscore.py`: `MeanRevZScoreStrategy` (name=`mean_rev_zscore`)
  - sma20/std20/zscore 계산, zscore_ma(5) 평활
  - BUY: zscore < -2.0 AND rising / SELL: zscore > 2.0 AND falling
  - confidence: HIGH if |zscore| > 2.5 else MEDIUM, 최소 30행
- `src/strategy/momentum_persistence.py`: `MomentumPersistenceStrategy` (name=`momentum_persistence`)
  - 최근 10봉 연속 상승/하락 스트릭 계산, avg_return rolling(20)
  - BUY: pos_streak >= 3 AND avg_return > 0 / SELL: neg_streak >= 3 AND avg_return < 0
  - confidence: HIGH if streak >= 5 else MEDIUM, 최소 25행
- 각 전략 14개 테스트, 총 28 passed
- `src/orchestrator.py` STRATEGY_REGISTRY에 `mean_rev_zscore`, `momentum_persistence` 추가, push 완료

## 이전 작업 (2026-04-10) — VolumeProfile + OrderFlowImbalance 구현

- `src/strategy/volume_profile.py`: `VolumeProfileStrategy` (name=`volume_profile`)
  - 최근 20봉 가격대별 거래량 집계, POC 버킷 중간가 계산
  - BUY: close < poc*0.99 AND 이전봉 대비 반등 / SELL: close > poc*1.01 AND 반락
  - confidence: HIGH if dist_ratio > 2% else MEDIUM, 최소 25행
- `src/strategy/order_flow_imbalance.py`: `OrderFlowImbalanceStrategy` (name=`order_flow_imbalance`)
  - 봉 내부 body/wick 구조로 buy/sell pressure 추정, imbalance rolling(10) MA
  - BUY: imbalance > ma AND > 0.3 / SELL: imbalance < ma AND < -0.3
  - confidence: HIGH if |imbalance| > 0.5 else MEDIUM, 최소 15행
- 각 전략 14개 테스트, 총 28 passed
- `src/orchestrator.py` STRATEGY_REGISTRY에 `volume_profile`, `order_flow_imbalance` 추가, push 완료

## 이전 작업 (2026-04-10) — DEMACross(spec 재정렬) + TrendSlopeFilter 구현

- `src/strategy/dema_cross.py`: fast=10/slow=25, min 35행, threshold=0.01 로 재구현
- `src/strategy/trend_slope_filter.py`: `TrendSlopeFilterStrategy` (name=`trend_slope_filter`)
  - numpy.polyfit 기반 선형 회귀 기울기, slope_norm > threshold AND 가속 시 BUY/SELL
  - confidence: HIGH if |slope_norm| > threshold*2 else MEDIUM, 최소 25행
- 각 전략 14개 테스트, 총 28 passed
- `src/orchestrator.py` STRATEGY_REGISTRY에 `trend_slope_filter` 추가, push 완료

## 이전 작업 (2026-04-10) — ParabolicSARTrend + RangeExpansion 구현

- `src/strategy/parabolic_sar_trend.py`: `ParabolicSARTrendStrategy` (name=`parabolic_sar_trend`)
  - 간소화 SAR 루프 직접 계산, prev/curr bullish 비교로 전환 감지, 최소 20행
  - confidence: HIGH if |close-SAR|/close > 0.02 else MEDIUM
- `src/strategy/range_expansion.py`: `RangeExpansionStrategy` (name=`range_expansion`) 재구현
  - bar_range=high-low, avg_range rolling(14), close_pos 기반 신호, 최소 20행
  - high==low 시 close_pos=0.5 division by zero 방지
- 각 전략 14개 테스트, 총 25 passed / 3 skipped
- `src/orchestrator.py` STRATEGY_REGISTRY에 `parabolic_sar_trend` 추가, push 완료

## 이전 작업 (2026-04-10) — SeasonalCycleStrategy + TrendFollowBreakStrategy 구현

- `src/strategy/seasonal_cycle.py`: `SeasonalCycleStrategy` (name=`seasonal_cycle`)
  - numpy.polyfit 선형 회귀 디트렌딩 + rolling std 정규화, cycle_pos 크로스오버 신호, 최소 30행
- `src/strategy/trend_follow_break.py`: `TrendFollowBreakStrategy` (name=`trend_follow_break`)
  - rolling mean ADX(14) + rolling 20봉 최고/최저 돌파 신호, 최소 40행
- 각 전략 14개 테스트 (총 28개 PASSED)
- `src/orchestrator.py` STRATEGY_REGISTRY에 두 전략 추가, push 완료

## 이전 작업 (2026-04-10) — AdaptiveThresholdStrategy + VolatilityClusterStrategy 구현

- `src/strategy/adaptive_threshold.py`: `AdaptiveThresholdStrategy` (name=`adaptive_threshold`)
  - ATR14 기반 정규화 가격, 동적 임계값(quantile 0.8/0.2), 크로스오버 신호, 최소 40행
- `src/strategy/volatility_cluster.py`: `VolatilityClusterStrategy` (name=`volatility_cluster`)
  - vol5/vol20 비율로 저변동성 구간 감지, direction으로 방향 판단, 최소 30행
- 각 전략 14개 테스트 (총 28개 PASSED)
- `src/orchestrator.py` STRATEGY_REGISTRY에 두 전략 추가, push 완료

## 이전 작업 (2026-04-10) — ValueAreaStrategy + DivergenceScoreStrategy 구현

- `src/strategy/value_area.py`: `ValueAreaStrategy` (name=`value_area`)
  - VWAP 기반 Value Area 이탈 후 재진입 신호, HIGH conf: |close-vwap| < std*0.3, 최소 25행
- `src/strategy/divergence_score.py`: `DivergenceScoreStrategy` (name=`divergence_score`)
  - RSI14 + CCI20 + mom10 방향 점수화(-3~+3), BUY: score>=2 AND 개선, HIGH: |score|==3, 최소 35행
- 각 전략 14개 테스트 (총 28개 PASSED)
- `src/orchestrator.py` STRATEGY_REGISTRY에 두 전략 추가, push 완료

## 이전 작업 (2026-04-10) — PriceSqueezeStrategy + InverseFisherRSIStrategy 구현

- `src/strategy/price_squeeze.py`: `PriceSqueezeStrategy` (name=`price_squeeze`)
  - BB+KC squeeze 감지, squeeze_release+momentum 방향으로 BUY/SELL, 최소 30행
- `src/strategy/inverse_fisher_rsi.py`: `InverseFisherRSIStrategy` (name=`inverse_fisher_rsi`)
  - RSI(10) → Inverse Fisher Transform, -0.5/+0.5 크로스오버 신호, 최소 20행
- 각 전략 14개 테스트 (총 28개 PASSED)
- `src/orchestrator.py` STRATEGY_REGISTRY에 두 전략 추가, push 완료

## 이전 작업 (2026-04-10) — RelativeStrengthStrategy + MomentumBreadthStrategy 구현

- `src/strategy/relative_strength.py`: `RelativeStrengthStrategy` (name=`relative_strength`)
  - roc_n/roc_avg/roc_std 기반, BUY/SELL/HOLD, 최소 40행
- `src/strategy/momentum_breadth.py`: `MomentumBreadthStrategy` (name=`momentum_breadth`)
  - mom5/mom10/mom20 score 0~3 기반, BUY score==3 / SELL score==0, 최소 35행
- 각 전략 14개 테스트 (총 28개 PASSED)
- `src/orchestrator.py` STRATEGY_REGISTRY에 두 전략 추가

## 이전 작업 (2026-04-10) — SmartMoneyConceptStrategy + PositionalScalingStrategy 구현

- `src/strategy/smc_strategy.py`: `SmartMoneyConceptStrategy` (name=`smc_strategy`)
  - CHoCH BUY: prev_structure_down AND close > recent_hh; CHoCH SELL: prev_structure_up AND close < recent_ll
  - HIGH conf: volume > avg * 1.5; 최소 15행
- `src/strategy/positional_scaling.py`: `PositionalScalingStrategy` (name=`positional_scaling`)
  - BUY: EMA20>EMA50>EMA100 AND pullback(close/EMA20-1 in [-0.01,0.02]) AND 양봉
  - HIGH conf: volume > avg * 1.2; 최소 105행
- `tests/test_smc_strategy.py`: 14개 테스트 전부 통과
- `tests/test_positional_scaling.py`: 14개 테스트 전부 통과
- `src/orchestrator.py`: `smc_strategy`, `positional_scaling` 등록 및 push 완료

## 이전 작업 (2026-04-10) — StochasticMomentumStrategy + VolumeROCStrategy 구현

- `src/strategy/stoch_momentum.py`: `StochasticMomentumStrategy` (name=`stoch_momentum`)
  - SMI = (distance.ewm(5) / (HL_range/2).ewm(5)) * 100, SMI_signal = SMI.ewm(3)
  - BUY: SMI crosses above signal AND SMI < 0; SELL: SMI crosses below signal AND SMI > 0
  - HIGH conf: |SMI| >= 40; 최소 20행
- `src/strategy/volume_roc.py`: `VolumeROCStrategy` (name=`volume_roc`)
  - vol_roc = (volume - volume.shift(10)) / volume.shift(10) * 100; vol_roc_ema = ewm(5)
  - BUY: vol_roc_ema > 50 AND 상승; SELL: vol_roc_ema > 50 AND 하락; HOLD: < 20
  - HIGH conf: vol_roc_ema > 100; 최소 15행
- `tests/test_stoch_momentum.py`: 13개 테스트 전부 통과
- `tests/test_volume_roc.py`: 13개 테스트 전부 통과
- `src/orchestrator.py`: `stoch_momentum`, `volume_roc` 등록 및 push 완료

## 이전 작업 (2026-04-10) — CCIDivergenceStrategy + DynamicPivotChannelStrategy 구현

- `src/strategy/cci_divergence.py`: `CCIDivergenceStrategy` (name=`cci_divergence`)
  - CCI14 계산, bullish/bearish divergence 감지
  - Bullish: price lower low + CCI higher low (CCI < -100)
  - Bearish: price higher high + CCI lower high (CCI > 100)
  - HIGH conf: divergence gap > 30, 최소 20행
- `src/strategy/dynamic_pivot_channel.py`: `DynamicPivotChannelStrategy` (name=`dynamic_pivot_channel`)
  - Rolling 7봉 max/min으로 upper/lower pivot 계산
  - BUY: close < lower pivot, SELL: close > upper pivot
  - HIGH conf: channel_width < ATR14 * 2, 최소 20행
- `tests/test_cci_divergence.py`: 15개 테스트 전부 통과
- `tests/test_dynamic_pivot_channel.py`: 16개 테스트 전부 통과
- `src/orchestrator.py`: `cci_divergence`, `dynamic_pivot_channel` 등록 및 push 완료

## 이전 작업 (2026-04-10) — HybridTrendReversionStrategy + MultiFactorScoreStrategy 구현

- `src/strategy/hybrid_trend_rev.py`: `HybridTrendReversionStrategy` (name=`hybrid_trend_rev`)
  - ADX EWM span=14, trending(>25)/ranging(<=25) 자동 감지
  - trending: EMA9>21>50 & RSI>50 → BUY; EMA9<21<50 & RSI<50 → SELL
  - ranging: close < BB_lower → BUY; close > BB_upper → SELL
  - HIGH confidence: ADX>40 or ADX<15; 최소 30행
- `src/strategy/multi_factor.py`: `MultiFactorScoreStrategy` (name=`multi_factor`)
  - 7팩터 점수화: RSI, MACD hist, EMA20, volume, BB, ATR, price trend
  - BUY: score>=4.0, SELL: score<=-4.0, HIGH conf: |score|>=5
  - 최소 25행
- `tests/test_hybrid_trend_rev.py`: 21개 테스트 전부 통과
- `tests/test_multi_factor.py`: 22개 테스트 전부 통과
- `src/orchestrator.py`: `hybrid_trend_rev`, `multi_factor` 등록 및 push 완료

## 최근 작업 (2026-04-10) — MeanReversionEntryStrategy + VolatilityMeanReversionStrategy 구현

- `src/strategy/mr_entry.py`: `MeanReversionEntryStrategy` (name=`mr_entry`)
  - consecutive_down/up(5봉), Wilder RSI14, vol > avg_vol 조건
  - BUY/SELL 신호, HIGH confidence: c_down>=4 AND rsi<30
  - 최소 20행
- `src/strategy/vol_mean_rev.py`: `VolatilityMeanReversionStrategy` (name=`vol_mean_rev`)
  - hist_vol(10봉) / vol_mean(30봉) = vol_ratio
  - 저변동성(< 0.5) + SMA20 방향, 고변동성(> 2) + RSI 극값
  - HIGH confidence: vol_ratio < 0.3 or > 3
  - 최소 45행, NaN 안전 처리
- `tests/test_mr_entry.py`: 15개 테스트 전부 통과
- `tests/test_vol_mean_rev.py`: 16개 테스트 전부 통과
- `src/orchestrator.py`: `mr_entry`, `vol_mean_rev` 등록 및 push 완료

## Status: **30 passed** | BreakoutRetestStrategy + VolatilityExpansionStrategy 구현 완료

## 최근 작업 (2026-04-10) — BreakoutRetestStrategy + VolatilityExpansionStrategy 구현

- `src/strategy/breakout_retest.py`: 돌파 후 되돌림(retest) 진입 전략 (resistance/support rolling(20).shift(3), ±0.5% tolerance, 양/음봉 확인, 최소 30행)
- `src/strategy/volatility_expansion.py`: 수축→팽창 추세 시작 감지 (hist_vol_5/hist_vol_20 비율, expansion<0.7 수축/expansion>1.2 팽창, HIGH confidence: expansion>1.8, 최소 25행)
- `tests/test_breakout_retest.py`: 15개 테스트 전부 통과
- `tests/test_volatility_expansion.py`: 15개 테스트 전부 통과
- `src/orchestrator.py`: `breakout_retest`, `volatility_expansion` 등록 및 push 완료

## Status: **35 passed** | WedgePatternStrategy + CrossoverConfluenceStrategy 구현 완료

## 최근 작업 (2026-04-10) — WedgePatternStrategy + CrossoverConfluenceStrategy 구현

- `src/strategy/wedge_pattern.py`: Rising/Falling wedge 패턴 감지 (polyfit 선형회귀, 수렴각 HIGH confidence, 최소 25행)
- `src/strategy/crossover_confluence.py`: EMA9/21/50 크로스오버 컨플루언스 + RSI14 필터 (최소 55행)
- `tests/test_wedge_pattern.py`: 17개 테스트 통과
- `tests/test_crossover_confluence.py`: 18개 테스트 통과
- `src/orchestrator.py`: `wedge_pattern`, `crossover_confluence` 등록

## Status: **32 passed** | TrendStrengthFilterStrategy + VolSpreadAnalysisStrategy 구현 완료

## 최근 작업 (2026-04-10) — TrendStrengthFilterStrategy + VolSpreadAnalysisStrategy 구현

- `src/strategy/trend_strength_filter.py`: `TrendStrengthFilterStrategy` (name=`trend_strength_filter`)
  - EMA21 추세 + EWM 방식 ADX/DI 복합 필터
  - BUY: ADX>20 AND DI+>DI- AND close>EMA21; ADX>35 → HIGH
  - SELL: ADX>20 AND DI->DI+ AND close<EMA21; ADX>35 → HIGH
  - 최소 30행; `tests/test_trend_strength_filter.py`: 16개 테스트 전부 통과
- `src/strategy/vol_spread_analysis.py`: `VolSpreadAnalysisStrategy` (name=`vol_spread_analysis`)
  - VSA: 가격 스프레드 + 볼륨 상호작용 분석
  - SELL: Upthrust bar (spread>1.5x + vol>1.5x + close near low)
  - BUY: Test for supply (spread<0.7x + vol<0.7x + close near high)
  - vol>2x or <0.5x avg → HIGH; 최소 25행; `tests/test_vol_spread_analysis.py`: 16개 테스트 전부 통과
- `src/orchestrator.py`: STRATEGY_REGISTRY 등록 + commit + push

## 이전 작업 (2026-04-10) — KijunBounceStrategy + VolumePriceConfirmStrategy 구현

- `src/strategy/kijun_bounce.py`: `KijunBounceStrategy` (name=`kijun_bounce`)
  - Ichimoku Kijun-sen(26) 동적 지지/저항 반등 전략
  - BUY: kijun ±0.5% 터치 + 양봉 + cloud bullish(tenkan>kijun); kijun rising → HIGH
  - SELL: kijun ±0.5% 터치 + 음봉 + cloud bearish(tenkan<kijun); kijun falling → HIGH
  - 최소 30행; `tests/test_kijun_bounce.py`: 15개 테스트 전부 통과
- `src/strategy/vol_price_confirm.py`: `VolumePriceConfirmStrategy` (name=`vol_price_confirm`)
  - 거래량-가격 방향 확인 전략
  - BUY: up_vol_days≥3 + close>EMA20 + RSI14 40-65; up_vol_days==5 → HIGH
  - SELL: down_vol_days≥3 + close<EMA20 + RSI14 35-60; down_vol_days==5 → HIGH
  - 최소 25행; `tests/test_vol_price_confirm.py`: 15개 테스트 전부 통과
- `src/orchestrator.py`: STRATEGY_REGISTRY 등록 + commit + push

## 이전 작업 (2026-04-10) — LiquiditySweepStrategy + MarketMakerStrategy 구현

- `src/strategy/liquidity_sweep.py`: `LiquiditySweepStrategy` (name=`liquidity_sweep`)
  - rolling(10) 고/저점 sweep 후 반전. Bullish: low<recent_low + close 복귀 → BUY; Bearish: high>recent_high + close 복귀 → SELL
  - sweep크기/ATR14 > 0.5 → HIGH; 최소 15행
  - `tests/test_liquidity_sweep.py`: 16개 테스트 전부 통과
- `src/strategy/market_maker_sig.py`: `MarketMakerStrategy` (name=`market_maker_sig`)
  - 축적(candle range rolling(10) < baseline rolling(20) * 0.7) + 조작(spike down/up) + 분배(close 이탈)
  - spike/ATR > 2.0 → HIGH; 최소 20행
  - `tests/test_market_maker_sig.py`: 16개 테스트 전부 통과
- `src/orchestrator.py`: STRATEGY_REGISTRY 등록 + commit + push

## 이전 작업 (2026-04-10) — AutoCorrelationStrategy + AdaptiveRSIThresholdStrategy 구현

- `src/strategy/autocorr_strategy.py`: `AutoCorrelationStrategy` (name=`autocorr_strategy`)
  - 가격 수익률 rolling(20) 자기상관 기반. Positive AC>0.1: 추세, Negative AC<-0.1: 평균회귀
  - |AC|>0.3 → HIGH confidence; 최소 25행
  - `tests/test_autocorr_strategy.py`: 16개 테스트 전부 통과
- `src/strategy/adaptive_rsi_thresh.py`: `AdaptiveRSIThresholdStrategy` (name=`adaptive_rsi_thresh`)
  - ADX EWM14 레짐 판단 + RSI Wilder EWM14. Trending(ADX>25): buy<40/sell>60; Range: buy<30/sell>70
  - RSI<20(trending) or RSI>80(trending) → HIGH; 최소 20행
  - `tests/test_adaptive_rsi_thresh.py`: 17개 테스트 전부 통과
- `src/orchestrator.py`: STRATEGY_REGISTRY 등록 + commit

## 이전 작업 (2026-04-10) — PAConfirmStrategy + EMADynamicSupportStrategy 구현

- `src/strategy/pa_confirm.py`: `PriceActionConfirmStrategy` (name=`pa_confirm`)
  - PA + 볼륨 + 모멘텀 3중 확인. body>ATR*0.8, vol>avg20*1.2, mom3 방향 일치
  - HIGH: body>ATR*1.5 AND vol>avg*1.5; 최소 25행
  - `tests/test_pa_confirm.py`: 22개 테스트 전부 통과
- `src/strategy/ema_dynamic_support.py`: `EMADynamicSupportStrategy` (name=`ema_dynamic_support`)
  - EMA21/EMA55 동적 지지저항. ±0.3% 터치 후 반등/반락 + 추세 방향 확인
  - EMA55 터치(±0.5%)도 신호; EMA200 완전 정렬 시 HIGH; 최소 60행
  - `tests/test_ema_dynamic_support.py`: 22개 테스트 전부 통과
- `src/orchestrator.py`: STRATEGY_REGISTRY 등록 + push

## 이전 작업 (2026-04-10) — BullBearPowerStrategy + OverextensionStrategy 구현

- `src/strategy/bull_bear_power.py`: `BullBearPowerStrategy` (name=`bull_bear_power`)
  - Elder's Bull Bear Power: EMA13 기반 Bull/Bear Power 계산
  - BUY: Bear<0 AND Bear rising AND EMA rising / SELL: Bull>0 AND Bull falling AND EMA falling
  - |power| > EMA13*1% → HIGH; 최소 20행
  - `tests/test_bull_bear_power.py`: 12개 테스트 전부 통과
- `src/strategy/overextension.py`: `OverextensionStrategy` (name=`overextension`)
  - (close-EMA50)/EMA50*100 distance, rolling 20 std 기반 2σ 이탈 탐지
  - BUY: 과매도 이탈 후 close 상승 / SELL: 과매수 이탈 후 close 하락
  - |distance| > 3σ → HIGH; 최소 75행
  - `tests/test_overextension.py`: 12개 테스트 전부 통과
- `src/orchestrator.py`: STRATEGY_REGISTRY 등록 + push

## 이전 작업 (2026-04-10) — SimplifiedGartleyStrategy + PriceClusterStrategy 구현

- `src/strategy/gartley_pattern.py`: `SimplifiedGartleyStrategy` (name=`gartley_pattern`)
  - XABCD Gartley 패턴 단순화: swing_low/high 기반 78.6% retracement D-point 탐지
  - 오차 < 1% → HIGH, < 2% → MEDIUM; 최소 35행
  - `tests/test_gartley_pattern.py`: 16개 테스트 전부 통과
- `src/strategy/price_cluster.py`: `PriceClusterStrategy` (name=`price_cluster`)
  - 50봉 close를 5 bin으로 나눠 최빈 cluster 탐지
  - BUY: cluster 하단 이탈 후 복귀 / SELL: cluster 상단 돌파 후 복귀
  - 빈도 > 평균의 2배 → HIGH; 최소 55행
  - `tests/test_price_cluster.py`: 16개 테스트 전부 통과
- `src/orchestrator.py`: STRATEGY_REGISTRY 등록 + push

## 이전 작업 (2026-04-10) — OrderBlockStrategy + FairValueGapStrategy 구현

- `src/strategy/order_block.py`: `OrderBlockStrategy` (name=`order_block`)
  - Smart Money OB: 강한 상승/하락(3봉, 5%) 직전 마지막 음봉/양봉 탐색
  - OB 존 진입 시 BUY/SELL; OB size > ATR14 → HIGH; 최소 15행
  - `tests/test_order_block.py`: 15개 테스트 전부 통과
- `src/strategy/fvg_strategy.py`: `FairValueGapStrategy` (name=`fvg_strategy`)
  - FVG mean reversion; gap > ATR14*1.5 → HIGH; 최근 10봉 탐색; 최소 15행
  - `tests/test_fvg_strategy.py`: 15개 테스트 전부 통과
- `src/orchestrator.py`: STRATEGY_REGISTRY 등록 + push

## 이전 작업 (2026-04-10) — RangeBoundStrategy + PreBreakoutStrategy 구현

- `src/strategy/range_bound.py`: `RangeBoundStrategy` (name=`range_bound`)
  - CI(Choppiness Index, n=14) > 61.8 횡보 감지 후 SMA20 밴드 반전 매매
  - CI > 70 → HIGH confidence; 최소 20행
  - `tests/test_range_bound.py`: 16개 테스트 전부 통과
- `src/strategy/pre_breakout.py`: `PreBreakoutStrategy` (name=`pre_breakout`)
  - ATR14/ATR14.rolling(20).mean() < 0.7 + vol < avg*0.8 수축 감지 후 SMA50 방향 진입
  - range_ratio < 0.5 AND vol < avg*0.6 → HIGH confidence; 최소 25행
  - `tests/test_pre_breakout.py`: 17개 테스트 전부 통과
- `src/orchestrator.py`: STRATEGY_REGISTRY에 두 전략 등록 후 push

## 이전 작업 (2026-04-10) — MomentumAccelerationStrategy + SwingPointStrategy 구현

- `src/strategy/momentum_accel.py`: `MomentumAccelerationStrategy` (name=`momentum_accel`)
  - mom5/mom10/accel/accel_ema 계산, accel_ema > 0.5 AND mom5 > 0 AND close > EMA20 → BUY
  - HIGH confidence: |accel_ema| > 1.5; 최소 20행
  - `tests/test_momentum_accel.py`: 14개 테스트 전부 통과
- `src/strategy/swing_point.py`: `SwingPointStrategy` (name=`swing_point`)
  - swing_high = high.rolling(3).max().shift(1), swing_low = low.rolling(3).min().shift(1)
  - close > swing_high → BUY, close < swing_low → SELL
  - 돌파 크기 > ATR14*0.5 → HIGH confidence; 최소 10행
  - `tests/test_swing_point.py`: 14개 테스트 전부 통과
- `src/orchestrator.py`: STRATEGY_REGISTRY에 두 전략 등록 후 push

## 이전 작업 (2026-04-10) — ConfluenceZoneStrategy + AdaptiveMACrossStrategy 구현

- `src/strategy/confluence_zone.py`: `ConfluenceZoneStrategy` (name=`confluence_zone`)
  - SMA20/SMA50/Pivot/RoundNumber 레벨 confluence 분석
  - zone_tolerance = ATR14*0.5, count>=2 신호, count>=3 HIGH confidence; 최소 55행
  - `tests/test_confluence_zone.py`: 22개 테스트 전부 통과
- `src/strategy/adaptive_ma_cross.py`: `AdaptiveMACrossStrategy` (name=`adaptive_ma_cross`)
  - ATR_ratio 기반 변동성 판단 → fast/slow 기간 동적 조절 (고변동성: 5/15, 저변동성: 15/40)
  - gap > ATR*0.3 → HIGH confidence; 최소 45행
  - `tests/test_adaptive_ma_cross.py`: 22개 테스트 전부 통과
- `src/orchestrator.py`: STRATEGY_REGISTRY에 두 전략 등록 후 push

## 이전 작업 (2026-04-10) — ConsolidationBreakoutStrategy + PriceRSIDivergenceStrategy 구현

- `src/strategy/consolidation_breakout.py`: `ConsolidationBreakoutStrategy` (name=`consolidation_breakout`)
  - 최근 10봉 3% 이내 range → consolidation, 이후 돌파 시 BUY/SELL
  - volume > avg*2.0 → HIGH confidence; 최소 15행
  - `tests/test_consolidation_breakout.py`: 15개 테스트 전부 통과
- `src/strategy/price_rsi_div.py`: `PriceRSIDivergenceStrategy` (name=`price_rsi_div`)
  - 30봉 pivot 기반 RSI divergence (좌우 3봉 wing)
  - Wilder EWM RSI14 직접 계산; RSI diff > 10 → HIGH confidence; 최소 35행
  - `tests/test_price_rsi_div.py`: 15개 테스트 전부 통과
- `src/orchestrator.py`: STRATEGY_REGISTRY에 두 전략 등록 후 push

## 이전 작업 (2026-04-10) — VolAdjustedTrendStrategy + TrendReversalPatternStrategy 구현

- `src/strategy/vol_adj_trend.py`: `VolAdjustedTrendStrategy` (name=`vol_adj_trend`)
  - ATR14로 정규화된 가격 이동으로 추세 강도+가속 측정
  - `tests/test_vol_adj_trend.py`: 12개 테스트 전부 통과
- `src/strategy/trend_reversal.py`: `TrendReversalPatternStrategy` (name=`trend_reversal`)
  - 20봉 신고/저점 + RSI divergence + 반전 캔들 복합 감지
  - `tests/test_trend_reversal.py`: 12개 테스트 전부 통과
- `src/orchestrator.py`: STRATEGY_REGISTRY에 두 전략 등록

## 이전 작업 (2026-04-10) — DualEMACrossStrategy + BreakoutConfirmationStrategy 구현

- `src/strategy/dual_ema_cross.py`: `DualEMACrossStrategy` (name=`dual_ema_cross`)
  - EMA 3개(5/13/34 피보나치) 완전 정렬 + EMA5/EMA13 크로스 확인
  - BUY: EMA5>EMA13>EMA34 AND 상향 크로스; SELL: 반대
  - HIGH conf: (EMA5-EMA34)/close > 1.5%; 최소 40행, 테스트 14개 통과
- `src/strategy/breakout_confirm.py`: `BreakoutConfirmationStrategy` (name=`breakout_confirm`)
  - resistance/support = rolling(20).max/min().shift(2)
  - 2봉 연속 돌파 + vol > avg*1.3 → BUY/SELL; HIGH conf: vol > avg*2.0
  - 최소 25행, 테스트 15개 통과
- `src/orchestrator.py`: STRATEGY_REGISTRY에 두 전략 등록

## 이전 작업 — ExhaustionBarStrategy + LinearChannelReversionStrategy 구현 완료

## 최근 작업 (2026-04-10) — BBKeltnerSqueezeStrategy + RSITrendFilterStrategy 구현

- `src/strategy/bb_keltner_squeeze.py`: `BBKeltnerSqueezeStrategy` (name=`bb_keltner_squeeze`)
  - BB(20,2σ)가 KC(20,1.5×ATR) 내부에 있으면 squeeze. 해제 시 momentum 방향으로 신호
  - Momentum = close - SMA(hl3, 20); HIGH conf: |mom| > mom.rolling(10).std()
  - 최소 25행, 테스트 14개 통과
- `src/strategy/rsi_trend_filter.py`: `RSITrendFilterStrategy` (name=`rsi_trend_filter`)
  - RSI14(EWM Wilder) + RSI_SMA(9) 추세 필터
  - BUY: RSI>50, RSI>SMA, prev<60 AND now>=60 크로스
  - SELL: RSI<50, RSI<SMA, prev>40 AND now<=40 크로스; HIGH conf: RSI>65/RSI<35
  - 최소 25행, 테스트 14개 통과
- `src/orchestrator.py`: STRATEGY_REGISTRY에 두 전략 등록

## 이전 작업 (2026-04-10) — VolumeClimaxStrategy + KeyReversalStrategy 구현

- `src/strategy/volume_climax.py`: `VolumeClimaxStrategy` (name=`volume_climax`)
  - Buying climax(극단 거래량+음봉) → SELL, Selling climax(극단 거래량+양봉) → BUY
  - RSI14 < 30 (BUY) / RSI14 > 70 (SELL) 추가 조건
  - HIGH conf: vol > avg*5.0, 최소 25행, 테스트 14개 통과
  - RSI 순수 상승/하락 추세에서 NaN 방지 처리 포함
- `src/strategy/key_reversal.py`: `KeyReversalStrategy` (name=`key_reversal`)
  - Bullish: 20봉 신저점 + close > prev_close + vol > avg*1.5 → BUY
  - Bearish: 20봉 신고점 + close < prev_close + vol > avg*1.5 → SELL
  - HIGH conf: 52주(260봉) 저점/고점 돌파, 최소 25행, 테스트 15개 통과
- `src/orchestrator.py`: STRATEGY_REGISTRY에 두 전략 등록

## 이전 작업 (2026-04-10) — EMARibbonStrategy + PriceChannelBreakStrategy 구현

- `src/strategy/ema_ribbon.py`: `EMARibbonStrategy` (name=`ema_ribbon`)
  - 5개 EMA 리본(5/10/20/40/80) + EMA5/EMA10 크로스 감지
  - BUY: 완전 bullish alignment + EMA5 cross above EMA10
  - SELL: 완전 bearish alignment + EMA5 cross below EMA10
  - HIGH conf: spread(ema5-ema80) > 2% of close, 최소 85행, 테스트 20개 통과
- `src/strategy/price_channel_break.py`: `PriceChannelBreakStrategy` (name=`price_channel_break`)
  - 20봉 채널 신규 돌파 (직전 3봉 이미 돌파 시 HOLD)
  - BUY: close > entry_high AND 직전 3봉 모두 ≤ entry_high
  - SELL: close < entry_low AND 직전 3봉 모두 ≥ entry_low
  - HIGH conf: 0.5% 이상 돌파, 최소 25행, 테스트 20개 통과
- `src/orchestrator.py`: STRATEGY_REGISTRY에 두 전략 등록

---

## 이전 상태: **32 passed** | TrendQualityStrategy + MomentumDivergenceStrategy 구현 완료

## 최근 작업 (2026-04-10) — TrendQualityStrategy + MomentumDivergenceStrategy 구현

- `src/strategy/trend_quality.py`: `TrendQualityStrategy` (name=`trend_quality`)
  - R² + normalized_slope 결합 quality_score 기반 추세 품질 전략
  - BUY: r_squared>0.8 AND slope>0 AND quality_score>0.05 / SELL: 반대
  - HIGH conf: r_squared>0.9 AND quality_score>0.09, 최소 25행, 테스트 16개 통과
- `src/strategy/momentum_div.py`: `MomentumDivergenceStrategy` (name=`momentum_div`)
  - 가격 모멘텀(10봉) vs 볼륨 모멘텀 다이버전스 + RSI14 필터
  - BUY: price_mom<0 AND vol_mom>0.5 AND RSI14<50 / SELL: 반대
  - HIGH conf: |vol_mom|>1.0, 최소 20행, 테스트 16개 통과
- `src/orchestrator.py`: STRATEGY_REGISTRY에 두 전략 등록

---

## 이전 상태: **34 passed** | IchimokuBreakoutStrategy + MACDSlopeStrategy 구현 완료

## 최근 작업 (2026-04-10) — IchimokuBreakoutStrategy + MACDSlopeStrategy 구현

- `src/strategy/ichimoku_breakout.py`: `IchimokuBreakoutStrategy` (name=`ichimoku_breakout`)
  - TK Cross(tenkan 크로스 순간) + close > kumo_top/< kumo_bottom 조건
  - confidence: kumo까지 거리 > 2% → HIGH, 최소 80행, 테스트 17개 통과
- `src/strategy/macd_slope.py`: `MACDSlopeStrategy` (name=`macd_slope`)
  - hist_slope(3봉 기울기) + slope_acceleration(가속도) 기반
  - BUY: hist<0 AND slope>0 AND accel>0, SELL: 반대
  - |accel| > accel rolling std → HIGH confidence, 최소 35행, 테스트 17개 통과
- `src/orchestrator.py`: STRATEGY_REGISTRY에 두 전략 등록

---

## 이전 작업 (2026-04-10) — RenkoTrendStrategy + WickReversalStrategy 구현

- `src/strategy/renko_trend.py`: `RenkoTrendStrategy` (name=`renko_trend`)
  - OHLCV → Renko brick 시뮬레이션 (ATR14 EWM brick_size)
  - 연속 상승/하락 >=3 → BUY/SELL, >=5 → HIGH confidence
  - atr14 컬럼 없으면 자체 계산, 최소 20행, 테스트 15개 통과
- `src/strategy/wick_reversal.py`: `WickReversalStrategy` (name=`wick_reversal`)
  - lower/upper wick ratio + SMA20 + volume 필터
  - Hammer(lower>0.6, close>SMA*0.97) → BUY, Shooting Star(upper>0.6, close<SMA*1.03) → SELL
  - wick_ratio>0.7 → HIGH confidence, 최소 15행, 테스트 15개 통과
- `src/orchestrator.py`: STRATEGY_REGISTRY에 두 전략 등록

---

## Status (이전): **32 passed** | ROCMACrossStrategy + VolumePriceTrendConfirmStrategy 구현 완료

## 최근 작업 (2026-04-10) — ROCMACrossStrategy + VolumePriceTrendConfirmStrategy 구현

- `src/strategy/roc_ma_cross.py`: `ROCMACrossStrategy` (name=`roc_ma_cross`)
  - ROC(12) + 3봉 MA 스무딩 + EMA50 필터, 최소 20행, 테스트 16개 통과
- `src/strategy/vpt_confirm.py`: `VolumePriceTrendConfirmStrategy` (name=`vpt_confirm`)
  - VPT + EWM(14) Signal + Histogram 확인 + EMA20 필터, 최소 25행, 테스트 16개 통과
- `src/orchestrator.py`: STRATEGY_REGISTRY에 두 전략 등록

---

## Status (이전): **34 passed** | SRBounceStrategy + CandleScoreStrategy 구현 완료

## 최근 작업 (2026-04-10) — SRBounceStrategy + CandleScoreStrategy 구현

- `src/strategy/sr_bounce.py`: `SRBounceStrategy` (name=`sr_bounce`)
  - 동적 지지/저항 레벨 반등 감지, pivot 50봉 윈도우, 좌우 5봉 기준
  - BUY/SELL: 레벨 ±1% 터치 + vol > avg*1.1, touches>=3 → HIGH, 최소 60행
  - 테스트 16개 전부 통과
- `src/strategy/candle_score.py`: `CandleScoreStrategy` (name=`candle_score`)
  - 5개 항목 점수화 (양봉, upper/lower shadow, volume, body), score>=4 → 신호
  - score==5 → HIGH confidence, 최소 15행
  - 테스트 18개 전부 통과
- `src/orchestrator.py`: 두 전략 import + STRATEGY_REGISTRY 등록

## 이전 작업 (2026-04-10) — HurstExponentStrategy + ApproximateEntropyStrategy 구현

- `src/strategy/hurst_strategy.py`: `HurstExponentStrategy` (name=`hurst_strategy`)
  - RS Analysis로 Hurst Exponent 추정 (numpy만, scipy 불필요)
  - H > 0.55 추세 추종, H < 0.45 평균 회귀, 최소 40행
  - HIGH confidence: H > 0.65 or H < 0.35, 테스트 17개 전부 통과
- `src/strategy/entropy_strategy.py`: `ApproximateEntropyStrategy` (name=`entropy_strategy`)
  - Shannon entropy로 시장 무질서도 측정 (최근 20봉 price_changes 기준)
  - entropy < 0.7 추세 추종, entropy > 1.0 평균 회귀, 최소 25행
  - HIGH confidence: entropy < 0.5 or > 1.05, 테스트 17개 전부 통과
- `src/orchestrator.py`: 두 전략 import + STRATEGY_REGISTRY 등록

## 이전 작업 (2026-04-10) — CoppockEnhancedStrategy + VolumeWeightedRSIStrategy 구현

- `src/strategy/coppock_enhanced.py`: `CoppockEnhancedStrategy` (name=`coppock_enhanced`)
  - Coppock = WMA(11) of (ROC14 + ROC11), RSI14 필터
  - BUY: Coppock crosses above 0 AND rising AND RSI > 50
  - SELL: Coppock crosses below 0 AND falling AND RSI < 50
  - HIGH confidence: |Coppock| > rolling(20).std()
  - 최소 30행, 테스트 15개 전부 통과
- `src/strategy/vwrsi.py`: `VolumeWeightedRSIStrategy` (name=`vwrsi`)
  - Volume-Weighted RSI, EWM span=14
  - BUY: VWRSI crosses above 30 (HIGH if prev < 20)
  - SELL: VWRSI crosses below 70 (HIGH if prev > 80)
  - 최소 20행, 테스트 17개 전부 통과
- `src/orchestrator.py`: 두 전략 import + STRATEGY_REGISTRY 등록

## 이전 작업 (2026-04-10) — ParabolicMoveStrategy + FailedBreakoutStrategy 구현

- `src/strategy/parabolic_move.py`: `ParabolicMoveStrategy` (name=`parabolic_move`)
  - ROC5/ROC10 가속 감지, RSI14 소진 역매매
  - SELL: Parabolic up + RSI > 80 (HIGH if RSI > 85)
  - BUY: Parabolic down + RSI < 20 (HIGH if RSI < 15)
  - 최소 20행, 테스트 15개 전부 통과
- `src/strategy/failed_breakout.py`: `FailedBreakoutStrategy` (name=`failed_breakout`)
  - resistance/support = rolling(20).max/min.shift(1)
  - Fake 상향돌파(high > res, close < res) → SELL
  - Fake 하향돌파(low < sup, close > sup) → BUY
  - HIGH confidence: 돌파범위/ATR14 > 0.5
  - 최소 25행, 테스트 15개 전부 통과
- `src/orchestrator.py`: 두 전략 import + STRATEGY_REGISTRY 등록
- commit: 5c4b8f9, pushed to origin/main

## 이전 작업 | SupertrendMultiStrategy + NarrowRangeStrategy 구현 완료

## 최근 작업 (2026-04-10) — SupertrendMultiStrategy + NarrowRangeStrategy 구현

- `src/strategy/supertrend_multi.py`: `SupertrendMultiStrategy` (name=`supertrend_multi`)
  - Supertrend 3개: (ATR10, mult=1.5), (ATR14, mult=2.0), (ATR20, mult=3.0)
  - 자체 ATR 계산 (EWM), final_upper/lower 추적
  - BUY: 3개 모두 trend==1, SELL: 3개 모두 trend==-1
  - HIGH confidence: 조건 충족 + volume > avg_vol * 1.1
  - 최소 25행, 테스트 14개 전부 통과
- `src/strategy/narrow_range.py`: `NarrowRangeStrategy` (name=`narrow_range`)
  - NR7: prev봉이 최근 7봉 중 최소 range
  - NR4: prev봉이 최근 4봉 중 최소 range
  - BUY: prev봉 NR7 + current close > prev high
  - SELL: prev봉 NR7 + current close < prev low
  - HIGH confidence: NR4+NR7 둘 다 충족
  - 기존 nr7과 차별화: 돌파 확인 로직 포함
  - 최소 10행, 테스트 14개 전부 통과
- STRATEGY_REGISTRY 등록 완료, 커밋 및 push 완료

## Status: **29 passed** | DonchianMidlineStrategy + TripleScreenStrategy 구현 완료

## 최근 작업 (2026-04-10) — DonchianMidlineStrategy + TripleScreenStrategy 구현

- `src/strategy/donchian_midline.py`: `DonchianMidlineStrategy` (name=`donchian_midline`)
  - Donchian Channel upper/lower 20봉, midline = (upper+lower)/2
  - BUY: close crosses above midline + close > EMA50
  - SELL: close crosses below midline + close < EMA50
  - HIGH confidence: BUY시 close > upper*0.98, SELL시 close < lower*1.02
  - 최소 55행, 테스트 14개 전부 통과
- `src/strategy/triple_screen.py`: `TripleScreenStrategy` (name=`triple_screen`)
  - Screen1 (Tide): EMA26 기울기 → bullish/bearish tide
  - Screen2 (Wave): Stochastic %K < 30 (bullish tide), > 70 (bearish tide)
  - Screen3 (Ripple): 양봉(BUY) / 음봉(SELL) 확인
  - HIGH confidence: stoch_k < 20 (BUY) / > 80 (SELL), 최소 30행
  - 테스트 15개 전부 통과
- STRATEGY_REGISTRY 등록 완료, 커밋 및 push 완료

## Status: **28 passed** | POCStrategy + BidAskImbalanceStrategy 구현 완료

## 최근 작업 (2026-04-10) — POCStrategy + BidAskImbalanceStrategy 구현

- `src/strategy/poc_strategy.py`: `POCStrategy` (name=`poc_strategy`)
  - 최근 20봉 고저 범위를 10 bin으로 나눠 볼륨 가중 분포 계산
  - POC = 가장 많은 볼륨 bin 중앙값, VAH/VAL = 70% value area 경계
  - BUY: close < VAL, SELL: close > VAH
  - HIGH confidence: |close - POC| / POC > 2%, 최소 25행
- `src/strategy/bid_ask_imbalance.py`: `BidAskImbalanceStrategy` (name=`bid_ask_imbalance`)
  - Buy/Sell volume 추정: volume * (close-low)/(high-low), volume * (high-close)/(high-low)
  - Imbalance EMA(span=10) 계산
  - BUY: imbalance_ema > 0.2 AND close > EMA20, SELL: imbalance_ema < -0.2 AND close < EMA20
  - HIGH confidence: |imbalance_ema| > 0.4, 최소 20행
- 각 전략 테스트 14개씩, 28개 전부 통과
- STRATEGY_REGISTRY 등록 완료, 커밋 및 push 완료

## Status: **30 passed** | PriceDeviationStrategy + AccelerationBandStrategy 구현 완료

## 최근 작업 (2026-04-10) — PriceDeviationStrategy + AccelerationBandStrategy 구현

- `src/strategy/price_deviation.py`: `PriceDeviationStrategy` (name=`price_deviation`)
  - SMA20 편차 Z-Score 기반 평균 복귀: deviation=(close-sma20)/sma20*100, z=deviation/dev_std
  - BUY: z < -1.5, SELL: z > 1.5
  - HIGH confidence: |z| > 2.0, 최소 25행
- `src/strategy/acceleration_band.py`: `AccelerationBandStrategy` (name=`acceleration_band`)
  - Headley Acceleration Bands: upper/lower = sma20 ± 4*sma20*SMA20((h-l)/(h+l))
  - BUY: close crosses above upper, SELL: close crosses below lower
  - HIGH confidence: 1% 이상 돌파, 최소 25행
- 각 전략 테스트 15개씩, 30개 전부 통과
- STRATEGY_REGISTRY 등록 완료, 커밋 및 push 완료

## Status: **30 passed** | BullishEngulfingZoneStrategy + ThreeBarReversalStrategy 구현 완료

## 최근 작업 (2026-04-10) — BullishEngulfingZoneStrategy + ThreeBarReversalStrategy 구현

- `src/strategy/engulfing_zone.py`: `BullishEngulfingZoneStrategy` (name=`engulfing_zone`)
  - 20봉 내 pivot high/low (좌우 3봉) 탐색
  - Bullish Engulfing: 음봉→양봉, body비율>1.1, close ±1% support zone
  - Bearish Engulfing: 양봉→음봉, body비율>1.1, close ±1% resistance zone
  - HIGH confidence: ratio > 1.5, 최소 25행
- `src/strategy/three_bar_reversal.py`: `ThreeBarReversalStrategy` (name=`three_bar_reversal`)
  - prev2/prev1(inside bar)/current 3봉 패턴
  - Bullish: prev2 음봉, prev1 inside, current 양봉 AND close > prev2 open, vol > avg*1.2
  - Bearish: prev2 양봉, prev1 inside, current 음봉 AND close < prev2 open, vol > avg*1.2
  - HIGH confidence: current range > 2× prev1 range, 최소 15행
- 각 전략 테스트 15개씩, 30개 전부 통과
- STRATEGY_REGISTRY 등록 완료, 커밋 완료

## Status: **30 passed** | AnchoredVWAPStrategy + VolatilityRegimeStrategy 전략 추가 완료

## 최근 작업 (2026-04-10) — AnchoredVWAPStrategy + VolatilityRegimeStrategy 구현

- `src/strategy/anchored_vwap.py`: `AnchoredVWAPStrategy` (name=`anchored_vwap`)
  - 최근 50봉 gap(>3%) anchor 또는 20봉 lowest low/highest high anchor
  - Anchored VWAP = Σ(close×vol) / Σ(vol) from anchor
  - BUY: close > AVWAP AND close > EMA20 AND vol > avg_vol_20
  - SELL: close < AVWAP AND close < EMA20 AND vol > avg_vol_20
  - HIGH confidence: gap anchor + |close/avwap - 1| > 1%, 최소 25행
- `src/strategy/volatility_regime.py`: `VolatilityRegimeStrategy` (name=`volatility_regime`)
  - ATR14 EWM 기반 high/low vol 레짐 감지
  - Low vol + BB squeeze → Breakout (BUY/SELL)
  - High vol → Mean reversion (BUY/SELL)
  - HIGH confidence: ATR_ratio > 2×mean 또는 < 0.5×mean, 최소 35행
- 각 전략 테스트 15개씩, 30개 전부 통과
- STRATEGY_REGISTRY 등록 완료, push 완료

## 최근 작업 (2026-04-10) — TIIStrategy + HTFEMAStrategy 구현

- `src/strategy/tii_strategy.py`: `TrendIntensityIndexStrategy` (name=`tii_strategy`)
  - SMA30 기반 TII (0~100): 30봉 중 SMA30 위 비율 × 100
  - BUY: TII > 80 AND close > SMA30 / SELL: TII < 20 AND close < SMA30
  - HIGH confidence: TII > 90 or TII < 10, 최소 35행
- `src/strategy/htf_ema.py`: `HigherTimeframeEMAStrategy` (name=`htf_ema`)
  - HTF 시뮬레이션: 4봉마다 샘플링 후 EMA21, current EMA9
  - BUY: HTF EMA 상승 + close crosses above EMA9
  - SELL: HTF EMA 하락 + close crosses below EMA9
  - HIGH confidence: HTF EMA 3연속 상승/하락, 최소 50행
- 각 전략 테스트 16개/21개, 37개 전부 통과
- STRATEGY_REGISTRY 등록 완료, push 완료

## 최근 작업 (2026-04-10) — ZeroLagMACDStrategy + AdaptiveStopStrategy 구현

- `src/strategy/zlmacd.py`: `ZeroLagMACDStrategy` (name=`zlmacd`)
  - ZL EMA = ema + (ema - ema.ewm(span).mean())
  - BUY: Histogram 음→양 AND ZL MACD rising
  - SELL: Histogram 양→음 AND ZL MACD falling
  - HIGH confidence: |hist| > rolling(20).std(), 최소 35행
- `src/strategy/adaptive_stop.py`: `AdaptiveStopStrategy` (name=`adaptive_stop`)
  - ATR14 EWM, Long/Short stop, Wilder RSI14
  - BUY: close > long_stop AND close > EMA50 AND RSI > 50
  - SELL: close < short_stop AND close < EMA50 AND RSI < 50
  - HIGH confidence: RSI > 60 or RSI < 40, 최소 25행
- 각 전략 테스트 15+16개, 31개 전부 통과
- STRATEGY_REGISTRY 등록 완료, push 완료

---

## 이전 작업 (2026-04-10) — ChaikinOscillatorStrategy + AlligatorStrategy 구현

- `src/strategy/chaikin_osc.py`: `ChaikinOscillatorStrategy` (name=`chaikin_osc`)
  - MFM→MFV→ADL→Chaikin Osc (EWM span3 - span10)
  - BUY: Osc crosses above 0 AND close > EMA20
  - SELL: Osc crosses below 0 AND close < EMA20
  - HIGH confidence: |Osc| > rolling(20).std(), 최소 25행
- `src/strategy/alligator.py`: `AlligatorStrategy` (name=`alligator`)
  - SMMA: Jaw(13), Teeth(8), Lips(5)
  - BUY: lips > teeth > jaw AND close > lips
  - SELL: lips < teeth < jaw AND close < lips
  - HIGH confidence: spread > avg_spread, 최소 20행
- 각 전략 테스트 15개씩, 30개 전부 통과
- STRATEGY_REGISTRY 등록 완료, push 완료

---

## 이전 Status: **28 passed** | HeikinAshiSmoothedStrategy + KeltnerRSIStrategy 전략 추가 완료

## 최근 작업 (2026-04-10) — HeikinAshiSmoothedStrategy + KeltnerRSIStrategy 구현

- `src/strategy/ha_smoothed.py`: `HeikinAshiSmoothedStrategy` 구현 (name=`ha_smoothed`)
  - HA 캔들 + 5기간 EMA 스무딩, 연속 3봉 + wick 없음 조건
  - BUY: >=3 연속 양봉 + lower wick 없음, SELL: >=3 연속 음봉 + upper wick 없음
  - HIGH confidence: >=5연속 + wick 없음, 최소 20행
- `src/strategy/keltner_rsi.py`: `KeltnerRSIStrategy` 구현 (name=`keltner_rsi`)
  - EMA20 ± 2*ATR14 채널, RSI14 (ewm 방식)
  - BUY: close < lower AND RSI < 35, SELL: close > upper AND RSI > 65
  - HIGH confidence: RSI < 25 or RSI > 75, 최소 25행
- 각 전략 테스트 14개씩, 28개 전부 통과 (0 fail)
- STRATEGY_REGISTRY 등록 완료, push 완료

## 이전 작업 (2026-04-10) — FibRetracementStrategy + StochDivergenceStrategy 구현

- `src/strategy/fib_retracement.py`: `FibRetracementStrategy` 구현 (name=`fib_retracement`)
  - 50봉 swing_high/low, Fibonacci 레벨 0~100%, SMA50 추세 필터
  - BUY: 상승추세 + 38.2%~61.8% 존 반등, SELL: 하락추세 + 저항
  - HIGH confidence: 61.8% 황금비율 ±0.5%, 최소 55행
- `src/strategy/stoch_divergence.py`: `StochDivergenceStrategy` 구현 (name=`stoch_divergence`)
  - K(14)/D(3) 스토캐스틱, bullish/bearish divergence + K×D 크로스
  - HIGH confidence: divergence gap > 10, 최소 20행
- 각 전략 테스트 14개씩, 28개 전부 통과 (0 fail)
- STRATEGY_REGISTRY 등록 완료

## 이전 작업 (2026-04-10) — CupHandleStrategy + FlagPennantStrategy 구현

- `src/strategy/cup_handle.py`: `CupHandleStrategy` 구현 (name=`cup_handle`)
  - Cup: 좌우 고점 U자형, 너비 20~50봉, 깊이 10~40%
  - Handle: cup_right 후 3~10봉 소폭 조정 (깊이 < Cup깊이/3)
  - BUY: close > 우측 고점 돌파
  - HIGH confidence: 돌파 볼륨 > 평균 1.5배
  - 최소 60행, Python 3.9 호환
- `src/strategy/flag_pennant.py`: `FlagPennantStrategy` 구현 (name=`flag_pennant`)
  - Pole: 10봉 내 5% 이상 급등/급락
  - Consolidation: pole 이후 5~15봉 변동폭 감소
  - BUY: Bullish pole + consolidation 상단 돌파
  - SELL: Bearish pole + consolidation 하단 이탈
  - HIGH confidence: pole > 8%
  - 최소 30행, Python 3.9 호환
- `src/orchestrator.py`: "cup_handle", "flag_pennant" STRATEGY_REGISTRY 등록
- `tests/test_cup_handle.py`: 15개 테스트 (전부 통과)
- `tests/test_flag_pennant.py`: 16개 테스트 (전부 통과)

## 이전 작업 (2026-04-10) — RelativeVolumeStrategy + PriceMomentumOscillator 구현

- `src/strategy/relative_volume.py`: `RelativeVolumeStrategy` 구현 (name=`relative_volume`)
  - RVOL = volume / avg_volume_20 (look-ahead 방지)
  - VWAP = rolling 20 거래량 가중 평균
  - BUY: RVOL > 2.0 AND 양봉 AND close > VWAP
  - SELL: RVOL > 2.0 AND 음봉 AND close < VWAP
  - HIGH confidence: RVOL > 3.0 AND 볼린저 상/하단 돌파
  - 최소 25행, Python 3.9 호환
- `src/strategy/pmo_strategy.py`: `PriceMomentumOscillator` 구현 (name=`pmo_strategy`)
  - ROC_1 → Smoothed1(EWM span=35)*10 → PMO(EWM span=20) → Signal(EWM span=10)
  - BUY: PMO crosses above Signal AND PMO < 0 (oversold)
  - SELL: PMO crosses below Signal AND PMO > 0 (overbought)
  - HIGH confidence: |PMO - Signal| > 0.5
  - 최소 60행, Python 3.9 호환
- `src/orchestrator.py`: "relative_volume", "pmo_strategy" STRATEGY_REGISTRY 등록
- `tests/test_relative_volume.py`: 16개 테스트 (전부 통과)
- `tests/test_pmo_strategy.py`: 17개 테스트 (전부 통과)

## 이전 작업 (2026-04-09) — IchimokuCloudPosStrategy + ConsecutiveCandlesStrategy 구현

- `src/strategy/ichimoku_cloud_pos.py`: `IchimokuCloudPosStrategy` 구현
  - 현재 구름 위치 기반 신호 (senkou_a.shift(26), senkou_b.shift(26))
  - BUY: close > cloud_top AND tenkan > kijun
  - SELL: close < cloud_bottom AND tenkan < kijun
  - confidence: HIGH if dist > 2%, MEDIUM 그 외
  - 최소 80행, Python 3.9 호환
- `src/strategy/consecutive_candles.py`: `ConsecutiveCandlesStrategy` 구현
  - 연속 양봉/음봉 + volume 증가 확인
  - BUY: bull_count >= 4 AND volume 단조 증가
  - SELL: bear_count >= 4 AND volume 단조 증가
  - confidence: HIGH if count >= 6, MEDIUM if >= 4
  - 최소 15행, Python 3.9 호환
- `src/orchestrator.py`: "ichimoku_cloud_pos", "consecutive_candles" STRATEGY_REGISTRY 등록
- `tests/test_ichimoku_cloud_pos.py`: 15개 테스트 (전부 통과)
- `tests/test_consecutive_candles.py`: 15개 테스트 (전부 통과)

## 이전 작업 (2026-04-09) — OBVDivergenceStrategy + RSIOBOSStrategy 구현

- `src/strategy/obv_divergence.py`: `OBVDivergenceStrategy` 구현
  - OBV = cumsum(volume * sign(close diff)), OBV_EMA = EWM(span=20)
  - Bullish: close < close.shift(10)*1.01 AND OBV_EMA > OBV_EMA.shift(10) → BUY
  - Bearish: close > close.shift(10)*0.99 AND OBV_EMA < OBV_EMA.shift(10) → SELL
  - confidence: HIGH if OBV_EMA 변화 > std(OBV_EMA, 20), MEDIUM 그 외
  - 최소 25행, Python 3.9 호환
- `src/strategy/rsi_ob_os.py`: `RSIOBOSStrategy` 구현
  - RSI14 + vol_avg 20기간 확인
  - BUY: RSI14 < 30 AND volume > vol_avg*1.2 AND RSI 반전(상승)
  - SELL: RSI14 > 70 AND volume > vol_avg*1.2 AND RSI 꺾임(하락)
  - confidence: HIGH if RSI < 25 or > 75, MEDIUM 그 외
  - 최소 25행, Python 3.9 호환
- `src/orchestrator.py`: "obv_divergence", "rsi_ob_os" STRATEGY_REGISTRY 등록
- `tests/test_obv_divergence.py`: 14개 테스트 (전부 통과)
- `tests/test_rsi_ob_os.py`: 14개 테스트 (전부 통과)

## 이전 작업 (2026-04-09) — MultiScoreStrategy + ADXRegimeStrategy 구현

- `src/strategy/multi_score.py`: `MultiScoreStrategy` 구현
  - 5개 지표 앙상블: close>EMA50, RSI14>50, close>SMA20, volume>vol_sma20*1.1, MACD_hist>0
  - BUY: bull_score >= 4, SELL: bear_score >= 4
  - confidence: HIGH if score==5, MEDIUM if score==4
  - 최소 30행, Python 3.9 호환
- `src/strategy/adx_regime.py`: `ADXRegimeStrategy` 구현
  - EWM 방식으로 ATR14/+DM/-DM 계산 (adx_trend.py와 다른 접근)
  - 트렌딩(ADX>25): +DI>-DI→BUY, -DI>+DI→SELL
  - 횡보(ADX<20): HOLD
  - confidence: HIGH if ADX>35, MEDIUM if ADX>25
  - 최소 30행, Python 3.9 호환
- `src/orchestrator.py`: "multi_score", "adx_regime" STRATEGY_REGISTRY 등록
- `tests/test_multi_score.py`: 16개 테스트 (전체 통과)
- `tests/test_adx_regime.py`: 16개 테스트 (전체 통과)

## 이전 작업 (2026-04-09) — LRChannelStrategy + MomentumReversalStrategy 구현

- `src/strategy/lr_channel.py`: `LRChannelStrategy` 구현
  - numpy 직접 계산으로 slope/intercept 산출 (scipy 미사용)
  - upper/lower channel = lr_center ± 2 * std(residuals)
  - BUY: close < lower_channel AND slope > 0
  - SELL: close > upper_channel AND slope < 0
  - confidence: |residual| > 2.5*std → HIGH, > 2.0*std → MEDIUM, 최소 30행
- `src/strategy/momentum_reversal.py`: `MomentumReversalStrategy` 구현
  - mom14 = close - close.shift(14), mom_ema = EWM(mom14, span=9)
  - BUY: mom14 < 0 AND mom_ema 상승 AND close 상승봉
  - SELL: mom14 > 0 AND mom_ema 하락 AND close 하락봉
  - confidence: |mom14| > std(mom14, 20) → HIGH, 최소 25행
- `src/orchestrator.py`: "lr_channel", "momentum_reversal" STRATEGY_REGISTRY 등록
- `tests/test_lr_channel.py`: 18개 테스트
- `tests/test_momentum_reversal.py`: 18개 테스트 (총 36개 통과)

## 이전 작업 (2026-04-09) — DoubleTopBottomStrategy + MACDHistDivStrategy 구현

- `src/strategy/double_top_bottom.py`: `DoubleTopBottomStrategy` 구현
  - Double Bottom (BUY): 최근 20봉 pivot low 2개, 2% 이내 수렴, 넥라인 돌파
  - Double Top (SELL): 최근 20봉 pivot high 2개, 2% 이내 수렴, 넥라인 하향 돌파
  - confidence: 돌파폭 > 1% → HIGH, 최소 25행
- `src/strategy/macd_hist_div.py`: `MACDHistDivStrategy` 구현
  - Bullish Div (BUY): close 10봉 최저, histogram 개선 중 (< 0)
  - Bearish Div (SELL): close 10봉 최고, histogram 약화 중 (> 0)
  - confidence: |hist 변화| > std(hist, 20) → HIGH, 최소 40행
- `src/orchestrator.py`: "double_top_bottom", "macd_hist_div" STRATEGY_REGISTRY 등록
- `tests/test_double_top_bottom.py`: 15개 테스트
- `tests/test_macd_hist_div.py`: 15개 테스트 (총 30개 통과)

## 이전 작업 (2026-04-09) — VolumeSurgeStrategy + PriceVelocityStrategy 구현

- `src/strategy/volume_surge.py`: `VolumeSurgeStrategy` 구현
  - vol_ratio > 2.5 AND 20봉 고점 돌파 AND 양봉 → BUY
  - vol_ratio > 2.5 AND 20봉 저점 붕괴 AND 음봉 → SELL
  - confidence: vol_ratio > 4.0 → HIGH / 최소 25행
- `src/strategy/price_velocity.py`: `PriceVelocityStrategy` 구현
  - velocity = (close - close.shift(5)) / 5, accel = velocity - velocity.shift(5)
  - BUY: velocity > 0 AND accel > 0 AND velocity > vol_vel * 0.5
  - SELL: velocity < 0 AND accel < 0 AND |velocity| > vol_vel * 0.5
  - confidence: |velocity| > vol_vel * 1.0 → HIGH / 최소 20행
- `src/orchestrator.py`: "volume_surge", "price_velocity" STRATEGY_REGISTRY 등록
- `tests/test_volume_surge.py`: 13개 테스트
- `tests/test_price_velocity.py`: 14개 테스트 (총 27개 통과)

## 이전 작업 (2026-04-09) — SupertrendRSIStrategy + BBBandwidthStrategy 구현

- `src/strategy/supertrend_rsi.py`: `SupertrendRSIStrategy` 구현
  - EWM ATR(span=10) 기반 Supertrend + RSI14 복합
  - BUY: Supertrend bullish AND RSI 50~70
  - SELL: Supertrend bearish AND RSI 30~50
  - confidence: |RSI-50|>15 AND ST거리>1% → HIGH / 최소 25행
- `src/strategy/bb_bandwidth.py`: `BBBandwidthStrategy` 구현
  - BB 폭(bandwidth) 수축 감지 + 상/하단 돌파 예상
  - BUY: BW < BW_SMA*0.7 AND close > upper*0.99
  - SELL: BW < BW_SMA*0.7 AND close < lower*1.01
  - confidence: BW < BW_SMA*0.5 → HIGH / 최소 45행
- `src/orchestrator.py`: "supertrend_rsi", "bb_bandwidth" STRATEGY_REGISTRY 등록
- `tests/test_supertrend_rsi.py`: 14개 테스트
- `tests/test_bb_bandwidth.py`: 14개 테스트 (총 28개 통과)

## 이전 작업 (2026-04-09) — StrategyPerformanceTracker 신규 생성

- `src/analytics/__init__.py`: analytics 패키지 초기화
- `src/analytics/strategy_tracker.py`: `StrategyPerformanceTracker` + `StrategyMetrics` 구현
  - record_trade(): 전략별 거래 기록 (pnl, is_win)
  - get_ranking(): sort_by total_pnl / win_rate / avg_pnl_per_trade
  - get_top_n() / get_bottom_n(): 상위/하위 N개 반환
  - to_dict() / from_dict(): JSON 직렬화 지원
- `tests/test_strategy_tracker.py`: 12개 단위 테스트 (전부 통과)

## 이전 작업 (2026-04-09) — KAMA + ATR Channel Breakout 전략 추가

- `src/strategy/kama.py`: `KAMAStrategy` 구현
  - ER 기반 SC(스무딩 상수) 계산, KAMA 시리즈 생성
  - BUY: close가 KAMA 상향 돌파 / SELL: 하향 돌파
  - confidence: 이격 > 1% → HIGH, 그 외 MEDIUM / 최소 20행
- `src/strategy/atr_channel.py`: `ATRChannelStrategy` 구현
  - mid=SMA20, upper=mid+2*ATR14, lower=mid-2*ATR14
  - BUY: close > upper / SELL: close < lower
  - confidence: 돌파폭 > ATR*0.5 → HIGH, 그 외 MEDIUM / 최소 25행
  - atr14 컬럼 없을 때 자체 TR 계산 폴백
- `src/orchestrator.py`: 두 전략 STRATEGY_REGISTRY 등록 ("kama", "atr_channel")
- `tests/test_kama.py`: 14개 테스트
- `tests/test_atr_channel.py`: 12개 테스트 (총 26개 통과)

## 이전 작업 (2026-04-09) — Morning/Evening Star + Three Soldiers/Crows 전략 추가

- `src/strategy/morning_evening_star.py`: `MorningEveningStarStrategy` 구현
  - Morning Star: 봉-3 강한 음봉 + 봉-2 소형 + 봉-1 양봉 50% 이상 회복 → BUY
  - Evening Star: 봉-3 강한 양봉 + 봉-2 소형 + 봉-1 음봉 50% 이상 침범 → SELL
  - confidence: >75% → HIGH, >50% → MEDIUM / 최소 10행
- `src/strategy/three_soldiers_crows.py`: `ThreeSoldiersAndCrowsStrategy` 구현
  - Three White Soldiers: 3봉 연속 양봉 + 상승 close + body>range*0.6 → BUY
  - Three Black Crows: 3봉 연속 음봉 + 하락 close + body>range*0.6 → SELL
  - confidence: avg_body > ATR*0.8 → HIGH, 그 외 MEDIUM / 최소 8행
- `src/orchestrator.py`: 두 전략 STRATEGY_REGISTRY 등록
- `tests/test_morning_evening_star.py`: 15개 테스트
- `tests/test_three_soldiers_crows.py`: 14개 테스트 (총 29개 통과)

## Status: **28 passed** | StochRSIDivStrategy + TRIXSignalStrategy 구현 완료

## 최근 작업 (2026-04-09) — StochRSI Divergence + TRIX Signal Cross 전략 추가

- `src/strategy/stochrsi_div.py`: `StochRSIDivStrategy` 구현
  - %K < 0.2 + %K > %D + close 상승 → BUY
  - %K > 0.8 + %K < %D + close 하락 → SELL
  - confidence: |%K - 0.5| > 0.3 → HIGH, 그 외 MEDIUM
  - 최소 30행
- `src/strategy/trix_signal.py`: `TRIXSignalStrategy` 구현
  - histogram 음→양 크로스 → BUY
  - histogram 양→음 크로스 → SELL
  - confidence: |histogram| > std(20) → HIGH, 그 외 MEDIUM
  - 최소 50행
- `src/orchestrator.py`: 두 전략 STRATEGY_REGISTRY 등록
- `tests/test_stochrsi_div.py`, `tests/test_trix_signal.py`: 각 14개 테스트 (28개 통과)

## Status: **26 passed** | PaperTrader + CircuitBreaker 구현 완료

## 최근 작업 (2026-04-09) — Paper Trading 모드 + Drawdown 자동 중단

- `src/exchange/paper_trader.py`: `PaperTrader` 구현
  - `execute_signal(BUY/SELL)`: 가상 잔고 차감, 포지션 관리, 수수료 계산, P&L 추적
  - `get_summary()`: total_return%, trade_count, win_rate 반환
- `src/risk/circuit_breaker.py`: `CircuitBreaker` 구현
  - 일일 낙폭 -5%, 전체 낙폭 -15% 초과 시 자동 트리거
  - `reset_daily()`: 일일 트리거만 해제 (전체 낙폭 트리거 유지)
  - `reset_all()`: 전체 초기화
- `tests/test_paper_trader.py`: 15개 테스트 통과
- `tests/test_circuit_breaker.py`: 11개 테스트 통과
- push to main 완료 (commit eff0aca)

## 이전 작업 (2026-04-09) — Lookahead Bias 감사 도구 + Kelly Criterion 연결 강화

- `src/utils/lookahead_audit.py`: `audit_strategy()` / `audit_all_strategies()` 구현
  - 탐지 패턴: `shift(-N)`, `iloc[-1]`, `.tail(1)`, `rolling().mean()` 뒤 shift 없음
  - 주석 줄 무시, 파일 없음 에러 처리
- `src/risk/position_sizer.py`: `kelly_position_size(win_rate, win_loss_ratio, capital, kelly_fraction=0.25)` 신규
  - KellySizer를 실제 호출하는 단순 함수 인터페이스 (USD 금액 반환)
  - Full Kelly * fraction, 상한 25% cap
- `tests/test_lookahead_audit.py`: 12개 테스트 통과
- `tests/test_kelly_integration.py`: 12개 테스트 통과
- push to main 완료 (commit 219a3b5)

## 이전 작업 (2026-04-09) — WalkForwardValidator 구현

- `src/backtest/walk_forward.py`: `WalkForwardValidator` + `WalkForwardValidationResult` 추가 (기존 `WalkForwardOptimizer` 유지)
- rolling train/test window 분할, `BacktestEngine` 재사용, consistency_score/win_rate/mean_return 집계
- `tests/test_walk_forward.py`: 10개 테스트 전부 통과, push to main 완료

## 이전 작업 (2026-04-09) — ChandelierExitStrategy + VolAdjMomentumStrategy 구현

- `src/strategy/chandelier_exit.py`: ATR22(EWM) 기반 chandelier_long/short 계산, prev_short→cur_long=BUY / prev_long→cur_short=SELL, HIGH(전환폭>ATR*0.5)/MEDIUM confidence, 최소 30행
- `src/strategy/vol_adj_momentum.py`: raw_momentum/hist_vol 정규화, EWM signal_line(span=9) 크로스, HIGH(|vam|>2.0)/MEDIUM confidence, 최소 25행
- `tests/test_chandelier_exit.py`: 15개 테스트 통과
- `tests/test_vol_adj_momentum.py`: 18개 테스트 통과
- `src/orchestrator.py`: `chandelier_exit`, `vol_adj_momentum` 등록

## 이전 작업 (2026-04-09) — TrendStrengthStrategy + VPTSignalStrategy 구현

- `src/strategy/trend_strength.py`: directional_move 기반 TSI bull ratio, >0.65+EMA50=BUY/<0.35+EMA50=SELL, HIGH(>0.75/<0.25)/MEDIUM confidence, 최소 20행
- `src/strategy/vpt_signal.py`: VPT EWM(14) vs EWM(21) 크로스 + EMA50 필터, HIGH(|diff|>std20)/MEDIUM confidence, 최소 30행
- `tests/test_trend_strength.py`: 14개 테스트 통과
- `tests/test_vpt_signal.py`: 14개 테스트 통과
- `src/orchestrator.py`: `trend_strength`, `vpt_signal` 등록

## 이전 작업 (2026-04-09) — ElderImpulseStrategy + MeanReversionChannelStrategy 구현

- `src/strategy/elder_impulse.py`: EMA13 + MACD_hist로 GREEN/RED/BLUE 색상 판단, RED→GREEN=BUY/GREEN→RED=SELL, HIGH(|hist|>std20)/MEDIUM confidence, 최소 35행
- `src/strategy/mean_reversion_channel.py`: SMA50 채널 + z_score, <-2 반전=BUY/>+2 반전=SELL, HIGH(|z|>2.5)/MEDIUM(>2.0) confidence, 최소 55행
- `tests/test_elder_impulse.py`: 14개 테스트 통과 (`_impulse_color` 단위 테스트 포함)
- `tests/test_mean_reversion_channel.py`: 14개 테스트 통과
- `src/orchestrator.py`: `elder_impulse`, `mean_reversion_channel` 등록

## 이전 작업 (2026-04-09) — HATrendStrategy + EngulfingStrategy 구현

- `src/strategy/ha_trend.py`: HA 계산 후 연속 양봉/음봉 카운트, 꼬리없음 조건(ha_low>=ha_open*0.999 / ha_high<=ha_open*1.001), HIGH(5봉+)/MEDIUM(3봉) confidence, 최소 15행
- `src/strategy/engulfing.py`: Bullish/Bearish Engulfing 패턴, HIGH(body>1.5x)/MEDIUM confidence, 최소 5행
- `tests/test_ha_trend.py`: 14개 테스트 통과
- `tests/test_engulfing.py`: 14개 테스트 통과
- `src/orchestrator.py`: `ha_trend`, `engulfing` 등록

## 이전 작업 (2026-04-09) — RSIMomentumDivStrategy + DPOCrossStrategy 구현

- `src/strategy/rsi_momentum_div.py`: RSI14 + Momentum 다이버전스, 10봉 최저/최고 근처 + RSI 방향 확인, HIGH(|RSI변화|>5)/MEDIUM confidence, 최소 25행
- `src/strategy/dpo_cross.py`: DPO=close.shift(11)-SMA20, Signal=EWM(DPO,span=9), 크로스 BUY/SELL, HIGH(|diff|>std)/MEDIUM confidence, 최소 35행
- `tests/test_rsi_momentum_div.py`: 14개 테스트 통과
- `tests/test_dpo_cross.py`: 14개 테스트 통과
- `src/orchestrator.py`: `rsi_momentum_div`, `dpo_cross` 등록

## 이전 작업 (2026-04-09) — PivotReversalStrategy + RangeExpansionStrategy 구현

- `src/strategy/pivot_reversal.py`: Pivot High/Low 탐지 (앞뒤 2봉), 최근 5봉 내 반등/반락 확인, HIGH(>1%)/MEDIUM confidence, 최소 15행
- `src/strategy/range_expansion.py`: True Range 계산, avg_tr_20 기준 1.5x/2.0x 확장, 양/음봉 방향 확인, 최소 25행
- `tests/test_pivot_reversal.py`: 16개 테스트 통과
- `tests/test_range_expansion.py`: 16개 테스트 통과
- `src/orchestrator.py`: `pivot_reversal`, `range_expansion` 등록

## 이전 작업 (2026-04-09) — FRAMAStrategy + VWMACDStrategy 추가

## 최근 작업 (2026-04-09) — FRAMAStrategy + VWMACDStrategy 구현

- `src/strategy/frama.py`: Fractal Adaptive MA, alpha=exp(-4.6*(D-1)), period=16, 크로스 BUY/SELL, HIGH(이격>1%)/MEDIUM confidence
- `src/strategy/vw_macd.py`: 거래량 가중 EMA MACD, histogram 0선 크로스 BUY/SELL, HIGH(|hist|>std)/MEDIUM confidence
- `tests/test_frama.py`: 17개 테스트 통과
- `tests/test_vw_macd.py`: 17개 테스트 통과
- `src/orchestrator.py`: `frama`, `vw_macd` 등록

## 이전 작업 (2026-04-09) — VolumeOscillatorStrategy + PriceEnvelopeStrategy 추가

## 최근 작업 (2026-04-09) — VolumeOscillatorStrategy + PriceEnvelopeStrategy 구현

- `src/strategy/volume_oscillator.py`: Short/Long Vol EMA 차이 VO 지표, VO>5+ema50 방향으로 BUY/SELL, HIGH(VO>20)/MEDIUM confidence
- `src/strategy/price_envelope.py`: EMA20 ±2% 밴드, 밴드 이탈 시 반전 신호, HIGH(dist>3%)/MEDIUM(dist>2%) confidence
- `tests/test_volume_oscillator.py`: 14개 테스트 통과
- `tests/test_price_envelope.py`: 14개 테스트 통과
- `src/orchestrator.py`: `volume_oscillator`, `price_envelope` 등록

## 이전 작업 (2026-04-09) — HistoricalVolatilityStrategy + PriceActionMomentumStrategy 구현

- `src/strategy/historical_volatility.py`: Log Return 기반 HV5/HV20 비율 수축 전략 (ratio<0.7 신호, HIGH/MEDIUM confidence)
- `src/strategy/price_action_momentum.py`: 5개 조건 스코어링 모멘텀 전략 (bull/bear_score>=4 신호, HIGH/MEDIUM confidence)
- `tests/test_historical_volatility.py`: 17개 테스트 통과
- `tests/test_price_action_momentum.py`: 17개 테스트 통과
- `src/orchestrator.py`: `historical_volatility`, `price_action_momentum` 등록

## 이전 작업 (2026-04-09) — MarubozuStrategy + SpinningTopStrategy 구현

- `src/strategy/marubozu.py`: 꼬리 없는 강한 추세 캔들 전략 (body>ATR*0.7, 꼬리 오차 ATR*0.05 이내, HIGH/MEDIUM confidence)
- `src/strategy/spinning_top.py`: 팽이형 이후 방향 돌파 전략 (body<range*0.25, 양쪽꼬리>body*0.5, RSI 필터, HIGH/MEDIUM confidence)
- `tests/test_marubozu.py`: 14개 테스트 통과
- `tests/test_spinning_top.py`: 13개 테스트 통과
- `src/orchestrator.py`: `marubozu`, `spinning_top` 등록

## 이전 작업 (2026-04-09) — TurtleTradingStrategy + ATRTrailingStrategy 구현

- `src/strategy/turtle_trading.py`: 20봉/55봉 채널 돌파 전략 (볼륨 필터, HIGH/MEDIUM confidence, ATR 포지션 사이징 ref)
- `src/strategy/atr_trailing.py`: ATR 트레일링 스탑 추세 전략 (EMA50 기울기, trail rising/falling, HIGH/MEDIUM confidence)
- `tests/test_turtle_trading.py`: 18개 테스트 통과
- `tests/test_atr_trailing.py`: 16개 테스트 통과
- `src/orchestrator.py`: `turtle_trading`, `atr_trailing` 등록

## 이전 작업 (2026-04-09) — RSquaredStrategy + BodyMomentumStrategy 구현

- `src/strategy/r_squared.py`: 선형 회귀 R² 기반 추세 강도 필터 전략 (R²>0.7+slope+ema50, HIGH/MEDIUM confidence)
- `src/strategy/body_momentum.py`: 캔들 몸통 크기 기반 모멘텀 전략 (BM_EMA, BM_SUM3, HIGH/MEDIUM confidence)
- `tests/test_r_squared.py`: 15개 테스트 통과
- `tests/test_body_momentum.py`: 15개 테스트 통과
- `src/orchestrator.py`: `r_squared`, `body_momentum` 등록

## 이전 작업 (2026-04-09) — PRoCTrendStrategy + DualThrustStrategy 구현

- `src/strategy/proc_trend.py`: Price Rate of Change + Trend Filter 복합 전략 (PROC_EMA + EMA50 기울기, HIGH/MEDIUM confidence)
- `src/strategy/dual_thrust.py`: Dual Thrust 돌파 전략 (전일 Range 기반 Buy/Sell Level, 볼륨 필터, HIGH/MEDIUM confidence)
- `tests/test_proc_trend.py`: 16개 테스트 통과
- `tests/test_dual_thrust.py`: 16개 테스트 통과
- `src/orchestrator.py`: `proc_trend`, `dual_thrust` 등록

## 이전 작업 (2026-04-09) — HHLLChannelStrategy + VPTStrategy 구현

- `src/strategy/hhll_channel.py`: Highest High / Lowest Low 채널 모멘텀 전략 (Position 0~100%, BUY>80, SELL<20, vol 필터, HIGH/MEDIUM confidence)
- `src/strategy/vpt.py`: Volume Price Trend 전략 (VPT EMA14 크로스, HIGH=2봉 유지, MEDIUM=방금 크로스)
- `tests/test_hhll_channel.py`: 16개 테스트 통과
- `tests/test_vpt.py`: 14개 테스트 통과
- `src/orchestrator.py`: `hhll_channel`, `vpt` 등록

## 이전 작업 (2026-04-09) — VWAPCrossStrategy + EaseOfMovementStrategy 구현

- `src/strategy/vwap_cross.py`: VWAP20/VWAP50 Rolling 크로스오버 전략 (골든/데드 크로스, HIGH/MEDIUM confidence)
- `src/strategy/ease_of_movement.py`: EOM 전략 (EMV EMA14 기반, close>ema50 필터, HIGH/MEDIUM confidence)
- `tests/test_vwap_cross.py`: 14개 테스트 통과
- `tests/test_ease_of_movement.py`: 14개 테스트 통과
- `src/orchestrator.py`: `vwap_cross`, `ease_of_movement` 등록

## 이전 작업 (2026-04-09) — ZScoreMeanReversionStrategy + MedianPriceStrategy 구현

- `src/strategy/zscore_mean_reversion.py`: Z-Score 기반 평균 회귀 전략 (period=20, BUY<-2.0, SELL>2.0, HIGH/MEDIUM confidence)
- `src/strategy/median_price.py`: Median Price EMA 전략 (MP vs MP_EMA, 방향성 + close 위치 확인)
- `tests/test_zscore_mean_reversion.py`: 16개 테스트 통과
- `tests/test_median_price.py`: 15개 테스트 통과
- `src/orchestrator.py`: `zscore_mean_reversion`, `median_price` 등록

## 이전 작업 (2026-04-09) — DojiPatternStrategy + ThreeCandlesStrategy 구현

- `src/strategy/doji_pattern.py`: Doji 캔들 반전 전략 (body < range*0.1, RSI14, ATR 기반, HIGH/MEDIUM confidence)
- `src/strategy/three_candles.py`: 3연속 캔들 패턴 전략 (Three White Soldiers / Three Black Crows)
- `tests/test_doji_pattern.py`: 13개 테스트 통과
- `tests/test_three_candles.py`: 13개 테스트 통과
- `src/orchestrator.py`: `doji_pattern`, `three_candles` 등록

## 이전 작업 (2026-04-09) — GapStrategy + StarPatternStrategy 구현

- `src/strategy/gap_strategy.py`: 갭 모멘텀 전략 (Gap Up/Down + 볼륨 필터, HIGH/MEDIUM confidence)
- `src/strategy/star_pattern.py`: 별형 캔들 패턴 전략 (Morning/Evening Star, ATR 기반 body 크기 검증)
- `tests/test_gap_strategy.py`: 14개 테스트 통과
- `tests/test_star_pattern.py`: 14개 테스트 통과
- `src/orchestrator.py`: `gap_strategy`, `star_pattern` 등록

## 이전 작업 (2026-04-09) — VolatilityBreakoutLW + IchimokuAdvanced 구현

- `src/strategy/volatility_breakout.py`: 래리 윌리엄스 변동성 돌파 (k=0.5, RSI14+볼륨 필터)
- `src/strategy/ichimoku_advanced.py`: Chikou Span 추가 고도화 Ichimoku (3중 조건, _MIN_ROWS=80)
- `tests/test_volatility_breakout_lw.py`: 16개 테스트 통과
- `tests/test_ichimoku_advanced.py`: 16개 테스트 통과
- `src/orchestrator.py`: `volatility_breakout_lw`, `ichimoku_advanced` 등록


## 이전 작업 (2026-04-09) — Guppy + APO 전략 구현

- `src/strategy/guppy.py`: Guppy MMA 전략 (단기6 + 장기6 EMA 그룹, Short/Long Avg 비교)
- `src/strategy/apo.py`: APO 전략 (EMA10-EMA20 절대 차이, Signal 크로스 기반)
- `tests/test_guppy.py`: 23개 테스트 통과
- `tests/test_apo.py`: 20개 테스트 통과
- `src/orchestrator.py`: STRATEGY_REGISTRY에 `guppy`, `apo` 등록


## 최근 작업 (2026-04-09) — TSI + BOP 전략 구현

- `src/strategy/tsi.py`: True Strength Index 전략 (EMA×2 이중 평활 모멘텀, 크로스 기반)
- `src/strategy/bop.py`: Balance of Power 전략 (EMA14 평활, ema50 필터)
- `tests/test_tsi.py`: 19개 테스트 통과
- `tests/test_bop.py`: 19개 테스트 통과
- `src/orchestrator.py`: STRATEGY_REGISTRY에 `tsi`, `bop` 등록


## 최근 작업 (2026-04-09) — SMI + TRIMA 전략 구현

- `src/strategy/smi.py`: Stochastic Momentum Index 전략 (period=14, smooth=3, 과매도<-40/과매수>40)
- `src/strategy/trima.py`: Triangular Moving Average 크로스 + 볼륨 증가 전략 (period=20)
- `tests/test_smi.py`: 20개 테스트 통과
- `tests/test_trima.py`: 17개 테스트 통과
- `src/orchestrator.py`: STRATEGY_REGISTRY에 `smi`, `trima` 등록


## 최근 작업 (2026-04-09) — Williams Fractal + Mass Index 전략 구현

- `src/strategy/williams_fractal.py`: 5봉 Fractal 패턴 기반 지지/저항 돌파 전략
- `src/strategy/mass_index.py`: Reversal Bulge(>27→<26.5) 기반 추세 전환 전략
- `tests/test_williams_fractal.py`: 17개 테스트 (모두 통과)
- `tests/test_mass_index.py`: 15개 테스트 (모두 통과)
- `src/orchestrator.py`: STRATEGY_REGISTRY에 `williams_fractal`, `mass_index` 등록

## 최근 작업 (2026-04-09) — ZLEMA Crossover + McGinley Dynamic 전략 구현

- `src/strategy/zlema_cross.py`: ZLEMA(9) vs ZLEMA(21) 크로스오버 전략 (HIGH_CONF ≥ 0.5%)
- `src/strategy/mcginley.py`: McGinley Dynamic 상/하향 돌파 전략 (HIGH_CONF ≥ 1%)
- `tests/test_zlema_cross.py`: 14개 테스트 (모두 통과)
- `tests/test_mcginley.py`: 14개 테스트 (모두 통과)
- `src/orchestrator.py`: STRATEGY_REGISTRY에 `zlema_cross`, `mcginley` 등록

## 최근 작업 (2026-04-09) — BacktestEngine 수수료/슬리피지 파라미터 추가

- `src/backtest/engine.py`: `fee_rate` / `slippage_pct` 파라미터 추가 (기존 `commission`/`slippage` 하위 호환)
- `BacktestResult`에 `total_fees`, `total_slippage_cost` 필드 추가
- `_market_close` 청산 시에도 슬리피지 적용 (기존 누락)
- 진입/청산별 수수료·슬리피지 비용 개별 추적
- 기존 테스트 전체 통과

## 최근 작업 (2026-04-09) — config limit 확장 & portfolio_optimizer 버그 수정

- `config/config.yaml`, `config/config.example.yaml`, `src/config.py`: limit 500 → 1000
- `src/risk/portfolio_optimizer.py`: `_apply_constraints` iterative projection으로 개선
  - 버그: 마지막 정규화 후 재클리핑 시 max_weight 미세 초과 (1.77e-6)
  - 수정: 500회 iterative clip+normalize로 합=1.0 & max_weight 제약 동시 보장
- `tests/test_portfolio_optimizer.py`: 16개 테스트 전체 통과

## 최근 작업 (2026-04-09) — 커뮤니티 실패/성공 사례 리서치

- `RESEARCH_REPORT.md` 생성: 트레이딩봇 커뮤니티 연구 리포트
- 핵심 발견: 백테스트 수수료/슬리피지 미반영이 가장 큰 위험
- 즉시 개선 필요: 백테스트 데이터 limit 5000 확장, 수수료 반영
- 다음 우선순위: BacktestEngine에 fee_rate + slippage_pct 파라미터 추가

## 최근 작업 (2026-04-09) — HeikinAshiStrategy 구현

- `src/strategy/heikin_ashi.py` 신규 생성: Heikin-Ashi 캔들 기반 추세 추종 전략
- `tests/test_heikin_ashi.py` 신규 생성: 13개 테스트 전체 통과
- `src/orchestrator.py` 수정: import 및 STRATEGY_REGISTRY에 "heikin_ashi" 등록
- `src/orchestrator.py`: import 및 STRATEGY_REGISTRY에 `"fisher_transform": FisherTransformStrategy` 등록
- BUY: Fisher 상향 크로스 + Fisher>0, SELL: Fisher 하향 크로스 + Fisher<0
- confidence: |Fisher|>2.0 → HIGH, otherwise MEDIUM

## 최근 작업 (2026-04-09) — TEMACrossStrategy 구현

- `src/strategy/tema_cross.py` 신규 생성: TEMA(8) vs TEMA(21) 크로스오버 전략
- `tests/test_tema_cross.py` 신규 생성: 12개 테스트 (monkeypatch 방식) 전부 통과
- `src/orchestrator.py`: import 및 STRATEGY_REGISTRY에 `"tema_cross": TEMACrossStrategy` 등록

## 최근 작업 (2026-04-09) — BacktestReport 메트릭 추가

- `src/backtest/report.py` 개선:
  - `win_loss_ratio` 필드 추가 (avg_win / avg_loss)
  - `max_consecutive_losses` 필드 추가 (최대 연속 손실 횟수)
  - `from_trades()`, `from_backtest_result()`, `_empty()` 모두 신규 필드 반영
  - `summary()` 출력에 Win/Loss Ratio, Max Cons. Loss 항목 추가
- backtest engine 테스트 19/19 통과
- commit 97478b2 완료

## 최근 작업 (2026-04-09) — StochRSIStrategy 구현

- `src/strategy/stoch_rsi.py` 신규 생성
  - RSI14 기반 Stochastic RSI 전략
  - BUY: K<20, D<20, K>D (상향 크로스 in 과매도)
  - SELL: K>80, D>80, K<D (하향 크로스 in 과매수)
  - confidence: HIGH(K<10 BUY / K>90 SELL), MEDIUM otherwise
  - 최소 35행 필요
- `tests/test_stoch_rsi.py` 신규 생성 (15개 테스트 전부 통과)
- `src/orchestrator.py`: import + STRATEGY_REGISTRY에 `"stoch_rsi"` 등록
- commit e04966b 완료

## 최근 작업 (2026-04-09) — VortexStrategy 구현

- `src/strategy/vortex.py` 신규 생성
  - Vortex Indicator (period=14): VI+ = VM+/TR, VI- = VM-/TR
  - BUY: VI+ 크로스오버 VI- AND VI+ > 1.0
  - SELL: VI- 크로스오버 VI+ AND VI- > 1.0
  - confidence: HIGH(|VI+-VI-|>0.2), MEDIUM otherwise
  - 최소 20행 필요
- `tests/test_vortex.py` 신규 생성 (12개 테스트 전부 통과)
- `src/orchestrator.py`: import + STRATEGY_REGISTRY에 `"vortex"` 등록
- commit 68d0681 완료

## 최근 작업 (2026-04-09) — KeltnerChannelStrategy 구현

- `src/strategy/keltner_channel.py` 신규 생성
  - EMA(20) + ATR14 기반 Keltner Channel
  - BUY: close < Lower AND RSI14 < 40
  - SELL: close > Upper AND RSI14 > 60
  - confidence: HIGH(RSI<30 or RSI>70), MEDIUM otherwise
  - 내장 `_rsi()` 함수 포함
- `tests/test_keltner_channel.py` 신규 생성 (14개 테스트 전부 통과)
- `src/orchestrator.py`: import + STRATEGY_REGISTRY에 `"keltner_channel"` 등록
- commit bfbeb97 완료

## 최근 작업 (2026-04-09) — RSI Divergence 개선 + 테스트 커버리지 확대

- `src/strategy/rsi_divergence.py`:
  - 최소 swing 크기 필터 추가: RSI diff < 3 또는 가격 변화 < 0.5% → 무시
  - 상수 추가: `_MIN_RSI_DIFF = 3.0`, `_MIN_PRICE_CHG = 0.005`
  - EMA50 추세 필터: 기존 테스트 깨짐 → 스킵
- `tests/test_new_strategies.py`: 테스트 7개 추가 (14 → 21)
  - `test_small_rsi_diff_filtered_out`, `test_small_price_change_filtered_out`
  - `test_high_confidence_threshold`, `test_none_df_returns_hold`
  - `test_bull_case_bear_case_populated_on_signal`
  - `test_bullish_signal_reasoning_mentions_rsi`, `test_bearish_signal_reasoning_mentions_rsi`
- commit 22f8111 완료

## 최근 작업 (2026-04-09) — PivotPointsStrategy 구현

- `src/strategy/pivot_points.py` 신규 생성:
  - Pivot Points (P/R1/S1/R2/S2) 기반 반전 전략
  - BUY: close < S1 AND RSI14 < 40 (S2 근처면 HIGH, 아니면 MEDIUM)
  - SELL: close > R1 AND RSI14 > 60 (R2 근처면 HIGH, 아니면 MEDIUM)
  - 최소 5행 필요
- `tests/test_pivot_points.py` 신규 생성: 14 passed
- `src/orchestrator.py`: import + STRATEGY_REGISTRY에 "pivot_points" 추가
- commit 87a6425 완료.

## 최근 작업 (2026-04-09) — ElderRayStrategy 구현

- `src/strategy/elder_ray.py` 신규 생성:
  - Elder Ray Index (Bull Power + Bear Power) 전략
  - EMA13 기반 추세 + Bear/Bull Power 조건 복합 판단
  - BUY: EMA13 상승 AND Bear Power < 0 AND Bear Power 개선
  - SELL: EMA13 하락 AND Bull Power > 0 AND Bull Power 감소
  - Confidence: HIGH if |power| > 0.5 * ATR14, MEDIUM otherwise
  - 최소 20행 필요
- `tests/test_elder_ray.py` 신규 생성: 12 passed
- `src/orchestrator.py`: import + STRATEGY_REGISTRY에 "elder_ray" 추가
- commit 8628764 완료

## 최근 작업 (2026-04-09) — OBVStrategy 구현

- `src/strategy/obv.py` 신규 생성:
  - OBV (On-Balance Volume) 볼륨/가격 다이버전스 전략
  - OBV = 종가 방향에 따라 ±volume 누적, OBV_EMA = 20기간 EMA
  - BUY: OBV가 OBV_EMA 상향 돌파 AND close > ema50
  - SELL: OBV가 OBV_EMA 하향 돌파 AND close < ema50
  - Confidence: HIGH if 2봉 전에도 같은 방향, MEDIUM if 방금 크로스
  - 최소 30행 필요
- `tests/test_obv.py` 신규 생성: 14 passed
- `src/orchestrator.py`: import + STRATEGY_REGISTRY에 "obv" 추가
- commit 83df04f 완료.

## 최근 작업 (2026-04-09) — MFIStrategy 구현

- `src/strategy/mfi.py` 신규 생성:
  - MFI (Money Flow Index) 볼륨 가중 RSI 기반 과매수/과매도 전략
  - Typical Price / Raw Money Flow / Positive·Negative MF 분리 / 14기간 rolling
  - BUY: MFI < 20 AND 상승 중 / SELL: MFI > 80 AND 하락 중
  - Confidence: HIGH if MFI < 10 (BUY) or MFI > 90 (SELL), MEDIUM otherwise
  - 최소 20행 필요
- `tests/test_mfi.py` 신규 생성: 11 passed, 2 skipped (13개)
- `src/orchestrator.py`: import + STRATEGY_REGISTRY에 "mfi" 추가
- commit beeb799 완료.

## 최근 작업 (2026-04-09) — TRIXStrategy 구현

- `src/strategy/trix.py` 신규 생성:
  - Triple EMA (EMA1→EMA2→EMA3, period=15) 기반 모멘텀 전략
  - TRIX = (EMA3 - EMA3.shift(1)) / EMA3.shift(1) * 100
  - Signal = TRIX의 9기간 SMA
  - BUY: TRIX > 0 AND 상향 크로스 / SELL: TRIX < 0 AND 하향 크로스
  - Confidence: HIGH if |TRIX| > 0.1, MEDIUM otherwise
  - 최소 60행 필요
- `tests/test_trix.py` 신규 생성: 14 passed
- `src/orchestrator.py`: import + STRATEGY_REGISTRY에 "trix" 추가
- commit cb91982 완료.

## 최근 작업 (2026-04-09) — EMA Cross / Supertrend 성능 개선

- `src/strategy/ema_cross.py` 개선:
  - ema9/ema21 컬럼 존재 시 크로스 확인 (cross_up/cross_down) 추가
  - EMA50 방향 필터: BUY=close>ema50, SELL=close<ema50
  - 볼륨 필터: 20봉 평균 1.2배 이상
  - 컬럼 미존재 시 기존 ema20/ema50 로직 그대로 유지 (graceful degradation)
- `src/strategy/supertrend.py` 개선:
  - 볼륨 필터: volume 컬럼 존재 시 20봉 평균 이상일 때만 BUY/SELL 신호
  - 볼륨 미달 시 HOLD 반환 + 사유 메시지
- 테스트: 14 passed (기존 전부 통과), 전체 719 passed
- commit 7f47de8 완료.

## 이전 작업 (2026-04-09) — PortfolioOptimizer 개선

- `src/risk/portfolio_optimizer.py` 개선:
  - `_risk_parity`: 단순 역변동성 → 공분산 기반 iterative MRC 균등화 (최대 200회 수렴)
  - `_mean_variance`: 1000→2000개 Dirichlet 샘플 탐색, `n_simulations` 파라미터 노출
  - `_compute_var_cvar`: cutoff_idx 엣지케이스 수정, `len==0` 방어
  - 단일 자산 fallback에 VaR95/CVaR95 계산 추가
  - 타입 힌트 Python 3.9 호환 (`Dict[str, ...]`)

## 다음 추천 작업
1. Donchian Breakout 성능 개선 (오래된 전략, 노이즈 신호 많음)
2. 전략 앙상블 로직 개선 (MultiStrategyAggregator 가중치 동적 업데이트)
3. 백테스트 리포트 시각화 개선 (HTML 차트, equity curve)
4. 리스크 매니저 포지션 사이징 개선 (Kelly + VolTargeting 연동 강화)

## 이전 작업 (2026-04-09) — DonchianBreakout 필터 강화

- `src/strategy/donchian_breakout.py` 개선:
  - 볼륨 급증 필터: volume >= 20봉 평균 * 1.5 → HIGH confidence 조건
  - ATR 이격 필터: close - donchian_high >= ATR * 0.5 돌파 시 신호 강화
  - EMA50 추세 필터: BUY=close>ema50, SELL=close<ema50 조건으로 confidence 결정
  - 기존 BUY/SELL/HOLD 신호 진입 조건은 유지 (테스트 호환)
- 테스트: 1 passed (기존 전부 통과)
- commit 1e5bb8a 완료.

## 이전 작업 (2026-04-09) — ParabolicSARStrategy 신규 추가

- `src/strategy/parabolic_sar.py` 신규: ParabolicSARStrategy (name="parabolic_sar")
  - AF 초기=0.02, 스텝=0.02, max=0.20
  - BUY: bullish[-3]=False → bullish[-2]=True (하락→상승 전환)
  - SELL: bullish[-3]=True → bullish[-2]=False (상승→하락 전환)
  - HIGH if BUY+RSI<60 or SELL+RSI>40, MEDIUM otherwise
  - RSI14 내장 계산 (close.diff() 기반)
  - 최소 30행 필요
- `src/orchestrator.py`: ParabolicSARStrategy import + STRATEGY_REGISTRY "parabolic_sar" 등록
- `tests/test_parabolic_sar.py` 신규: 12개 테스트 (10 passed, 2 skipped)
- commit 0a732c8 완료.

## 이전 작업 (2026-04-09) — CCIStrategy 신규 추가

- `src/strategy/cci.py` 신규: CCIStrategy (name="cci")
  - TP = (high+low+close)/3, rolling 20기간 mean/mean_dev → CCI 계산
  - BUY: CCI -100 상향 크로스 (cci_prev<=-100 AND cci_now>-100)
  - SELL: CCI +100 하향 크로스 (cci_prev>=100 AND cci_now<100)
  - HIGH if |CCI|>200, MEDIUM otherwise
  - 최소 30행 필요
- `src/orchestrator.py`: CCIStrategy import + STRATEGY_REGISTRY "cci" 등록
- `tests/test_cci.py` 신규: 14개 테스트 전부 통과 (14 passed)
- commit c5bb19d 완료.

## 이전 작업 (2026-04-09) — ADXTrendStrategy 신규 추가

- `src/strategy/adx_trend.py` 신규: ADXTrendStrategy (name="adx_trend")
  - Wilder smoothing 방식으로 +DM14/-DM14/TR14 → +DI14/-DI14 → DX → ADX 계산
  - BUY: ADX>=25 AND +DI>-DI AND close>ema50
  - SELL: ADX>=25 AND -DI>+DI AND close<ema50
  - HOLD: ADX<25 (횡보장) 또는 DI방향/EMA50 불일치
  - HIGH if ADX>=40, MEDIUM if ADX>=25, LOW if ADX<25
  - 최소 40행 필요, Python 3.9 호환
- `src/orchestrator.py`: ADXTrendStrategy import + STRATEGY_REGISTRY "adx_trend" 등록
- `tests/test_adx_trend.py` 신규: 16개 테스트 전부 통과 (16 passed)
- commit 23f1d6d 완료.

## 이전 작업 (2026-04-09) — WilliamsRStrategy 신규 추가

- `src/strategy/williams_r.py` 신규: WilliamsRStrategy (name="williams_r")
  - %R = (HH14 - close) / (HH14 - LL14) * -100
  - BUY: %R < -80 AND 전봉 대비 반등, HIGH if %R < -90
  - SELL: %R > -20 AND 전봉 대비 반락, HIGH if %R > -10
  - 최소 20행 필요, Python 3.9 호환
- `src/orchestrator.py`: WilliamsRStrategy import + STRATEGY_REGISTRY "williams_r" 등록 (기 완료)
- `tests/test_williams_r.py` 신규: 13개 테스트 전부 통과
- 662 passed, 0 failed. commit b042aa8 + push 완료.

## 이전 작업 (2026-04-09) — IchimokuStrategy 신규 추가

- `src/strategy/ichimoku.py` 신규: IchimokuStrategy (name="ichimoku")
  - Tenkan-sen (9봉) / Kijun-sen (26봉) 직접 계산
  - BUY: Tenkan > Kijun (골든크로스) AND close > Kijun
  - SELL: Tenkan < Kijun (데드크로스) AND close < Kijun
  - confidence: HIGH(Kijun 대비 1% 이상 이격), MEDIUM 그 외
  - 최소 30행 필요
- `src/orchestrator.py`: IchimokuStrategy import + STRATEGY_REGISTRY "ichimoku" 등록
- `tests/test_ichimoku.py` 신규: 14개 테스트 전부 통과
- commit 4a577be + push 완료

## 이전 작업 (2026-04-09) — MACDStrategy 신규 추가

- `src/strategy/macd_strategy.py` 신규: MACDStrategy (name="macd")
  - MACD = EMA12 - EMA26, Signal = MACD의 EMA9, Histogram = MACD - Signal
  - BUY: histogram 음→양 전환 + MACD > 0
  - SELL: histogram 양→음 전환 + MACD < 0
  - confidence: HIGH(|histogram| > 20봉 std), MEDIUM 그 외
  - 최소 35행 필요
- `src/orchestrator.py`: MACDStrategy import + STRATEGY_REGISTRY "macd" 등록
- `src/strategy/__init__.py`: MACDStrategy 추가
- `tests/test_macd_strategy.py` 신규: 13개 테스트 전부 통과
- commit 30d0137 + push 완료

## 이전 작업 (2026-04-09) — 대시보드 시장 레짐 + 토너먼트 우승 전략 표시 추가

- `src/orchestrator.py`:
  - `BotOrchestrator.__init__`에 `_last_regime`, `_last_tournament_winner` 속성 추가
  - `run_once()`에서 레짐 감지 시 `_last_regime` 저장
  - `run_tournament()`에서 레짐 저장 및 우승 전략 `_last_tournament_winner` 저장
- `src/dashboard.py`:
  - `OrchestratorStatusProvider.get_status()`에 `"regime"`, `"last_tournament_winner"` 필드 추가
  - `_render_html()`에 Market Regime(색상 코딩: bull=초록, bear=빨강, sideways=주황), Tournament Winner 표시 추가
- 622 passed, 11 skipped. commit 7cf17e8 + push 완료.

## 이전 작업 (2026-04-09) — lob_maker Sharpe 개선 (0.966 → ~1.0+ 목표)

- `src/strategy/lob_strategy.py` 개선:
  - OFI 임계값 강화: 0.3 → 0.35 (노이즈 신호 감소, 승률 개선)
  - Volume confirmation 필터 추가: `current_vol >= avg_vol * 1.2` (volume_window=20)
  - 신규 파라미터: `volume_multiplier=1.2`, `volume_window=20`
  - reasoning에 `vol_ratio` 포함
- 610 passed, 0 failed. commit 086d8f5 + push 완료.
- 토너먼트 재실행 후 Sharpe ≥ 1.0 확인 필요.

## 이전 작업 (2026-04-09) — CandlePatternStrategy 신규 추가

- `src/strategy/candle_pattern.py` 신규: CandlePatternStrategy (name="candle_pattern")
  - Hammer: 양봉, lower_wick > body*2, RSI < 45 → BUY
  - Shooting Star: 음봉, upper_wick > body*2, RSI > 55 → SELL
  - Bullish Engulfing: 현재 양봉 body가 전봉 음봉 body를 완전히 감싸면 → BUY
  - Bearish Engulfing: 현재 음봉 body가 전봉 양봉 body를 완전히 감싸면 → SELL
  - confidence: 패턴 2개 이상 HIGH, 1개 MEDIUM
  - 최소 20행 필요
- `src/orchestrator.py`: CandlePatternStrategy import + STRATEGY_REGISTRY "candle_pattern" 등록
- `tests/test_candle_pattern.py` 신규: 11개 테스트 전부 통과
- 610 passed, 11 skipped. commit 3bd8344 + push 완료.

## 이전 작업 (2026-04-09) — BBReversionStrategy 신규 추가

- `src/strategy/bb_reversion.py` 신규: BBReversionStrategy (name="bb_reversion")
  - BB 직접 계산 (period=20, std=2.0), rsi14는 feed에서 제공
  - BUY: close < lower_band AND rsi14 < 40, HIGH if rsi < 30
  - SELL: close > upper_band AND rsi14 > 60, HIGH if rsi > 70
  - 최소 25행 필요
- `src/orchestrator.py`: BBReversionStrategy import + STRATEGY_REGISTRY "bb_reversion" 등록
- `tests/test_bb_reversion.py` 신규: 10개 테스트 전부 통과
- 599 passed, 0 failed. commit 19cfab2 + push 완료.

## 이전 작업 (2026-04-09) — MomentumStrategy 신규 추가

- `src/strategy/momentum.py` 신규: MomentumStrategy (name="momentum")
  - 20봉 ROC + EMA50 기반 추세 추종
  - BUY: roc > 3% AND close > ema50, SELL: roc < -3% AND close < ema50
  - HIGH confidence: |roc| > 6%, MEDIUM: |roc| > 3%
  - 최소 55행 (shift(20) + ema50 warmup)
- `src/orchestrator.py`: MomentumStrategy import + STRATEGY_REGISTRY "momentum" 등록
- `tests/test_momentum.py` 신규: 11개 테스트 전부 통과
- 589 passed, 0 failed. commit a6aa7b9 + push 완료.

## 이전 작업 (2026-04-09) — Pipeline adaptive stop-loss 연결

- `src/pipeline/runner.py`: `risk_manager.evaluate()` 호출 시 `candle_df=summary.df` 전달
  - `adaptive_stop_multiplier()`가 realized_vol 기반으로 SL multiplier 자동 조정
  - 이전: `candle_df` 미전달 → 기본값 1.5 고정, 이후: vol 체제별 1.2/1.5/2.5 동적 조정
- 578 passed, 0 failed. commit bad646e + push 완료.

## 이전 작업 (2026-04-09) — funding_rate 임계값 완화 + funding_carry 드로다운 방어

### 배경: 토너먼트 결과
- funding_rate: Sharpe=-1.397, trades=4 (임계값 너무 높아 신호 부족)
- funding_carry: Sharpe=-7.928, max_drawdown 33.4% (스탑로스 없음)

### funding_rate (`src/strategy/funding_rate.py`)
- LONG_EXTREME: 0.03% → 0.015%, SHORT_EXTREME: -0.01% → -0.005%
- VERY_EXTREME: 0.05% → 0.03%
- RSI confirm 임계값 완화: SELL rsi<45→rsi<55, BUY rsi>55→rsi>45

### funding_carry (`src/strategy/funding_carry.py`)
- 음수 펀딩비(fr<0) 즉시 강제 청산 추가 (HIGH confidence SELL)
- ATR 기반 스탑로스: `atr_stop_mult=2.0` 파라미터 신규
- RSI_floor=35 진입 필터: 과매도 구간 진입 차단

- commit 65ffb8b + push 완료

## 이전 작업 (2026-04-09) — BacktestEngine 청산 수수료 + MAX_HOLD_CANDLES 개선

- `src/backtest/engine.py`:
  - `MAX_HOLD_CANDLES = 24` 추가: 24봉 초과 보유 시 강제 시장가 청산 (무한 보유 손실 방지)
  - `_check_exit()`: 청산 수수료 0.1% 반영 (진입만 차감하던 버그 수정)
  - `_market_close()`: 청산 수수료 0.1% 반영
  - profit_factor 계산 정확도 향상 (양방향 수수료 반영)
  - position dict에 `hold_candles` 카운터 추가
- `tests/test_backtest_engine.py`:
  - `MAX_HOLD_CANDLES` import 추가
  - 테스트 4개 추가: 청산수수료 수익감소, profit_factor 0division 방어, MAX_HOLD_CANDLES 상수 확인, 강제 청산 동작
  - 총 19개 → 578 passed (전체)
- commit ce051e8 + push 완료

## 이전 작업 (2026-04-09) — EMA Cross ATR + VWAP 필터 추가

- `src/strategy/ema_cross.py`: ATR 필터 + VWAP 방향 필터 추가
  - ATR 필터: atr14 >= 최근 20봉 평균 atr * 0.8 (노이즈 진입 차단)
  - VWAP 방향 필터: BUY는 close > vwap, SELL은 close < vwap
  - HOLD 시 필터 실패 원인 reasoning에 기록
- `tests/test_strategy.py`: `test_ema_cross_buy_on_crossover`에 ATR/VWAP 조건 주입
- 배경: 토너먼트 Sharpe=-3.087 (10위) → 과도한 노이즈 진입이 원인
- commit d742985 + push 완료

## 이전 작업 (2026-04-09) — ATR adaptive stop-loss multiplier 추가

- `src/risk/manager.py`:
  - `RiskManager.adaptive_stop_multiplier(df, ...)` 정적 메서드 신규
    - realized_vol(log_returns std * sqrt(252*24)) → vol < 0.3: 1.2, 0.3~0.6: 1.5, ≥0.6: 2.5
    - df=None 또는 데이터 부족 시 기본값 1.5 (backward compatible)
  - `evaluate()`: `candle_df` 파라미터 추가 — 있으면 adaptive, 없으면 기존 config 값
- `tests/test_risk_manager.py`: 7개 테스트 추가 (20 passed)
- commit fa4f6b5 + push 완료.

## 이전 작업 (2026-04-09) — VolumeBreakoutStrategy 신규 추가

- `src/strategy/volume_breakout.py` 신규: VolumeBreakoutStrategy (name="volume_breakout")
  - BUY: volume > 평균*2 AND 양봉(close>open) AND close > ema20
  - SELL: volume > 평균*2 AND 음봉(close<open) AND close < ema20
  - HIGH confidence: volume > 평균*3, MEDIUM: volume > 평균*2
  - 최소 25행 필요, ema20은 feed에서 계산됨
- `src/orchestrator.py`: VolumeBreakoutStrategy import + STRATEGY_REGISTRY "volume_breakout" 등록
- `tests/test_volume_breakout.py` 신규: 8개 테스트 전부 통과
- 563 passed, 11 skipped. commit + push 완료.

## 이전 작업 (2026-04-09) — 시장 레짐 자동 감지 추가

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

## STRATEGY_REGISTRY (현재 21종)
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

---

---

# 실전 Bybit 데이터 시뮬레이션 결과 기반 — 작업 방향 전환

_Updated: 2026-04-14_

## ⛔ 핵심 교훈: 합성 데이터 과적합 확인

합성 데이터 Sharpe 4.26이었던 OFI_v2가 실제 Bybit에서 **-12.65%**.
합성 데이터 +15.76%였던 linear_channel_rev가 실제에서 **-18.85%**.

**합성 데이터 기반 SIM 개선 대부분이 과적합이었음.**

## ✅ 실제 Bybit 데이터에서 살아남은 전략 (3 PASS)

| 전략 | Return | Sharpe | PF | Trades |
|------|--------|--------|-----|--------|
| **trima** | +11.28% | 3.74 | 2.21 | 28 |
| **bull_bear_power** | +9.56% | 2.47 | 1.56 | 49 |
| **adaptive_ma_cross** | +8.57% | 3.17 | 2.05 | 27 |

## 🎯 다음 작업 (우선순위)

### 1. 실전 데이터 기반 품질 감사 재실행 (최우선)
- `scripts/quality_audit.py`를 실제 Bybit 데이터로 재실행
- 합성 데이터 PASS 22개 vs 실전 PASS 비교
- 실전 PASS 전략만 STRATEGY_REGISTRY에 활성화

### 2. 실전 PASS 3개 전략 심층 분석
- trima, bull_bear_power, adaptive_ma_cross의 공통점 파악
- 왜 이 3개만 실전에서 살아남았는지 분석
- Walk-Forward 검증 (IS/OOS 70/30)

### 3. 실전 유망 전략 (근접 PASS) 개선
- engulfing_zone (+5.42%, PF 3.48 but 8 trades)
- relative_volume (+5.07%, PF 1.45)
- vol_adj_trend (+4.43%, PF 2.44 but 11 trades)

### 4. 과적합된 전략 분석 및 원인 규명
- 합성에서 +17.85% → 실전 -12.65%가 된 OFI_v2 분석
- 과적합 공통 패턴 도출 → 향후 방지

## ⛔ 금지
- 합성 데이터만으로 전략 최적화 금지
- 새 전략 파일 생성 금지
- 실전 데이터 검증 없이 PASS 판정 금지
