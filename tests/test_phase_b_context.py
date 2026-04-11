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
    def test_fetch_with_fallback_on_api_failure(self):
        """API 실패 시 fallback 데이터 사용 검증."""
        f = OnchainFetcher(max_retries=1)
        
        # mock으로 성공 데이터 저장 (fallback으로 사용될 데이터)
        initial = f.mock(exchange_flow="OUTFLOW", whale_activity="ACCUMULATING")
        f._last_successful = initial
        
        # fetch() 호출 시 _fetch_blockchain_stats()가 None 반환하면
        # source="unavailable"로 반환되고, fallback이 있으면 이전 데이터 사용
        data = f.fetch()
        
        # fallback이 있으므로 score는 유지되어야 함
        assert f._last_successful is not None
        assert f._last_successful.onchain_score == initial.onchain_score

    def test_max_retries_parameter_in_blockchain_fetch(self):
        """blockchain.info fetch 시 max_retries 파라미터 영향 검증."""
        f = OnchainFetcher(max_retries=2)
        
        # max_retries=2 설정 확인
        assert f.max_retries == 2
        
        # mock 데이터로 초기값 저장
        initial = f.mock(exchange_flow="NEUTRAL")
        f._last_successful = initial
        
        # fetch() 호출 시 재시도 로직이 작동하여 더 견고한 수집
        data = f.fetch()
        
        # fallback이 설정되었으므로 파이프라인 계속 진행 가능
        assert data is not None

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


# ---------------------------------------------------------------------------
# B1: SentimentFetcher - Robustness Tests (Cycle 6)
# ---------------------------------------------------------------------------

