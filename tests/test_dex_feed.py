"""DEX Price Feed 단위 테스트 (재시도, fallback 포함)."""

import time
from unittest.mock import MagicMock, patch

import pytest

from src.data.dex_feed import DEXPriceFeed, SYMBOL_MAP


class TestDEXPriceFeedBasic:
    """기본 기능: mock, get_price, get_spread"""

    def test_mock_creation(self):
        """mock으로 생성한 피드는 즉시 가격 반환"""
        feed = DEXPriceFeed.mock("BTC", 50000.0)
        assert feed.get_price("BTC") == 50000.0

    def test_mock_symbol_price(self):
        """mock으로 여러 심볼 설정"""
        feed = DEXPriceFeed.mock("ETH", 3000.0)
        assert feed.get_price("ETH") == 3000.0

    def test_get_price_unknown_symbol(self):
        """알려지지 않은 심볼은 0.0 반환"""
        feed = DEXPriceFeed()
        price = feed.get_price("UNKNOWN")
        assert price == 0.0

    def test_get_spread_both_zero(self):
        """dex_price 또는 cex_price가 0이면 spread_pct=0, arb_direction=NONE"""
        feed = DEXPriceFeed.mock("BTC", 0.0)
        result = feed.get_spread(cex_price=50000.0, symbol="BTC")
        assert result["spread_pct"] == 0.0
        assert result["arb_direction"] == "NONE"

    def test_get_spread_sell_dex(self):
        """spread_pct > 0.3% → SELL_DEX"""
        feed = DEXPriceFeed.mock("BTC", 50200.0)
        result = feed.get_spread(cex_price=50000.0, symbol="BTC")
        assert result["arb_direction"] == "SELL_DEX"
        assert result["spread_pct"] > 0.3

    def test_get_spread_buy_dex(self):
        """spread_pct < -0.3% → BUY_DEX"""
        feed = DEXPriceFeed.mock("BTC", 49800.0)
        result = feed.get_spread(cex_price=50000.0, symbol="BTC")
        assert result["arb_direction"] == "BUY_DEX"
        assert result["spread_pct"] < -0.3

    def test_get_spread_none(self):
        """spread_pct in [-0.3%, 0.3%] → NONE"""
        feed = DEXPriceFeed.mock("BTC", 50000.0)
        result = feed.get_spread(cex_price=50000.0, symbol="BTC")
        assert result["arb_direction"] == "NONE"
        assert result["spread_pct"] == 0.0


class TestDEXPriceFeedRetry:
    """재시도 로직 테스트"""

    def test_retry_success_on_second_attempt(self):
        """API가 첫 시도는 실패, 두 번째는 성공"""
        feed = DEXPriceFeed(max_retries=2)

        with patch("src.data.dex_feed.requests.get") as mock_get:
            # 첫 시도: 실패, 두 번째: 성공
            mock_get.side_effect = [
                Exception("Timeout"),
                MagicMock(
                    json=lambda: {"bitcoin": {"usd": 50000.0}},
                    raise_for_status=lambda: None,
                ),
            ]

            with patch("src.data.dex_feed.time.sleep"):  # sleep 무시
                price = feed.get_price("BTC")

        assert price == 50000.0

    def test_retry_all_attempts_fail_fallback(self):
        """모든 재시도가 실패 → fallback 사용"""
        feed = DEXPriceFeed(max_retries=2)

        # 첫 호출: 성공 (fallback 저장)
        with patch("src.data.dex_feed.requests.get") as mock_get:
            mock_get.return_value = MagicMock(
                json=lambda: {"bitcoin": {"usd": 50000.0}},
                raise_for_status=lambda: None,
            )
            price1 = feed.get_price("BTC")
            assert price1 == 50000.0

        # 두 번째 호출: 모든 재시도 실패 → fallback 반환
        with patch("src.data.dex_feed.requests.get") as mock_get:
            mock_get.side_effect = Exception("Network error")

            with patch("src.data.dex_feed.time.sleep"):
                price2 = feed.get_price("BTC")

        assert price2 == 50000.0  # fallback

    def test_retry_no_fallback_returns_zero(self):
        """fallback도 없고 모든 재시도 실패 → 0.0"""
        feed = DEXPriceFeed(max_retries=2)

        with patch("src.data.dex_feed.requests.get") as mock_get:
            mock_get.side_effect = Exception("API error")

            with patch("src.data.dex_feed.time.sleep"):
                price = feed.get_price("BTC")

        assert price == 0.0

    def test_retry_backoff_timing(self):
        """exponential backoff 타이밍: 1s, 2s"""
        feed = DEXPriceFeed(max_retries=2)

        with patch("src.data.dex_feed.requests.get") as mock_get:
            mock_get.side_effect = [
                Exception("Fail 1"),
                Exception("Fail 2"),
                Exception("Fail 3"),
            ]

            with patch("src.data.dex_feed.time.sleep") as mock_sleep:
                feed.get_price("BTC")

        # 2번의 재시도 → sleep(1), sleep(2) 호출
        assert mock_sleep.call_count == 2
        mock_sleep.assert_any_call(1)
        mock_sleep.assert_any_call(2)


