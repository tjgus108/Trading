"""
MonteCarlo 클래스 단위 테스트 - 경계 조건 & 복원력 체크.
"""

import numpy as np
import pandas as pd
import pytest

from src.backtest.monte_carlo import MonteCarlo, MonteCarloResult


def test_monte_carlo_basic():
    """정상 케이스: 500개 수익률로 100번 시뮬레이션."""
    returns = pd.Series(np.random.randn(500) * 0.001 + 0.0005)
    mc = MonteCarlo(n_simulations=100, block_size=20, seed=42)
    result = mc.run(returns)
    
    assert isinstance(result, MonteCarloResult)
    assert len(result.final_returns) == 100
    assert len(result.sharpes) == 100
    assert len(result.max_drawdowns) == 100


def test_monte_carlo_empty_returns():
    """빈 Series: 예외 없이 처리, 결과는 0 또는 NaN."""
    returns = pd.Series(dtype=float)
    mc = MonteCarlo(n_simulations=100, block_size=20)
    result = mc.run(returns)
    
    # 빈 배열에서 np.prod(1+[]) = 1, 따라서 final_return = 0
    assert len(result.final_returns) == 100
    assert np.all(result.final_returns == 0.0)
    # Sharpe와 MDD는 NaN
    assert np.all(np.isnan(result.sharpes))
    assert np.all(np.isnan(result.max_drawdowns))


def test_monte_carlo_single_trade():
    """1개 trade만: block_size=1로 자동 조정."""
    returns = pd.Series([0.001])
    mc = MonteCarlo(n_simulations=50, block_size=20, seed=42)
    result = mc.run(returns)
    
    # block_size가 1로 조정됨
    assert len(result.final_returns) == 50
    # 모든 시뮬이 동일한 수익률을 반복
    assert np.allclose(result.final_returns, [0.001] * 50, atol=1e-10)


def test_monte_carlo_negative_returns():
    """음의 수익률도 처리."""
    returns = pd.Series([-0.001, -0.002, -0.0015] * 100)
    mc = MonteCarlo(n_simulations=100, block_size=10, seed=42)
    result = mc.run(returns)
    
    assert len(result.final_returns) == 100
    # 모든 최종 수익률이 음수
    assert np.all(result.final_returns < 0)


def test_monte_carlo_block_size_exceeds_data():
    """block_size > data length: 경고 후 block_size=1로 조정."""
    returns = pd.Series(np.random.randn(5) * 0.001)
    mc = MonteCarlo(n_simulations=50, block_size=20)
    
    # 경고가 로깅될 것
    result = mc.run(returns)
    assert len(result.final_returns) == 50


def test_monte_carlo_with_nans():
    """NaN 값 포함: dropna() 후 처리."""
    data = np.random.randn(100) * 0.001
    data[10] = np.nan
    data[50] = np.nan
    returns = pd.Series(data)
    
    mc = MonteCarlo(n_simulations=50, block_size=10)
    result = mc.run(returns)
    
    # NaN 제거 후 98개 데이터로 실행
    assert len(result.final_returns) == 50


def test_monte_carlo_result_properties():
    """MonteCarloResult의 percentile 프로퍼티 정상 동작."""
    returns = pd.Series(np.random.randn(200) * 0.001 + 0.0003)
    mc = MonteCarlo(n_simulations=100, block_size=20, seed=42)
    result = mc.run(returns)
    
    # percentile 체크
    assert result.p5_return <= result.p50_return <= result.p95_return
    assert result.p5_sharpe <= result.median_sharpe
    assert result.median_mdd <= result.p95_mdd
    
    # 확률도 [0, 1] 범위
    prob = result.prob_positive()
    assert 0.0 <= prob <= 1.0


def test_monte_carlo_seed_reproducibility():
    """seed로 재현성 검증."""
    returns = pd.Series(np.random.randn(500) * 0.001 + 0.0005)
    
    mc1 = MonteCarlo(n_simulations=100, block_size=20, seed=42)
    result1 = mc1.run(returns)
    
    mc2 = MonteCarlo(n_simulations=100, block_size=20, seed=42)
    result2 = mc2.run(returns)
    
    # 동일한 seed면 동일 결과
    np.testing.assert_array_almost_equal(result1.final_returns, result2.final_returns)


