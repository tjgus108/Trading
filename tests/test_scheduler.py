"""
CandleScheduler 단위 테스트.

실제 sleep 은 발생하지 않도록 time.sleep 과 threading.Event.wait 을 mock 한다.
"""

import threading
import time
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch, call

import pytest

from src.scheduler import CandleScheduler, TIMEFRAME_SECONDS, CANDLE_SETTLE_SECONDS


# ──────────────────────────────────────────────────────────────────────────────
# next_candle_close 테스트
# ──────────────────────────────────────────────────────────────────────────────

class TestNextCandleClose:
    """next_candle_close 가 항상 미래 시각을 반환하는지 검증."""

    def setup_method(self):
        self.scheduler = CandleScheduler()

    @pytest.mark.parametrize("timeframe", list(TIMEFRAME_SECONDS.keys()))
    def test_always_in_future(self, timeframe):
        """반환된 시각이 현재보다 뒤여야 한다."""
        now = datetime.now(timezone.utc)
        result = self.scheduler.next_candle_close(timeframe)
        assert result > now, f"[{timeframe}] next_candle_close {result} is not after {now}"

    @pytest.mark.parametrize("timeframe", list(TIMEFRAME_SECONDS.keys()))
    def test_interval_alignment(self, timeframe):
        """
        반환된 epoch 초가 해당 타임프레임 간격의 배수여야 한다.
        예) 1h → epoch % 3600 == 0
        """
        result = self.scheduler.next_candle_close(timeframe)
        interval = TIMEFRAME_SECONDS[timeframe]
        ts = int(result.timestamp())
        assert ts % interval == 0, (
            f"[{timeframe}] timestamp {ts} is not aligned to interval {interval}"
        )

    @pytest.mark.parametrize("timeframe", list(TIMEFRAME_SECONDS.keys()))
    def test_within_one_interval(self, timeframe):
        """다음 캔들 종료까지의 대기 시간이 정확히 1 interval 이하여야 한다."""
        now = datetime.now(timezone.utc)
        result = self.scheduler.next_candle_close(timeframe)
        interval = TIMEFRAME_SECONDS[timeframe]
        diff = (result - now).total_seconds()
        assert 0 < diff <= interval, (
            f"[{timeframe}] wait time {diff:.1f}s not in (0, {interval}]"
        )

    def test_unsupported_timeframe(self):
        """지원하지 않는 타임프레임은 ValueError."""
        with pytest.raises(ValueError, match="Unsupported timeframe"):
            self.scheduler.next_candle_close("3h")


# ──────────────────────────────────────────────────────────────────────────────
# 타임프레임별 간격 정합성
# ──────────────────────────────────────────────────────────────────────────────

class TestTimeframeIntervals:
    """TIMEFRAME_SECONDS 상수가 올바른 값을 갖는지 검증."""

    def test_1m(self):
        assert TIMEFRAME_SECONDS["1m"] == 60

    def test_5m(self):
        assert TIMEFRAME_SECONDS["5m"] == 300

    def test_15m(self):
        assert TIMEFRAME_SECONDS["15m"] == 900

    def test_1h(self):
        assert TIMEFRAME_SECONDS["1h"] == 3600

    def test_4h(self):
        assert TIMEFRAME_SECONDS["4h"] == 14400

    def test_1d(self):
        assert TIMEFRAME_SECONDS["1d"] == 86400

    def test_all_timeframes_present(self):
        expected = {"1m", "5m", "15m", "1h", "4h", "1d"}
        assert set(TIMEFRAME_SECONDS.keys()) == expected


# ──────────────────────────────────────────────────────────────────────────────
# run_loop / stop_event 테스트
# ──────────────────────────────────────────────────────────────────────────────