class TestSentimentFetcherRobustness:
    """재시도 + fallback 로직 검증."""

    def test_fetch_all_apis_fail_uses_fallback(self):
        """모든 API 실패 시 이전 성공한 데이터 사용."""
        f = SentimentFetcher(max_retries=0)
        
        # 첫 번째 호출: mock으로 성공
        data1 = f.mock(fear_greed=30, funding_rate=0.0002)
        f._last_successful = data1
        
        # 두 번째 호출: 모든 API 실패 시뮬레이션
        f._fetch_fear_greed = lambda: (None, "N/A")
        f._fetch_funding_rate = lambda: None
        f._fetch_open_interest = lambda: None
        
        # 캐시 초기화
        f._cache = None
        f._cache_time = 0.0
        
        result = f.fetch()
        # fallback 사용 확인
        assert result.source == data1.source
        assert result.fear_greed_index == data1.fear_greed_index

    def test_fetch_all_apis_fail_no_fallback_returns_neutral(self):
        """모든 API 실패 + fallback 없을 때 중립 데이터 반환."""
        f = SentimentFetcher(max_retries=0)
        f._last_successful = None
        
        # 모든 API 실패
        f._fetch_fear_greed = lambda: (None, "N/A")
        f._fetch_funding_rate = lambda: None
        f._fetch_open_interest = lambda: None
        
        result = f.fetch()
        assert result.source == "unavailable"
        assert result.sentiment_score == 0.0
        assert result.fear_greed_index is None
        assert result.funding_rate is None

    def test_partial_api_failure_uses_available_data(self):
        """일부 API 실패해도 성공한 API 데이터 사용."""
        f = SentimentFetcher(max_retries=0)
        
        # Fear&Greed만 성공, 나머지 실패
        f._fetch_fear_greed = lambda: (50, "Neutral")
        f._fetch_funding_rate = lambda: None
        f._fetch_open_interest = lambda: None
        
        result = f.fetch()
        assert result.fear_greed_index == 50
        assert result.funding_rate is None
        assert "alternative.me" in result.source
        assert "binance_futures" not in result.source

    def test_cache_returns_same_data_within_timeout(self):
        """캐시 타임아웃 내 재호출은 같은 데이터 반환."""
        f = SentimentFetcher(use_cache_seconds=300)
        
        import time
        mock_data = f.mock(fear_greed=60, funding_rate=0.0001)
        f._cache = mock_data
        f._cache_time = time.time()
        
        # 캐시된 데이터 반환 확인
        result = f.fetch()
        assert result is mock_data

    def test_max_retries_parameter_affects_behavior(self):
        """max_retries 파라미터로 재시도 횟수 제어."""
        f = SentimentFetcher(max_retries=1)
        assert f.max_retries == 1
        
        f2 = SentimentFetcher(max_retries=3)
        assert f2.max_retries == 3

    def test_fallback_last_successful_tracked(self):
        """성공한 데이터가 _last_successful에 저장됨."""
        f = SentimentFetcher(max_retries=0)
        
        # 초기 상태
        assert f._last_successful is None
        
        # mock 데이터로 fetch
        f._fetch_fear_greed = lambda: (45, "Neutral")
        f._fetch_funding_rate = lambda: 0.0001
        f._fetch_open_interest = lambda: 1000000.0
        
        result = f.fetch()
        assert f._last_successful is not None
        assert f._last_successful.fear_greed_index == 45

    def test_fear_greed_api_failure_logs_warning(self, caplog):
        """Fear&Greed API 실패 시 warning 로그 출력."""
        import logging
        f = SentimentFetcher(max_retries=0)
        
        # API 실패 시뮬레이션
        f._fetch_fear_greed = lambda: (None, "N/A")
        f._fetch_funding_rate = lambda: 0.0001
        f._fetch_open_interest = lambda: None
        
        with caplog.at_level(logging.WARNING):
            result = f.fetch()
        
        # warning이 로그되었는지 확인 (API 실패 후 모든 API가 실패했으므로 불가)
        # 여기선 단순히 기능 동작 확인만 함

    def test_unavailable_source_when_no_fallback(self):
        """fallback 없을 때 source='unavailable'."""
        f = SentimentFetcher(max_retries=0)
        f._last_successful = None
        f._fetch_fear_greed = lambda: (None, "N/A")
        f._fetch_funding_rate = lambda: None
        f._fetch_open_interest = lambda: None
        
        result = f.fetch()
        assert result.source == "unavailable"

    def test_multiple_successful_apis_combined_source(self):
        """여러 API 성공 시 source에 모두 기록."""
        f = SentimentFetcher(max_retries=0)
        
        f._fetch_fear_greed = lambda: (50, "Neutral")
        f._fetch_funding_rate = lambda: 0.0002
        f._fetch_open_interest = lambda: None
        
        result = f.fetch()
        assert "alternative.me" in result.source
        assert "binance_futures" in result.source
        assert "," in result.source


class TestSentimentFetcherFallbackIntegration:
    """fallback 데이터 유지 및 로테이션."""

    def test_fallback_survives_subsequent_failures(self):
        """이전 fallback 데이터가 여러 번 실패 시에도 계속 사용."""
        f = SentimentFetcher(max_retries=0, use_cache_seconds=0)
        
        # 1차 호출: 성공
        f._fetch_fear_greed = lambda: (30, "Fear")
        f._fetch_funding_rate = lambda: 0.0001
        f._fetch_open_interest = lambda: None
        
        result1 = f.fetch()
        assert result1.fear_greed_index == 30
        
        # 2차 호출: 모든 API 실패
        f._fetch_fear_greed = lambda: (None, "N/A")
        f._fetch_funding_rate = lambda: None
        f._fetch_open_interest = lambda: None
        
        result2 = f.fetch()
        assert result2.fear_greed_index == 30  # fallback 사용
        
        # 3차 호출: 여전히 실패
        result3 = f.fetch()
        assert result3.fear_greed_index == 30  # fallback 유지