class TestDEXPriceFeedCache:
    """캐시 동작 테스트"""

    def test_cache_ttl_valid(self):
        """캐시 TTL 내에서 재호출"""
        feed = DEXPriceFeed()

        with patch("src.data.dex_feed.requests.get") as mock_get:
            mock_get.return_value = MagicMock(
                json=lambda: {"bitcoin": {"usd": 50000.0}},
                raise_for_status=lambda: None,
            )
            price1 = feed.get_price("BTC")
            price2 = feed.get_price("BTC")

        assert price1 == price2 == 50000.0
        # 한 번만 호출 (캐시 때문)
        assert mock_get.call_count == 1

    def test_cache_ttl_expired(self):
        """캐시 만료 후 재호출"""
        feed = DEXPriceFeed()

        with patch("src.data.dex_feed.time.time") as mock_time:
            with patch("src.data.dex_feed.requests.get") as mock_get:
                mock_time.return_value = 0.0
                mock_get.return_value = MagicMock(
                    json=lambda: {"bitcoin": {"usd": 50000.0}},
                    raise_for_status=lambda: None,
                )
                price1 = feed.get_price("BTC")

                # 60초 후 (TTL=60)
                mock_time.return_value = 61.0
                mock_get.return_value = MagicMock(
                    json=lambda: {"bitcoin": {"usd": 55000.0}},
                    raise_for_status=lambda: None,
                )
                price2 = feed.get_price("BTC")

        assert price1 == 50000.0
        assert price2 == 55000.0
        # 캐시 만료되어 2번 호출
        assert mock_get.call_count == 2


class TestDEXPriceFeedSymbols:
    """심볼 매핑 테스트"""

    def test_btc_variants(self):
        """BTC, BTC/USDT 모두 bitcoin으로 매핑"""
        feed = DEXPriceFeed()

        with patch("src.data.dex_feed.requests.get") as mock_get:
            mock_get.return_value = MagicMock(
                json=lambda: {"bitcoin": {"usd": 50000.0}},
                raise_for_status=lambda: None,
            )

            price1 = feed.get_price("BTC")
            price2 = feed.get_price("BTC/USDT")

        assert price1 == 50000.0
        assert price2 == 50000.0

    def test_eth_variants(self):
        """ETH, ETH/USDT 모두 ethereum으로 매핑"""
        feed = DEXPriceFeed()

        with patch("src.data.dex_feed.requests.get") as mock_get:
            mock_get.return_value = MagicMock(
                json=lambda: {"ethereum": {"usd": 3000.0}},
                raise_for_status=lambda: None,
            )

            price1 = feed.get_price("ETH")
            price2 = feed.get_price("ETH/USDT")

        assert price1 == 3000.0
        assert price2 == 3000.0
