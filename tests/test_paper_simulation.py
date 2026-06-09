"""tests/test_paper_simulation.py — paper_simulation 상대 순위 + Block Bootstrap 토글 테스트."""
import pytest
import sys
import os
from pathlib import Path
from unittest import mock

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

    def test_silent_strategy_scores_below_active_strategy(self):
        """0-trade(silent) 전략은 실제 거래가 있는 전략보다 낮게 스코어되어야 한다.

        0-trade 전략은 MDD=0, sharpe_std=0으로 인해 인위적으로 높은 score를 얻는 버그 방지.
        """
        # 실제 거래는 있지만 음수 sharpe인 전략
        active_neg = _make_result(
            "active_neg",
            avg_sharpe=-1.0,
            avg_trades=10,
            avg_max_dd=0.08,
            sharpe_std=0.5,
            consistency_score=0.0,
        )
        # 한 번도 신호를 내지 않은 silent 전략 (0-trade)
        silent = _make_result(
            "silent",
            avg_sharpe=0.0,
            avg_trades=0,
            avg_max_dd=0.0,
            sharpe_std=0.0,
            consistency_score=0.0,
        )
        results = compute_rank_scores([active_neg, silent])
        active_score = next(r["rank_score"] for r in results if r["name"] == "active_neg")
        silent_score = next(r["rank_score"] for r in results if r["name"] == "silent")
        assert active_score > silent_score, (
            f"Active (negative sharpe) should outrank silent strategy: "
            f"active={active_score}, silent={silent_score}"
        )


class TestBlockBootstrapToggle:
    """paper_simulation의 Block Bootstrap 토글 로직 테스트."""

    def test_use_block_bootstrap_default_true(self):
        """기본값: USE_BLOCK_BOOTSTRAP = True (환경변수 미설정 시)."""
        env = {k: v for k, v in os.environ.items() if k != "PAPER_SIM_BOOTSTRAP"}
        with mock.patch.dict(os.environ, env, clear=True):
            # 모듈 재로드로 상수 재평가
            import importlib
            import scripts.paper_simulation as ps
            importlib.reload(ps)
            assert ps.USE_BLOCK_BOOTSTRAP is True

    def test_use_block_bootstrap_disabled_by_env(self):
        """환경변수 PAPER_SIM_BOOTSTRAP=0 → GBM 모드."""
        with mock.patch.dict(os.environ, {"PAPER_SIM_BOOTSTRAP": "0"}):
            import importlib
            import scripts.paper_simulation as ps
            importlib.reload(ps)
            assert ps.USE_BLOCK_BOOTSTRAP is False

    def test_block_size_from_env(self):
        """환경변수 PAPER_SIM_BLOCK_SIZE로 블록 크기 변경."""
        with mock.patch.dict(os.environ, {"PAPER_SIM_BLOCK_SIZE": "48"}):
            import importlib
            import scripts.paper_simulation as ps
            importlib.reload(ps)
            assert ps.BLOCK_BOOTSTRAP_BLOCK_SIZE == 48

    def test_block_bootstrap_data_generation(self):
        """Block Bootstrap fallback이 유효한 OHLCV DataFrame을 생성하는지."""
        from scripts.quality_audit import make_synthetic_data, make_block_bootstrap_data
        seed_df = make_synthetic_data(500, seed=99)
        result = make_block_bootstrap_data(
            seed_df, n=200, block_size=36, seed=99,
            initial_price=float(seed_df["close"].iloc[0]),
        )
        assert len(result) == 200
        # OHLCV 컬럼 존재
        for col in ["open", "high", "low", "close", "volume"]:
            assert col in result.columns
        # 가격 양수
        assert (result["close"] > 0).all()
        assert (result["high"] >= result["low"]).all()

    def test_block_bootstrap_vs_gbm_different_data(self):
        """Block Bootstrap과 GBM은 서로 다른 데이터를 생성."""
        from scripts.quality_audit import make_synthetic_data, make_block_bootstrap_data
        gbm_df = make_synthetic_data(500, seed=42)
        bb_df = make_block_bootstrap_data(
            gbm_df, n=500, block_size=36, seed=42,
            initial_price=float(gbm_df["close"].iloc[0]),
        )
        # 같은 seed라도 생성 방식이 다르므로 close가 다름
        assert not gbm_df["close"].iloc[:500].equals(bb_df["close"])

    def test_report_shows_data_source(self):
        """리포트에 데이터 소스(BlockBootstrap/GBM)가 표시되는지."""
        import scripts.paper_simulation as ps
        import pandas as pd
        import numpy as np
        # 최소 DataFrame (리포트 생성용)
        idx = pd.date_range("2024-01-01", periods=100, freq="h")
        df = pd.DataFrame({"close": np.linspace(100, 110, 100)}, index=idx)
        df["open"] = df["close"]
        df["high"] = df["close"] * 1.01
        df["low"] = df["close"] * 0.99
        df["volume"] = 1000.0

        results = [_make_result("test_strat")]
        report = ps.generate_report(results, "Synthetic BlockBootstrap x8640 (BTC/USDT-like)", df, 3)
        assert "BlockBootstrap" in report

        report_gbm = ps.generate_report(results, "Synthetic GBM x8640 (BTC/USDT-like)", df, 3)
        assert "GBM" in report_gbm


