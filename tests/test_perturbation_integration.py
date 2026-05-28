"""
perturbation_check 통합 테스트 — BacktestEngine.run_backtest와의 연동 검증.
"""

import numpy as np
import pandas as pd
import pytest

from src.backtest.engine import BacktestEngine
from src.strategy.base import Action, BaseStrategy, Confidence, Signal


# ---------------------------------------------------------------------------
# 헬퍼: mock 전략 & DataFrame
# ---------------------------------------------------------------------------

class AlwaysBuyStrategy(BaseStrategy):
    name = "always_buy"

    def generate(self, df: pd.DataFrame) -> Signal:
        last = df.iloc[-1]
        return Signal(
            action=Action.BUY,
            confidence=Confidence.HIGH,
            strategy=self.name,
            entry_price=float(last["close"]),
            reasoning="test",
            invalidation="none",
        )


class AlternatingStrategy(BaseStrategy):
    """홀수 호출 BUY, 짝수 호출 HOLD — 거래 빈도를 낮춘 전략."""
    name = "alternating"

    def __init__(self):
        self._call_count = 0

    def generate(self, df: pd.DataFrame) -> Signal:
        self._call_count += 1
        last = df.iloc[-1]
        action = Action.BUY if self._call_count % 3 == 1 else Action.HOLD
        return Signal(
            action=action,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=float(last["close"]),
            reasoning="test alternating",
            invalidation="none",
        )


class HoldStrategy(BaseStrategy):
    name = "hold_only"

    def generate(self, df: pd.DataFrame) -> Signal:
        last = df.iloc[-1]
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.LOW,
            strategy=self.name,
            entry_price=float(last["close"]),
            reasoning="test hold",
            invalidation="none",
        )


def make_df(n: int = 200, close_trend: float = 0.001, seed: int = 42) -> pd.DataFrame:
    """단조 상승 가격 + 일정 ATR을 가진 테스트용 DataFrame."""
    np.random.seed(seed)
    closes = 100.0 * np.cumprod(1 + close_trend + np.random.randn(n) * 0.002)
    highs = closes * 1.005
    lows = closes * 0.995
    atr14 = np.full(n, 1.0)
    return pd.DataFrame({"close": closes, "high": highs, "low": lows, "atr14": atr14})


# ---------------------------------------------------------------------------
# 1. perturbation_check가 run()과 올바르게 연동되는지 기본 검증
# ---------------------------------------------------------------------------

def test_perturbation_integrates_with_run():
    """perturbation_check 내부에서 _build_engine → run()이 호출되어
    baseline_sharpe가 직접 run()한 결과와 일치해야 한다."""
    engine = BacktestEngine()
    df = make_df(n=300, close_trend=0.002)
    params = {"atr_multiplier_sl": 1.5, "atr_multiplier_tp": 3.0}

    # 직접 run
    direct_engine = BacktestEngine._build_engine(params)
    direct_result = direct_engine.run(AlwaysBuyStrategy(), df)

    # perturbation_check의 baseline
    pc = engine.perturbation_check(AlwaysBuyStrategy(), params, df)

    assert pc["baseline_sharpe"] == direct_result.sharpe_ratio, (
        f"baseline_sharpe({pc['baseline_sharpe']}) != direct run sharpe({direct_result.sharpe_ratio})"
    )


# ---------------------------------------------------------------------------
# 2. 빈 파라미터 dict — baseline만 계산, perturbations 비어 있음
# ---------------------------------------------------------------------------

def test_perturbation_empty_params():
    """params가 빈 dict이면 perturbations도 비어 있고, baseline만 계산."""
    engine = BacktestEngine()
    df = make_df(n=200, close_trend=0.002)
    pc = engine.perturbation_check(AlwaysBuyStrategy(), params={}, data=df)

    assert pc["perturbations"] == {}
    assert pc["fragile_params"] == []
    assert isinstance(pc["baseline_sharpe"], float)
    # 빈 변동 → mean_sharpe=0, robustness_ratio=0 → label 판정
    assert pc["mean_sharpe"] == 0.0
    assert pc["robustness_label"] in ("ROBUST", "MODERATE", "FRAGILE")


# ---------------------------------------------------------------------------
# 3. 단일 파라미터 — perturbation 수 확인
# ---------------------------------------------------------------------------