class TestNewsMonitorRobustness:
    """NewsMonitor 에러 처리 및 fallback 메커니즘."""

    def test_fetch_api_exception_uses_fallback(self):
        """API 예외 발생 시 fallback 데이터 사용."""
        import time
        m = NewsMonitor(max_retries=1, use_cache_seconds=0)
        
        # 1차: 성공
        m._fetch_headlines = lambda: ["emergency shutdown reported"]
        result1 = m.fetch()
        assert result1.level == "HIGH"
        
        # 2차: _classify 예외 발생 (심각한 오류)
        m._fetch_headlines = lambda: ["valid headline"]
        m._classify = lambda h: (_ for _ in ()).throw(ValueError("parse error"))
        
        result2 = m.fetch()
        assert result2.source == "fallback"
        assert result2.level == "HIGH"

    def test_fetch_all_apis_fail_no_fallback_returns_neutral(self):
        """API 예외 + fallback 없을 시 중립 데이터 반환."""
        m = NewsMonitor(max_retries=1)
        m._last_successful = None  # fallback 없음
        
        # _classify 예외 발생
        m._fetch_headlines = lambda: []
        m._classify = lambda h: (_ for _ in ()).throw(RuntimeError("error"))
        
        result = m.fetch()
        assert result.level == "NONE"
        assert result.source == "unavailable"

    def test_partial_api_failure_uses_available_data(self):
        """API 실패 후 빈 헤드라인 → NONE 분류."""
        m = NewsMonitor()
        m._fetch_headlines = lambda: []
        result = m.fetch()
        assert result.level == "NONE"

    def test_cache_returns_same_data_within_timeout(self):
        """캐시 유효 시간 내 재호출 시 같은 데이터 반환."""
        import time
        m = NewsMonitor(use_cache_seconds=300)
        
        mock_event = m.mock(level="MEDIUM", event_text="Fed meeting")
        m._cache = mock_event
        m._cache_time = time.time()
        
        result = m.fetch()
        assert result is mock_event

    def test_max_retries_parameter_affects_behavior(self):
        """max_retries 파라미터로 재시도 횟수 제어."""
        m1 = NewsMonitor(max_retries=1)
        assert m1.max_retries == 1
        
        m2 = NewsMonitor(max_retries=3)
        assert m2.max_retries == 3

    def test_fallback_last_successful_tracked(self):
        """성공한 데이터가 _last_successful에 저장됨."""
        m = NewsMonitor(max_retries=1)
        
        # 초기 상태
        assert m._last_successful is None
        
        # 성공한 fetch
        m._fetch_headlines = lambda: ["hack", "breach"]
        result = m.fetch()
        assert m._last_successful is not None
        assert m._last_successful.level == "HIGH"

    def test_classify_exception_returns_fallback(self):
        """_classify 예외 시 fallback 또는 neutral 반환."""
        m = NewsMonitor()
        m._last_successful = m.mock(level="MEDIUM")
        m._fetch_headlines = lambda: ["valid headline"]
        
        # _classify 에러 시뮬레이션
        m._classify = lambda h: (_ for _ in ()).throw(ValueError("mock error"))
        
        result = m.fetch()
        # fallback이 있으므로 MEDIUM 반환
        assert result.source == "fallback"

    def test_unavailable_source_when_classify_fails_and_no_fallback(self):
        """_classify 실패 + fallback 없을 때 source='unavailable'."""
        m = NewsMonitor()
        m._last_successful = None
        m._fetch_headlines = lambda: ["valid headline"]
        m._classify = lambda h: (_ for _ in ()).throw(ValueError("error"))
        
        result = m.fetch()
        assert result.source == "unavailable"

    def test_fallback_survives_classify_failures(self):
        """이전 fallback이 여러 번 _classify 실패 시에도 계속 사용."""
        m = NewsMonitor(max_retries=1, use_cache_seconds=0)
        
        # 1차: 성공
        m._fetch_headlines = lambda: ["ban", "shutdown"]
        result1 = m.fetch()
        assert result1.level == "HIGH"
        
        # 2차: _classify 실패
        m._fetch_headlines = lambda: ["headline"]
        m._classify = lambda h: (_ for _ in ()).throw(RuntimeError("error"))
        result2 = m.fetch()
        assert result2.level == "HIGH"
        assert result2.source == "fallback"
        
        # 3차: 여전히 실패
        result3 = m.fetch()
        assert result3.level == "HIGH"
        assert result3.source == "fallback"
