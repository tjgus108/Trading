"""
StrategyRotationManager: 월 1회 자동 재검증 기반 전략 로테이션.

- 심볼별로 PASS 전략 목록을 유지
- 주기적으로(기본 30일) walk-forward 재검증 실행
- FAIL 전환된 전략 자동 제거, 새 PASS 전략 자동 추가
- Regime 정보를 활용해 regime별 전략 가중치 조정

Usage:
    manager = StrategyRotationManager()
    active = manager.get_active_strategies("BTC/USDT")
    manager.revalidate("BTC/USDT", df, pass_list, engine)
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

STATE_DIR = Path(__file__).resolve().parent.parent.parent / ".claude-state"
ROTATION_STATE_FILE = STATE_DIR / "rotation_state.json"

PASS_CRITERIA = {
    "min_sharpe": 1.0,
    "min_pf": 1.5,
    "min_trades": 15,
    "max_mdd": 0.20,
}

REVALIDATION_DAYS = 30


class StrategyRotationManager:
    """심볼별 전략 로테이션 관리."""

    def __init__(self, state_file: Optional[Path] = None):
        self._state_file = state_file or ROTATION_STATE_FILE
        self._state = self._load_state()

    def get_active_strategies(self, symbol: str) -> List[str]:
        """현재 PASS 상태인 전략 이름 목록."""
        sym_state = self._state.get(symbol, {})
        return [
            name for name, info in sym_state.get("strategies", {}).items()
            if info.get("status") == "PASS"
        ]

    def get_strategy_info(self, symbol: str, strategy_name: str) -> Optional[dict]:
        """특정 전략의 상세 정보."""
        return self._state.get(symbol, {}).get("strategies", {}).get(strategy_name)

    def needs_revalidation(self, symbol: str) -> bool:
        """재검증이 필요한지 확인 (마지막 검증 후 REVALIDATION_DAYS 경과)."""
        sym_state = self._state.get(symbol, {})
        last_validated = sym_state.get("last_validated")
        if not last_validated:
            return True
        last_dt = datetime.fromisoformat(last_validated)
        elapsed = (datetime.now(timezone.utc) - last_dt).days
        return elapsed >= REVALIDATION_DAYS

    def revalidate(
        self,
        symbol: str,
        results: List[dict],
    ) -> Dict[str, str]:
        """
        Walk-forward 결과를 받아 전략 상태를 업데이트.

        Args:
            symbol: "BTC/USDT" 등
            results: paper_simulation의 evaluate_strategy_walk_forward 결과 리스트.
                     각 dict에 name, avg_sharpe, avg_pf, avg_trades, avg_mdd,
                     overall_passed, avg_return 등 포함.

        Returns:
            변경 사항 dict: {strategy_name: "PASS->FAIL" | "FAIL->PASS" | "NEW_PASS" | ...}
        """
        if symbol not in self._state:
            self._state[symbol] = {"strategies": {}, "last_validated": None}

        sym = self._state[symbol]
        old_strategies = sym.get("strategies", {})
        changes = {}

        for r in results:
            name = r["name"]
            new_pass = r.get("overall_passed", False)
            new_status = "PASS" if new_pass else "FAIL"

            old_info = old_strategies.get(name, {})
            old_status = old_info.get("status", "UNKNOWN")

            if old_status != new_status:
                if old_status == "UNKNOWN":
                    changes[name] = f"NEW_{new_status}"
                else:
                    changes[name] = f"{old_status}->{new_status}"

            sym["strategies"][name] = {
                "status": new_status,
                "avg_return": r.get("avg_return", 0.0),
                "avg_sharpe": r.get("avg_sharpe", 0.0),
                "avg_pf": r.get("avg_pf", 0.0),
                "avg_trades": r.get("avg_trades", 0),
                "avg_mdd": r.get("avg_mdd", 0.0),
                "consistency": f"{r.get('passed_windows', 0)}/{r.get('total_windows', 0)}",
                "last_validated": datetime.now(timezone.utc).isoformat(),
            }

        sym["last_validated"] = datetime.now(timezone.utc).isoformat()
        self._save_state()

        if changes:
            logger.info("[Rotation] %s changes: %s", symbol, changes)
        else:
            logger.info("[Rotation] %s: no status changes", symbol)

        return changes

    def rotation_summary(self) -> str:
        """전체 로테이션 상태 요약 문자열."""
        lines = ["=== Strategy Rotation Status ==="]
        for symbol, sym_state in self._state.items():
            strategies = sym_state.get("strategies", {})
            active = [n for n, s in strategies.items() if s.get("status") == "PASS"]
            total = len(strategies)
            last = sym_state.get("last_validated", "never")
            lines.append(f"{symbol}: {len(active)}/{total} PASS (last: {last})")
            for name in active:
                info = strategies[name]
                lines.append(
                    f"  {name}: ret={info.get('avg_return', 0):.2%} "
                    f"sharpe={info.get('avg_sharpe', 0):.2f} "
                    f"cons={info.get('consistency', '?')}"
                )
        return "\n".join(lines)

    def recommend_for_regime(
        self, symbol: str, regime: str
    ) -> List[str]:
        """
        Regime에 맞는 전략 추천.

        Bundle PASS 전략 우선순위 (Cycle 324 F(리서치) — 레짐 스위칭 로드맵):
          TREND_UP:   order_flow_imbalance_v2 + supertrend_multi (추세 추종)
          TREND_DOWN: vwap_cross + value_area (mean reversion, 숏 친화)
          HIGH_VOL:   cmf 중심 + 낮은 MDD 전략 (볼륨 필터 강함)
          RANGING:    포지션 최소화 (상위 2개만 활성화)
        """
        active = self.get_active_strategies(symbol)
        if not active:
            return active

        strategies = self._state[symbol]["strategies"]

        # Bundle PASS 전략별 레짐 친화도 매핑
        BUNDLE_REGIME_MAP: dict[str, list[str]] = {
            "TREND_UP": ["order_flow_imbalance_v2", "supertrend_multi"],
            "TREND_DOWN": ["vwap_cross", "value_area"],
            "HIGH_VOL": ["cmf"],
        }

        if regime == "HIGH_VOL":
            # Bundle PASS 중 cmf 우선, 나머지는 MDD 기준 보수 정렬
            bundle_preferred = [n for n in BUNDLE_REGIME_MAP["HIGH_VOL"] if n in active]
            remainder = [n for n in active if n not in bundle_preferred]
            remainder_sorted = sorted(remainder, key=lambda n: strategies[n].get("avg_mdd", 1.0))
            return (bundle_preferred + remainder_sorted)[:3]

        if regime == "TREND_UP":
            bundle_preferred = [n for n in BUNDLE_REGIME_MAP["TREND_UP"] if n in active]
            trend_keywords = [
                "momentum", "trend", "breakout", "supertrend",
                "ema", "macd", "impulse", "force",
            ]
            fallback = [n for n in active if n not in bundle_preferred
                        and any(k in n.lower() for k in trend_keywords)]
            combined = bundle_preferred + fallback
            return combined if combined else active

        if regime == "TREND_DOWN":
            bundle_preferred = [n for n in BUNDLE_REGIME_MAP["TREND_DOWN"] if n in active]
            mr_keywords = [
                "reversion", "mean_rev", "band", "rsi", "range",
                "value", "cluster", "channel", "vwap",
            ]
            fallback = [n for n in active if n not in bundle_preferred
                        and any(k in n.lower() for k in mr_keywords)]
            combined = bundle_preferred + fallback
            return combined if combined else active

        if regime == "RANGING":
            # 횡보장: 전략 최소화 — MDD 낮은 상위 2개만 활성화
            return sorted(active, key=lambda n: strategies[n].get("avg_mdd", 1.0))[:2]

        return active

    def _load_state(self) -> dict:
        if self._state_file.exists():
            try:
                return json.loads(self._state_file.read_text())
            except (json.JSONDecodeError, OSError):
                logger.warning("Failed to load rotation state, starting fresh")
        return {}

    def _save_state(self) -> None:
        self._state_file.parent.mkdir(parents=True, exist_ok=True)
        self._state_file.write_text(json.dumps(self._state, indent=2, default=str))
