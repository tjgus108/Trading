# Next Steps

## Cycle 1 - Category A: Quality Assurance ✅ COMPLETED

**Task:** Fix pandas ChainedAssignmentWarning in test files

**Files Modified:**
1. `/home/user/Trading/tests/test_phase_a_strategies.py` (lines 177, 244, 256)
   - Changed `df["col"].iloc[idx] = value` → `df.loc[df.index[idx], "col"] = value`
   
2. `/home/user/Trading/tests/test_volatility_breakout_v2.py` (lines 36, 51, 152)
   - Changed chained iloc assignment → loc-based assignment

**Test Results:**
- test_phase_a_strategies.py: 26 passed ✅
- test_volatility_breakout_v2.py: 14 passed ✅
- Full test suite: 5739 passed, 25 skipped ✅
- No ChainedAssignmentWarning detected

**Root Cause Analysis:**
- Pandas 2.0+ Copy-on-Write mode triggers warnings when using chained indexing like `df["col"].iloc[:]`
- `.loc` is the recommended method for label-based indexing with safe assignment

---

## Cycle 1 - Category C: Data & Infrastructure ✅ COMPLETED

**Task:** Fix websocket race condition + review DataFeed cache

**Files Modified:**
1. `/home/user/Trading/src/data/websocket_feed.py` (lines 109-111)
   - Added explicit `self._loop is not None` guard in `stop()` method
   - Added clarifying comment explaining race condition: `stop()` may be called before `_run_loop()` assigns `self._loop`
   - The `_stop_event.set()` ensures clean exit via `_stop_event.is_set()` check in `_connect_with_retry`

**DataFeed Cache Review:**
- Cache key: `(symbol, timeframe, limit)` tuple ✅
- TTL expiry: `if now - ts < self._cache_ttl` correctly skips expired entries ✅
- Auto-refresh: Fresh fetch on expiry ✅
- Existing tests: `test_phase_d.py` covers WebSocket functionality, 16 feed-related tests pass ✅

**Test Results:**
- Feed/websocket tests: 16 passed, 1 skipped ✅
- Full test suite: 5739 passed, 25 skipped ✅

---

## Cycle 1 - Category F: Research ✅ COMPLETED

**리서치 결과 요약:** `.claude-state/RESEARCH_LOG.md` 참고

**즉시 적용 가능한 개선점 3개 (우선순위 순):**

1. **다층 서킷브레이커** (`src/risk/` 신규 또는 기존 리스크 모듈 수정)
   - 일일 드로다운 3% / 주간 7% 초과 시 자동 거래 중단
   - October 2025 봇 청산 연쇄($19B) 방지 패턴에서 도출

2. **ATR 기반 변동성 레짐 필터** (`src/strategy/base.py` 또는 `src/risk/`)
   - ATR(14) 고변동성 감지 시 포지션 50% 자동 축소 또는 BUY 억제
   - May 2025 AI 봇 플래시 크래시 가속 케이스에서 도출

3. **슬리피지 시뮬레이션 강화** (`src/backtest/engine.py`)
   - 호가창 깊이 기반 슬리피지 모델 추가
   - OKX 2024 플래시 크래시에서 저유동성 봇 피해 패턴 반영

---

## Next: Cycle 2 - Category B
(Pending)

---

## Cycle 2 - Category B: Risk Management ✅ COMPLETED

**Task:** DrawdownMonitor 3층 서킷브레이커 구현

**Files Modified:**
1. `/home/user/Trading/src/risk/drawdown_monitor.py` (전체 재작성, 116 → 208 lines)
   - `AlertLevel` enum 추가 (NONE / WARNING / HALT / FORCE_LIQUIDATE)
   - `DrawdownStatus` dataclass에 `alert_level`, `daily_drawdown_pct`, `weekly_drawdown_pct`, `monthly_drawdown_pct` 필드 추가
   - `DrawdownMonitor.__init__`에 `daily_limit=0.03`, `weekly_limit=0.07`, `monthly_limit=0.15` 파라미터 추가
   - `set_daily_start()`, `set_weekly_start()`, `set_monthly_start()` 메서드 추가
   - `_check_tiered()` 내부 메서드: 월간 > 주간 > 일일 우선순위 체크
   - `reset_daily()` 메서드: WARNING 레벨만 자동 해제
   - FORCE_LIQUIDATE는 `force_resume()`으로만 해제

**Files Created:**
1. `/home/user/Trading/tests/test_drawdown_monitor.py` (12개 테스트)

