# Code Review Report — Phase D
_Date: 2026-04-08_

## Summary

Phase D implementation is generally solid. The design patterns (graceful degradation, thread safety via locks, retry backoff) are correct. Two CRITICAL issues were found and fixed: `eval()` in walk_forward.py and missing `weights_only=` in `torch.load`. Several WARNINGs and NOTEs remain documented below but do not affect current test coverage.

All 245 tests pass (5 skipped) after fixes.

---

## ensemble.py

### Issues Found

- **[NOTE] Line 206 — NEUTRAL votes excluded from `valid_votes`**
  `valid_votes = [v for v in [claude, openai] if v not in ("N/A", "NEUTRAL")]`
  If both return NEUTRAL, falls through to `return rule, 0.4`. This is intentional (no strong LLM opinion → low confidence), but NEUTRAL is treated identically to N/A, which loses the distinction between "model answered NEUTRAL" and "model unavailable". Not a bug, but consider separating the two cases for cleaner reasoning strings.

- **[NOTE] Line 127 — Sequential API calls (no parallelism)**
  `_ask_claude()` and `_ask_openai()` are called sequentially. In a pipeline thread context this doubles latency. Consider `concurrent.futures.ThreadPoolExecutor` to call both in parallel.

- **[NOTE] Thread safety — no instance-level lock**
  `_claude_client` and `_openai_client` are initialized once in `__init__` and then only read. The Anthropic/OpenAI client objects themselves are documented as thread-safe for concurrent calls, so this is acceptable. No lock is required.

- **[NOTE] Confidence values are bounded correctly**
  All return paths in `_compute_consensus` return confidence in `[0.35, 0.90]`. `_neutral` returns `0.5`. Bounds are safe.

- **[NOTE] Line 206 — `_compute_consensus` with one valid HOLD-only vote**
  If one vote is e.g. "BUY" and the other is "NEUTRAL", `valid_votes = ["BUY"]` and it hits the single-vote branch. If `vote == rule`, returns `(rule, 0.65)`. If `vote != rule` and vote is BUY/SELL → returns `("HOLD", 0.5)`. Correct behavior.

---

## websocket_feed.py

### Issues Found

- **[WARNING] Line 109-110 — `stop()` race condition: `_loop` may not yet be set**
  In `stop()`:
  ```python
  if self._loop and not self._loop.is_closed():
      self._loop.call_soon_threadsafe(self._loop.stop)
  ```
  `_loop` is set inside `_run_loop()` on the background thread. If `stop()` is called before the thread starts or before `_run_loop` assigns `self._loop`, `_loop` is `None` and `call_soon_threadsafe` is skipped. The `_stop_event.set()` still causes the asyncio loop to exit cleanly on the next `_stop_event.is_set()` check inside `_connect_with_retry`, so this is **not a hard bug** — but the `_thread.join(timeout=5)` may block the full 5 seconds in this race. Low-impact in practice since `start()` always precedes `stop()` in normal usage.

- **[NOTE] Line 154 — `candle_count()` reads `_candles` without lock**
  `len(self._candles)` is read without `_lock`. In CPython, `deque.__len__` is atomic due to the GIL, but this is an implementation detail. Low risk, but for correctness add `with self._lock`.

- **[NOTE] Line 79 — `_last_obi` written without lock**
  `_last_obi` is written in the WebSocket receive loop but never actually populated in `_process_message`. The OBI feature is declared but not implemented (no bid/ask data in kline messages). `get_order_book_imbalance()` will always return `None`. This is a stub — document or implement separately via the order book stream endpoint.

- **[NOTE] Lines 195 — `websockets.connect()` API may differ by version**
  `websockets` v14+ deprecated `websockets.connect` in favor of `websockets.connect` (still works) but the `ping_interval`/`ping_timeout` parameter names are stable. No issue with current usage.

- **[NOTE] Retry logic is correct**
  Exponential backoff: `RETRY_BASE ** retry_count` gives 2, 4, 8, 16, 32 seconds for retries 1–5. `_retry_count` is reset to 0 on successful `_listen()` return. Logic is correct.

- **[NOTE] `_connected = False` is set on exception but not on clean exit**
  If `_listen()` returns cleanly (e.g. after `break` from `_stop_event`), `_connected` stays `True`. This is a minor stale-state issue since `stop()` is the only caller that triggers the break, and after `stop()` the feed is discarded. Low impact.

---

## walk_forward.py

### Issues Found

- **[CRITICAL — FIXED] Line 221 — `eval(best_key)` security risk**
  ```python
  best_final_params = dict(sorted(eval(best_key)))  # str → dict 복원
  ```
  `best_key` is produced by `str(sorted(best_params.items()))` where `best_params` comes from `param_grid` values. In current usage param values are numeric literals, so exploitation risk is low — but `eval` on any string derived from external input is a security smell and will trigger SAST scanners.

  **Fixed:** replaced with `ast.literal_eval(best_key)` which only evaluates Python literals and raises `ValueError` on arbitrary code.

- **[WARNING] Line 186-187 — IS/OOS ratio when `best_is_sharpe == 0`**
  ```python
  ratio = (oos_result.sharpe_ratio / best_is_sharpe if best_is_sharpe > 0 else 0.0)
  ```
  When IS Sharpe is zero (all strategies lose money in-sample), ratio is forced to `0.0`. This means `is_overfit()` returns `True` (ratio 0.0 < 0.5). Acceptable conservative behavior, but a negative IS Sharpe with a positive OOS Sharpe would also be clipped to 0. Worth documenting.

