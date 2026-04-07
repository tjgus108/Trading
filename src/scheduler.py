"""
CandleScheduler: 타임프레임별 캔들 완성 시각에 맞춰 파이프라인을 반복 실행한다.

사용 예:
    stop = threading.Event()
    scheduler = CandleScheduler()
    scheduler.run_loop(pipeline_fn, timeframe="1h", stop_event=stop)
"""

import logging
import threading
import time
from datetime import datetime, timezone, timedelta
from typing import Callable

logger = logging.getLogger(__name__)

# 지원 타임프레임 → 초 단위 간격
TIMEFRAME_SECONDS: dict[str, int] = {
    "1m":  60,
    "5m":  5 * 60,
    "15m": 15 * 60,
    "1h":  60 * 60,
    "4h":  4 * 60 * 60,
    "1d":  24 * 60 * 60,
}

# 캔들 완성 후 거래소 데이터 반영 대기 시간 (초)
CANDLE_SETTLE_SECONDS = 30

# stop_event 폴링 간격 (초) — 긴 sleep 중에도 Ctrl+C에 반응하도록 쪼갬
POLL_INTERVAL = 60


class CandleScheduler:
    """
    타임프레임에 정렬된 캔들 완성 시각을 계산하고,
    각 사이클마다 pipeline_fn 을 호출한다.
    """

    def next_candle_close(self, timeframe: str) -> datetime:
        """
        현재 시각 이후 첫 번째 캔들 종료 시각(UTC)을 반환한다.

        예) timeframe="1h", 현재 14:23 → 15:00:00 UTC
            timeframe="4h", 현재 05:10 → 08:00:00 UTC
        """
        interval = self._interval_seconds(timeframe)
        now = datetime.now(timezone.utc)
        now_ts = now.timestamp()

        # 현재 epoch 를 interval 로 나눠 다음 경계 계산
        next_ts = (int(now_ts) // interval + 1) * interval
        return datetime.fromtimestamp(next_ts, tz=timezone.utc)

    def run_loop(
        self,
        pipeline_fn: Callable[[], None],
        timeframe: str,
        stop_event: threading.Event,
    ) -> None:
        """
        캔들 완성 시각에 맞춰 pipeline_fn 을 반복 호출한다.

        - 각 캔들 완성 후 CANDLE_SETTLE_SECONDS 초 추가 대기
        - stop_event 가 set 되면 다음 sleep 주기에서 루프 종료
        - pipeline_fn 에서 예외가 발생해도 로그만 남기고 계속 실행
        """
        self._validate_timeframe(timeframe)
        logger.info(
            "[scheduler] Starting candle scheduler — timeframe=%s settle=%ds",
            timeframe,
            CANDLE_SETTLE_SECONDS,
        )

        while not stop_event.is_set():
            next_close = self.next_candle_close(timeframe)
            wait_target = next_close + timedelta(seconds=CANDLE_SETTLE_SECONDS)
            now = datetime.now(timezone.utc)
            total_wait = (wait_target - now).total_seconds()

            logger.info(
                "[scheduler] Next candle close: %s  (waiting %.1fs + %ds settle)",
                next_close.strftime("%Y-%m-%d %H:%M:%S UTC"),
                max(0, total_wait - CANDLE_SETTLE_SECONDS),
                CANDLE_SETTLE_SECONDS,
            )

            # 목표 시각까지 POLL_INTERVAL 단위로 쪼개어 sleep
            self._interruptible_sleep(total_wait, stop_event)

            if stop_event.is_set():
                break

            logger.info("[scheduler] Candle closed — running pipeline")
            try:
                pipeline_fn()
            except Exception as exc:
                logger.error(
                    "[scheduler] pipeline_fn raised an exception (continuing): %s",
                    exc,
                    exc_info=True,
                )

        logger.info("[scheduler] Scheduler stopped (stop_event set)")

    # ──────────────────────────────────────────────────────────────
    # 내부 헬퍼
    # ──────────────────────────────────────────────────────────────

    @staticmethod
    def _interval_seconds(timeframe: str) -> int:
        """타임프레임 문자열을 초로 변환. 미지원 시 ValueError."""
        try:
            return TIMEFRAME_SECONDS[timeframe]
        except KeyError:
            supported = ", ".join(TIMEFRAME_SECONDS)
            raise ValueError(
                f"Unsupported timeframe '{timeframe}'. Supported: {supported}"
            )

    @staticmethod
    def _validate_timeframe(timeframe: str) -> None:
        CandleScheduler._interval_seconds(timeframe)  # ValueError 전파

    @staticmethod
    def _interruptible_sleep(seconds: float, stop_event: threading.Event) -> None:
        """
        seconds 만큼 대기하되 POLL_INTERVAL 단위로 stop_event 를 확인한다.
        stop_event 가 set 되면 즉시 반환한다.
        """
        remaining = max(0.0, seconds)
        while remaining > 0 and not stop_event.is_set():
            chunk = min(remaining, POLL_INTERVAL)
            stop_event.wait(timeout=chunk)
            remaining -= chunk
