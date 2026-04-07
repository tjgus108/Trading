"""
D1. MultiLLMEnsemble: Claude + GPT-4o 동시 신호 → 합의 시 진입.

설계:
  - Claude (Haiku 분류 → Sonnet 심층분석) + OpenAI GPT-4o (선택)
  - 합의(consensus): 두 LLM 모두 같은 방향 → 신호 강화
  - 의견 불일치 → HOLD 권고
  - OpenAI API 없으면 Claude 단독 모드 (graceful degradation)
  - 비용 최적화: 분류는 Haiku, 합의 확인은 GPT-4o-mini

원칙:
  - LLM은 신호 강화/약화 판단만 — 주문 결정은 코드
  - API 실패 시 neutral 반환 — 파이프라인 블록 금지
  - 비용: Claude Haiku + GPT-4o-mini 조합 → 최대 95% 절감

사례: Multi-LLM 봇 비용 $340 → $136/월 (ROADMAP D1)
"""

import logging
import os
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)

_CLAUDE_HAIKU = "claude-haiku-4-5-20251001"
_CLAUDE_SONNET = "claude-sonnet-4-6"
_GPT4O_MINI = "gpt-4o-mini"
_GPT4O = "gpt-4o"

_MAX_TOKENS = 20  # 분류 응답은 짧게 (BUY/SELL/HOLD/NEUTRAL)


@dataclass
class EnsembleSignal:
    """멀티 LLM 앙상블 결과."""
    consensus: str          # "BUY" | "SELL" | "HOLD" | "NEUTRAL"
    confidence: float       # 0.0~1.0 (합의도)
    claude_vote: str        # Claude의 판단
    openai_vote: str        # OpenAI의 판단 ("N/A" if unavailable)
    reasoning: str
    models_used: list[str]

    def agrees_with(self, action: str) -> bool:
        """규칙 기반 신호와 LLM 앙상블이 일치하는지."""
        return self.consensus == action and self.confidence >= 0.6

    def conflicts_with(self, action: str) -> bool:
        """명확하게 반대 의견인지."""
        opposites = {"BUY": "SELL", "SELL": "BUY"}
        return self.consensus == opposites.get(action) and self.confidence >= 0.7

    def summary(self) -> str:
        return (
            f"ENSEMBLE: consensus={self.consensus} conf={self.confidence:.2f} "
            f"claude={self.claude_vote} openai={self.openai_vote} "
            f"models={self.models_used}"
        )


