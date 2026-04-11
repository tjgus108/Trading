"""
SentimentFetcher 일관성 테스트: 동일 입력 → 동일 출력.
각 소스별 개별 실패 시나리오.
"""

import unittest
from unittest.mock import patch, MagicMock
import time
import json
from src.data.sentiment import SentimentFetcher, SentimentData


class TestSentimentConsistency(unittest.TestCase):
    """동일 입력 → 동일 출력 일관성 테스트"""

    def setUp(self):
        self.fetcher = SentimentFetcher(symbol="BTC/USDT", use_cache_seconds=300, max_retries=0)

    def test_mock_consistency_same_input(self):
        """mock()은 동일 입력 → 동일 출력"""
        result1 = self.fetcher.mock(fear_greed=50, funding_rate=0.0001)
        result2 = self.fetcher.mock(fear_greed=50, funding_rate=0.0001)
        
        self.assertEqual(result1.fear_greed_index, result2.fear_greed_index)
        self.assertEqual(result1.sentiment_score, result2.sentiment_score)
        self.assertEqual(result1.funding_rate, result2.funding_rate)
        self.assertEqual(result1.fear_greed_label, result2.fear_greed_label)

    def test_compute_score_consistency(self):
        """_compute_score는 동일 입력 → 동일 출력"""
        score1 = self.fetcher._compute_score(fg=50, fr=0.0001)
        score2 = self.fetcher._compute_score(fg=50, fr=0.0001)
        self.assertEqual(score1, score2)

        score3 = self.fetcher._compute_score(fg=10, fr=-0.0005)
        score4 = self.fetcher._compute_score(fg=10, fr=-0.0005)
        self.assertEqual(score3, score4)

    def test_fg_label_consistency(self):
        """_fg_label은 동일 입력 → 동일 출력"""
        label1 = self.fetcher._fg_label(15)
        label2 = self.fetcher._fg_label(15)
        self.assertEqual(label1, label2)
        self.assertEqual(label1, "Extreme Fear")

        label3 = self.fetcher._fg_label(85)
        label4 = self.fetcher._fg_label(85)
        self.assertEqual(label3, label4)
        self.assertEqual(label3, "Extreme Greed")

    @patch('urllib.request.urlopen')
    def test_cache_consistency(self, mock_urlopen):
        """캐시 내 재호출은 동일 데이터 반환"""
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "data": [{
                "value": "50",
                "value_classification": "Neutral"
            }]
        }).encode()
        mock_resp.__enter__.return_value = mock_resp
        mock_resp.__exit__.return_value = None
        mock_urlopen.return_value = mock_resp

        result1 = self.fetcher.fetch()
        result2 = self.fetcher.fetch()  # 캐시 재사용
        
        self.assertEqual(result1.fear_greed_index, result2.fear_greed_index)
        self.assertEqual(result1.sentiment_score, result2.sentiment_score)


class TestSentimentFearGreedFailure(unittest.TestCase):
    """Fear & Greed API 개별 실패 시나리오"""

    def setUp(self):
        self.fetcher = SentimentFetcher(symbol="BTC/USDT", use_cache_seconds=0, max_retries=0)

    @patch('urllib.request.urlopen')
    def test_fear_greed_api_failure_returns_none(self, mock_urlopen):
        """Fear & Greed API 실패 → fear_greed_index=None"""
        mock_urlopen.side_effect = ConnectionError("API timeout")
        
        result = self.fetcher.fetch()
        
        self.assertIsNone(result.fear_greed_index)
        self.assertEqual(result.fear_greed_label, "N/A")

    @patch('urllib.request.urlopen')
    def test_fear_greed_invalid_json_failure(self, mock_urlopen):
        """Fear & Greed API 잘못된 JSON 반환 → fear_greed_index=None"""
        mock_resp = MagicMock()
        mock_resp.read.return_value = b"invalid json {{"
        mock_resp.__enter__.return_value = mock_resp
        mock_resp.__exit__.return_value = None
        mock_urlopen.return_value = mock_resp
        
        result = self.fetcher.fetch()
        
        self.assertIsNone(result.fear_greed_index)
        self.assertEqual(result.fear_greed_label, "N/A")