**Test Results:**
- test_drawdown_monitor.py: 12 passed ✅
- test_circuit_breaker.py: 10 passed ✅ (기존 유지)
- test_risk.py: 7 passed ✅ (기존 유지)

---

---

## Cycle 2 - Category D: ML & Signals ✅ COMPLETED

**Task:** Walk-Forward 토너먼트 통합 - 테스트 커버리지 보강

**조사 결과:** Walk-Forward 통합은 이미 `src/orchestrator.py` lines 1014-1052에 완전히 구현되어 있음.
- `TournamentResult.wf_stable`, `wf_fallback` 필드 존재 (line 757-762)
- 1위 UNSTABLE → 2위 fallback 로직 완성 (line 1038-1046)
- 기존 테스트 2개 존재 (stable/unstable 케이스)

**Files Modified:**
1. `/home/user/Trading/tests/test_orchestrator.py` (lines 272-315 추가)
   - `test_tournament_wf_skipped_when_insufficient_data`: 데이터 < 250봉 시 wf_stable=None, 1위 유지
   - `test_tournament_wf_exception_is_non_fatal`: WF 예외 발생 시 non-fatal 처리, 1위 유지

**Test Results:**
- test_orchestrator.py: 12 passed ✅ (기존 8 + 기존 WF 2 + 신규 2)

---

## Next: Cycle 2 - 추가 작업 후보
- ATR 기반 변동성 레짐 필터 (`src/risk/` 또는 `src/strategy/`)
- Kelly Sizer 파라미터 config화 (`src/risk/kelly_sizer.py`)

---

## Cycle 3 - Category E: Execution ✅ COMPLETED

**Task:** Paper Trading 모드 검증 + 활성화

**Files Modified:**
1. `/home/user/Trading/src/exchange/paper_trader.py` (lines 127-129)
   - 버그 수정: SELL에서 실제 판매량이 보유량을 초과할 때 fee 및 actual_qty 재계산
   - `sell_qty = min(actual_qty, held)` 이후 `actual_qty`를 `sell_qty`로 업데이트
   - fee를 sell_qty 기반으로 재계산하여 포지션 부족 시 수수료 오버차징 방지

2. `/home/user/Trading/tests/test_paper_trader.py` (lines 245-366 추가)
   - 5개 추가 테스트 (총 27개 → 22개 기존 + 5개 신규)
   - `test_multiple_symbols_independent_positions`: 여러 심볼 독립적 포지션 관리
   - `test_cumulative_pnl_after_multiple_rounds`: 누적 P&L 정합성
   - `test_partial_fill_sell_qty_capped_at_position`: SELL 시 보유량 제한
   - `test_loss_trade_negative_pnl`: 손실 거래 처리
   - `test_fee_impact_on_balance_and_pnl`: 수수료 영향 검증

**Paper Trading 현황:**
- **구현 상태**: PaperTrader + PaperConnector 완성 (모의거래 100% 가능)
- **포지션 관리**: 다중 심볼 지원, 가중평균 진입가 계산 ✅
- **P&L 추적**: 개별/누적 P&L 정확 계산 ✅
- **슬리피지 시뮬레이션**: ±범위 내 임의 변동 ✅
- **부분체결**: 확률 기반 시뮬레이션 ✅
- **타임아웃**: 확률 기반 시뮬레이션 ✅
- **수수료**: BUY/SELL 모두 정확 반영 ✅
- **여러 심볼**: 완벽 독립 관리 ✅

**활성화 방법:**
```python
# 방법 1: PaperConnector 직접 사용
from src.exchange.paper_connector import PaperConnector
connector = PaperConnector(symbol="BTC/USDT", initial_balance=10000.0)
order = connector.create_order("BTC/USDT", "buy", 1.0, price=50000.0)

# 방법 2: Orchestrator에서 사용 (향후)
# config.yaml에서 exchange.paper_trading=true 설정 시 자동 활성화
```

**Test Results:**
- test_paper_trader.py: 27 passed ✅
- Full test suite: 5766 passed, 25 skipped ✅
- 버그 수정 후 모든 테스트 통과

**기술 정리:**
- 부분체결 후 포지션 추적: min(actual_qty, held)로 자동 cap
- 여러 심볼: dict 기반 포지션/진입가 독립 관리
- 누적 P&L: 각 SELL 트레이드마다 total_pnl += pnl
- 수수료: fee = price × qty × fee_rate (BUY/SELL 동일)

---

## Next: 추가 작업 후보 (Cycle 3~4)
- Orchestrator에 paper_trading 플래그 통합 (config)
- 슬리피지 강화 옵션 2 (호가창 깊이 기반 모델)
- Risk Agent 연동 (pre-execution 체크)