class MultiLLMEnsemble:
    """
    멀티 LLM 앙상블.

    analyze()로 EnsembleSignal 반환.
    OpenAI API 없으면 Claude 단독.
    모든 API 없으면 neutral 반환.
    """

    def __init__(
        self,
        use_openai: bool = True,
        claude_model: str = _CLAUDE_HAIKU,
        openai_model: str = _GPT4O_MINI,
    ):
        self._claude_model = claude_model
        self._openai_model = openai_model

        self._claude_client = None
        self._openai_client = None

        # Claude 초기화
        if os.environ.get("ANTHROPIC_API_KEY"):
            try:
                import anthropic
                self._claude_client = anthropic.Anthropic()
                logger.info("MultiLLMEnsemble: Claude ready (%s)", claude_model)
            except ImportError:
                logger.warning("anthropic 패키지 미설치")

        # OpenAI 초기화
        if use_openai and os.environ.get("OPENAI_API_KEY"):
            try:
                import openai
                self._openai_client = openai.OpenAI()
                logger.info("MultiLLMEnsemble: OpenAI ready (%s)", openai_model)
            except ImportError:
                logger.debug("openai 패키지 미설치 — Claude 단독 모드")

        if not self._claude_client and not self._openai_client:
            logger.info("MultiLLMEnsemble: API 키 없음 — neutral 모드")

    @property
    def is_enabled(self) -> bool:
        return self._claude_client is not None or self._openai_client is not None

    def analyze(
        self,
        symbol: str,
        rule_signal: str,           # 규칙 기반 신호: BUY/SELL/HOLD
        signal_context: str,        # 신호 근거 (간략)
        market_summary: str = "",   # 시장 요약 (가격, RSI 등)
    ) -> EnsembleSignal:
        """
        두 LLM에게 신호 타당성 평가 요청 → 합의 결과 반환.

        API 없으면 rule_signal 그대로 NEUTRAL confidence로 반환.
        """
        if not self.is_enabled:
            return self._neutral(rule_signal, "API 키 없음")

        prompt = self._build_prompt(symbol, rule_signal, signal_context, market_summary)

        claude_vote = self._ask_claude(prompt)
        openai_vote = self._ask_openai(prompt)

        consensus, confidence = self._compute_consensus(
            rule_signal, claude_vote, openai_vote
        )

        models_used = []
        if self._claude_client:
            models_used.append(self._claude_model)
        if self._openai_client:
            models_used.append(self._openai_model)

        result = EnsembleSignal(
            consensus=consensus,
            confidence=confidence,
            claude_vote=claude_vote,
            openai_vote=openai_vote,
            reasoning=f"rule={rule_signal} | claude={claude_vote} | openai={openai_vote}",
            models_used=models_used,
        )
        logger.info(result.summary())
        return result

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _build_prompt(
        self, symbol: str, signal: str, context: str, market: str
    ) -> str:
        return (
            f"Trading signal review for {symbol}.\n"
            f"Rule-based signal: {signal}\n"
            f"Reason: {context[:200]}\n"
            + (f"Market: {market[:100]}\n" if market else "")
            + f"\nDoes this signal make sense given current market conditions?\n"
            f"Reply with ONLY one word: BUY, SELL, HOLD, or NEUTRAL.\n"
            f"(NEUTRAL = no strong opinion)"
        )

    def _ask_claude(self, prompt: str) -> str:
        if not self._claude_client:
            return "N/A"
        try:
            resp = self._claude_client.messages.create(
                model=self._claude_model,
                max_tokens=_MAX_TOKENS,
                messages=[{"role": "user", "content": prompt}],
            )
            vote = resp.content[0].text.strip().upper()
            return vote if vote in ("BUY", "SELL", "HOLD", "NEUTRAL") else "NEUTRAL"
        except Exception as e:
            logger.debug("Claude vote failed: %s", e)
            return "N/A"

    def _ask_openai(self, prompt: str) -> str:
        if not self._openai_client:
            return "N/A"
        try:
            resp = self._openai_client.chat.completions.create(
                model=self._openai_model,
                max_tokens=_MAX_TOKENS,
                messages=[{"role": "user", "content": prompt}],
            )
            vote = resp.choices[0].message.content.strip().upper()
            return vote if vote in ("BUY", "SELL", "HOLD", "NEUTRAL") else "NEUTRAL"
        except Exception as e:
            logger.debug("OpenAI vote failed: %s", e)
            return "N/A"

    def _compute_consensus(
        self, rule: str, claude: str, openai: str
    ) -> tuple[str, float]:
        """
        합의 계산.

        양쪽 모두 같은 방향 → consensus=그방향, confidence=0.9
        한쪽만 동의 → confidence=0.6
        반대 의견 → HOLD, confidence=0.3
        한쪽 N/A → 유효한 쪽만 사용
        """
        valid_votes = [v for v in [claude, openai] if v not in ("N/A", "NEUTRAL")]

        # 둘 다 N/A 또는 NEUTRAL → rule signal 그대로 낮은 confidence
        if not valid_votes:
            return rule, 0.4

        # 한쪽만 유효
        if len(valid_votes) == 1:
            vote = valid_votes[0]
            if vote == rule:
                return rule, 0.65
            elif vote in ("BUY", "SELL") and vote != rule:
                # 반대 의견 → HOLD
                return "HOLD", 0.5
            return rule, 0.5

        # 둘 다 유효
        if claude == openai:
            if claude == rule:
                return rule, 0.90   # 완전 합의
            elif claude in ("BUY", "SELL"):
                return claude, 0.75  # 두 LLM 합의, rule과 다름
            return "HOLD", 0.60

        # 의견 불일치
        if rule in (claude, openai):
            return rule, 0.55       # 규칙과 한쪽 LLM 일치
        return "HOLD", 0.35         # 모두 불일치 → 보수적 HOLD

    def _neutral(self, rule_signal: str, note: str) -> EnsembleSignal:
        return EnsembleSignal(
            consensus=rule_signal,
            confidence=0.5,
            claude_vote="N/A",
            openai_vote="N/A",
            reasoning=note,
            models_used=[],
        )
