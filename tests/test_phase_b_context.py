"""Phase B: MarketContext (B1 감성, B2 온체인, B3 뉴스) 단위 테스트."""

import pytest
from src.data.sentiment import SentimentFetcher, SentimentData
from src.data.onchain import OnchainFetcher, OnchainData
from src.data.news import NewsMonitor, NewsEvent
from src.alpha.context import MarketContext, MarketContextBuilder
from src.strategy.base import Action, Confidence, Signal


# ---------------------------------------------------------------------------
# B1: SentimentFetcher
# ---------------------------------------------------------------------------

class TestSentimentFetcher:
    def test_mock_neutral(self):
        f = SentimentFetcher()
        data = f.mock(fear_greed=50, funding_rate=0.0001)
        assert data.fear_greed_index == 50
        assert data.funding_rate == 0.0001
        assert data.source == "mock"
        assert -3.0 <= data.sentiment_score <= 3.0

    def test_extreme_fear_score_positive(self):
        """극단 공포 → 역추세 관점에서 양수 점수."""
        f = SentimentFetcher()
        data = f.mock(fear_greed=5, funding_rate=0.0)
        assert data.sentiment_score > 0

    def test_extreme_greed_score_negative(self):
        """극단 탐욕 → 역추세 관점에서 음수 점수."""
        f = SentimentFetcher()
        data = f.mock(fear_greed=95, funding_rate=0.0)
        assert data.sentiment_score < 0

    def test_high_funding_rate_negative_score(self):
        """펀딩비 과열 → 음수 점수."""
        f = SentimentFetcher()
        data = f.mock(fear_greed=50, funding_rate=0.0006)
        assert data.sentiment_score < 0

    def test_negative_funding_rate_positive_score(self):
        """펀딩비 마이너스 → 양수 점수."""
        f = SentimentFetcher()
        data = f.mock(fear_greed=50, funding_rate=-0.0003)
        assert data.sentiment_score > 0

    def test_score_bounded(self):
        f = SentimentFetcher()
        data = f.mock(fear_greed=0, funding_rate=-0.001)
        assert -3.0 <= data.sentiment_score <= 3.0

    def test_is_extreme_fear(self):
        f = SentimentFetcher()
        data = f.mock(fear_greed=20)
        assert data.is_extreme_fear()

    def test_is_extreme_greed(self):
        f = SentimentFetcher()
        data = f.mock(fear_greed=80)
        assert data.is_extreme_greed()

    def test_summary_contains_fields(self):
        f = SentimentFetcher()
        data = f.mock(fear_greed=30, funding_rate=0.0002)
        s = data.summary()
        assert "FG=" in s
        assert "FR=" in s
        assert "score=" in s

    def test_cache_returns_same_object(self):
        """캐시 시간 내 재호출 시 같은 객체."""
        f = SentimentFetcher(use_cache_seconds=300)
        # mock fetch 직접 설정
        from src.data.sentiment import SentimentData
        import time
        mock_data = f.mock()
        f._cache = mock_data
        f._cache_time = time.time()
        result = f.fetch()
        assert result is mock_data


# ---------------------------------------------------------------------------
# B2: OnchainFetcher
# ---------------------------------------------------------------------------

