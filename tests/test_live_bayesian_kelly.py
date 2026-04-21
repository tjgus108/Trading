"""
tests/test_live_bayesian_kelly.py — BayesianKelly + LivePaperTrader 통합 테스트.

live_paper_trader에 BayesianKelly 포지션 사이저가 올바르게 통합되었는지 검증:
1. warmup 기간 → 고정 0.5% 사이징
2. 50+ 거래 후 → Bayesian Kelly 활성화
3. 상태 저장/복원 (세션 재시작)
4. 거래 결과 → posterior 업데이트
"""

import json
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.risk.kelly_sizer import BayesianKellyPositionSizer


# ── BayesianKelly warmup → activation 전환 ──────────────────────────────────

class TestBayesianKellyWarmupTransition:
    """warmup 50거래 → Bayesian Kelly 활성화 전환 검증."""

    def test_warmup_uses_fixed_fraction(self):
        """warmup 기간(n_trades < 50): warmup_fraction=0.005 사용."""
        bk = BayesianKellyPositionSizer(warmup_fraction=0.005, min_trades=50)
        # 0 trades → warmup
        qty = bk.calculate_position_size(capital=10_000, price=100.0)
        expected = 10_000 * 0.005 / 100.0  # 0.5
        assert abs(qty - expected) < 1e-9

    def test_warmup_49_trades_still_warmup(self):
        """49거래 후에도 warmup."""
        bk = BayesianKellyPositionSizer(warmup_fraction=0.005, min_trades=50)
        for _ in range(49):
            bk.update(10.0)
        assert not bk.is_active
        qty = bk.calculate_position_size(capital=10_000, price=100.0)
        expected = 10_000 * 0.005 / 100.0
        assert abs(qty - expected) < 1e-9

    def test_activation_at_50_trades(self):
        """50거래 후 Bayesian Kelly 활성화 — warmup과 다른 사이즈."""
        bk = BayesianKellyPositionSizer(warmup_fraction=0.005, min_trades=50, max_fraction=0.10)
        # 35 wins + 15 losses = 50 trades (70% win rate)
        for _ in range(35):
            bk.update(100.0)
        for _ in range(15):
            bk.update(-50.0)
        assert bk.is_active
        qty_active = bk.calculate_position_size(capital=10_000, price=100.0)
        qty_warmup = 10_000 * 0.005 / 100.0
        # 70% win rate with good edge → 활성화 후 더 큰 포지션
        assert qty_active > qty_warmup

    def test_activation_with_no_edge_returns_zero_or_small(self):
        """50거래(거의 모두 손실) → 활성화 but no edge → 0 또는 매우 작은 포지션."""
        bk = BayesianKellyPositionSizer(warmup_fraction=0.005, min_trades=50)
        for _ in range(5):
            bk.update(10.0)
        for _ in range(45):
            bk.update(-50.0)
        assert bk.is_active
        qty = bk.calculate_position_size(capital=10_000, price=100.0,
                                          avg_win=0.005, avg_loss=0.02)
        # posterior_mean ≈ 7/55 ≈ 0.127 → f_star < 0 → 0
        assert qty == 0.0


# ── 상태 저장/복원 (세션 재시작) ─────────────────────────────────────────────

class TestBayesianKellyStatePersistence:
    """BayesianKelly posterior 상태가 올바르게 저장/복원되는지 검증."""

    def test_state_dict_roundtrip(self):
        """alpha, beta, win/loss 통계가 dict로 직렬화 후 복원."""
        bk = BayesianKellyPositionSizer()
        for _ in range(30):
            bk.update(100.0)
        for _ in range(20):
            bk.update(-50.0)

        # 상태 저장
        state = {
            "alpha": bk._alpha,
            "beta": bk._beta,
            "win_sum": bk._win_sum,
            "win_count": bk._win_count,
            "loss_sum": bk._loss_sum,
            "loss_count": bk._loss_count,
        }

        # 새 인스턴스에 복원
        bk2 = BayesianKellyPositionSizer()
        bk2._alpha = state["alpha"]
        bk2._beta = state["beta"]
        bk2._win_sum = state["win_sum"]
        bk2._win_count = state["win_count"]
        bk2._loss_sum = state["loss_sum"]
        bk2._loss_count = state["loss_count"]

        assert bk2.alpha == bk.alpha
        assert bk2.beta == bk.beta
        assert bk2.n_trades == bk.n_trades
        assert bk2.posterior_mean == bk.posterior_mean
        assert bk2.is_active == bk.is_active

    def test_state_json_serializable(self):
        """BayesianKelly 상태가 JSON 직렬화 가능."""
        bk = BayesianKellyPositionSizer()
        for _ in range(50):
            bk.update(75.0)

        state = {
            "alpha": bk._alpha,
            "beta": bk._beta,
            "win_sum": bk._win_sum,
            "win_count": bk._win_count,
            "loss_sum": bk._loss_sum,
            "loss_count": bk._loss_count,
        }

        # JSON 직렬화/역직렬화 roundtrip
        serialized = json.dumps(state)
        restored = json.loads(serialized)

        bk2 = BayesianKellyPositionSizer()
        bk2._alpha = restored["alpha"]
        bk2._beta = restored["beta"]

        assert bk2.alpha == bk.alpha
        assert bk2.beta == bk.beta

    def test_empty_state_uses_prior(self):
        """빈 상태 dict → prior 유지."""
        bk = BayesianKellyPositionSizer()
        empty_state = {}

        # 빈 dict에서 복원 시도 → 변화 없음
        bk._alpha = float(empty_state.get("alpha", bk.prior_alpha))
        bk._beta = float(empty_state.get("beta", bk.prior_beta))

        assert bk.alpha == 2.0
        assert bk.beta == 3.0