---

## Cycle 3 - Category A: Quality Assurance ✅ COMPLETED

**Task:** Improve quality_audit.py synthetic data to fix 5 missing indicator errors

**Files Modified:**
1. `/home/user/Trading/scripts/quality_audit.py` (lines 71-83 added)
   - Added `ema20` = EMA(20) for EmaCrossStrategy, VolumeBreakoutStrategy
   - Added `donchian_high`, `donchian_low` (20 period) for DonchianBreakoutStrategy
   - Added `vwap` = cumulative VWAP calculation for VWAPReversionStrategy
   - Added `vwap20` = 20-period rolling VWAP approximation for VWAPReversionStrategy

**Results Before:**
- BacktestEngine errors: 5
  - donchian_breakout.DonchianBreakoutStrategy: KeyError 'donchian_high'
  - ema_cross.EmaCrossStrategy: KeyError 'ema20'
  - volume_breakout.VolumeBreakoutStrategy: KeyError 'ema20'
  - vpt_confirm.VolumePriceTrendConfirmStrategy: KeyError 'ema20'
  - vwap_reversion.VWAPReversionStrategy: KeyError 'vwap'

**Results After:**
- BacktestEngine errors: 0 ✅
- Backtest completed: 348/348 strategies
- PASS strategies: 22 (increased from 21)
  - volume_breakout now PASSES with Sharpe=5.911, PF=2.66, WinRate=60%
- Full test suite: 5766 passed, 25 skipped ✅
- No regressions

**Root Cause:**
- 5 strategies required technical indicators not included in make_synthetic_data()
- All fixes were in the synthetic data generation function (CSV not touched)


---

## Cycle 4 - Category B: Risk Management ✅ COMPLETED

**Task:** CircuitBreaker ATR 변동성 급등 감지 추가

**Files Modified:**
1. `/home/user/Trading/src/risk/circuit_breaker.py` (전체 재작성, 93 → 121 lines)
   - `atr_surge_multiplier` 파라미터 추가 (기본값 2.0)
   - `check()` 시그니처 확장: `current_atr`, `baseline_atr` optional 파라미터 추가
   - 반환 dict에 `volatility_surge: bool`, `size_multiplier: float` 필드 추가
   - ATR surge 로직: `current_atr >= baseline_atr × multiplier` → `size_multiplier=0.5`, `triggered=False`
   - 낙폭 조건 트리거 시 `size_multiplier=0.0` (완전 차단)
   - `_make_result()` 헬퍼 메서드로 반환 일관성 확보

2. `/home/user/Trading/tests/test_circuit_breaker.py` (lines 106-149 추가, 4개 신규 테스트)
   - `test_atr_surge_returns_half_size_multiplier`: ATR 2배 이상 → size_multiplier=0.5
   - `test_atr_below_surge_threshold_no_effect`: ATR 1.9배 → 정상 통과
   - `test_atr_surge_does_not_override_drawdown_trigger`: 낙폭 우선, triggered=True
   - `test_atr_surge_without_atr_args_no_effect`: 파라미터 미전달 → 스킵

**Test Results:**
- test_circuit_breaker.py: 14 passed ✅ (기존 10 + 신규 4)

**설계 결정:**
- ATR surge 단독으로 triggered=True 유발 안 함 → 포지션 축소 신호이지 완전 차단 아님
- 낙폭 조건이 더 심각하면 drawdown 조건이 ATR surge를 덮음
- `size_multiplier` 필드로 호출자가 포지션 크기를 조정할 수 있게 함

---

## Cycle 4 - Category C: Data & Infrastructure ✅ COMPLETED

**Task:** OrderFlow/VPIN 정확도 검증

**Bug Found & Fixed:**
- `/home/user/Trading/src/data/order_flow.py` (lines 138-141)
  - **Issue:** `close == open` 케이스가 SELL로 잘못 분류됨 (close > open 만 체크)
  - **Fix:** NEUTRAL 봉(close==open) 추가 처리
    - `buy_frac[df["close"] > df["open"]] = 1.0` (BUY)
    - `buy_frac[df["close"] == df["open"]] = 0.5` (NEUTRAL)
    - Default `buy_frac = 0.0` (SELL)
  - **Impact:** VPIN 계산 정확도 향상 (neutral candles 올바른 처리)

