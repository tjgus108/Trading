"""
MarketContext: B1~B3 알파 소스를 통합한 시장 컨텍스트.

TradingPipeline이 이 컨텍스트를 참조해 신호 confidence를 조정하고
HIGH 이벤트 발생 시 포지션 축소를 권고한다.

설계 원칙:
  - LLM은 분석만, 주문은 코드 — 컨텍스트는 확인/강화에만 사용
  - API 실패 시 중립(score=0) — 파이프라인 블록 금지
  - 컨텍스트 score가 신호 방향과 일치하면 HIGH confidence 부여
  - HIGH 뉴스 이벤트 → 신규 진입 차단 or 포지션 축소 권고
"""

import logging
from dataclasses import dataclass, field
from typing import Optional

from src.data.sentiment import SentimentData, SentimentFetcher
from src.data.onchain import OnchainData, OnchainFetcher
from src.data.news import NewsEvent, NewsMonitor
from src.strategy.base import Action, Confidence, Signal

logger = logging.getLogger(__name__)


@dataclass
class MarketContext:
    """B1 + B2 + B3 통합 컨텍스트."""
    sentiment: Optional[SentimentData] = None
    onchain: Optional[OnchainData] = None
    news: Optional[NewsEvent] = None

    @property
    def composite_score(self) -> float:
        """종합 점수 [-3, +3]. 높을수록 강세."""
        score = 0.0
        weight_s, weight_o = 0.6, 0.4  # 감성 60%, 온체인 40%
        if self.sentiment:
            score += self.sentiment.sentiment_score * weight_s
        if self.onchain:
            score += self.onchain.onchain_score * weight_o
        return max(-3.0, min(3.0, score))

    @property
    def news_risk_level(self) -> str:
        return self.news.level if self.news else "NONE"

    def is_entry_blocked(self) -> bool:
        """HIGH 뉴스 이벤트 시 신규 진입 차단."""
        return self.news is not None and self.news.level == "HIGH"

    def should_reduce_position(self) -> bool:
        """HIGH 이벤트 시 포지션 50% 축소 권고."""
        return self.news is not None and self.news.level == "HIGH"

    def context_aligns(self, action: Action) -> bool:
        """컨텍스트 점수가 신호 방향과 일치하는지."""
        if action == Action.BUY:
            return self.composite_score >= 0.5
        if action == Action.SELL:
            return self.composite_score <= -0.5
        return False

    def adjust_signal(self, signal: Signal) -> tuple[Signal, list[str]]:
        """
        MarketContext 기반으로 신호 confidence 조정 + 메모 반환.
        신호 객체는 불변 — 새 Signal 반환.

        반환: (adjusted_signal, notes)
        """
        notes = []

        if signal.action == Action.HOLD:
            return signal, notes

        # HIGH 뉴스 → 진입 차단 (HOLD로 변환)
        if self.is_entry_blocked():
            notes.append(f"NEWS HIGH: {self.news.event[:60]}... → 신규 진입 차단")
            blocked = Signal(
                action=Action.HOLD,
                confidence=Confidence.HIGH,
                strategy=signal.strategy,
                entry_price=signal.entry_price,
                reasoning=f"[NEWS_BLOCK] {signal.reasoning}",
                invalidation=f"뉴스 리스크 해소 (expires: {self.news.expires_at})",
                bull_case=signal.bull_case,
                bear_case=signal.bear_case,
            )
            return blocked, notes

        # 컨텍스트 점수로 confidence 조정
        aligns = self.context_aligns(signal.action)
        score = self.composite_score

        if aligns and signal.confidence == Confidence.MEDIUM:
            # 컨텍스트가 신호와 일치 → confidence 상향
            adjusted = Signal(
                action=signal.action,
                confidence=Confidence.HIGH,
                strategy=signal.strategy,
                entry_price=signal.entry_price,
                reasoning=signal.reasoning,
                invalidation=signal.invalidation,
                bull_case=signal.bull_case,
                bear_case=signal.bear_case,
            )
            notes.append(f"Context boost: score={score:+.2f} aligns with {signal.action.value}")
            return adjusted, notes

        if not aligns and abs(score) >= 1.5:
            # 컨텍스트가 신호와 반대 → HOLD (보수적)
            notes.append(f"Context conflict: score={score:+.2f} conflicts {signal.action.value} → HOLD")
            conflicted = Signal(
                action=Action.HOLD,
                confidence=Confidence.MEDIUM,
                strategy=signal.strategy,
                entry_price=signal.entry_price,
                reasoning=f"[CTX_CONFLICT] score={score:+.2f} — {signal.reasoning}",
                invalidation="컨텍스트 전환 시 재평가",
                bull_case=signal.bull_case,
                bear_case=signal.bear_case,
            )
            return conflicted, notes

        # MEDIUM 뉴스 → 신규 진입 보류 메모만
        if self.news and self.news.level == "MEDIUM":
            notes.append(f"NEWS MEDIUM: {self.news.event[:60]}... → 신호 유지 (주의 요망)")

        return signal, notes

    def summary_lines(self) -> list[str]:
        lines = []
        if self.sentiment:
            lines.append(self.sentiment.summary())
        if self.onchain:
            lines.append(self.onchain.summary())
        if self.news:
            lines.append(self.news.summary())
        lines.append(f"CONTEXT: composite_score={self.composite_score:+.2f} news_risk={self.news_risk_level}")
        return lines


class MarketContextBuilder:
    """
    B1 + B2 + B3 데이터를 병렬 수집해 MarketContext 빌드.
    각 소스 실패 시 None으로 채워 계속 진행.
    """

    def __init__(self, symbol: str = "BTC/USDT"):
        self._symbol = symbol
        self._sentiment_fetcher = SentimentFetcher(symbol=symbol)
        self._onchain_fetcher = OnchainFetcher()
        self._news_monitor = NewsMonitor()

    def set_high_risk_callback(self, callback) -> None:
        """HIGH 이벤트 즉시 알림용 콜백 설정."""
        self._news_monitor.on_high_risk_callback = callback

    def build(self, use_mock: bool = False) -> MarketContext:
        """
        MarketContext 빌드.
        use_mock=True: API 호출 없이 중립 mock 데이터 사용.
        """
        if use_mock:
            return MarketContext(
                sentiment=self._sentiment_fetcher.mock(),
                onchain=self._onchain_fetcher.mock(),
                news=self._news_monitor.mock(),
            )

        import concurrent.futures

        sentiment, onchain, news = None, None, None

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
            fs = pool.submit(self._safe_sentiment)
            fo = pool.submit(self._safe_onchain)
            fn = pool.submit(self._safe_news)
            sentiment = fs.result()
            onchain = fo.result()
            news = fn.result()

        ctx = MarketContext(sentiment=sentiment, onchain=onchain, news=news)
        for line in ctx.summary_lines():
            logger.info(line)
        return ctx

    def _safe_sentiment(self) -> Optional[SentimentData]:
        try:
            return self._sentiment_fetcher.fetch()
        except Exception as e:
            logger.warning("SentimentFetcher failed: %s", e)
            return None

    def _safe_onchain(self) -> Optional[OnchainData]:
        try:
            return self._onchain_fetcher.fetch()
        except Exception as e:
            logger.warning("OnchainFetcher failed: %s", e)
            return None

    def _safe_news(self) -> Optional[NewsEvent]:
        try:
            return self._news_monitor.fetch()
        except Exception as e:
            logger.warning("NewsMonitor failed: %s", e)
            return None
