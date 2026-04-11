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
