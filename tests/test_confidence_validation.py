"""
Signal.confidence 비정상 값 입력 검증 테스트.
"""
import pytest
from src.strategy.base import Action, Confidence, Signal


def _valid_signal(**kwargs) -> Signal:
    defaults = dict(
        action=Action.HOLD,
        confidence=Confidence.LOW,
        strategy="test",
        entry_price=100.0,
        reasoning="ok",
        invalidation="none",
    )
    defaults.update(kwargs)
    return Signal(**defaults)


class TestConfidenceValidation:

    def test_valid_confidence_values(self):
        """Confidence enum은 HIGH/MEDIUM/LOW 세 값만 허용."""
        for val in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW):
            sig = _valid_signal(confidence=val)
            assert sig.confidence == val

    def test_invalid_string_raises(self):
        """잘못된 문자열('VERY_HIGH')은 ValueError를 발생시켜야 한다."""
        with pytest.raises(ValueError):
            Confidence("VERY_HIGH")

    def test_invalid_numeric_raises(self):
        """숫자 값(0.9)은 Confidence enum으로 변환 불가 → ValueError."""
        with pytest.raises(ValueError):
            Confidence(0.9)

    def test_signal_default_confidence_is_enum(self):
        """Signal에 Confidence 멤버를 직접 전달하면 그대로 유지된다."""
        sig = _valid_signal(confidence=Confidence.MEDIUM)
        assert sig.confidence is Confidence.MEDIUM
        assert isinstance(sig.confidence, Confidence)
