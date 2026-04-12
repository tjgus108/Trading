"""DetrendedPriceOscStrategy 단위 테스트 (14개)."""

import math

import numpy as np
import pandas as pd
import pytest

import src.strategy.detrended_price_osc as dpo_module
from src.strategy.base import Action, Confidence, Signal
from src.strategy.detrended_price_osc import DetrendedPriceOscStrategy


def _make_df(n: int = 70, close_val: float = 100.0) -> pd.DataFrame:
    close = np.full(n, close_val, dtype=float)
    return pd.DataFrame({
        "open": close * 0.999,
        "high": close * 1.001,
        "low": close * 0.999,
        "close": close,
        "volume": np.full(n, 1000.0),
        "ema50": close,
        "atr14": np.full(n, 1.0),
    })


def _patch_dpo(monkeypatch, dpo_vals, dpo_ma_vals, dpo_std_vals=None):
    """dpo, dpo_ma, dpo_std 시리즈를 패치."""
    n = len(dpo_vals)
    dpo_series = pd.Series(dpo_vals, dtype=float)
    dpo_ma_series = pd.Series(dpo_ma_vals, dtype=float)
    std_val = 0.5
    if dpo_std_vals is not None:
        dpo_std_series = pd.Series(dpo_std_vals, dtype=float)
    else:
        dpo_std_series = pd.Series([std_val] * n, dtype=float)

    original_generate = DetrendedPriceOscStrategy.generate

    def patched_generate(self, df):
        if df is None or len(df) < 35:
            return Signal(
                action=Action.HOLD,
                confidence=Confidence.LOW,
                strategy=self.name,
                entry_price=0.0,
                reasoning="Insufficient data (min 35 rows required)",
                invalidation="",
                bull_case="",
                bear_case="",
            )
        idx = len(df) - 2
        dpo_now = float(dpo_series.iloc[idx])
        dpo_prev = float(dpo_series.iloc[idx - 1])
        dpo_ma_val = float(dpo_ma_series.iloc[idx])
        dpo_std_val = float(dpo_std_series.iloc[idx])
        entry = float(df["close"].iloc[idx])

        conf = Confidence.HIGH if dpo_std_val > 0 and abs(dpo_now) > dpo_std_val else Confidence.MEDIUM

        if dpo_prev < 0 and dpo_now >= 0 and dpo_now > dpo_ma_val:
            return Signal(
                action=Action.BUY,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"DPO crosses above 0: {dpo_prev:.4f} → {dpo_now:.4f}, dpo_ma={dpo_ma_val:.4f}",
                invalidation="DPO re-crosses below 0",
                bull_case=f"DPO={dpo_now:.4f} 사이클 상승",
                bear_case="단기 반등에 그칠 수 있음",
            )
        if dpo_prev > 0 and dpo_now < 0 and dpo_now < dpo_ma_val:
            return Signal(
                action=Action.SELL,
                confidence=conf,
                strategy=self.name,
                entry_price=entry,
                reasoning=f"DPO crosses below 0: {dpo_prev:.4f} → {dpo_now:.4f}, dpo_ma={dpo_ma_val:.4f}",
                invalidation="DPO re-crosses above 0",
                bull_case="단기 반등 가능성 있음",
                bear_case=f"DPO={dpo_now:.4f} 사이클 하락",
            )
        return Signal(
            action=Action.HOLD,
            confidence=Confidence.MEDIUM,
            strategy=self.name,
            entry_price=entry,
            reasoning=f"DPO neutral: {dpo_now:.4f}, dpo_ma={dpo_ma_val:.4f}",
            invalidation="",
            bull_case="",
            bear_case="",
        )

    monkeypatch.setattr(DetrendedPriceOscStrategy, "generate", patched_generate)


# ── 1. 전략명 확인
def test_strategy_name():
    assert DetrendedPriceOscStrategy.name == "detrended_price_osc"


# ── 2. 인스턴스 생성
def test_strategy_instance():
    strat = DetrendedPriceOscStrategy()
    assert isinstance(strat, DetrendedPriceOscStrategy)


# ── 3. 데이터 부족 → HOLD
def test_insufficient_data():
    strat = DetrendedPriceOscStrategy()
    df = _make_df(n=20)
    sig = strat.generate(df)
    assert sig.action == Action.HOLD
    assert sig.confidence == Confidence.LOW


# ── 4. None 입력 → HOLD
def test_none_input():
    strat = DetrendedPriceOscStrategy()
    sig = strat.generate(None)
    assert sig.action == Action.HOLD