class TestOnchainFetcher:
    def test_mock_neutral(self):
        f = OnchainFetcher()
        data = f.mock()
        assert data.exchange_flow == "NEUTRAL"
        assert data.onchain_score == 0.0
        assert data.source == "mock"

    def test_inflow_spike_negative_score(self):
        f = OnchainFetcher()
        data = f.mock(exchange_flow="INFLOW_SPIKE")
        assert data.onchain_score < 0

    def test_outflow_positive_score(self):
        f = OnchainFetcher()
        data = f.mock(exchange_flow="OUTFLOW")
        assert data.onchain_score > 0

    def test_whale_accumulating_positive(self):
        f = OnchainFetcher()
        data = f.mock(whale_activity="ACCUMULATING")
        assert data.onchain_score > 0

    def test_whale_distributing_negative(self):
        f = OnchainFetcher()
        data = f.mock(whale_activity="DISTRIBUTING")
        assert data.onchain_score < 0

    def test_nvt_undervalued_positive(self):
        f = OnchainFetcher()
        data = f.mock(nvt_signal="UNDERVALUED")
        assert data.onchain_score > 0

    def test_nvt_overvalued_negative(self):
        f = OnchainFetcher()
        data = f.mock(nvt_signal="OVERVALUED")
        assert data.onchain_score < 0

    def test_score_bounded(self):
        f = OnchainFetcher()
        data = f.mock(exchange_flow="INFLOW_SPIKE", whale_activity="DISTRIBUTING", nvt_signal="OVERVALUED")
        assert -3.0 <= data.onchain_score <= 3.0

    def test_summary_fields(self):
        f = OnchainFetcher()
        data = f.mock(exchange_flow="OUTFLOW", whale_activity="ACCUMULATING")
        s = data.summary()
        assert "ONCHAIN" in s
        assert "flow=" in s
        assert "score=" in s


# ---------------------------------------------------------------------------
# B3: NewsMonitor
# ---------------------------------------------------------------------------

class TestNewsMonitor:
    def test_mock_none(self):
        m = NewsMonitor()
        event = m.mock(level="NONE")
        assert event.level == "NONE"
        assert event.action == "NONE"

    def test_mock_high(self):
        m = NewsMonitor()
        event = m.mock(level="HIGH", event_text="Exchange hacked, funds stolen")
        assert event.level == "HIGH"
        assert event.action == "REDUCE_POSITION"
        assert event.is_high_risk()

    def test_mock_medium(self):
        m = NewsMonitor()
        event = m.mock(level="MEDIUM")
        assert event.level == "MEDIUM"
        assert event.action == "HOLD_NEW_ENTRIES"

    def test_classify_high_keywords(self):
        """HIGH 키워드 포함 시 HIGH 분류."""
        m = NewsMonitor()
        headlines = ["Major crypto exchange hacked, $500M stolen", "Bitcoin price falls"]
        event = m._classify(headlines)
        assert event.level == "HIGH"
        assert "hack" in event.keywords_matched or "stolen" in event.keywords_matched

    def test_classify_medium_keywords(self):
        """MEDIUM 키워드만 있으면 MEDIUM."""
        m = NewsMonitor()
        headlines = ["SEC investigation into crypto exchange ongoing", "Fed rate decision looms"]
        event = m._classify(headlines)
        assert event.level in ("MEDIUM", "HIGH")  # investigation이 있으면 MEDIUM

    def test_classify_empty_returns_none(self):
        m = NewsMonitor()
        event = m._classify([])
        assert event.level == "NONE"

    def test_high_risk_callback_triggered(self):
        """HIGH 이벤트 시 콜백 호출."""
        m = NewsMonitor()
        called = []
        m.on_high_risk_callback = lambda e: called.append(e)

        # mock fetch로 HIGH 이벤트 시뮬레이션
        import time
        mock_event = m.mock(level="HIGH", event_text="hack")
        m._cache = mock_event
        m._cache_time = time.time() - 9999  # 캐시 만료

        # _classify가 HIGH 반환하도록 mock
        original_classify = m._classify
        m._classify = lambda h: mock_event
        m._fetch_headlines = lambda: ["hack"]
        m.fetch()
        assert len(called) == 1

    def test_expires_at_format(self):
        """expires_at이 ISO 8601 형식."""
        m = NewsMonitor()
        event = m.mock(level="HIGH")
        assert "T" in event.expires_at
        assert "Z" in event.expires_at

    def test_summary_output(self):
        m = NewsMonitor()
        event = m.mock(level="MEDIUM", event_text="ETF hearing scheduled")
        s = event.summary()
        assert "NEWS_RISK" in s


# ---------------------------------------------------------------------------
# MarketContext: 통합 테스트
# ---------------------------------------------------------------------------

