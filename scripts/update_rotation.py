"""
PAPER_SIMULATION_REPORT.md를 파싱해서 rotation_state.json을 업데이트.

paper_simulation.py 실행 후 이 스크립트를 돌리면
StrategyRotationManager에 최신 결과가 반영된다.

Usage:
    python scripts/update_rotation.py
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.strategy.rotation import StrategyRotationManager

STATE_DIR = Path(__file__).resolve().parent.parent / ".claude-state"
REPORT_PATH = STATE_DIR / "PAPER_SIMULATION_REPORT.md"


def parse_report(report_text: str) -> dict:
    """리포트 마크다운에서 심볼별 전략 결과를 파싱."""
    symbol_results = {}
    current_symbol = None

    for line in report_text.split("\n"):
        # 심볼 헤더 감지: "# Paper Trading 시뮬레이션 리포트 — BTC/USDT"
        m = re.match(r"^# Paper Trading.*— (\w+/\w+)", line)
        if m:
            current_symbol = m.group(1)
            symbol_results[current_symbol] = []
            continue

        if not current_symbol:
            continue

        # 전체 결과 테이블 행: | `strategy_name` | +1.23% | 1.50 | 1.50 | 20 | 3/6 | PASS |
        m = re.match(
            r"^\|\s*`(\w+)`\s*\|\s*([+-]?\d+\.?\d*)%\s*\|\s*([+-]?\d+\.?\d*)\s*\|\s*"
            r"([+-]?\d+\.?\d*)\s*\|\s*(\d+)\s*\|\s*(\d+)/(\d+)\s*\|\s*(PASS|FAIL)\s*\|",
            line,
        )
        if m:
            name = m.group(1)
            avg_return = float(m.group(2)) / 100
            avg_sharpe = float(m.group(3))
            avg_pf = float(m.group(4))
            avg_trades = int(m.group(5))
            passed_windows = int(m.group(6))
            total_windows = int(m.group(7))
            overall_passed = m.group(8) == "PASS"

            symbol_results[current_symbol].append({
                "name": name,
                "avg_return": avg_return,
                "avg_sharpe": avg_sharpe,
                "avg_pf": avg_pf,
                "avg_trades": avg_trades,
                "avg_mdd": 0.0,
                "passed_windows": passed_windows,
                "total_windows": total_windows,
                "overall_passed": overall_passed,
            })

    return symbol_results


def main():
    if not REPORT_PATH.exists():
        print("[ERROR] PAPER_SIMULATION_REPORT.md not found")
        return 1

    report = REPORT_PATH.read_text()
    symbol_results = parse_report(report)

    if not symbol_results:
        print("[ERROR] No results parsed from report")
        return 1

    mgr = StrategyRotationManager()

    for symbol, results in symbol_results.items():
        if not results:
            print(f"[SKIP] {symbol}: no results parsed")
            continue
        changes = mgr.revalidate(symbol, results)
        active = mgr.get_active_strategies(symbol)
        print(f"[{symbol}] {len(active)} PASS strategies")
        if changes:
            for name, change in changes.items():
                print(f"  {name}: {change}")

    print(f"\n{mgr.rotation_summary()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