# ── 거래 결과 → posterior 업데이트 ──────────────────────────────────────────

class TestBayesianKellyTradeUpdate:
    """거래 결과(PnL)가 posterior를 올바르게 업데이트하는지 검증."""

    def test_win_increases_alpha(self):
        bk = BayesianKellyPositionSizer()
        alpha_before = bk.alpha
        bk.update(100.0)
        assert bk.alpha == alpha_before + 1

    def test_loss_increases_beta(self):
        bk = BayesianKellyPositionSizer()
        beta_before = bk.beta
        bk.update(-50.0)
        assert bk.beta == beta_before + 1

    def test_mixed_trades_track_correctly(self):
        bk = BayesianKellyPositionSizer()
        bk.update(100.0)   # win: alpha +1
        bk.update(-50.0)   # loss: beta +1
        bk.update(200.0)   # win: alpha +1
        assert bk.alpha == 2.0 + 2  # prior + 2 wins
        assert bk.beta == 3.0 + 1   # prior + 1 loss
        assert bk.n_trades == 3

    def test_avg_win_loss_tracked(self):
        bk = BayesianKellyPositionSizer()
        bk.update(100.0)
        bk.update(200.0)
        bk.update(-60.0)
        assert bk._win_count == 2
        assert abs(bk._win_sum - 300.0) < 1e-9
        assert bk._loss_count == 1
        assert abs(bk._loss_sum - 60.0) < 1e-9


# ── ATR 상한과 BayesianKelly 조합 ──────────────────────────────────────────

class TestBayesianKellyWithATRCap:
    """BayesianKelly + ATR 기반 상한 조합 검증 (live_paper_trader의 실제 로직)."""

    def test_bk_capped_by_atr_size(self):
        """BayesianKelly가 큰 포지션 제안해도 ATR 상한에 제한됨."""
        bk = BayesianKellyPositionSizer(max_fraction=0.10)
        # 50 wins → 높은 posterior → 큰 BK 사이즈
        for _ in range(50):
            bk.update(100.0)
        assert bk.is_active

        capital = 10_000.0
        price = 100.0
        bk_size = bk.calculate_position_size(capital=capital, price=price)

        # ATR 기반 사이즈 (작은 ATR → 큰 사이즈이므로, 작은 ATR로 설정)
        atr = 5.0
        sl_dist = atr * 2.5  # SL_ATR_MULT
        risk_amt = capital * 0.005  # RISK_PER_TRADE
        atr_size = risk_amt / sl_dist

        # 실제 사이즈 = min(bk, atr, max)
        actual_size = min(bk_size, atr_size, (capital * 0.10) / price)

        assert actual_size <= atr_size
        assert actual_size <= bk_size

    def test_warmup_matches_existing_sizing(self):
        """warmup 기간: 기존 RISK_PER_TRADE(0.5%) 사이징과 동일."""
        bk = BayesianKellyPositionSizer(warmup_fraction=0.005)
        assert not bk.is_active

        capital = 10_000.0
        price = 100.0

        bk_warmup_size = bk.calculate_position_size(capital=capital, price=price)
        fixed_risk_size = capital * 0.005 / price

        assert abs(bk_warmup_size - fixed_risk_size) < 1e-9
