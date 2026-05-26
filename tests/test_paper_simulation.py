"""tests/test_paper_simulation.py — paper_simulation 상대 순위 로직 테스트."""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.backtest.report import compute_rank_scores


def _make_result(
    name: str,
    avg_sharpe: float = 0.5,
    avg_profit_factor: float = 1.0,
    avg_trades: float = 20.0,
    avg_max_dd: float = 0.10,
    consistency_score: float = 0.5,
    sharpe_std: float = 0.3,
    overall_passed: bool = False,
    passed_windows: int = 1,
    total_windows: int = 4,
    avg_return: float = 0.01,
    avg_win_rate: float = 0.50,
) -> dict:
    return {
        "name": name,
        "avg_sharpe": avg_sharpe,
        "avg_profit_factor": avg_profit_factor,
        "avg_trades": avg_trades,
        "avg_max_dd": avg_max_dd,
        "consistency_score": consistency_score,
        "sharpe_std": sharpe_std,
        "overall_passed": overall_passed,
        "passed_windows": passed_windows,
        "total_windows": total_windows,
        "avg_return": avg_return,
        "avg_win_rate": avg_win_rate,
        "avg_final_balance": 10000 * (1 + avg_return),
        "window_results": [],
    }


class TestComputeRankScores:
    """compute_rank_scores 단위 테스트."""

    def test_empty_list_returns_empty(self):
        assert compute_rank_scores([]) == []

    def test_single_result_gets_score_50(self):
        results = [_make_result("strat_a")]
        out = compute_rank_scores(results)
        assert len(out) == 1
        assert out[0]["rank_score"] == 50.0
        assert out[0]["percentile"] == "p50"

    def test_two_results_ranked_correctly(self):
        """높은 Sharpe/PF/trades + 낮은 MDD/std인 전략이 더 높은 score."""
        good = _make_result(
            "good", avg_sharpe=2.0, avg_profit_factor=3.0,
            avg_trades=50, avg_max_dd=0.05, sharpe_std=0.1,
            consistency_score=1.0,
        )
        bad = _make_result(
            "bad", avg_sharpe=-0.5, avg_profit_factor=0.5,
            avg_trades=5, avg_max_dd=0.30, sharpe_std=1.5,
            consistency_score=0.0,
        )
        results = compute_rank_scores([good, bad])
        assert results[0]["rank_score"] > results[1]["rank_score"]
        # good은 100, bad는 0
        assert results[0]["rank_score"] == pytest.approx(100.0, abs=0.1)
        assert results[1]["rank_score"] == pytest.approx(0.0, abs=0.1)

    def test_percentile_labels_assigned(self):
        results = [
            _make_result("a", avg_sharpe=3.0),
            _make_result("b", avg_sharpe=2.0),
            _make_result("c", avg_sharpe=1.0),
        ]
        compute_rank_scores(results)
        pctls = {r["name"]: r["percentile"] for r in results}
        # a: 최고 → p100, c: 최저 → p0
        assert pctls["a"] == "p100"
        assert pctls["c"] == "p0"

    def test_all_identical_scores_get_50(self):
        """모든 지표가 동일하면 모두 score=50."""
        results = [_make_result(f"s{i}") for i in range(5)]
        compute_rank_scores(results)
        for r in results:
            assert r["rank_score"] == pytest.approx(50.0, abs=0.1)

    def test_rank_score_between_0_and_100(self):
        """score는 항상 0~100 범위."""
        results = [
            _make_result("a", avg_sharpe=5.0, avg_trades=100, avg_max_dd=0.01),
            _make_result("b", avg_sharpe=-2.0, avg_trades=1, avg_max_dd=0.50),
            _make_result("c", avg_sharpe=0.0, avg_trades=30, avg_max_dd=0.15),
        ]
        compute_rank_scores(results)
        for r in results:
            assert 0.0 <= r["rank_score"] <= 100.0

    def test_mdd_inversion(self):
        """MDD가 낮은 전략이 높은 전략보다 유리."""
        low_mdd = _make_result("low_mdd", avg_max_dd=0.02)
        high_mdd = _make_result("high_mdd", avg_max_dd=0.40)
        results = compute_rank_scores([low_mdd, high_mdd])
        assert results[0]["rank_score"] > results[1]["rank_score"]

    def test_sharpe_std_inversion(self):
        """Sharpe 표준편차가 낮은(안정적) 전략이 유리."""
        stable = _make_result("stable", sharpe_std=0.05)
        unstable = _make_result("unstable", sharpe_std=2.0)
        results = compute_rank_scores([stable, unstable])
        assert results[0]["rank_score"] > results[1]["rank_score"]

    def test_missing_sharpe_std_defaults_to_zero(self):
        """sharpe_std 키가 없으면 0으로 처리."""
        r = _make_result("no_std")
        del r["sharpe_std"]
        results = compute_rank_scores([r])
        assert results[0]["rank_score"] == 50.0

    def test_does_not_mutate_unrelated_fields(self):
        """기존 필드(name, avg_return 등)가 변경되지 않음."""
        r = _make_result("check", avg_return=0.05, avg_sharpe=1.5)
        compute_rank_scores([r])
        assert r["name"] == "check"
        assert r["avg_return"] == 0.05
        assert r["avg_sharpe"] == 1.5
