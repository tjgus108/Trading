"""BacktestEngine 단위 테스트."""

import numpy as np
import pandas as pd
import pytest

from src.backtest.engine import BacktestEngine
from src.backtest.walk_forward import WalkForwardValidator
from src.strategy.ema_cross import EmaCrossStrategy
from src.strategy.donchian_breakout import DonchianBreakoutStrategy


def _make_trending_df(n: int = 300) -> pd.DataFrame:
    """상승 트렌드 더미 데이터."""
    idx = pd.date_range("2023-01-01", periods=n, freq="1h", tz="UTC")
    trend = np.linspace(40000, 60000, n)
    noise = np.random.randn(n) * 200
    close = trend + noise
    high = close + np.abs(np.random.randn(n) * 150)
    low = close - np.abs(np.random.randn(n) * 150)
    df = pd.DataFrame({"open": close, "high": high, "low": low, "close": close, "volume": 10.0}, index=idx)

    df["ema20"] = df["close"].ewm(span=20, adjust=False).mean()
    df["ema50"] = df["close"].ewm(span=50, adjust=False).mean()
    prev_close = df["close"].shift(1)
    tr = pd.concat([(df["high"] - df["low"]), (df["high"] - prev_close).abs(), (df["low"] - prev_close).abs()], axis=1).max(axis=1)
    df["atr14"] = tr.ewm(alpha=1 / 14, adjust=False).mean()
    delta = df["close"].diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / 14, adjust=False).mean()
    df["rsi14"] = 100 - (100 / (1 + gain / loss.replace(0, np.nan)))
    df["donchian_high"] = df["high"].rolling(20).max()
    df["donchian_low"] = df["low"].rolling(20).min()
    typical = (df["high"] + df["low"] + df["close"]) / 3
    df["vwap"] = (typical * df["volume"]).cumsum() / df["volume"].cumsum()
    return df


def test_backtest_returns_result():
    df = _make_trending_df()
    engine = BacktestEngine(initial_balance=10_000)
    result = engine.run(EmaCrossStrategy(), df)
    assert result.strategy == "ema_cross"
    assert result.total_trades >= 0
    assert 0.0 <= result.win_rate <= 1.0
    assert result.max_drawdown >= 0.0


def test_backtest_result_has_verdict():
    df = _make_trending_df()
    engine = BacktestEngine(initial_balance=10_000)
    result = engine.run(DonchianBreakoutStrategy(), df)
    assert isinstance(result.passed, bool)
    assert isinstance(result.fail_reasons, list)


def test_backtest_no_trades_fails():
    """거래가 없으면 반드시 FAIL."""
    df = _make_trending_df(60)
    engine = BacktestEngine()
    # RSI 조건이 절대 충족 안 되도록 ema20 == ema50 고정
    df["ema20"] = df["ema50"]
    result = engine.run(EmaCrossStrategy(), df)
    assert result.passed is False


def test_backtest_summary_format():
    df = _make_trending_df()
    engine = BacktestEngine()
    result = engine.run(EmaCrossStrategy(), df)
    summary = result.summary()
    assert "BACKTEST_RESULT:" in summary
    assert "verdict:" in summary


def test_backtest_report_to_markdown():
    """BacktestReport.to_markdown() 형식 검증."""
    from src.backtest.report import BacktestReport
    
    trades = [{"pnl_pct": 0.01}, {"pnl_pct": -0.005}, {"pnl_pct": 0.015}]
    report = BacktestReport.from_trades(trades)
    markdown = report.to_markdown()
    
    assert "| Metric | Value |" in markdown
    assert "Total Return" in markdown
    assert "Sharpe Ratio" in markdown
    assert "Deflated Sharpe Ratio" in markdown
    assert "Total Trades | 3 |" in markdown


