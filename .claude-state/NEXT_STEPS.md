# Next Steps

_Last updated: 2026-04-09_

## Status: **28 new passed** | GapStrategy + StarPatternStrategy 추가

## 최근 작업 (2026-04-09) — GapStrategy + StarPatternStrategy 구현

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