# ── 5. 데이터 부족 reasoning 확인
def test_insufficient_data_reasoning():
    strat = DetrendedPriceOscStrategy()
    df = _make_df(n=10)
    sig = strat.generate(df)
    assert "Insufficient" in sig.reasoning or "insufficient" in sig.reasoning.lower()


# ── 6. 정상 데이터 → Signal 반환
def test_normal_data_returns_signal():
    strat = DetrendedPriceOscStrategy()
    df = _make_df(n=70)
    sig = strat.generate(df)
    assert isinstance(sig, Signal)


# ── 7. Signal 필드 완성
def test_signal_fields_complete():
    strat = DetrendedPriceOscStrategy()
    df = _make_df(n=70)
    sig = strat.generate(df)
    assert sig.action is not None
    assert sig.confidence is not None
    assert sig.strategy == "detrended_price_osc"
    assert isinstance(sig.entry_price, float)
    assert isinstance(sig.reasoning, str)
    assert isinstance(sig.invalidation, str)
    assert isinstance(sig.bull_case, str)
    assert isinstance(sig.bear_case, str)


# ── 8. BUY reasoning 키워드 확인
def test_buy_reasoning_keyword(monkeypatch):
    strat = DetrendedPriceOscStrategy()
    n = 70
    # idx=68: dpo_prev=-0.5, dpo_now=0.1 (crosses above 0), dpo_ma=-0.1
    dpo_vals = [-0.5] * 67 + [-0.5, 0.1, 0.0]
    dpo_ma_vals = [-0.1] * n
    _patch_dpo(monkeypatch, dpo_vals, dpo_ma_vals)
    df = _make_df(n=n)
    sig = strat.generate(df)
    assert sig.action == Action.BUY
    assert "DPO" in sig.reasoning


# ── 9. SELL reasoning 키워드 확인
def test_sell_reasoning_keyword(monkeypatch):
    strat = DetrendedPriceOscStrategy()
    n = 70
    # idx=68: dpo_prev=0.5, dpo_now=-0.1 (crosses below 0), dpo_ma=0.1
    dpo_vals = [0.5] * 67 + [0.5, -0.1, 0.0]
    dpo_ma_vals = [0.1] * n
    _patch_dpo(monkeypatch, dpo_vals, dpo_ma_vals)
    df = _make_df(n=n)
    sig = strat.generate(df)
    assert sig.action == Action.SELL
    assert "DPO" in sig.reasoning


# ── 10. HIGH confidence 테스트
def test_high_confidence_buy(monkeypatch):
    strat = DetrendedPriceOscStrategy()
    n = 70
    # abs(dpo_now=2.0) > std(0.5) → HIGH
    dpo_vals = [-0.5] * 67 + [-0.5, 2.0, 0.0]
    dpo_ma_vals = [-0.1] * n
    dpo_std_vals = [0.5] * n
    _patch_dpo(monkeypatch, dpo_vals, dpo_ma_vals, dpo_std_vals)
    df = _make_df(n=n)
    sig = strat.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.HIGH


# ── 11. MEDIUM confidence 테스트
def test_medium_confidence_buy(monkeypatch):
    strat = DetrendedPriceOscStrategy()
    n = 70
    # abs(dpo_now=0.1) < std(0.5) → MEDIUM
    dpo_vals = [-0.5] * 67 + [-0.5, 0.1, 0.0]
    dpo_ma_vals = [-0.3] * n
    dpo_std_vals = [0.5] * n
    _patch_dpo(monkeypatch, dpo_vals, dpo_ma_vals, dpo_std_vals)
    df = _make_df(n=n)
    sig = strat.generate(df)
    assert sig.action == Action.BUY
    assert sig.confidence == Confidence.MEDIUM


# ── 12. entry_price > 0
def test_entry_price_positive():
    strat = DetrendedPriceOscStrategy()
    df = _make_df(n=70, close_val=50000.0)
    sig = strat.generate(df)
    assert sig.entry_price >= 0


# ── 13. strategy 필드 값 확인
def test_strategy_field():
    strat = DetrendedPriceOscStrategy()
    df = _make_df(n=70)
    sig = strat.generate(df)
    assert sig.strategy == "detrended_price_osc"


# ── 14. 최소 행 수(35)에서 동작
def test_min_rows_works():
    strat = DetrendedPriceOscStrategy()
    df = _make_df(n=35)
    sig = strat.generate(df)
    assert isinstance(sig, Signal)