- **[NOTE] `_split_windows` may return fewer windows than `n_windows`**
  The loop breaks early if `oos_end > n`. This is handled gracefully — `param_oos_map` empty check at line 209 catches the zero-window case. Correct.

- **[NOTE] Line 293 — `_optimize_in_sample` initializes `best_params = combinations[0]`**
  If all combinations fail with exceptions, `best_params` is `combinations[0]` with `best_sharpe = 0.0`. This is reasonable fallback behavior.

---

## lstm_model.py

### Issues Found

- **[CRITICAL — FIXED] Line 285 — `torch.load` without `weights_only=`**
  ```python
  data = torch.load(path, map_location="cpu")
  ```
  In PyTorch >= 2.0 this emits a `FutureWarning`; in >= 2.4 the default changes to `weights_only=True`, which would break loading of saved scaler objects (sklearn `StandardScaler` is a Python object, not a tensor). Since the saved checkpoint contains `"scaler": scaler` (a sklearn object), `weights_only=True` would raise an error.

  **Fixed:** explicitly set `weights_only=False` to document the intent and silence the warning.

- **[WARNING] Line 154-159 — `_prepare_sequences` has no future data leakage**
  ```python
  for i in range(self.sequence_len, len(X)):
      seq_X.append(X[i - self.sequence_len:i])
      seq_y.append(y[i])
  ```
  Sequence at index `i` uses rows `[i-seq_len : i]` (exclusive end), so the label at `i` is not included in the input window. No leakage. Correct.

- **[WARNING] Line 186-193 — Train/val/test split on sequential sequences**
  Split is done on the already-sequenced array, not on the raw time series, so there is no overlap between splits. Correct.

- **[NOTE] Lines 330-340 — numpy fallback proba values**
  BUY case: `p_buy=0.6, p_sell=0.2, p_hold = 1-0.6-0.2 = 0.2` → sums to 1.0. OK.
  SELL case: `p_buy=0.2, p_sell=0.6, p_hold = 0.2` → sums to 1.0. OK.
  HOLD case: `p_buy=0.3, p_sell=0.3, p_hold = 0.4` → sums to 1.0. OK.
  All proba triples sum to 1.0. Correct.

- **[NOTE] numpy fallback accuracy**
  `_train_numpy` uses `np.sign(X_test["return_5"])` as prediction. This is a pure momentum signal — no learning, no look-ahead bias (return_5 is a past 5-bar return, not future). Accuracy around 50% is expected for random markets. The fallback is correctly described as "low accuracy, guaranteed operation." Acceptable.

- **[NOTE] Line 220 — `best_state` may be unbound if `val_loader` is empty**
  If the validation split has zero samples, the `if val_loss < best_val_loss` branch never executes and `best_state` is never assigned. `model.load_state_dict(best_state)` at line 227 would raise `UnboundLocalError`. Guard: initialize `best_state = model.state_dict()` before the epoch loop.

---

## pipeline/runner.py

### Issues Found

- **[NOTE] Lines 139, 148 — `conflicts_with()` call is correct**
  `ens.conflicts_with(signal.action.value)` passes a string like "BUY" or "SELL". `conflicts_with` compares against `opposites.get(action)` which is defined for "BUY"→"SELL" and "SELL"→"BUY". Since ensemble is only called when `signal.action != Action.HOLD` (line 128), the action is always BUY or SELL. Correct.

- **[NOTE] Lines 141-155 — Signal reconstruction after conflict is correct**
  The new `Signal(action=Action.HOLD, ...)` copies all fields from the original signal and overrides action + reasoning. All required fields (`strategy`, `entry_price`, `bull_case`, `bear_case`) are preserved. Correct.

- **[WARNING] Line 155 — Early return after ensemble conflict skips Step 3 (Risk)**
  When ensemble conflicts, the pipeline returns at `pipeline_step="alpha"` with `status="OK"` and `signal.action=HOLD`. This is intentional (HOLD signals skip risk/execution per line 174-179). However, the return at line 155 happens before the generic `if signal.action == Action.HOLD` check at line 175, meaning the `"HOLD — no order"` note at line 178 is NOT appended. Two notes are added instead: `"ENSEMBLE conflict → HOLD 전환"` and `"HOLD — ensemble conflict"`. Minor duplication, not a bug.

- **[NOTE] Lines 189-190 — Risk uses `iloc[-2]` and `iloc[-3]`**
  This assumes at least 3 rows in `summary.df`. If `df` has fewer rows, this raises `IndexError`. However, `DataFeed.fetch()` typically returns 500 candles, so this is acceptable in practice.

---

## Action Items (must fix)

- [x] **FIXED** `walk_forward.py` line 221: replaced `eval(best_key)` with `ast.literal_eval(best_key)`
- [x] **FIXED** `lstm_model.py` line 285: added `weights_only=False` to `torch.load`
- [ ] `lstm_model.py` line ~200: initialize `best_state = model.state_dict()` before epoch loop to prevent `UnboundLocalError` when val set is empty
- [ ] `websocket_feed.py`: implement or remove `_last_obi` / `get_order_book_imbalance()` stub — currently always returns `None`
- [ ] `websocket_feed.py` `candle_count()`: acquire `_lock` for correctness (low priority on CPython)
- [ ] `ensemble.py`: consider parallelizing `_ask_claude` and `_ask_openai` with `ThreadPoolExecutor` to halve latency

---

## Test Results

```
245 passed, 5 skipped in 10.08s
```

All Phase D tests pass after the two critical fixes.