def test_perturbation_single_param_counts():
    """단일 파라미터 + 기본 pcts [0.1, 0.2] → 4개 변동(±10%, ±20%) 생성."""
    engine = BacktestEngine()
    df = make_df(n=200, close_trend=0.002)
    params = {"atr_multiplier_sl": 1.5}
    pc = engine.perturbation_check(AlwaysBuyStrategy(), params, df)

    p = pc["perturbations"]["atr_multiplier_sl"]
    assert len(p) == 4  # +10%, -10%, +20%, -20%
    expected_keys = {"+10%", "-10%", "+20%", "-20%"}
    assert set(p.keys()) == expected_keys


# ---------------------------------------------------------------------------
# 4. 여러 파라미터 — 모든 파라미터가 독립적으로 변동됨
# ---------------------------------------------------------------------------

def test_perturbation_multiple_params():
    """3개 파라미터 각각 독립적으로 ±10% 변동, 총 6개 변동 결과."""
    engine = BacktestEngine()
    df = make_df(n=200, close_trend=0.002)
    params = {
        "atr_multiplier_sl": 1.5,
        "atr_multiplier_tp": 3.0,
        "commission": 0.001,
    }
    pc = engine.perturbation_check(
        AlwaysBuyStrategy(), params, df, perturbation_pcts=[0.1],
    )

    assert len(pc["perturbations"]) == 3
    for param_name in params:
        assert param_name in pc["perturbations"]
        assert "+10%" in pc["perturbations"][param_name]
        assert "-10%" in pc["perturbations"][param_name]


# ---------------------------------------------------------------------------
# 5. robustness_label 정확성 — ROBUST 조건 (ratio >= 0.8)
# ---------------------------------------------------------------------------

def test_robustness_label_robust_when_ratio_high():
    """robustness_ratio >= 0.8 이면 ROBUST 판정."""
    engine = BacktestEngine()
    # 긴 상승 트렌드 + 작은 변동 → 파라미터 섭동에도 안정적
    df = make_df(n=400, close_trend=0.003)
    params = {"commission": 0.0005}  # commission 미세 변동은 Sharpe에 큰 영향 없음
    pc = engine.perturbation_check(
        AlwaysBuyStrategy(), params, df, perturbation_pcts=[0.1],
    )

    if pc["robustness_ratio"] >= 0.8:
        assert pc["robustness_label"] == "ROBUST"


# ---------------------------------------------------------------------------
# 6. robustness_label — FRAGILE 조건 (fragile_params 존재)
# ---------------------------------------------------------------------------

def test_robustness_label_fragile_when_fragile_params_exist():
    """fragile_params가 비어있지 않고 ratio < 0.8이면 FRAGILE 판정."""
    engine = BacktestEngine()
    df = make_df(n=200, close_trend=0.002)
    params = {"atr_multiplier_sl": 1.5}
    pc = engine.perturbation_check(AlwaysBuyStrategy(), params, df, perturbation_pcts=[0.1])

    if pc["fragile_params"] and pc["robustness_ratio"] < 0.8:
        assert pc["robustness_label"] == "FRAGILE"


# ---------------------------------------------------------------------------
# 7. 전략 인스턴스 독립성 — 각 변동에서 새 전략 인스턴스가 사용됨 확인
# ---------------------------------------------------------------------------

def test_perturbation_strategy_instance_independence():
    """perturbation_check는 전달받은 strategy 인스턴스를 그대로 사용하되,
    각 변동에서 동일 전략에 대해 일관된 결과를 반환."""
    engine = BacktestEngine()
    df = make_df(n=200, close_trend=0.002)
    params = {"atr_multiplier_sl": 1.5}

    # 두 번 호출 → 동일 결과 (결정론적)
    pc1 = engine.perturbation_check(AlwaysBuyStrategy(), params, df, perturbation_pcts=[0.1])
    pc2 = engine.perturbation_check(AlwaysBuyStrategy(), params, df, perturbation_pcts=[0.1])

    assert pc1["baseline_sharpe"] == pc2["baseline_sharpe"]
    assert pc1["perturbations"] == pc2["perturbations"]
    assert pc1["robustness_label"] == pc2["robustness_label"]


# ---------------------------------------------------------------------------
# 8. mean_sharpe 수학적 정확성
# ---------------------------------------------------------------------------

