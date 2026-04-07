"""
C2. LLMAnalyst: Claude API를 호출해 시장 분석 메모를 생성.

설계 원칙:
  - LLM은 분석(텍스트)만 — 주문 결정은 절대 LLM에 맡기지 않음
  - 이벤트 기반 호출 (매 사이클 X, 중요 신호 발생 시만)
  - 모델 라우팅: Haiku(분류/요약) / Sonnet(심층 분석)
  - API 실패 시 빈 문자열 반환 — 파이프라인 블록 금지
  - ANTHROPIC_API_KEY 없으면 mock 텍스트 반환

출력: 텍스트 메모 (PipelineResult.notes에 추가)
주문 결정: 절대 이 클래스에서 하지 않음
"""

import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

# 비용 최적화 모델 라우팅 (ROADMAP C2 참조)
_HAIKU_MODEL = "claude-haiku-4-5-20251001"    # 분류, 요약 (저비용)
_SONNET_MODEL = "claude-sonnet-4-6"           # 심층 분석 (중간비용)

_MAX_TOKENS = 300   # 분석 메모는 짧게
_ENABLED = bool(os.environ.get("ANTHROPIC_API_KEY"))


class LLMAnalyst:
    """
    Claude API 기반 시장 분석가.

    주의: 이 클래스는 분석 텍스트만 반환. 주문 신호 생성 금지.
    """

    def __init__(self, use_haiku: bool = True, enabled: Optional[bool] = None):
        self._use_haiku = use_haiku
        self._enabled = enabled if enabled is not None else _ENABLED
        self._model = _HAIKU_MODEL if use_haiku else _SONNET_MODEL
        self._client = None

        if self._enabled:
            try:
                import anthropic
                self._client = anthropic.Anthropic()
                logger.info("LLMAnalyst ready (model=%s)", self._model)
            except ImportError:
                logger.warning("anthropic 패키지 미설치: pip install anthropic")
                self._enabled = False

    def analyze_signal(
        self,
        symbol: str,
        signal_action: str,
        signal_reasoning: str,
        context_summary: str = "",
        market_data: str = "",
    ) -> str:
        """
        신호 발생 시 Claude에게 분석 요청.

        Returns:
            분석 텍스트 (1~5문장). API 실패 시 "".
        """
        if not self._enabled:
            return self._mock_analysis(signal_action)

        prompt = self._build_prompt(
            symbol=symbol,
            signal_action=signal_action,
            signal_reasoning=signal_reasoning,
            context_summary=context_summary,
            market_data=market_data,
        )

        try:
            response = self._client.messages.create(
                model=self._model,
                max_tokens=_MAX_TOKENS,
                messages=[{"role": "user", "content": prompt}],
            )
            text = response.content[0].text.strip()
            logger.info("LLM analysis: %s...", text[:80])
            return text
        except Exception as e:
            logger.warning("LLM API call failed: %s", e)
            return ""

    def classify_news_risk(self, headline: str) -> str:
        """
        뉴스 헤드라인을 HIGH/MEDIUM/LOW/NONE으로 분류 (Haiku 사용).
        키워드 분류 보완용. API 실패 시 "NONE" 반환.
        """
        if not self._enabled:
            return "NONE"

        prompt = (
            f"Classify this crypto news headline risk level for active positions.\n"
            f"Reply with ONLY one word: HIGH, MEDIUM, LOW, or NONE.\n\n"
            f"Headline: {headline[:200]}"
        )

        try:
            response = self._client.messages.create(
                model=_HAIKU_MODEL,  # 분류는 항상 Haiku
                max_tokens=10,
                messages=[{"role": "user", "content": prompt}],
            )
            result = response.content[0].text.strip().upper()
            if result in ("HIGH", "MEDIUM", "LOW", "NONE"):
                return result
            return "NONE"
        except Exception as e:
            logger.debug("LLM classify failed: %s", e)
            return "NONE"

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _build_prompt(
        self,
        symbol: str,
        signal_action: str,
        signal_reasoning: str,
        context_summary: str,
        market_data: str,
    ) -> str:
        lines = [
            f"You are a crypto market analyst reviewing a trading signal.",
            f"",
            f"Symbol: {symbol}",
            f"Signal: {signal_action}",
            f"Reason: {signal_reasoning}",
        ]
        if context_summary:
            lines += [f"Market Context: {context_summary}"]
        if market_data:
            lines += [f"Key Data: {market_data}"]
        lines += [
            f"",
            f"Provide a 2-3 sentence analysis of this signal's validity.",
            f"Focus on: risk factors, conflicting signals, confidence level.",
            f"IMPORTANT: Do NOT give buy/sell recommendations. Analysis only.",
        ]
        return "\n".join(lines)

    def _mock_analysis(self, action: str) -> str:
        """API 없을 때 mock 텍스트. 테스트/데모용."""
        if action == "BUY":
            return "[Mock LLM] Signal looks constructive. Monitor support levels and funding rate for confirmation."
        if action == "SELL":
            return "[Mock LLM] Bearish signal detected. Watch for potential short squeeze if funding rate is very negative."
        return "[Mock LLM] Neutral market conditions. No strong directional bias."