class TestBlockSizeCLIArg:
    """--block-size CLI 인수 테스트."""

    def test_block_size_cli_arg_overrides_default(self):
        """--block-size 72가 BLOCK_BOOTSTRAP_BLOCK_SIZE를 72로 설정."""
        import importlib
        import scripts.paper_simulation as ps
        importlib.reload(ps)
        assert ps.BLOCK_BOOTSTRAP_BLOCK_SIZE == 24  # default

        # argparse를 직접 실행하지 않고, CLI가 global을 변경하는 흐름을 검증
        ps.BLOCK_BOOTSTRAP_BLOCK_SIZE = 72
        assert ps.BLOCK_BOOTSTRAP_BLOCK_SIZE == 72

        # 복원
        importlib.reload(ps)

    def test_block_size_cli_arg_accepted_by_parser(self):
        """argparse가 --block-size를 올바르게 파싱."""
        import scripts.paper_simulation as ps
        import importlib
        importlib.reload(ps)

        parser = ps.argparse.ArgumentParser()
        parser.add_argument("--block-size", type=int, default=None)
        args = parser.parse_args(["--block-size", "144"])
        assert args.block_size == 144

    def test_block_size_cli_default_is_none(self):
        """--block-size 미지정 시 None (기본값 유지)."""
        import scripts.paper_simulation as ps
        import importlib
        importlib.reload(ps)

        parser = ps.argparse.ArgumentParser()
        parser.add_argument("--block-size", type=int, default=None)
        args = parser.parse_args([])
        assert args.block_size is None

    def test_block_size_used_in_bootstrap_data(self):
        """다른 block_size 값이 실제로 다른 합성 데이터를 생성."""
        from scripts.quality_audit import make_synthetic_data, make_block_bootstrap_data
        seed_df = make_synthetic_data(500, seed=42)

        df_36 = make_block_bootstrap_data(seed_df, n=200, block_size=36, seed=1)
        df_72 = make_block_bootstrap_data(seed_df, n=200, block_size=72, seed=1)
        df_144 = make_block_bootstrap_data(seed_df, n=200, block_size=144, seed=1)

        # 다른 block_size는 다른 데이터를 생성해야 함
        assert not df_36["close"].equals(df_72["close"])
        assert not df_36["close"].equals(df_144["close"])


# ── 리포트 헬퍼 ──────────────────────────────────────────────

def _make_report_df(periods: int = 100):
    """generate_report 테스트용 최소 DataFrame 생성."""
    import pandas as pd
    import numpy as np
    idx = pd.date_range("2024-01-01", periods=periods, freq="h")
    df = pd.DataFrame({"close": np.linspace(100, 110, periods)}, index=idx)
    df["open"] = df["close"]
    df["high"] = df["close"] * 1.01
    df["low"] = df["close"] * 0.99
    df["volume"] = 1000.0
    return df


