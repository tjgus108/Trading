"""
BaseStrategy: 모든 전략의 인터페이스.
백테스트와 라이브 실행 모두 동일한 코드 경로를 사용한다.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, FrozenSet, Optional, Sequence, Union

import pandas as pd


class Action(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class Confidence(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


REASONING_MAX_LEN = 500


@dataclass
class Signal:
    action: Action
    confidence: Confidence
    strategy: str
    entry_price: float
    reasoning: str
    invalidation: str
    bull_case: str = ""
    bear_case: str = ""
    metadata: Optional[Dict[str, Any]] = field(default=None)

    def __post_init__(self) -> None:
        if len(self.reasoning) > REASONING_MAX_LEN:
            raise ValueError(
                f"reasoning exceeds {REASONING_MAX_LEN} chars "
                f"(got {len(self.reasoning)})"
            )


class SessionType(str, Enum):
    ACTIVE = "active"    # EU-US overlap: 12:00-16:00 UTC weekday
    REDUCED = "reduced"  # all other times / weekends


def is_active_session(
    timestamp: Union[datetime, pd.Timestamp, None] = None,
) -> SessionType:
    """Return ACTIVE during EU-US overlap (12:00-16:00 UTC, Mon-Fri), else REDUCED.

    Args:
        timestamp: UTC datetime to check. Defaults to current UTC time.

    Returns:
        SessionType.ACTIVE or SessionType.REDUCED
    """
    if timestamp is None:
        ts = datetime.now(timezone.utc)
    elif isinstance(timestamp, pd.Timestamp):
        ts = timestamp.to_pydatetime()
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
    else:
        ts = timestamp
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)

    # weekday(): 0=Mon … 4=Fri, 5=Sat, 6=Sun
    if ts.weekday() >= 5:
        return SessionType.REDUCED

    if 12 <= ts.hour < 16:
        return SessionType.ACTIVE

    return SessionType.REDUCED


class BaseStrategy(ABC):
    """전략 기반 클래스. generate()만 구현하면 된다."""

    name: str = "base"

    @abstractmethod
    def generate(self, df: pd.DataFrame) -> Signal:
        """
        마지막 완성된 캔들 기준으로 신호 생성.
        df: DataFeed.fetch()가 반환한 DataFrame (지표 포함)
        """
        ...

    def _last(self, df: pd.DataFrame) -> pd.Series:
        """마지막 완성 캔들 (인덱스 -2: 현재 진행 중인 캔들 제외)."""
        return df.iloc[-2]


class RegimeGuardedStrategy(BaseStrategy):
    """레짐 기반 전략 래퍼: 허용된 레짐에서만 inner 전략 실행, 그 외 HOLD.

    inner_strategy를 감싸서, regime_detector.detect(df) 결과가
    allowed_regimes에 포함될 때만 inner 전략의 신호를 통과시킨다.
    그 외에는 HOLD(NEUTRAL) 신호를 반환한다.

    사용 예::

        from src.ml.regime_detector import RegimeDetector
        from src.strategy.ema_cross import EmaCrossStrategy

        guarded = RegimeGuardedStrategy(
            inner_strategy=EmaCrossStrategy(),
            regime_detector=RegimeDetector(),
            allowed_regimes=["TREND"],
        )
        signal = guarded.generate(df)
    """

    def __init__(
        self,
        inner_strategy: BaseStrategy,
        regime_detector,
        allowed_regimes: Optional[Sequence[str]] = None,
    ) -> None:
        """
        Args:
            inner_strategy: 감싸려는 원본 전략 (BaseStrategy 구현체).
            regime_detector: detect(df) -> str 메서드를 가진 레짐 감지기.
            allowed_regimes: 허용할 레짐 문자열 목록.
                None 이면 {"TREND", "RANGE"} 기본값 사용 (CRISIS 제외).
        """
        self._inner = inner_strategy
        self._detector = regime_detector
        self._allowed: FrozenSet[str] = frozenset(
            r.upper() for r in (allowed_regimes or ["TREND", "RANGE"])
        )
        self.name = f"guarded_{inner_strategy.name}"

    def generate(self, df: pd.DataFrame) -> Signal:
        """레짐 판별 후 허용된 레짐이면 inner 전략 호출, 아니면 HOLD."""
        # 안전 기본값: df가 None이거나 비어 있으면 HOLD
        if df is None or len(df) < 2:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning="insufficient data",
                invalidation="",
            )

        regime = self._detector.detect(df).upper()

        if regime not in self._allowed:
            entry = float(df["close"].iloc[-2])
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"regime={regime} not in allowed={sorted(self._allowed)}",
                invalidation=f"regime changes to one of {sorted(self._allowed)}",
                metadata={"regime": regime, "guarded": True},
            )

        signal = self._inner.generate(df)
        # 메타데이터에 레짐 정보 추가
        meta = dict(signal.metadata) if signal.metadata else {}
        meta["regime"] = regime
        meta["guarded"] = False
        return Signal(
            action=signal.action,
            confidence=signal.confidence,
            strategy=self.name,
            entry_price=signal.entry_price,
            reasoning=signal.reasoning,
            invalidation=signal.invalidation,
            bull_case=signal.bull_case,
            bear_case=signal.bear_case,
            metadata=meta,
        )
