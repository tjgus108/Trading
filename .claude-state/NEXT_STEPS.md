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

## Next: Cycle 2 - Category B
(Pending)