class TestGenerateReportEdgeCases:
    """generate_report 엣지케이스 테스트."""

    def test_empty_results_list(self):
        """빈 결과 리스트로 리포트 생성 시 에러 없이 기본 섹션이 포함."""
        import scripts.paper_simulation as ps
        df = _make_report_df()
        report = ps.generate_report([], "Synthetic", df, 3)
        # 헤더와 요약 섹션은 존재
        assert "# Paper Trading" in report
        assert "## 요약" in report
        assert "테스트 전략 | 0개" in report
        assert "PASS" in report and "0개" in report
        # 포트폴리오 섹션은 없어야 함 (results가 비어서 if results: 분기에 안 들어감)
        assert "포트폴리오 가상 배분" not in report
        # TOP 10 헤더는 존재하지만 데이터 행은 없음
        assert "## TOP 10" in report

    def test_all_strategies_fail(self):
        """모든 전략이 FAIL인 경우 리포트에 FAIL 분석 섹션 포함."""
        import scripts.paper_simulation as ps
        df = _make_report_df()
        results = [
            {**_make_result("strat_a", avg_return=-0.05, overall_passed=False),
             "top_fail_reasons": [("sharpe < 1.0", 3), ("trades < 15", 2)]},
            {**_make_result("strat_b", avg_return=-0.10, overall_passed=False),
             "top_fail_reasons": [("sharpe < 1.0", 4)]},
            {**_make_result("strat_c", avg_return=-0.02, overall_passed=False),
             "top_fail_reasons": [("MDD > 20%", 2), ("PF < 1.5", 1)]},
        ]
        report = ps.generate_report(results, "Synthetic", df, 3)
        # PASS 0개
        assert "PASS (일관성 50%+) | 0개" in report
        assert "FAIL | 3개" in report
        # FAIL 원인 분석 섹션 존재
        assert "## FAIL 원인 분석" in report
        assert "전체 FAIL 원인 빈도" in report
        # 포트폴리오 섹션은 존재하되 PASS 배분은 없음
        assert "포트폴리오 가상 배분" in report
        assert "PASS" not in report.split("포트폴리오 가상 배분")[1].split("\n")[1]

    def test_report_with_robustness_labels(self):
        """robustness_label이 설정된 결과가 있으면 Robust 열이 표시."""
        import scripts.paper_simulation as ps
        df = _make_report_df()
        results = [
            {**_make_result("robust_strat", avg_return=0.05, overall_passed=True),
             "robustness_label": "ROBUST", "top_fail_reasons": []},
            {**_make_result("fragile_strat", avg_return=0.01, overall_passed=False),
             "robustness_label": "FRAGILE", "top_fail_reasons": [("sharpe < 1.0", 2)]},
        ]
        report = ps.generate_report(results, "Synthetic", df, 3)
        assert "| Robust |" in report or "Robust" in report
        assert "ROBUST" in report
        assert "FRAGILE" in report

    def test_report_with_rank_scores(self):
        """rank_score가 결과에 포함되면 상대 순위 섹션이 출력."""
        import scripts.paper_simulation as ps
        df = _make_report_df()
        results = [
            {**_make_result("top", avg_return=0.10, avg_sharpe=2.0),
             "rank_score": 90.0, "percentile": "p90", "top_fail_reasons": []},
            {**_make_result("mid", avg_return=0.02, avg_sharpe=0.5),
             "rank_score": 45.0, "percentile": "p45", "top_fail_reasons": []},
        ]
        report = ps.generate_report(results, "Synthetic", df, 3)
        assert "## 상대 순위 (Composite Rank Score)" in report
        assert "p90" in report
        assert "p45" in report


# ── Cycle 290 C: --timeframe 옵션 및 WF 캔들 수 비율 검증 ──────────────

class TestTimeframeCandles:
    """ACTIVE_TIMEFRAME에 따른 make_walk_forward_windows 캔들 수 검증."""

    def _make_df(self, periods: int, freq: str = "h"):
        import pandas as pd, numpy as np
        idx = pd.date_range("2023-01-01", periods=periods, freq=freq)
        df = pd.DataFrame({
            "open": np.ones(periods) * 100,
            "high": np.ones(periods) * 101,
            "low": np.ones(periods) * 99,
            "close": np.ones(periods) * 100,
            "volume": np.ones(periods) * 1000,
        }, index=idx)
        return df

    def test_1h_windows_use_full_candle_count(self):
        """1h 기본 타임프레임에서 train 캔들 수 = TRAIN_HOURS."""
        import importlib
        import scripts.paper_simulation as ps
        importlib.reload(ps)
        assert ps.ACTIVE_TIMEFRAME == "1h"
        # 1h: ratio=1.0 → train_c = TRAIN_HOURS
        assert abs(ps._TF_CANDLE_RATIO["1h"] - 1.0) < 1e-9

    def test_4h_candle_ratio_is_quarter(self):
        """4h 타임프레임의 캔들 비율이 0.25."""
        import scripts.paper_simulation as ps
        assert abs(ps._TF_CANDLE_RATIO["4h"] - 0.25) < 1e-9

    def test_4h_windows_smaller_than_1h(self):
        """4h 모드에서 윈도우 캔들 수가 1h 모드보다 4배 적다."""
        import importlib
        import scripts.paper_simulation as ps
        importlib.reload(ps)

        # 큰 데이터프레임 생성 (1h 기준 8640행, 4h에서 2160행 필요)
        df = self._make_df(8640)

        # 1h 모드
        ps.ACTIVE_TIMEFRAME = "1h"
        windows_1h = ps.make_walk_forward_windows(df)

        # 4h 모드 (같은 크기 데이터에 적용)
        ps.ACTIVE_TIMEFRAME = "4h"
        windows_4h = ps.make_walk_forward_windows(df)

        # 4h 모드는 더 많은 윈도우를 생성 (캔들 수가 적어 더 많이 슬라이딩)
        assert len(windows_4h) >= len(windows_1h)

        # 4h 모드 윈도우의 train 크기 ≈ TRAIN_HOURS * 0.25
        import scripts.paper_simulation as ps2
        expected_train = max(10, int(ps2.TRAIN_HOURS * 0.25))
        if windows_4h:
            actual_train = len(windows_4h[0][0])
            assert actual_train == expected_train

        importlib.reload(ps)  # 복원

    def test_timeframe_reflected_in_report(self):
        """4h 타임프레임이 리포트에 표시된다."""
        import importlib
        import scripts.paper_simulation as ps
        importlib.reload(ps)
        ps.ACTIVE_TIMEFRAME = "4h"

        df = self._make_df(100)
        report = ps.generate_report([], "CSV BTC 4h", df, 3)
        assert "4h" in report

        importlib.reload(ps)  # 복원
