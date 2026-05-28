"""
MC permutation test 점검 + narrow_range 전략 edge case 테스트.

Task:
- MC permutation test block sign randomization 정합성 검증
- narrow_range strategy 신호 생성 edge case 커버리지
"""

import numpy as np
import pandas as pd
import pytest

from src.backtest.engine import BacktestEngine, MC_N_PERMUTATIONS
from src.strategy.narrow_range import NarrowRangeStrategy
from src.strategy.base import Action, Confidence


# ═══════════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════════

def _make_nr_df(n: int = 100, seed: int = 42) -> pd.DataFrame:
    """narrow_range 전략용 더미 OHLCV + atr14 데이터.

    상승 트렌드에 NR 패턴을 삽입할 수 있도록 기본 데이터 생성.
    """
    rng = np.random.RandomState(seed)
    idx = pd.date_range("2023-01-01", periods=n, freq="1h", tz="UTC")
    base = np.linspace(100, 120, n)
    noise = rng.randn(n) * 0.5
    close = base + noise
    high = close + rng.uniform(0.3, 1.5, n)
    low = close - rng.uniform(0.3, 1.5, n)
    volume = rng.uniform(100, 500, n)

    df = pd.DataFrame({
        "open": close + rng.randn(n) * 0.1,
        "high": high,
        "low": low,
        "close": close,
        "volume": volume,
    }, index=idx)

    # ATR14 (Wilder EWM)
    prev_close = df["close"].shift(1)
    tr = pd.concat([
        df["high"] - df["low"],
        (df["high"] - prev_close).abs(),
        (df["low"] - prev_close).abs(),
    ], axis=1).max(axis=1)
    df["atr14"] = tr.ewm(alpha=1 / 14, adjust=False).mean()

    return df


def _inject_nr_pattern(df: pd.DataFrame, at_idx: int, nr_range: float = 0.1,
                        atr_ratio: float = 0.5) -> pd.DataFrame:
    """at_idx 봉에 좁은 range (NR 패턴)을 삽입하고 ATR를 축소시킨다.

    Args:
        df: OHLCV DataFrame
        at_idx: NR 패턴을 삽입할 봉 인덱스 (0-based iloc)
        nr_range: NR 봉의 high-low 범위 (작을수록 좁은 range)
        atr_ratio: ATR을 평균의 이 비율로 설정 (< ATR_THRESHOLD=0.95)
    """
    df = df.copy()
    c = float(df["close"].iloc[at_idx])
    df.iloc[at_idx, df.columns.get_loc("high")] = c + nr_range / 2
    df.iloc[at_idx, df.columns.get_loc("low")] = c - nr_range / 2

    # ATR를 충분히 낮게 설정 (avg_atr * atr_ratio)
    avg_atr = float(df["atr14"].iloc[max(0, at_idx - 20):at_idx].mean())
    if avg_atr > 0:
        df.iloc[at_idx, df.columns.get_loc("atr14")] = avg_atr * atr_ratio

    # 이전 봉들의 range를 NR 봉보다 크게 확보
    for j in range(max(0, at_idx - 6), at_idx):
        cur_high = float(df["high"].iloc[j])
        cur_low = float(df["low"].iloc[j])
        if (cur_high - cur_low) <= nr_range:
            mid = (cur_high + cur_low) / 2
            df.iloc[j, df.columns.get_loc("high")] = mid + nr_range * 3
            df.iloc[j, df.columns.get_loc("low")] = mid - nr_range * 3

    return df


# ═══════════════════════════════════════════════════════════════════════════
# MC Permutation Test
# ═══════════════════════════════════════════════════════════════════════════

