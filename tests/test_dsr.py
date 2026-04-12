"""Deflated Sharpe Ratio 테스트."""
import numpy as np
import pytest
from src.backtest.report import BacktestReport, deflated_sharpe_ratio


def test_deflated_sharpe_ratio_calculation():
    """deflated_sharpe_ratio 함수 단위 테스트."""
    # 정규분포 수익률
    pnls = np.array([0.01, -0.005, 0.015, 0.005, -0.003, 0.008])
    sr = 1.2
    dsr = deflated_sharpe_ratio(pnls, sr)
    
    # DSR은 수치적으로 유효해야 함
    assert isinstance(dsr, float)
    assert not np.isnan(dsr)
    assert not np.isinf(dsr)


def test_deflated_sharpe_ratio_small_sample():
    """작은 표본 (n<3)에서 DSR = SR."""
    pnls = np.array([0.01, -0.005])
    sr = 1.0
    dsr = deflated_sharpe_ratio(pnls, sr)
    assert dsr == sr


def test_deflated_sharpe_ratio_in_report():
    """BacktestReport에서 DSR 필드 검증."""
    trades = [
        {"pnl_pct": 0.01},
        {"pnl_pct": -0.005},
        {"pnl_pct": 0.015},
        {"pnl_pct": -0.003},
        {"pnl_pct": 0.008},
    ]
    
    report = BacktestReport.from_trades(trades)
    
    # DSR 필드 존재 및 유효성
    assert hasattr(report, 'deflated_sharpe_ratio')
    assert isinstance(report.deflated_sharpe_ratio, float)
    assert not np.isnan(report.deflated_sharpe_ratio)
    assert not np.isinf(report.deflated_sharpe_ratio)
    
    # DSR은 유한한 값
    assert abs(report.deflated_sharpe_ratio) < 1e6