class TestSentimentFundingRateFailure(unittest.TestCase):
    """펀딩비 API 개별 실패 시나리오"""

    def setUp(self):
        self.fetcher = SentimentFetcher(symbol="BTC/USDT", use_cache_seconds=0, max_retries=0)

    @patch('urllib.request.urlopen')
    def test_funding_rate_api_failure_returns_none(self, mock_urlopen):
        """펀딩비 API 실패 → funding_rate=None"""
        def side_effect(req, timeout=None):
            if "fng" in req.full_url:
                resp = MagicMock()
                resp.read.return_value = json.dumps({
                    "data": [{"value": "50", "value_classification": "Neutral"}]
                }).encode()
                resp.__enter__.return_value = resp
                resp.__exit__.return_value = None
                return resp
            else:
                raise ConnectionError("Binance API timeout")
        
        mock_urlopen.side_effect = side_effect
        
        result = self.fetcher.fetch()
        
        self.assertEqual(result.fear_greed_index, 50)
        self.assertIsNone(result.funding_rate)
        self.assertEqual(result.source, "alternative.me")

    @patch('urllib.request.urlopen')
    def test_funding_rate_missing_field(self, mock_urlopen):
        """펀딩비 API 필드 누락 → funding_rate=0"""
        def side_effect(req, timeout=None):
            if "fng" in req.full_url:
                resp = MagicMock()
                resp.read.return_value = json.dumps({
                    "data": [{"value": "50", "value_classification": "Neutral"}]
                }).encode()
                resp.__enter__.return_value = resp
                resp.__exit__.return_value = None
                return resp
            else:
                resp = MagicMock()
                resp.read.return_value = json.dumps({}).encode()  # lastFundingRate 없음
                resp.__enter__.return_value = resp
                resp.__exit__.return_value = None
                return resp
        
        mock_urlopen.side_effect = side_effect
        
        result = self.fetcher.fetch()
        
        self.assertEqual(result.fear_greed_index, 50)
        self.assertEqual(result.funding_rate, 0.0)  # .get() 기본값


class TestSentimentOpenInterestFailure(unittest.TestCase):
    """Open Interest API 개별 실패 시나리오"""

    def setUp(self):
        self.fetcher = SentimentFetcher(symbol="BTC/USDT", use_cache_seconds=0, max_retries=0)

    @patch('urllib.request.urlopen')
    def test_open_interest_api_failure_returns_none(self, mock_urlopen):
        """Open Interest API 실패 → open_interest=None"""
        call_count = [0]
        
        def side_effect(req, timeout=None):
            call_count[0] += 1
            if "fng" in req.full_url:
                resp = MagicMock()
                resp.read.return_value = json.dumps({
                    "data": [{"value": "50", "value_classification": "Neutral"}]
                }).encode()
                resp.__enter__.return_value = resp
                resp.__exit__.return_value = None
                return resp
            elif "premiumIndex" in req.full_url:
                resp = MagicMock()
                resp.read.return_value = json.dumps({"lastFundingRate": 0.0001}).encode()
                resp.__enter__.return_value = resp
                resp.__exit__.return_value = None
                return resp
            else:  # openInterest
                raise ConnectionError("Open Interest API timeout")
        
        mock_urlopen.side_effect = side_effect
        
        result = self.fetcher.fetch()
        
        self.assertEqual(result.fear_greed_index, 50)
        self.assertEqual(result.funding_rate, 0.0001)
        self.assertIsNone(result.open_interest)


class TestSentimentAllSourcesFailure(unittest.TestCase):
    """모든 소스 실패 → fallback/neutral"""

    def setUp(self):
        self.fetcher = SentimentFetcher(symbol="BTC/USDT", use_cache_seconds=0, max_retries=0)

    @patch('urllib.request.urlopen')
    def test_all_apis_fail_returns_neutral(self, mock_urlopen):
        """모든 API 실패 → neutral 데이터"""
        mock_urlopen.side_effect = ConnectionError("All APIs timeout")
        
        result = self.fetcher.fetch()
        
        self.assertIsNone(result.fear_greed_index)
        self.assertIsNone(result.funding_rate)
        self.assertEqual(result.sentiment_score, 0.0)
        self.assertEqual(result.source, "unavailable")

    @patch('urllib.request.urlopen')
    def test_all_apis_fail_uses_fallback(self, mock_urlopen):
        """모든 API 실패 시 fallback 데이터 사용"""
        # 첫 호출: 성공
        success_resp = MagicMock()
        success_resp.read.return_value = json.dumps({
            "data": [{"value": "30", "value_classification": "Fear"}]
        }).encode()
        success_resp.__enter__.return_value = success_resp
        success_resp.__exit__.return_value = None
        
        # 두 번째 호출: 실패
        fail_side_effects = [
            ConnectionError("FG timeout"),
            ConnectionError("Funding timeout"),
            ConnectionError("OI timeout"),
        ]
        
        call_order = [0]
        def side_effect(req, timeout=None):
            if call_order[0] == 0:
                call_order[0] += 1
                return success_resp
            else:
                raise fail_side_effects[call_order[0] % len(fail_side_effects)]
        
        mock_urlopen.side_effect = side_effect
        
        # 첫 번째 fetch: 성공
        result1 = self.fetcher.fetch()
        self.assertEqual(result1.fear_greed_index, 30)
        
        # 캐시 무효화
        self.fetcher._cache_time = 0
        self.fetcher._cache = None
        
        # 두 번째 fetch: 실패하지만 fallback 사용
        mock_urlopen.side_effect = ConnectionError("All fail")
        result2 = self.fetcher.fetch()
        
        # fallback 데이터 확인
        self.assertEqual(result2.fear_greed_index, 30)
        self.assertEqual(result2.fear_greed_label, "Fear")


if __name__ == "__main__":
    unittest.main()