**Tests Added:**
- `/home/user/Trading/tests/test_order_flow.py` (lines 145-203)
  - `TestVPINCalculator` 클래스 추가 (8개 테스트)
  - `test_vpin_all_neutral_candles`: neutral 봉 처리 검증
  - `test_vpin_perfect_buy_pressure`: 100% BUY 압력 (VPIN=1.0)
  - `test_vpin_perfect_sell_pressure`: 100% SELL 압력 (VPIN=1.0)
  - `test_vpin_balanced_buy_sell`: 균형잡힌 거래량 (VPIN=1.0)
  - `test_vpin_bounded_zero_to_one`: 범위 검증 [0,1]
  - `test_vpin_get_latest`: 최종값 반환 검증
  - `test_vpin_get_latest_insufficient_data`: 데이터 부족 시 0.5 반환
  - `test_vpin_get_latest_nan`: NaN 처리 검증

**Test Results:**
- test_order_flow.py: 26 passed ✅ (18 기존 + 8 신규)
- Full test suite: 5778 passed, 25 skipped ✅
- No regressions

**Summary:** VPIN 계산의 중립 봉 분류 오류를 수정. OFI 정확도 향상으로 order flow imbalance 신호 신뢰성 증대.

---

## Cycle 5 - Category E: Execution ✅ COMPLETED

**Task:** TWAP 실행기 검증 및 버그 수정 (부분 체결/타임아웃)

**Files Modified:**
1. `/home/user/Trading/src/exchange/twap.py` (전체 재작성, 152 → 231 lines)
   - **추가 필드:**
     - `filled_qty: float` (실제 체결 수량, 부분 체결 반영)
     - `partial_fills: int` (부분 체결된 슬라이스 개수)
     - `timeout_occurred: bool` (타임아웃 발생 여부)
   - **생성자 확장:** `timeout_per_slice` 파라미터 추가
   - **부분 체결 처리:** dry_run에서 20% 확률로 부분 체결 시뮬레이션, 실제 주문에서는 connector 응답의 'filled' 필드 반영
   - **타임아웃 로직:** 슬라이스별/전체 타임아웃 체크 → `timeout_occurred=True` 설정 및 루프 조기 종료
   - **예외 처리:** connector 에러 발생 시 `timeout_occurred=True`, 루프 종료
   - **슬리피지 계산:** `total_filled` 기반 재계산 (부분 체결 반영)

2. `/home/user/Trading/tests/test_kelly_twap.py` (lines 173-177 수정 + lines 198-278 추가)
   - `test_twap_result_fields` 수정: 새로운 필드 확인
   - **신규 테스트 5개 (부분 체결/타임아웃 관련):**
     - `test_twap_partial_fill_tracking`: 부분 체결 시뮬레이션 및 추적
     - `test_twap_filled_qty_calculation`: filled_qty 정확도 검증
     - `test_twap_timeout_flag_no_timeout`: 타임아웃 없는 정상 케이스
     - `test_twap_timeout_per_slice_respected`: 타임아웃 경계값 테스트
     - `test_twap_result_new_fields`: 새 필드 존재 확인

**Test Results:**
- test_kelly_twap.py: 19 passed ✅ (기존 14 + 신규 5)
- Full test suite: OK (회귀 없음)

**기술 정리:**
- **부분 체결:** connector.place_order() 응답에서 'filled' 필드 추출, 없으면 slice_qty 가정
- **타임아웃:** `timeout_per_slice * n_slices` 전체 제한 + 슬라이스별 체크
- **예외 처리:** connector 에러 → timeout_occurred=True, 루프 종료
- **슬리피지:** sum(filled_quantities)로 재계산하여 부분 체결 반영

---

## Next: 추가 작업 후보 (Cycle 5~)
- Orchestrator 통합: TWAP 실행기 자동 호출 (대형 주문 감지)
- Risk Agent 연동 (TWAP 전 approval 체크)
- 호가창 깊이 기반 슬리피지 모델 추가

---

## Cycle 6 - Category C: Data & Infrastructure ✅ COMPLETED

**Task:** SentimentFetcher 견고성 강화 (재시도 + fallback)

**Files Modified:**
1. `/home/user/Trading/src/data/sentiment.py` (lines 1-227 전체 수정)
   - `__init__`에 `max_retries` 파라미터 추가 (기본값 2)
   - `_last_successful` 필드 추가: 이전 성공한 데이터 저장
   - 모든 `_fetch_*` 메서드에 재시도 로직 추가
     - exponential backoff: 0.5s × 2^attempt (0.5s, 1s, 2s)
     - 시도 실패 시 debug 로그, 모든 시도 완료 후 warning 로그
   - `fetch()` 메서드에 fallback 로직 추가
     - 일부 API 실패: 성공한 API만 사용
     - 모든 API 실패: `_last_successful` 반환
     - fallback도 없음: 중립 데이터(`score=0, source="unavailable"`) 반환
   - 문서화 강화: graceful degradation 명시

