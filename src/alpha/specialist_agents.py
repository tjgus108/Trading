"""
F1. FLAG-Trader 패턴: 3개 전문 LLM 에이전트.

ACL 2025 FLAG-Trader 논문 기반.
각 에이전트는 독립 도메인을 분석 → SpecialistVote 반환.
SpecialistEnsemble이 합의 점수로 최종 신호 결정.

에이전트 분리:
  TechnicalAnalystAgent  — 가격/지표 분석 (RSI, EMA, ATR, 볼린저)
  SentimentAnalystAgent  — Fear&Greed, 펀딩비, 뉴스 감성
  OnchainAnalystAgent    — 온체인 지표 (NVT, 고래 흐름, 해시레이트)
"""

import logging
import os
from dataclasses import dataclass

import pandas as pd
from typing import List

logger = logging.getLogger(__name__)

_HAIKU_MODEL = "claude-haiku-4-5-20251001"
_MAX_TOKENS = 150


@dataclass
class SpecialistVote:
    """전문 에이전트 분석 결과."""
    agent_name: str
    action: str          # "BUY" / "SELL" / "HOLD"
    confidence: float    # 0.0 ~ 1.0
    reasoning: str


class TechnicalAnalystAgent:
    """가격/지표 분석 전문 에이전트 (RSI, EMA, ATR, 볼린저)."""

    name = "technical"

    def __init__(self):
        self._client = None
        if os.environ.get("ANTHROPIC_API_KEY"):
            try:
                import anthropic
                self._client = anthropic.Anthropic()
                logger.info("TechnicalAnalystAgent: Claude Haiku ready")
            except ImportError:
                logger.warning("anthropic 패키지 미설치 — mock mode")

    def analyze(self, df: pd.DataFrame) -> SpecialistVote:
        """
        신호 결정 로직:
        1. RSI: rsi14 > 70 → SELL (과매수), rsi14 < 30 → BUY (과매도)
        2. EMA: close > ema20 > ema50 → BUY, 반대 → SELL
        3. 두 신호 일치 → confidence 0.75, 불일치 → HOLD confidence 0.4
        """
        rsi_signal = self._rsi_signal(df)
        ema_signal = self._ema_signal(df)

        if rsi_signal == ema_signal and rsi_signal != "HOLD":
            action = rsi_signal
            confidence = 0.75
            reasoning = f"RSI + EMA 일치: {action}"
        elif rsi_signal != "HOLD" and ema_signal == "HOLD":
            action = rsi_signal
            confidence = 0.55
            reasoning = f"RSI 신호({rsi_signal}), EMA 중립"
        elif ema_signal != "HOLD" and rsi_signal == "HOLD":
            action = ema_signal
            confidence = 0.55
            reasoning = f"EMA 신호({ema_signal}), RSI 중립"
        else:
            action = "HOLD"
            confidence = 0.4
            reasoning = f"RSI({rsi_signal}) + EMA({ema_signal}) 불일치 또는 중립"

        # Claude Haiku로 2문장 분석 추가 (optional)
        llm_note = self._llm_analysis(df, action, reasoning)
        if llm_note:
            reasoning = f"{reasoning} | LLM: {llm_note}"

        return SpecialistVote(
            agent_name=self.name,
            action=action,
            confidence=max(0.0, min(1.0, confidence)),
            reasoning=reasoning,
        )

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _rsi_signal(self, df: pd.DataFrame) -> str:
        if "rsi14" not in df.columns or df.empty:
            return "HOLD"
        rsi = df["rsi14"].iloc[-1]
        if rsi < 30:
            return "BUY"
        if rsi > 70:
            return "SELL"
        return "HOLD"

    def _ema_signal(self, df: pd.DataFrame) -> str:
        required = {"close", "ema20", "ema50"}
        if not required.issubset(df.columns) or df.empty:
            return "HOLD"
        last = df.iloc[-1]
        close, ema20, ema50 = last["close"], last["ema20"], last["ema50"]
        if close > ema20 > ema50:
            return "BUY"
        if close < ema20 < ema50:
            return "SELL"
        return "HOLD"

    def _llm_analysis(self, df: pd.DataFrame, action: str, reasoning: str) -> str:
        if not self._client:
            return ""
        try:
            last = df.iloc[-1] if not df.empty else {}
            rsi_val = last.get("rsi14", "N/A") if hasattr(last, "get") else "N/A"
            prompt = (
                f"Technical signal: {action}\n"
                f"Reason: {reasoning}\n"
                f"RSI14: {rsi_val}\n"
                f"Provide 2 sentences of technical analysis. No buy/sell recommendation."
            )
            resp = self._client.messages.create(
                model=_HAIKU_MODEL,
                max_tokens=_MAX_TOKENS,
                messages=[{"role": "user", "content": prompt}],
            )
            return resp.content[0].text.strip()
        except Exception as e:
            logger.debug("TechnicalAgent LLM call failed: %s", e)
            return ""


