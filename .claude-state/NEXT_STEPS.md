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