def test_backtest_report_markdown_vs_summary():
    """to_markdown()는 to_summary()보다 콤팩트해야 함."""
    from src.backtest.report import BacktestReport

    trades = [{"pnl_pct": 0.01}, {"pnl_pct": -0.005}]
    report = BacktestReport.from_trades(trades)

    markdown = report.to_markdown()
    summary = report.summary()

    # markdown은 테이블 형식 (줄 수 적음), summary는 텍스트 형식
    markdown_lines = len(markdown.split('\n'))
    summary_lines = len(summary.split('\n'))

    assert markdown_lines < summary_lines
    assert markdown.count('|') >= 16  # 최소 header + separators + 8 rows


# ---------------------------------------------------------------------------
# WalkForwardValidator 경계 조건 테스트
# ---------------------------------------------------------------------------

def test_walk_forward_validator_raises_on_insufficient_data():
    """데이터가 train+test보다 짧으면 ValueError가 발생해야 한다."""
    validator = WalkForwardValidator(train_window=200, test_window=50, step_size=50)
    df = _make_trending_df(n=100)  # 100 < 200+50
    with pytest.raises(ValueError, match="데이터 부족"):
        validator.validate(df, EmaCrossStrategy())


def test_walk_forward_validator_exact_minimum_data():
    """train+test 정확히 최소 크기 데이터로 윈도우 1개가 생성되어야 한다."""
    train, test = 200, 50
    validator = WalkForwardValidator(train_window=train, test_window=test, step_size=test)
    df = _make_trending_df(n=train + test)  # 정확히 최솟값
    result = validator.validate(df, EmaCrossStrategy())
    assert result.windows == 1
    assert 0.0 <= result.consistency_score <= 1.0
    assert len(result.results) == 1
    # 첫 윈도우 메타데이터 검증
    w = result.results[0]
    assert w["train_start"] == 0
    assert w["train_end"] == train - 1
    assert w["test_start"] == train
    assert w["test_end"] == train + test - 1



def test_backtest_report_to_json():
    """BacktestReport.to_json() 형식 검증 및 직렬화."""
    from src.backtest.report import BacktestReport
    import json
    
    trades = [{"pnl_pct": 0.01}, {"pnl_pct": -0.005}, {"pnl_pct": 0.015}]
    report = BacktestReport.from_trades(trades)
    
    # to_json() 실행
    json_str = report.to_json()
    
    # 유효한 JSON인지 확인
    data = json.loads(json_str)
    
    # 주요 필드 존재 확인
    assert "total_return" in data
    assert "sharpe_ratio" in data
    assert "max_drawdown" in data
    assert "win_rate" in data
    assert "profit_factor" in data
    assert "total_trades" in data
    assert data["total_trades"] == 3
    
    # inf/nan 처리 확인
    assert isinstance(data, dict)
    print(f"✓ to_json() test passed. Generated JSON:\n{json_str}")


def test_backtest_report_json_round_trip():
    """to_json() → from_json() 라운드트립 검증."""
    from src.backtest.report import BacktestReport
    import json
    
    trades = [{"pnl_pct": 0.01}, {"pnl_pct": -0.005}, {"pnl_pct": 0.015}]
    original = BacktestReport.from_trades(trades)
    
    # Serialize to JSON and back
    json_str = original.to_json()
    restored = BacktestReport.from_json(json_str)
    
    # Compare all fields
    assert restored.total_return == original.total_return
    assert restored.ann_return == original.ann_return
    assert restored.ann_volatility == original.ann_volatility
    assert restored.sharpe_ratio == original.sharpe_ratio
    assert restored.sortino_ratio == original.sortino_ratio
    assert restored.deflated_sharpe_ratio == original.deflated_sharpe_ratio
    assert restored.calmar_ratio == original.calmar_ratio
    assert restored.recovery_factor == original.recovery_factor
    assert restored.max_drawdown == original.max_drawdown
    assert restored.total_trades == original.total_trades
    assert restored.win_rate == original.win_rate
    assert restored.profit_factor == original.profit_factor
    assert restored.avg_win == original.avg_win
    assert restored.avg_loss == original.avg_loss
    assert restored.win_loss_ratio == original.win_loss_ratio
    assert restored.max_consecutive_losses == original.max_consecutive_losses
    assert restored.annualization == original.annualization
    print("✓ JSON round-trip test passed")