class SentimentAnalystAgent:
    """Fear&Greed, 펀딩비, 뉴스 감성 전문 에이전트."""

    name = "sentiment"

    def analyze(
        self, df: pd.DataFrame, sentiment_score: float = 0.0
    ) -> SpecialistVote:
        """
        sentiment_score: SentimentFetcher.get_score() 결과 (-3 ~ +3)
        - score > 1.0  → BUY  confidence 0.65
        - score < -1.0 → SELL confidence 0.65
        - 기타         → HOLD confidence 0.45
        volume_ratio_20 > 2.0 → confidence +0.1
        """
        if sentiment_score > 1.0:
            action = "BUY"
            confidence = 0.65
            reasoning = f"긍정 감성 (score={sentiment_score:+.2f})"
        elif sentiment_score < -1.0:
            action = "SELL"
            confidence = 0.65
            reasoning = f"부정 감성 (score={sentiment_score:+.2f})"
        else:
            action = "HOLD"
            confidence = 0.45
            reasoning = f"중립 감성 (score={sentiment_score:+.2f})"

        # 거래량 급등 보너스
        if not df.empty and "volume_ratio_20" in df.columns:
            vol_ratio = df["volume_ratio_20"].iloc[-1]
            if vol_ratio > 2.0:
                confidence = min(1.0, confidence + 0.1)
                reasoning += f" | 거래량 급등 volume_ratio={vol_ratio:.2f}"

        return SpecialistVote(
            agent_name=self.name,
            action=action,
            confidence=max(0.0, min(1.0, confidence)),
            reasoning=reasoning,
        )


class OnchainAnalystAgent:
    """온체인 지표 전문 에이전트 (NVT, 고래 흐름, 해시레이트)."""

    name = "onchain"

    def analyze(
        self, df: pd.DataFrame, onchain_score: float = 0.0
    ) -> SpecialistVote:
        """
        onchain_score: OnchainFetcher.get_score() 결과 (-3 ~ +3)
        - score > 1.5  → BUY  confidence 0.70
        - score < -1.5 → SELL confidence 0.70
        - 기타         → HOLD confidence 0.5
        """
        if onchain_score > 1.5:
            action = "BUY"
            confidence = 0.70
            reasoning = f"온체인 강세 (score={onchain_score:+.2f})"
        elif onchain_score < -1.5:
            action = "SELL"
            confidence = 0.70
            reasoning = f"온체인 약세 (score={onchain_score:+.2f})"
        else:
            action = "HOLD"
            confidence = 0.5
            reasoning = f"온체인 중립 (score={onchain_score:+.2f})"

        return SpecialistVote(
            agent_name=self.name,
            action=action,
            confidence=max(0.0, min(1.0, confidence)),
            reasoning=reasoning,
        )


class SpecialistEnsemble:
    """3개 에이전트 합의 → 최종 신호."""

    def __init__(self):
        self.technical = TechnicalAnalystAgent()
        self.sentiment = SentimentAnalystAgent()
        self.onchain = OnchainAnalystAgent()

    def analyze(
        self,
        df: pd.DataFrame,
        sentiment_score: float = 0.0,
        onchain_score: float = 0.0,
    ) -> SpecialistVote:
        """
        합의 로직:
        1. 3개 중 2개 이상 동일 방향 → 해당 방향, confidence = 평균
        2. 모두 다른 방향 → HOLD confidence 0.35
        3. 1개만 비HOLD → 해당 방향 confidence * 0.7
        에이전트 개별 실패 시 HOLD로 대체 (graceful degradation).
        """
        agent_calls = [
            (self.technical, "analyze", (df,), {}),
            (self.sentiment, "analyze", (df,), {"sentiment_score": sentiment_score}),
            (self.onchain, "analyze", (df,), {"onchain_score": onchain_score}),
        ]
        votes: List[SpecialistVote] = []
        for agent, method, args, kwargs in agent_calls:
            try:
                vote = getattr(agent, method)(*args, **kwargs)
                votes.append(vote)
            except Exception as e:
                logger.warning(
                    "Agent %s failed, substituting HOLD: %s",
                    getattr(agent, "name", "unknown"),
                    e,
                )
                votes.append(
                    SpecialistVote(
                        agent_name=getattr(agent, "name", "unknown"),
                        action="HOLD",
                        confidence=0.0,
                        reasoning=f"agent error: {e}",
                    )
                )

        if not votes:
            return SpecialistVote(
                agent_name="ensemble",
                action="HOLD",
                confidence=0.0,
                reasoning="no votes collected",
            )
        return self._compute_consensus(votes)

    def _compute_consensus(self, votes: List[SpecialistVote]) -> SpecialistVote:
        from collections import Counter

        actions = [v.action for v in votes]
        counts = Counter(actions)

        # 2개 이상 동일 방향
        for action, count in counts.most_common():
            if count >= 2:
                matching = [v for v in votes if v.action == action]
                avg_conf = sum(v.confidence for v in matching) / len(matching)
                reasoning_parts = [f"{v.agent_name}:{v.action}({v.confidence:.2f})" for v in votes]
                return SpecialistVote(
                    agent_name="ensemble",
                    action=action,
                    confidence=max(0.0, min(1.0, avg_conf)),
                    reasoning=" | ".join(reasoning_parts),
                )

        # 모두 다른 방향이거나 전부 HOLD
        non_hold = [v for v in votes if v.action != "HOLD"]

        if len(non_hold) == 1:
            # 1개만 비HOLD → 해당 방향 confidence * 0.7
            v = non_hold[0]
            reasoning_parts = [f"{vt.agent_name}:{vt.action}({vt.confidence:.2f})" for vt in votes]
            return SpecialistVote(
                agent_name="ensemble",
                action=v.action,
                confidence=max(0.0, min(1.0, v.confidence * 0.7)),
                reasoning=" | ".join(reasoning_parts),
            )

        # 모두 다른 방향 (BUY/SELL/HOLD 각 1개씩 포함 등) → HOLD
        reasoning_parts = [f"{v.agent_name}:{v.action}({v.confidence:.2f})" for v in votes]
        return SpecialistVote(
            agent_name="ensemble",
            action="HOLD",
            confidence=0.35,
            reasoning="합의 실패: " + " | ".join(reasoning_parts),
        )