def test_monte_carlo_zero_volatility():
    """0 변동성 returns: Sharpe 계산 안정성."""
    returns = pd.Series([0.0001] * 100)
    mc = MonteCarlo(n_simulations=50, block_size=10)
    result = mc.run(returns)
    
    # 0 변동성이므로 Sharpe는 0.0
    assert len(result.sharpes) == 50
    assert np.all(result.sharpes == 0.0)


def test_monte_carlo_annualization_param():
    """다른 annualization 값으로도 정상 동작."""
    returns = pd.Series(np.random.randn(500) * 0.001 + 0.0005)
    
    mc_daily = MonteCarlo(n_simulations=50, block_size=20, annualization=252)
    result_daily = mc_daily.run(returns)
    
    mc_hourly = MonteCarlo(n_simulations=50, block_size=20, annualization=252*24)
    result_hourly = mc_hourly.run(returns)
    
    # 둘 다 결과를 반환해야 함
    assert len(result_daily.sharpes) == 50
    assert len(result_hourly.sharpes) == 50


# ---------------------------------------------------------------------------
# Cycle 38: Empty Array Bug Fix Regression Tests (Cycle 36 수정 검증)
# ---------------------------------------------------------------------------

def test_monte_carlo_block_bootstrap_empty_array():
    """_block_bootstrap이 빈 배열을 안전하게 처리."""
    mc = MonteCarlo(n_simulations=1, block_size=20)
    
    # 직접 호출: 빈 배열
    result = mc._block_bootstrap(np.array([], dtype=float), target_len=100)
    assert isinstance(result, np.ndarray)
    assert len(result) == 0


def test_monte_carlo_block_bootstrap_zero_target_len():
    """_block_bootstrap이 target_len=0을 안전하게 처리."""
    mc = MonteCarlo(n_simulations=1, block_size=20)
    r = np.array([0.001, 0.002, 0.003], dtype=float)
    
    # target_len이 0이면 빈 배열 반환
    result = mc._block_bootstrap(r, target_len=0)
    assert isinstance(result, np.ndarray)
    assert len(result) == 0


def test_monte_carlo_run_with_many_nans_resulting_empty():
    """대부분 NaN인 Series: dropna() 후 빈 배열, 안전하게 처리."""
    # 거의 모든 값이 NaN
    data = [np.nan] * 95 + [0.001, 0.002, 0.003, 0.004, 0.005]  # 5개 유효값
    returns = pd.Series(data)
    
    mc = MonteCarlo(n_simulations=30, block_size=10, seed=42)
    result = mc.run(returns)
    
    # 예외 없이 완료, 결과는 유효함
    assert len(result.final_returns) == 30
    assert len(result.sharpes) == 30
    assert len(result.max_drawdowns) == 30



def test_monte_carlo_seed_reproducibility_comprehensive():
    """seed 고정 시 전체 결과(final_returns, sharpes, mdds) 재현 가능 검증."""
    returns = pd.Series(np.random.RandomState(123).randn(300) * 0.001 + 0.0002)
    
    # 동일 seed로 3회 실행
    results = []
    for _ in range(3):
        mc = MonteCarlo(n_simulations=150, block_size=15, seed=999, risk_free_rate=0.04)
        results.append(mc.run(returns))
    
    # 모든 메트릭 일치 검증
    for i in range(1, 3):
        np.testing.assert_array_equal(results[0].final_returns, results[i].final_returns,
                                       err_msg=f"Run {i}: final_returns differ")
        np.testing.assert_array_equal(results[0].sharpes, results[i].sharpes,
                                       err_msg=f"Run {i}: sharpes differ")
        np.testing.assert_array_equal(results[0].max_drawdowns, results[i].max_drawdowns,
                                       err_msg=f"Run {i}: max_drawdowns differ")
    
    # percentile도 동일
    assert results[0].p5_return == results[1].p5_return
    assert results[0].p50_return == results[2].p50_return
    assert results[0].p5_sharpe == results[2].p5_sharpe
    assert results[0].median_mdd == results[1].median_mdd
    assert results[0].p95_mdd == results[2].p95_mdd