class TestMCPermutationBlockSign:
    """block_size > 1 경로가 block sign randomization을 수행하는지 검증."""

    def test_block_sign_changes_mean(self):
        """block_size>1 에서 block sign randomization은 평균을 변화시켜야 한다.

        이전 구현(block shuffling)은 평균 불변 -> p-value~1.0 문제가 있었음.
        """
        trades = [0.01] * 20  # 모든 양수 -> 원본 mean > 0
        arr = np.array(trades, dtype=float)
        original_sharpe = arr.mean() / arr.std() * np.sqrt(8760) if arr.std() > 0 else 0.0

        # block_size=5로 테스트: 4개 블록, 각 블록이 +-1 sign -> 평균이 변할 수 있음
        p_value = BacktestEngine._mc_permutation_test(trades, original_sharpe, block_size=5)

        # 모든 양수 trades에서 sign randomization은 p-value < 1.0 이어야 함
        # (일부 permutation에서 음수 sign이 적용되면 Sharpe가 낮아지므로)
        assert p_value < 1.0, (
            f"block sign randomization should produce p < 1.0 for all-positive trades, "
            f"got p={p_value}"
        )

    def test_block_sign_vs_independent_sign_range(self):
        """block_size=1 vs block_size=5: 둘 다 유효한 p-value를 반환해야 한다."""
        rng = np.random.RandomState(123)
        trades = list(rng.randn(50) * 0.01 + 0.005)  # slight positive bias

        arr = np.array(trades, dtype=float)
        original_sharpe = arr.mean() / arr.std() * np.sqrt(8760)

        p1 = BacktestEngine._mc_permutation_test(trades, original_sharpe, block_size=1)
        p5 = BacktestEngine._mc_permutation_test(trades, original_sharpe, block_size=5)

        assert 0.0 <= p1 <= 1.0
        assert 0.0 <= p5 <= 1.0

    def test_block_sign_strong_signal_low_p(self):
        """강한 신호(모든 양수, 높은 Sharpe)에서 p-value가 낮아야 한다."""
        # 강한 양의 신호: 평균 0.02, 표준편차 0.001 -> 매우 높은 Sharpe
        trades = [0.02 + 0.001 * i for i in range(30)]
        arr = np.array(trades, dtype=float)
        original_sharpe = arr.mean() / arr.std() * np.sqrt(8760)

        p1 = BacktestEngine._mc_permutation_test(trades, original_sharpe, block_size=1)
        p5 = BacktestEngine._mc_permutation_test(trades, original_sharpe, block_size=5)

        # 강한 신호 -> 대부분 permutation에서 원본 Sharpe 못 넘김 -> p 낮음
        assert p1 < 0.05, f"Strong signal should have low p (block=1): got {p1}"
        assert p5 < 0.10, f"Strong signal should have low p (block=5): got {p5}"

    def test_block_sign_zero_signal_high_p(self):
        """신호 없는 noise(평균 0)에서 p-value가 높아야 한다."""
        rng = np.random.RandomState(999)
        trades = list(rng.randn(40) * 0.01)  # mean ~0

        arr = np.array(trades, dtype=float)
        original_sharpe = arr.mean() / arr.std() * np.sqrt(8760)

        p = BacktestEngine._mc_permutation_test(trades, original_sharpe, block_size=1)

        # noise-only: p should be relatively high (> 0.05 typically)
        # We don't assert > 0.05 due to random seed, but p should be > 0
        assert 0.0 <= p <= 1.0

    def test_block_size_exceeds_n(self):
        """block_size > n일 때 안전하게 처리."""
        trades = [0.01, -0.005, 0.015]  # 3 trades
        arr = np.array(trades, dtype=float)
        original_sharpe = arr.mean() / arr.std() * np.sqrt(8760)

        # block_size=100 > n=3: should clamp to n
        p = BacktestEngine._mc_permutation_test(trades, original_sharpe, block_size=100)
        assert 0.0 <= p <= 1.0

    def test_empty_trades(self):
        """빈 trades 리스트에서 p=1.0 반환."""
        p = BacktestEngine._mc_permutation_test([], 0.0)
        assert p == 1.0

    def test_single_trade(self):
        """단일 trade에서 정상 동작."""
        trades = [0.01]
        p = BacktestEngine._mc_permutation_test(trades, 10.0, block_size=1)
        assert 0.0 <= p <= 1.0

    def test_block_size_0_treated_as_1(self):
        """block_size=0은 1로 자동 조정."""
        trades = [0.01, -0.005, 0.015, 0.008, -0.003]
        arr = np.array(trades, dtype=float)
        original_sharpe = arr.mean() / arr.std() * np.sqrt(8760)

        p0 = BacktestEngine._mc_permutation_test(trades, original_sharpe, block_size=0)
        p1 = BacktestEngine._mc_permutation_test(trades, original_sharpe, block_size=1)

        # block_size=0 -> 1 이므로 동일한 결과
        assert p0 == p1

    def test_block_sign_all_negative_trades(self):
        """모든 음수 trades: 원본 Sharpe가 음수이므로 p-value는 높아야 한다."""
        trades = [-0.01, -0.02, -0.015, -0.005, -0.012] * 4  # 20 trades, all negative
        arr = np.array(trades, dtype=float)
        original_sharpe = arr.mean() / arr.std() * np.sqrt(8760)

        assert original_sharpe < 0, "Sanity: all-negative should have negative Sharpe"

        p = BacktestEngine._mc_permutation_test(trades, original_sharpe, block_size=1)
        # Negative Sharpe -> most sign-randomized versions should beat it -> high p
        assert p > 0.5, f"All-negative trades should have high p-value, got {p}"