class TestRunLoop:
    """stop_event 로 루프가 종료되는지 검증 (실제 sleep 없이 mock 사용)."""

    def _make_scheduler(self):
        return CandleScheduler()

    def test_stop_event_before_start_exits_immediately(self):
        """stop_event 가 이미 set 된 상태면 pipeline_fn 을 호출하지 않고 즉시 종료."""
        scheduler = self._make_scheduler()
        stop_event = threading.Event()
        stop_event.set()

        pipeline_fn = MagicMock()

        # _interruptible_sleep 을 즉시 반환하도록 patch
        with patch.object(CandleScheduler, "_interruptible_sleep"):
            scheduler.run_loop(pipeline_fn, "1h", stop_event)

        pipeline_fn.assert_not_called()

    def test_pipeline_called_once_then_stop(self):
        """
        첫 번째 사이클에서 pipeline_fn 이 호출된 뒤 stop_event 가 set 되면
        루프가 종료되는지 확인한다.
        """
        scheduler = self._make_scheduler()
        stop_event = threading.Event()
        pipeline_fn = MagicMock()

        call_count = [0]

        def fake_sleep(seconds, event):
            # sleep 은 즉시 반환하고, pipeline 이 한 번 호출된 후 stop
            pass

        original_pipeline = pipeline_fn.side_effect

        def pipeline_side_effect():
            call_count[0] += 1
            stop_event.set()  # 첫 호출 후 중단 신호

        pipeline_fn.side_effect = pipeline_side_effect

        with patch.object(CandleScheduler, "_interruptible_sleep", side_effect=fake_sleep):
            scheduler.run_loop(pipeline_fn, "1h", stop_event)

        assert call_count[0] == 1
        pipeline_fn.assert_called_once()

    def test_pipeline_exception_does_not_stop_loop(self):
        """
        pipeline_fn 이 예외를 던져도 루프가 중단되지 않고 다음 사이클로 넘어가야 한다.
        두 번째 호출에서 stop_event 를 set 해 루프를 종료한다.
        """
        scheduler = self._make_scheduler()
        stop_event = threading.Event()
        call_count = [0]

        def pipeline_fn():
            call_count[0] += 1
            if call_count[0] == 1:
                raise RuntimeError("Simulated pipeline error")
            # 두 번째 호출에서 종료
            stop_event.set()

        with patch.object(CandleScheduler, "_interruptible_sleep"):
            scheduler.run_loop(pipeline_fn, "5m", stop_event)

        assert call_count[0] == 2, "두 번 호출되어야 함 (첫 번째 에러 후 계속)"

    def test_unsupported_timeframe_raises(self):
        """run_loop 에 미지원 타임프레임을 주면 ValueError 가 즉시 발생해야 한다."""
        scheduler = self._make_scheduler()
        stop_event = threading.Event()
        pipeline_fn = MagicMock()

        with pytest.raises(ValueError, match="Unsupported timeframe"):
            scheduler.run_loop(pipeline_fn, "2h", stop_event)

    def test_settle_delay_included_in_wait(self):
        """
        _interruptible_sleep 에 전달되는 초 값이 캔들 완성 후 settle 지연을
        포함하는지 검증한다 (>= CANDLE_SETTLE_SECONDS).
        """
        scheduler = self._make_scheduler()
        stop_event = threading.Event()
        captured_seconds = []

        def fake_sleep(seconds, event):
            captured_seconds.append(seconds)
            stop_event.set()  # 첫 사이클 후 종료

        pipeline_fn = MagicMock()

        with patch.object(CandleScheduler, "_interruptible_sleep", side_effect=fake_sleep):
            scheduler.run_loop(pipeline_fn, "1h", stop_event)

        assert len(captured_seconds) >= 1
        # settle delay 가 포함됐으므로 CANDLE_SETTLE_SECONDS 이상이어야 함
        assert captured_seconds[0] >= CANDLE_SETTLE_SECONDS


# ──────────────────────────────────────────────────────────────────────────────
# _interruptible_sleep 테스트
# ──────────────────────────────────────────────────────────────────────────────

class TestInterruptibleSleep:
    """_interruptible_sleep 이 stop_event 에 올바르게 반응하는지 검증."""

    def test_exits_when_stop_event_set(self):
        """stop_event 를 즉시 set 하면 sleep 이 조기에 종료된다."""
        stop_event = threading.Event()
        stop_event.set()  # 미리 set

        start = time.monotonic()
        # 10초 sleep 요청이지만 즉시 반환되어야 함
        CandleScheduler._interruptible_sleep(10, stop_event)
        elapsed = time.monotonic() - start

        assert elapsed < 1.0, f"stop_event set 후에도 {elapsed:.2f}s 대기함"

    def test_zero_seconds_returns_immediately(self):
        """0초 대기는 즉시 반환."""
        stop_event = threading.Event()
        start = time.monotonic()
        CandleScheduler._interruptible_sleep(0, stop_event)
        elapsed = time.monotonic() - start
        assert elapsed < 0.5


# ──────────────────────────────────────────────────────────────────────────────
# 연속 에러 → graceful shutdown 테스트
# ──────────────────────────────────────────────────────────────────────────────

class TestConsecutiveErrors:
    """연속 실패 시 stop_event 가 set 되고 루프가 종료되는지 검증."""

    def test_stop_after_max_consecutive_errors(self):
        """
        pipeline_fn 이 계속 예외를 던지면 max_consecutive_errors 도달 시
        stop_event 가 set 되고 루프가 종료되어야 한다.
        """
        scheduler = CandleScheduler()
        stop_event = threading.Event()
        call_count = [0]

        def always_fail():
            call_count[0] += 1
            raise RuntimeError("persistent error")

        with patch.object(CandleScheduler, "_interruptible_sleep"):
            scheduler.run_loop(always_fail, "1h", stop_event, max_consecutive_errors=3)

        assert stop_event.is_set(), "stop_event 가 set 되어야 함"
        assert call_count[0] == 3, f"정확히 3번 호출 후 종료 예상, 실제: {call_count[0]}"

    def test_error_counter_resets_on_success(self):
        """
        성공 후에는 연속 에러 카운터가 리셋되어 이후 실패가 다시 카운트되어야 한다.
        패턴: fail, fail, success, fail, fail → 종료 없이 총 5회 호출 후 stop_event 로 종료.
        """
        scheduler = CandleScheduler()
        stop_event = threading.Event()
        call_count = [0]
        # 호출 순서: fail, fail, success, fail, fail, stop
        responses = [True, True, False, True, True]

        def sometimes_fail():
            idx = call_count[0]
            call_count[0] += 1
            if idx < len(responses) and responses[idx]:
                raise RuntimeError("planned error")
            if idx >= len(responses):
                stop_event.set()

        with patch.object(CandleScheduler, "_interruptible_sleep"):
            scheduler.run_loop(sometimes_fail, "1h", stop_event, max_consecutive_errors=3)

        assert call_count[0] >= 5, f"5회 이상 호출 예상, 실제: {call_count[0]}"
        # 중간에 성공이 있었으므로 카운터가 3에 달하지 않아 stop_event 는 외부 set
        assert stop_event.is_set()
