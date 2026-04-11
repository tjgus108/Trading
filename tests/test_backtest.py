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