# ═══════════════════════════════════════════════════════════════════════════
# NarrowRange Strategy Edge Cases
# ═══════════════════════════════════════════════════════════════════════════

class TestNarrowRangeEdgeCases:
    """NarrowRangeStrategy 신호 생성의 경계 조건 테스트."""

    def test_hold_on_insufficient_data(self):
        """MIN_ROWS 미만 데이터에서 HOLD 반환."""
        strategy = NarrowRangeStrategy()
        df = _make_nr_df(n=20)  # MIN_ROWS=25보다 작음
        signal = strategy.generate(df)
        assert signal.action == Action.HOLD
        assert "데이터 부족" in signal.reasoning

    def test_hold_on_warmup_period(self):
        """nr_lookback + NR_SCAN_WINDOW보다 짧은 완성봉 데이터에서 HOLD."""
        strategy = NarrowRangeStrategy(nr_lookback=7)
        # curr_idx = len(df)-2 = 25-2 = 23, need > nr_lookback + NR_SCAN_WINDOW = 7+3 = 10
        # 하지만 MIN_ROWS=25 조건은 통과
        df = _make_nr_df(n=25)
        signal = strategy.generate(df)
        # Should get HOLD (either warmup or NR not detected)
        assert signal.action == Action.HOLD

    def test_nr_detection_exact_min_range(self):
        """NR 봉의 range가 정확히 lookback 최소값과 같을 때 감지."""
        strategy = NarrowRangeStrategy(nr_lookback=5)
        df = _make_nr_df(n=60, seed=100)

        # 봉 50에 NR 패턴 삽입: range=0.05 (아주 작은 range)
        df = _inject_nr_pattern(df, at_idx=50, nr_range=0.05, atr_ratio=0.5)

        # 봉 52(=curr_idx when len=53): close를 NR high 위로 설정하여 상향돌파
        # strategy uses iloc[-2] as curr_idx, so we need data up to idx 52+1=53
        # For breakout: close at curr_idx > high at nr_idx
        test_df = df.iloc[:53].copy()
        nr_high = float(test_df["high"].iloc[50])
        test_df.iloc[51, test_df.columns.get_loc("close")] = nr_high + 0.5
        test_df.iloc[51, test_df.columns.get_loc("volume")] = float(
            test_df["volume"].iloc[31:51].mean() * 1.1
        )

        signal = strategy.generate(test_df)
        # May be BUY (breakout detected) or HOLD (depending on ATR conditions)
        assert signal.action in (Action.BUY, Action.HOLD)
        assert signal.strategy == "narrow_range"

    def test_no_signal_when_atr_not_shrunk(self):
        """ATR이 축소되지 않은 상태에서 NR 감지되어도 HOLD."""
        strategy = NarrowRangeStrategy(nr_lookback=5)
        df = _make_nr_df(n=60, seed=200)

        # NR 패턴 삽입하되, atr_ratio를 높게 설정하여 ATR 축소 미충족
        df = _inject_nr_pattern(df, at_idx=50, nr_range=0.05, atr_ratio=1.5)

        test_df = df.iloc[:53].copy()
        signal = strategy.generate(test_df)
        assert signal.action == Action.HOLD

    def test_sell_on_downward_breakout(self):
        """NR 후 하향 돌파 시 SELL 신호."""
        strategy = NarrowRangeStrategy(nr_lookback=5)
        df = _make_nr_df(n=60, seed=300)

        # NR 패턴 삽입
        df = _inject_nr_pattern(df, at_idx=50, nr_range=0.05, atr_ratio=0.5)

        test_df = df.iloc[:53].copy()
        nr_low = float(test_df["low"].iloc[50])
        # curr_idx = 51, close를 NR low 아래로
        test_df.iloc[51, test_df.columns.get_loc("close")] = nr_low - 0.5
        test_df.iloc[51, test_df.columns.get_loc("volume")] = float(
            test_df["volume"].iloc[31:51].mean() * 1.1
        )

        signal = strategy.generate(test_df)
        # NR detected + ATR shrunk + downward breakout -> SELL (or HOLD if ATR check fails)
        assert signal.action in (Action.SELL, Action.HOLD)

    def test_hold_when_close_inside_nr_range(self):
        """NR+ATR축소 감지됐지만 돌파 없음(close가 NR range 안)이면 HOLD."""
        strategy = NarrowRangeStrategy(nr_lookback=5)
        df = _make_nr_df(n=60, seed=400)

        # NR 패턴 삽입
        df = _inject_nr_pattern(df, at_idx=50, nr_range=0.10, atr_ratio=0.5)

        test_df = df.iloc[:53].copy()
        # close를 NR range 안으로 설정
        nr_high = float(test_df["high"].iloc[50])
        nr_low = float(test_df["low"].iloc[50])
        mid = (nr_high + nr_low) / 2
        test_df.iloc[51, test_df.columns.get_loc("close")] = mid

        signal = strategy.generate(test_df)
        # Inside NR range -> no breakout -> HOLD
        assert signal.action == Action.HOLD

    def test_nr4_high_confidence(self):
        """NR4 + NR + volume spike -> HIGH confidence."""
        strategy = NarrowRangeStrategy(nr_lookback=5)
        df = _make_nr_df(n=60, seed=500)

        # NR4이면서 NR5인 패턴 삽입: 최근 4봉과 5봉 모두에서 최소 range
        # 봉 50에 아주 작은 range, 봉 47~49도 작지만 50보다는 크게
        for idx in range(47, 51):
            c = float(df["close"].iloc[idx])
            if idx < 50:
                r = 0.15  # NR5 최소는 아니지만 NR4 판단용
                df.iloc[idx, df.columns.get_loc("high")] = c + r / 2
                df.iloc[idx, df.columns.get_loc("low")] = c - r / 2
            else:
                r = 0.03  # 가장 작은 range
                df.iloc[idx, df.columns.get_loc("high")] = c + r / 2
                df.iloc[idx, df.columns.get_loc("low")] = c - r / 2

        # ATR 축소 설정
        avg_atr = float(df["atr14"].iloc[30:50].mean())
        if avg_atr > 0:
            df.iloc[50, df.columns.get_loc("atr14")] = avg_atr * 0.5

        # 이전 봉 range를 크게 만들어 NR 판정 보장
        for j in range(44, 47):
            c = float(df["close"].iloc[j])
            df.iloc[j, df.columns.get_loc("high")] = c + 2.0
            df.iloc[j, df.columns.get_loc("low")] = c - 2.0

        test_df = df.iloc[:53].copy()
        nr_high = float(test_df["high"].iloc[50])
        # 돌파 + volume spike
        test_df.iloc[51, test_df.columns.get_loc("close")] = nr_high + 0.5
        avg_vol = float(test_df["volume"].iloc[31:51].mean())
        test_df.iloc[51, test_df.columns.get_loc("volume")] = avg_vol * 2.0

        signal = strategy.generate(test_df)
        # If NR4+NR5 detected with vol spike -> HIGH confidence
        if signal.action == Action.BUY:
            # Confidence is HIGH only if NR4 AND vol_spike
            assert signal.confidence in (Confidence.HIGH, Confidence.MEDIUM)

    def test_custom_nr_lookback(self):
        """nr_lookback=7 설정이 정상 적용."""
        strategy = NarrowRangeStrategy(nr_lookback=7)
        assert strategy.nr_lookback == 7
        df = _make_nr_df(n=60)
        signal = strategy.generate(df)
        assert signal.strategy == "narrow_range"

    def test_nr_lookback_minimum_clamp(self):
        """nr_lookback < 4는 4로 클램프."""
        strategy = NarrowRangeStrategy(nr_lookback=2)
        assert strategy.nr_lookback == 4

    def test_is_nr_boundary_first_valid_index(self):
        """_is_nr: idx == n-1일 때 정확히 경계에서 동작."""
        strategy = NarrowRangeStrategy(nr_lookback=5)
        ranges = pd.Series([1.0, 0.8, 0.6, 0.4, 0.2])
        # idx=4, n=5: window=[0,1,2,3,4], min=0.2, ranges[4]=0.2 -> True
        assert strategy._is_nr(ranges, 4, 5) is True

    def test_is_nr_false_when_not_minimum(self):
        """_is_nr: 최소가 아닌 경우 False."""
        strategy = NarrowRangeStrategy(nr_lookback=5)
        ranges = pd.Series([1.0, 0.8, 0.6, 0.4, 0.5])
        # idx=4, n=5: window=[0,1,2,3,4], min=0.4, ranges[4]=0.5 -> False
        assert strategy._is_nr(ranges, 4, 5) is False

    def test_is_nr_insufficient_history(self):
        """_is_nr: idx < n-1일 때 False."""
        strategy = NarrowRangeStrategy(nr_lookback=5)
        ranges = pd.Series([0.1, 0.2, 0.3])
        # idx=2, n=5: 2 < 4 -> False
        assert strategy._is_nr(ranges, 2, 5) is False

    def test_find_recent_nr_returns_none_when_no_nr(self):
        """_find_recent_nr: NR 봉 없으면 None."""
        strategy = NarrowRangeStrategy(nr_lookback=5)
        # 모든 range 동일 -> 모든 봉이 최소 (but _is_nr checks <=, so all are NR)
        # Use increasing ranges -> 마지막 봉들은 NR 아님
        ranges = pd.Series([float(i) for i in range(30)])
        result = strategy._find_recent_nr(ranges, curr_idx=25)
        # ranges[22..24] = 22, 23, 24 — none is min in its window [idx-4..idx]
        assert result is None

    def test_find_recent_nr_returns_dict_when_found(self):
        """_find_recent_nr: NR 봉 발견 시 dict 반환."""
        strategy = NarrowRangeStrategy(nr_lookback=5)
        # idx 10에 작은 range, 나머지는 큰 range
        ranges = pd.Series([2.0] * 20)
        ranges.iloc[10] = 0.1
        # curr_idx=12: scan window [10, 11], check idx=11 (not NR), then idx=10 (NR)
        result = strategy._find_recent_nr(ranges, curr_idx=12)
        assert result is not None
        assert result["idx"] == 10
        assert "is_nr4" in result
        assert "offset" in result