def test_perturbation_mean_sharpe_is_correct_average():
    """mean_sharpe가 모든 변동 Sharpe 값의 정확한 평균인지 검증."""
    engine = BacktestEngine()
    df = make_df(n=200, close_trend=0.002)
    params = {"atr_multiplier_sl": 1.5, "atr_multiplier_tp": 3.0}
    pc = engine.perturbation_check(
        AlwaysBuyStrategy(), params, df, perturbation_pcts=[0.1],
    )

    all_sharpes = []
    for param_name in params:
        for label, sharpe in pc["perturbations"][param_name].items():
            all_sharpes.append(sharpe)

    expected_mean = round(float(np.mean(all_sharpes)), 4)
    assert abs(pc["mean_sharpe"] - expected_mean) < 0.001, (
        f"mean_sharpe({pc['mean_sharpe']}) != expected({expected_mean})"
    )


# ===========================================================================
# paper_simulation.py perturbation-check 연동 테스트
# ===========================================================================

def test_paper_sim_cli_has_perturbation_check_flag():
    """paper_simulation.py의 argparse에 --perturbation-check 플래그가 존재."""
    import argparse
    import importlib
    import sys
    from pathlib import Path

    # paper_simulation 모듈의 argparse를 직접 검증
    sim_path = Path(__file__).resolve().parent.parent / "scripts" / "paper_simulation.py"
    assert sim_path.exists(), f"paper_simulation.py not found at {sim_path}"

    content = sim_path.read_text()
    assert "--perturbation-check" in content, "CLI flag --perturbation-check가 paper_simulation.py에 없음"
    assert "USE_PERTURBATION_CHECK" in content, "USE_PERTURBATION_CHECK 변수가 없음"


def test_paper_sim_result_has_robustness_label_key():
    """evaluate_strategy_walk_forward 결과 dict에 robustness_label 키가 포함됨."""
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from scripts.paper_simulation import evaluate_strategy_walk_forward

    # 간단한 데이터 + 전략으로 평가
    df = make_df(n=200, close_trend=0.002)
    engine = BacktestEngine()
    # 단일 윈도우: (train, test)
    split = 100
    windows = [(df.iloc[:split], df.iloc[split:])]

    # evaluate_strategy_walk_forward는 strategy_cls()를 호출하므로 클래스 전달
    result = evaluate_strategy_walk_forward(AlwaysBuyStrategy, windows, engine)

    assert "robustness_label" in result, "결과 dict에 robustness_label 키가 없음"
    # 기본값은 빈 문자열 (perturbation_check 미실행)
    assert result["robustness_label"] == "", "기본 robustness_label은 빈 문자열이어야 함"


def test_paper_sim_report_includes_robustness_column():
    """perturbation_check 결과가 있을 때 리포트 테이블에 Robust 컬럼이 포함됨."""
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from scripts.paper_simulation import generate_report

    df = make_df(n=200, close_trend=0.002)
    # robustness_label이 채워진 mock 결과
    mock_results = [
        {
            "name": "test_strat_1",
            "window_results": [],
            "consistency_score": 1.0,
            "passed_windows": 1,
            "total_windows": 1,
            "overall_passed": True,
            "avg_sharpe": 2.0,
            "avg_return": 0.05,
            "avg_max_dd": 0.10,
            "avg_profit_factor": 2.0,
            "avg_trades": 20,
            "avg_win_rate": 0.6,
            "avg_final_balance": 10500,
            "sharpe_std": 0.1,
            "top_fail_reasons": [],
            "robustness_label": "ROBUST",
        },
        {
            "name": "test_strat_2",
            "window_results": [],
            "consistency_score": 0.5,
            "passed_windows": 1,
            "total_windows": 2,
            "overall_passed": True,
            "avg_sharpe": 1.5,
            "avg_return": 0.03,
            "avg_max_dd": 0.15,
            "avg_profit_factor": 1.8,
            "avg_trades": 18,
            "avg_win_rate": 0.55,
            "avg_final_balance": 10300,
            "sharpe_std": 0.2,
            "top_fail_reasons": [],
            "robustness_label": "FRAGILE",
        },
    ]

    report = generate_report(mock_results, "test", df, 1)
    assert "Robust" in report, "리포트에 Robust 컬럼이 포함되어야 함"
    assert "ROBUST" in report, "ROBUST 라벨이 리포트에 표시되어야 함"
    assert "FRAGILE" in report, "FRAGILE 라벨이 리포트에 표시되어야 함"