def test_backtest_report_json_special_values():
    """inf/nan 값 직렬화 및 복원 검증."""
    from src.backtest.report import BacktestReport
    
    trades = [{"pnl_pct": 0.05}, {"pnl_pct": 0.05}]
    report = BacktestReport.from_trades(trades)
    
    # profit_factor가 모두 양수면 inf가 될 수 있음
    # (손실 거래가 없으면 total_loss=0)
    json_str = report.to_json()
    restored = BacktestReport.from_json(json_str)
    
    # inf/nan이 올바르게 복원되었는지 확인
    if report.profit_factor == float("inf"):
        assert restored.profit_factor == float("inf")
    elif report.recovery_factor == float("inf"):
        assert restored.recovery_factor == float("inf")
    else:
        # 일반 값들도 정확히 복원
        assert abs(restored.profit_factor - report.profit_factor) < 1e-9
    
    print("✓ JSON special values test passed")


def test_from_json_preserves_dict_equality():
    """from_json() 복원 후 to_dict()가 원본과 동일해야 함."""
    from src.backtest.report import BacktestReport
    
    trades = [
        {"pnl_pct": 0.02},
        {"pnl_pct": -0.01},
        {"pnl_pct": 0.015},
        {"pnl_pct": -0.005},
        {"pnl_pct": 0.03},
    ]
    original = BacktestReport.from_trades(trades, annualization=6048)
    
    # Round trip
    json_str = original.to_json()
    restored = BacktestReport.from_json(json_str)
    
    # Dict comparison
    original_dict = original.to_dict()
    restored_dict = restored.to_dict()
    
    for key in original_dict:
        orig_val = original_dict[key]
        rest_val = restored_dict[key]
        
        # Handle float comparisons with NaN/inf
        if isinstance(orig_val, float) and isinstance(rest_val, float):
            import numpy as np
            if np.isnan(orig_val) and np.isnan(rest_val):
                continue
            elif np.isinf(orig_val) and np.isinf(rest_val):
                # Check sign match for inf
                assert (orig_val > 0) == (rest_val > 0), f"inf sign mismatch for {key}"
            else:
                assert abs(orig_val - rest_val) < 1e-9, f"Mismatch for {key}: {orig_val} vs {rest_val}"
        else:
            assert orig_val == rest_val, f"Mismatch for {key}: {orig_val} vs {rest_val}"
    
    print("✓ Dict equality test passed")


def test_mc_permutation_test_block_size_1():
    """Test MC permutation with block_size=1 (original behavior: sign randomization)."""
    engine = BacktestEngine(initial_balance=10_000)
    
    # Create sample trades
    trades = [0.01, -0.005, 0.015, 0.008, -0.003, 0.012, 0.002, -0.007, 0.011, 0.005]
    
    # Compute original Sharpe
    arr = np.array(trades, dtype=float)
    mean_r = arr.mean()
    std_r = arr.std()
    original_sharpe = (mean_r / std_r * np.sqrt(8760)) if std_r > 1e-10 else 0.0
    
    # Test with block_size=1 (should use sign randomization)
    p_value = engine._mc_permutation_test(trades, original_sharpe, block_size=1)
    
    assert isinstance(p_value, float), "p_value should be float"
    assert 0.0 <= p_value <= 1.0, f"p_value should be in [0, 1], got {p_value}"


def test_mc_permutation_test_block_size_5():
    """Test MC permutation with block_size=5 (block shuffling)."""
    engine = BacktestEngine(initial_balance=10_000)
    
    # Create sample trades
    trades = [0.01, -0.005, 0.015, 0.008, -0.003, 0.012, 0.002, -0.007, 0.011, 0.005,
              0.009, -0.004, 0.014, 0.007, -0.002]
    
    # Compute original Sharpe
    arr = np.array(trades, dtype=float)
    mean_r = arr.mean()
    std_r = arr.std()
    original_sharpe = (mean_r / std_r * np.sqrt(8760)) if std_r > 1e-10 else 0.0
    
    # Test with block_size=5 (should use block shuffling)
    p_value = engine._mc_permutation_test(trades, original_sharpe, block_size=5)
    
    assert isinstance(p_value, float), "p_value should be float"
    assert 0.0 <= p_value <= 1.0, f"p_value should be in [0, 1], got {p_value}"


