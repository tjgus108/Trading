"""
BaseStrategy: 모든 전략의 인터페이스.
백테스트와 라이브 실행 모두 동일한 코드 경로를 사용한다.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Optional

import pandas as pd


class Action(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class Confidence(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


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