2. `/home/user/Trading/tests/test_phase_b_context.py` (lines 317-414 추가)
   - `TestSentimentFetcherRobustness` 클래스: 9개 테스트
     - `test_fetch_all_apis_fail_uses_fallback`: fallback 데이터 사용 검증
     - `test_fetch_all_apis_fail_no_fallback_returns_neutral`: fallback 없을 시 중립 데이터
     - `test_partial_api_failure_uses_available_data`: 일부 API 실패 처리
     - `test_cache_returns_same_data_within_timeout`: 캐시 타임아웃 검증
     - `test_max_retries_parameter_affects_behavior`: 재시도 파라미터 동작
     - `test_fallback_last_successful_tracked`: `_last_successful` 저장 확인
     - `test_fear_greed_api_failure_logs_warning`: 로그 출력 검증
     - `test_unavailable_source_when_no_fallback`: source 필드 검증
     - `test_multiple_successful_apis_combined_source`: 여러 API 성공 시 source 통합
   - `TestSentimentFetcherFallbackIntegration` 클래스: 1개 통합 테스트
     - `test_fallback_survives_subsequent_failures`: fallback 데이터 지속성 검증

**Test Results:**
- test_phase_b_context.py: 50 passed ✅ (기존 40 + 신규 10)
- 전체 robustness 테스트: 10개 모두 통과
- 기존 테스트 40개 회귀 없음

**기술 정리:**
- **재시도 로직:** exponential backoff로 transient 에러 자동 복구
- **Fallback:** 과거 성공한 데이터 유지로 일시적 API 장애 극복
- **부분 실패 처리:** 일부 API 실패해도 사용 가능한 데이터 반환
- **로깅:** 재시도 시도별 debug + 최종 실패 시 warning으로 운영자 알림
- **graceful degradation:** 모든 API 실패 시 중립 데이터로 파이프라인 계속 진행

---

## Cycle 6 - Category A: Quality Assurance ✅ COMPLETED

**Task:** Fix numpy warnings in strategy code (19 warnings → 0)

**Files Modified:**
1. `/home/user/Trading/src/strategy/sine_wave.py` (lines 33-35)
   - **Issue:** `RuntimeWarning: invalid value encountered in divide`
   - **Root Cause:** `np.where(std20 > 0, ...)` 조건이 NaN 체크를 하지 않아 NaN/0 나눗셈 발생
   - **Fix:** 수동 마스킹으로 NaN 값 사전 필터링
   ```python
   # Before: zscore = np.where(std20 > 0, (close_arr - sma20) / std20, 0.0)
   # After:
   zscore = np.zeros(n)
   mask = (~np.isnan(std20)) & (std20 > 0)
   zscore[mask] = (close_arr[mask] - sma20[mask]) / std20[mask]
   ```

2. `/home/user/Trading/src/strategy/trend_persistence.py` (lines 35-40)
   - **Issue:** `RuntimeWarning: Degrees of freedom <= 0 for slice` (12개 경고)
   - **Root Cause:** `autocorr(lag=1)`이 샘플 수 < 2일 때 호출되어 자유도 부족
   - **Fix:** `min_periods` 체크 강화 (2 → 3)
   ```python
   # Before: lambda x: pd.Series(x).autocorr(lag=1) if len(x) >= 2 else 0.0
   # After:  lambda x: pd.Series(x).autocorr(lag=1) if len(x) >= 3 else 0.0
   ```

**Test Results:**
- test_sine_wave.py: 18 passed, 0 warnings ✅
- test_trend_persistence.py: 14 passed, 0 warnings ✅
- Full test suite: 5817 passed, 25 skipped, **0 warnings** ✅ (19 → 0)

**경고 제거 요약:**
- **12개 warnings (SineWaveStrategy):** NaN 마스킹으로 제거
- **7개 warnings (TrendPersistenceStrategy):** autocorr 자유도 체크 강화로 제거
- **전체 19개 경고 완전 제거**

---

## Next: 추가 작업 후보 (Cycle 6~)
- NewsMonitor 에러 처리 강화 (CryptoPanic API 타임아웃)
- OnchainFetcher 재시도 로직 추가 (현재 한 번만 시도)
- Orchestrator에 sentiment fetch timeout 설정
