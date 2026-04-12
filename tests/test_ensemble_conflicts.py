"""
EnsembleSignal.conflicts_with() 엣지 케이스 테스트.
_compute_consensus: both-fail / one-fail edge cases.
_ask_parallel: 10초 타임아웃 경계값 테스트.
"""
import time
from concurrent.futures import Future
from unittest.mock import MagicMock, patch

import pytest

from src.alpha.ensemble import EnsembleSignal, MultiLLMEnsemble


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


class TestComputeConsensus:
    """_compute_consensus 직접 검증 (no API 호출)."""

    def _ensemble(self):
        """API 키 없이 인스턴스 생성 — neutral 모드."""
        return MultiLLMEnsemble(use_openai=False)

    def test_both_fail_returns_rule_with_low_confidence(self):
        """Claude + OpenAI 둘 다 N/A → rule signal, confidence=0.4."""
        e = self._ensemble()
        consensus, conf = e._compute_consensus("BUY", "N/A", "N/A")
        assert consensus == "BUY"
        assert conf == 0.4

    def test_both_neutral_returns_rule_with_low_confidence(self):
        """NEUTRAL은 N/A와 동일 처리 → rule signal, confidence=0.4."""
        e = self._ensemble()
        consensus, conf = e._compute_consensus("SELL", "NEUTRAL", "NEUTRAL")
        assert consensus == "SELL"
        assert conf == 0.4

    def test_one_fail_agrees_with_rule(self):
        """한쪽 N/A, 나머지가 rule과 동의 → rule signal, confidence=0.65."""
        e = self._ensemble()
        consensus, conf = e._compute_consensus("BUY", "BUY", "N/A")
        assert consensus == "BUY"
        assert conf == 0.65

    def test_one_fail_disagrees_with_rule(self):
        """한쪽 N/A, 나머지가 반대 의견 → HOLD, confidence=0.5."""
        e = self._ensemble()
        consensus, conf = e._compute_consensus("BUY", "SELL", "N/A")
        assert consensus == "HOLD"
        assert conf == 0.5

    def test_openai_fail_claude_agrees(self):
        """OpenAI N/A, Claude가 rule 동의 → rule signal, confidence=0.65."""
        e = self._ensemble()
        consensus, conf = e._compute_consensus("SELL", "N/A", "SELL")
        assert consensus == "SELL"
        assert conf == 0.65


class TestAskParallelTimeout:
    """_ask_parallel 10초 타임아웃 경계 테스트 (실제 API 호출 없음)."""

    def _ensemble_with_mock_clients(self):
        """Claude + OpenAI 클라이언트를 mock으로 주입한 인스턴스."""
        e = MultiLLMEnsemble.__new__(MultiLLMEnsemble)
        e._claude_model = "claude-haiku-test"
        e._openai_model = "gpt-4o-mini-test"
        e._claude_client = MagicMock()
        e._openai_client = MagicMock()
        return e

    def test_timeout_boundary_returns_na(self):
        """future.result(timeout=10) 초과 시 결과가 N/A로 폴백.

        실제 sleep 없이 Future.result 자체를 TimeoutError로 mock — 즉시 실행.
        """
        from concurrent.futures import TimeoutError as FutureTimeout

        e = self._ensemble_with_mock_clients()

        timed_out = Future()
        ok_future = Future()
        ok_future.set_result("SELL")

        submit_calls = iter([timed_out, ok_future])

        def fake_submit(fn, *args, **kwargs):
            return next(submit_calls)

        # timed_out future는 result(timeout=10) 호출 시 TimeoutError 발생
        with patch("src.alpha.ensemble.ThreadPoolExecutor") as MockExec:
            mock_executor = MagicMock()
            MockExec.return_value.__enter__ = MagicMock(return_value=mock_executor)
            MockExec.return_value.__exit__ = MagicMock(return_value=False)
            mock_executor.submit.side_effect = fake_submit

            # timed_out.result(timeout=10) → TimeoutError
            with patch.object(timed_out, "result", side_effect=FutureTimeout("timeout")):
                claude_vote, openai_vote = e._ask_parallel("test prompt")

        assert claude_vote == "N/A"
        assert openai_vote == "SELL"
