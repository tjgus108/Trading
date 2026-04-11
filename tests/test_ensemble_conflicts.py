"""
EnsembleSignal.conflicts_with() 엣지 케이스 테스트.
"""
import pytest
from src.alpha.ensemble import EnsembleSignal


def make_signal(consensus: str, confidence: float) -> EnsembleSignal:
    return EnsembleSignal(
        consensus=consensus,
        confidence=confidence,
        claude_vote=consensus,
        openai_vote=consensus,
        reasoning="test",
        models_used=["test-model"],
    )


class TestConflictsWith:
    # --- 동일 action (conflicts_with 는 반대 의견만 True) ---

    def test_same_action_buy_not_conflict(self):
        """BUY 신호 vs BUY action — 반대가 아니므로 False."""
        sig = make_signal("BUY", 0.9)
        assert sig.conflicts_with("BUY") is False

    def test_same_action_sell_not_conflict(self):
        """SELL 신호 vs SELL action — 반대가 아니므로 False."""
        sig = make_signal("SELL", 0.9)
        assert sig.conflicts_with("SELL") is False

    # --- action=HOLD 엣지 케이스 ---

    def test_hold_action_never_conflict(self):
        """action=HOLD 는 opposites에 없음 → opposites.get('HOLD')=None → False."""
        sig = make_signal("BUY", 0.95)
        assert sig.conflicts_with("HOLD") is False

    def test_consensus_hold_never_conflict(self):
        """consensus=HOLD 는 BUY/SELL의 opposite이 아님 → conflicts False."""
        sig = make_signal("HOLD", 0.95)
        assert sig.conflicts_with("BUY") is False
        assert sig.conflicts_with("SELL") is False

    # --- confidence 경계값 ---

    def test_conflict_exactly_at_threshold(self):
        """confidence=0.7 (임계값) — conflicts_with 조건: >= 0.7 → True."""
        sig = make_signal("SELL", 0.7)
        assert sig.conflicts_with("BUY") is True

    def test_no_conflict_below_threshold(self):
        """confidence=0.69 — 임계값 미만 → False."""
        sig = make_signal("SELL", 0.69)
        assert sig.conflicts_with("BUY") is False

    # --- 실제 충돌 케이스 ---

    def test_buy_conflicts_sell_high_confidence(self):
        """consensus=BUY, action=SELL, confidence=0.8 → True."""
        sig = make_signal("BUY", 0.8)
        assert sig.conflicts_with("SELL") is True

    def test_sell_conflicts_buy_high_confidence(self):
        """consensus=SELL, action=BUY, confidence=0.9 → True."""
        sig = make_signal("SELL", 0.9)
        assert sig.conflicts_with("BUY") is True

    # --- NEUTRAL consensus ---

    def test_neutral_consensus_not_conflict(self):
        """consensus=NEUTRAL 는 opposites에 없음 → False."""
        sig = make_signal("NEUTRAL", 0.95)
        assert sig.conflicts_with("BUY") is False
        assert sig.conflicts_with("SELL") is False