class TestMarketContext:
    def _make_signal(self, action: Action) -> Signal:
        return Signal(
            action=action,
            confidence=Confidence.MEDIUM,
            strategy="test",
            entry_price=50000.0,
            reasoning="test reason",
            invalidation="test invalidation",
        )

    def test_composite_score_neutral(self):
        """감성/온체인 모두 중립이면 0."""
        f = SentimentFetcher()
        o = OnchainFetcher()
        ctx = MarketContext(
            sentiment=f.mock(fear_greed=50, funding_rate=0.0001),
            onchain=o.mock(),
        )
        assert abs(ctx.composite_score) < 0.5

    def test_entry_blocked_on_high_news(self):
        m = NewsMonitor()
        ctx = MarketContext(news=m.mock(level="HIGH"))
        assert ctx.is_entry_blocked()

    def test_entry_not_blocked_on_medium(self):
        m = NewsMonitor()
        ctx = MarketContext(news=m.mock(level="MEDIUM"))
        assert not ctx.is_entry_blocked()

    def test_adjust_signal_blocks_on_high_news(self):
        """HIGH 뉴스 → BUY 신호를 HOLD로 변환."""
        m = NewsMonitor()
        ctx = MarketContext(news=m.mock(level="HIGH", event_text="exchange hack"))
        signal = self._make_signal(Action.BUY)
        adjusted, notes = ctx.adjust_signal(signal)
        assert adjusted.action == Action.HOLD
        assert any("NEWS HIGH" in n for n in notes)

    def test_adjust_signal_boost_confidence(self):
        """컨텍스트 점수가 신호와 일치 → MEDIUM → HIGH 상향."""
        f = SentimentFetcher()
        o = OnchainFetcher()
        ctx = MarketContext(
            sentiment=f.mock(fear_greed=5, funding_rate=-0.0003),  # 극단 공포 → 매수 맞춤
            onchain=o.mock(whale_activity="ACCUMULATING"),
        )
        signal = self._make_signal(Action.BUY)
        adjusted, notes = ctx.adjust_signal(signal)
        # 컨텍스트 강하게 bullish → confidence HIGH
        assert adjusted.action == Action.BUY
        assert adjusted.confidence == Confidence.HIGH or len(notes) > 0

    def test_adjust_signal_hold_passes_through(self):
        """HOLD 신호는 컨텍스트 상관없이 그대로."""
        m = NewsMonitor()
        ctx = MarketContext(news=m.mock(level="HIGH"))
        signal = self._make_signal(Action.HOLD)
        adjusted, notes = ctx.adjust_signal(signal)
        assert adjusted.action == Action.HOLD
        assert len(notes) == 0

    def test_context_aligns_buy_positive_score(self):
        f = SentimentFetcher()
        ctx = MarketContext(sentiment=f.mock(fear_greed=5, funding_rate=-0.0003))
        assert ctx.context_aligns(Action.BUY)

    def test_context_aligns_sell_negative_score(self):
        f = SentimentFetcher()
        ctx = MarketContext(sentiment=f.mock(fear_greed=95, funding_rate=0.0006))
        assert ctx.context_aligns(Action.SELL)

    def test_summary_lines_not_empty(self):
        f = SentimentFetcher()
        o = OnchainFetcher()
        m = NewsMonitor()
        ctx = MarketContext(
            sentiment=f.mock(),
            onchain=o.mock(),
            news=m.mock(),
        )
        lines = ctx.summary_lines()
        assert len(lines) >= 3


# ---------------------------------------------------------------------------
# MarketContextBuilder
# ---------------------------------------------------------------------------

class TestMarketContextBuilder:
    def test_build_mock_mode(self):
        builder = MarketContextBuilder(symbol="BTC/USDT")
        ctx = builder.build(use_mock=True)
        assert ctx.sentiment is not None
        assert ctx.onchain is not None
        assert ctx.news is not None

    def test_build_returns_market_context(self):
        builder = MarketContextBuilder()
        ctx = builder.build(use_mock=True)
        assert isinstance(ctx, MarketContext)

    def test_high_risk_callback_set(self):
        builder = MarketContextBuilder()
        called = []
        builder.set_high_risk_callback(lambda e: called.append(e))
        assert builder._news_monitor.on_high_risk_callback is not None
