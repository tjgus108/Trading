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