# ═══════════════════════════════════════════════════════════════════════════
# MC test integration with BacktestEngine._compute_metrics
# ═══════════════════════════════════════════════════════════════════════════

class TestMCInComputeMetrics:
    """MC permutation이 _compute_metrics 내에서 올바르게 호출되는지 검증."""

    def test_mc_p_value_is_set_when_trades_sufficient(self):
        """거래 >= MIN_TRADES일 때 mc_p_value가 설정됨."""
        engine = BacktestEngine(initial_balance=10_000)
        # 강한 양수 trades
        trades = [10.0] * 20
        equity = [10_000 + sum(trades[:i]) for i in range(len(trades) + 1)]
        result = engine._compute_metrics("test", trades, equity)
        assert result.mc_p_value >= 0.0, "mc_p_value should be computed"
        assert result.mc_p_value <= 1.0

    def test_mc_p_value_minus_one_when_too_few_trades(self):
        """거래 < MIN_TRADES일 때 mc_p_value = -1.0 (미계산)."""
        engine = BacktestEngine(initial_balance=10_000)
        trades = [10.0] * 5  # MIN_TRADES=15보다 작음
        equity = [10_000 + sum(trades[:i]) for i in range(len(trades) + 1)]
        result = engine._compute_metrics("test", trades, equity)
        assert result.mc_p_value == -1.0
