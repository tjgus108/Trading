"""
RegimeStrategyRouter: 현재 레짐에 따라 활성 전략 목록과 포지션 스케일을 결정.

레짐:
  TREND  — ADX>25 또는 EMA20>EMA50>EMA200 구조
  RANGE  — ATR < MA(ATR,20) + BB 폭 좁음
  CRISIS — ATR > MA(ATR,20)*2.0

포지션 스케일:
  TREND / RANGE → 1.0x
  CRISIS        → 0.5x
"""

from __future__ import annotations

from typing import Dict, List


# 기본 레짐-전략 매핑 (REGIME_STRATEGY_MAP.md 기준)
DEFAULT_STRATEGY_MAP: Dict[str, List[str]] = {
    "TREND": [
        "cmf",
        "elder_impulse",
        "volume_breakout",
        "supertrend_multi",
        "momentum_quality",
        "price_action_momentum",
        "relative_volume",
    ],
    "RANGE": [
        "wick_reversal",
        "engulfing_zone",
        "price_cluster",
        "value_area",
        "narrow_range",
        "frama",
        "positional_scaling",
    ],
    # CRISIS: 모든 전략 허용하되 position scale 0.5x
    "CRISIS": [],
}

# 레짐별 포지션 배수
POSITION_SCALE: Dict[str, float] = {
    "TREND": 1.0,
    "RANGE": 1.0,
    "CRISIS": 0.5,
}

_KNOWN_REGIMES = frozenset(DEFAULT_STRATEGY_MAP.keys())


class RegimeStrategyRouter:
    """레짐 기반 전략 라우터.

    Parameters
    ----------
    strategy_map:
        레짐 → 전략 이름 목록.  None 이면 DEFAULT_STRATEGY_MAP 사용.
    """

    def __init__(
        self,
        strategy_map: Dict[str, List[str]] | None = None,
    ) -> None:
        self._map: Dict[str, List[str]] = (
            strategy_map if strategy_map is not None else DEFAULT_STRATEGY_MAP
        )
        # 전략이 속하는 레짐 역방향 인덱스 (CRISIS 전략은 명시 목록이 비어 있으므로 별도 처리)
        self._strategy_regime: Dict[str, str] = {}
        for regime, strategies in self._map.items():
            for s in strategies:
                self._strategy_regime[s] = regime

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_active_strategies(self, regime: str) -> List[str]:
        """현재 레짐에 맞는 전략 목록 반환.

        CRISIS 레짐: 매핑에 명시된 CRISIS 목록이 비어 있으면
        TREND + RANGE 전체를 반환하되, scale_position 으로 50% 감소를 적용해야 함.
        """
        regime_upper = regime.upper()
        if regime_upper not in self._map:
            # 알 수 없는 레짐 → 빈 목록 (안전 기본값)
            return []

        crisis_list = self._map.get("CRISIS", [])
        if regime_upper == "CRISIS":
            if crisis_list:
                return list(crisis_list)
            # 명시 목록 없음 → 전체 전략 반환 (scale_position 0.5x 적용 필요)
            all_strategies: List[str] = []
            for r, strats in self._map.items():
                if r != "CRISIS":
                    all_strategies.extend(strats)
            return all_strategies

        return list(self._map.get(regime_upper, []))

    def scale_position(self, regime: str, base_size: float) -> float:
        """레짐에 따라 base_size 를 스케일링하여 반환."""
        scale = POSITION_SCALE.get(regime.upper(), 1.0)
        return base_size * scale

    def should_skip(self, strategy_name: str, regime: str) -> bool:
        """해당 전략이 현재 레짐에서 스킵되어야 하면 True.

        CRISIS 레짐: 스킵하지 않음 — 대신 scale_position 으로 크기 감소.
        """
        regime_upper = regime.upper()
        if regime_upper == "CRISIS":
            return False  # 스킵 아닌 크기 감소

        if regime_upper not in self._map:
            return True  # 알 수 없는 레짐 → 안전하게 스킵

        active = self.get_active_strategies(regime_upper)
        return strategy_name not in active