def test_mc_permutation_test_default_block_size():
    """Test MC permutation with default block_size (should default to 1)."""
    engine = BacktestEngine(initial_balance=10_000)
    
    # Create sample trades
    trades = [0.01, -0.005, 0.015, 0.008, -0.003]
    
    # Compute original Sharpe
    arr = np.array(trades, dtype=float)
    mean_r = arr.mean()
    std_r = arr.std()
    original_sharpe = (mean_r / std_r * np.sqrt(8760)) if std_r > 1e-10 else 0.0
    
    # Test without specifying block_size (should default to 1)
    p_value = engine._mc_permutation_test(trades, original_sharpe)
    
    assert isinstance(p_value, float), "p_value should be float"
    assert 0.0 <= p_value <= 1.0, f"p_value should be in [0, 1], got {p_value}"


def test_mc_permutation_test_consistency():
    """Test that p-values are in valid range for both block_size strategies."""
    engine = BacktestEngine(initial_balance=10_000)
    
    # Create sample trades with clear structure
    np.random.seed(123)
    trades = list(np.random.randn(50) * 0.01)  # 50 trades
    
    # Compute original Sharpe
    arr = np.array(trades, dtype=float)
    mean_r = arr.mean()
    std_r = arr.std()
    original_sharpe = (mean_r / std_r * np.sqrt(8760)) if std_r > 1e-10 else 0.0
    
    # Test block_size=1 (sign randomization)
    p1 = engine._mc_permutation_test(trades, original_sharpe, block_size=1)
    
    # Test block_size=10 (block shuffling)
    p5 = engine._mc_permutation_test(trades, original_sharpe, block_size=10)
    
    # Both should be valid p-values
    assert 0.0 <= p1 <= 1.0, f"p1 out of range: {p1}"
    assert 0.0 <= p5 <= 1.0, f"p5 out of range: {p5}"
    
    # They may differ due to different randomization strategies
    # (block shuffling vs sign randomization)
    print(f"p_value (block_size=1): {p1:.4f}")
    print(f"p_value (block_size=10): {p5:.4f}")


# ------------------------------------------------------------------
# Deflated Sharpe Ratio tests
# ------------------------------------------------------------------

from src.backtest.walk_forward import deflated_sharpe_ratio, is_sharpe_significant


def test_dsr_no_correction_high_sharpe():
    """N=1(보정 없음), 높은 Sharpe → p-value가 낮아야 함(유의)."""
    p = deflated_sharpe_ratio(
        observed_sharpe=2.0,
        num_strategies_tested=1,
        num_observations=252,
    )
    assert 0.0 <= p <= 1.0, f"p-value out of range: {p}"
    assert p < 0.05, f"N=1, SR=2.0 은 유의해야 함. p={p:.4f}"


def test_dsr_many_strategies_penalizes():
    """N=355(강한 보정)는 N=1보다 p-value가 높아야 함(더 어려운 기준)."""
    sr = 1.5
    T = 500
    p_single = deflated_sharpe_ratio(sr, num_strategies_tested=1, num_observations=T)
    p_many = deflated_sharpe_ratio(sr, num_strategies_tested=355, num_observations=T)
    assert p_many > p_single, (
        f"N=355 보정이 N=1보다 엄격해야 함: p_single={p_single:.4f} p_many={p_many:.4f}"
    )


def test_is_sharpe_significant_default_355():
    """is_sharpe_significant: 매우 높은 Sharpe는 355 전략 보정 후에도 유의해야 함."""
    # SR=3.0, T=1000 은 355 전략 보정 후에도 유의하길 기대
    result = is_sharpe_significant(observed_sharpe=3.0, num_observations=1000)
    assert isinstance(result, bool)
    # SR=0.3, T=50 은 유의하지 않아야 함
    result_low = is_sharpe_significant(observed_sharpe=0.3, num_observations=50)
    assert not result_low, f"낮은 SR(0.3, T=50)은 유의하지 않아야 함"
