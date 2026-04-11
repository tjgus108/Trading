"""
OnchainFetcher 동일 입력 → 동일 출력 일관성 검증 테스트.
"""

import pytest
from src.data.onchain import OnchainFetcher, OnchainData


class TestOnchainConsistency:
    """동일한 mock 입력으로 동일한 출력 검증."""

    def test_mock_consistency_same_call_twice(self):
        """동일한 mock 호출 2회 → 동일한 결과."""
        fetcher = OnchainFetcher()
        
        # 첫 번째 호출
        result1 = fetcher.mock(
            exchange_flow="INFLOW_SPIKE",
            whale_activity="ACCUMULATING",
            nvt_signal="UNDERVALUED",
        )
        
        # 두 번째 호출 (동일한 파라미터)
        result2 = fetcher.mock(
            exchange_flow="INFLOW_SPIKE",
            whale_activity="ACCUMULATING",
            nvt_signal="UNDERVALUED",
        )
        
        # 모든 필드 검증
        assert result1.exchange_flow == result2.exchange_flow
        assert result1.whale_activity == result2.whale_activity
        assert result1.nvt_signal == result2.nvt_signal
        assert result1.onchain_score == result2.onchain_score
        assert result1.source == result2.source
        assert result1.hash_rate_change == result2.hash_rate_change
        assert result1.tx_volume_usd == result2.tx_volume_usd

    def test_mock_score_consistency(self):
        """동일한 신호 조합 → 동일한 score 계산."""
        fetcher = OnchainFetcher()
        
        # 테스트 케이스: 각 신호 조합
        test_cases = [
            ("NEUTRAL", "NEUTRAL", "FAIR"),
            ("INFLOW_SPIKE", "ACCUMULATING", "UNDERVALUED"),
            ("OUTFLOW", "DISTRIBUTING", "OVERVALUED"),
            ("NEUTRAL", "ACCUMULATING", "FAIR"),
        ]
        
        for exchange, whale, nvt in test_cases:
            result1 = fetcher.mock(
                exchange_flow=exchange,
                whale_activity=whale,
                nvt_signal=nvt,
            )
            result2 = fetcher.mock(
                exchange_flow=exchange,
                whale_activity=whale,
                nvt_signal=nvt,
            )
            
            # score 값이 일관성 있게 계산되는지 검증
            assert result1.onchain_score == result2.onchain_score, \
                f"Score mismatch for {exchange}/{whale}/{nvt}: {result1.onchain_score} vs {result2.onchain_score}"

    def test_score_bounds(self):
        """score가 항상 [-3.0, +3.0] 범위 내."""
        fetcher = OnchainFetcher()
        
        # 극단적 조합들
        extreme_cases = [
            ("INFLOW_SPIKE", "DISTRIBUTING", "OVERVALUED"),  # 최악
            ("OUTFLOW", "ACCUMULATING", "UNDERVALUED"),      # 최고
        ]
        
        for exchange, whale, nvt in extreme_cases:
            result = fetcher.mock(
                exchange_flow=exchange,
                whale_activity=whale,
                nvt_signal=nvt,
            )
            assert -3.0 <= result.onchain_score <= 3.0, \
                f"Score {result.onchain_score} out of bounds"


class TestOnchainCacheTTL:
    """TTL 캐시 동작 검증."""

    def test_cache_initialized(self):
        """캐시 초기화: _cache=None, _cache_time=0."""
        fetcher = OnchainFetcher(use_cache_seconds=600)
        assert fetcher._cache is None, "캐시 초기값 검증 실패"
        assert fetcher._cache_time == 0.0, "캐시 시간 초기값 검증 실패"

    def test_cache_ttl_parameter(self):
        """use_cache_seconds 파라미터 동작."""
        fetcher1 = OnchainFetcher(use_cache_seconds=100)
        assert fetcher1.use_cache_seconds == 100
        
        fetcher2 = OnchainFetcher(use_cache_seconds=1)
        assert fetcher2.use_cache_seconds == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
