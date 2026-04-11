"""
B2. OnchainFetcher: 온체인 데이터 수집.

데이터 소스:
  - blockchain.com REST API (무료, BTC 네트워크 기본 지표)
  - Glassnode (GLASSNODE_API_KEY 있을 때)
  - 연결 실패 시 graceful degradation: fallback 또는 중립 데이터 반환

onchain-agent가 이 모듈을 사용한다.

신호 해석:
  exchange_inflow_spike → 매도 경계 (거래소 입금 급증)
  whale_accumulation   → 매수 신호
  nvt < 65             → 저평가
  nvt > 95             → 과열
"""

import json
import logging
import os
import time
import urllib.request
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)

BLOCKCHAIN_STATS_URL = "https://api.blockchain.info/stats"
_FETCH_TIMEOUT = 8


@dataclass
class OnchainData:
    """B2 온체인 신호 집계."""
    exchange_flow: str          # "INFLOW_SPIKE" | "OUTFLOW" | "NEUTRAL"
    whale_activity: str         # "ACCUMULATING" | "DISTRIBUTING" | "NEUTRAL"
    nvt_signal: str             # "UNDERVALUED" | "FAIR" | "OVERVALUED" | "N/A"
    hash_rate_change: Optional[float]   # 24h 해시레이트 변화율 (%)
    tx_volume_usd: Optional[float]      # 24h 거래량 USD
    onchain_score: float        # [-3, +3]
    source: str

    def summary(self) -> str:
        return (
            f"ONCHAIN: flow={self.exchange_flow} whale={self.whale_activity} "
            f"nvt={self.nvt_signal} score={self.onchain_score:+.1f} src={self.source}"
        )


class OnchainFetcher:
    """
    온체인 데이터 수집기 (재시도 + fallback 지원).

    fetch()로 OnchainData 반환.
    - API 성공 시: 실제 데이터 반환
    - 일부 API 실패: 성공한 API 데이터만 사용
    - 모든 API 실패: fallback(이전 성공 데이터) 또는 중립 데이터 반환
    
    파이프라인 블록 절대 금지.
    """

    def __init__(self, use_cache_seconds: int = 600, max_retries: int = 2):
        self.use_cache_seconds = use_cache_seconds
        self.max_retries = max_retries  # 각 API별 최대 재시도 횟수
        self._glassnode_key = os.environ.get("GLASSNODE_API_KEY")
        self._cache: Optional[OnchainData] = None
        self._cache_time: float = 0.0
        self._last_successful: Optional[OnchainData] = None  # 이전 성공한 데이터

    def fetch(self) -> OnchainData:
        """최신 온체인 데이터 반환. cache_seconds 내 재호출 시 캐시 반환.
        
        모든 API 실패 시:
        1. 이전 성공한 데이터 반환 (fallback)
        2. 그것도 없으면 중립 데이터 반환 (score=0)
        """
        now = time.time()
        if self._cache and (now - self._cache_time) < self.use_cache_seconds:
            return self._cache

        stats = self._fetch_blockchain_stats()
        data = self._analyze(stats)
        
        # blockchain.info 성공했으면 데이터 저장
        if stats is not None or data.source != "unavailable":
            self._last_successful = data
        else:
            # 모든 API 실패 - fallback 사용
            if self._last_successful:
                logger.warning("All onchain APIs failed, using fallback data from %s", self._last_successful.source)
                data = self._last_successful
            else:
                logger.warning("All onchain APIs failed, no fallback available. Returning neutral.")
        
        self._cache = data
        self._cache_time = now
        logger.info(data.summary())
        return data

    def mock(
        self,
        exchange_flow: str = "NEUTRAL",
        whale_activity: str = "NEUTRAL",
        nvt_signal: str = "FAIR",
    ) -> OnchainData:
        """테스트/데모용 mock."""
        score = self._score_from_fields(exchange_flow, whale_activity, nvt_signal)
        return OnchainData(
            exchange_flow=exchange_flow,
            whale_activity=whale_activity,
            nvt_signal=nvt_signal,
            hash_rate_change=None,
            tx_volume_usd=None,
            onchain_score=score,
            source="mock",
        )

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _fetch_blockchain_stats(self) -> Optional[dict]:
        """blockchain.info API 조회 (재시도 포함)."""
        for attempt in range(self.max_retries + 1):
            try:
                req = urllib.request.Request(
                    BLOCKCHAIN_STATS_URL,
                    headers={"User-Agent": "TradingBot/1.0"},
                )
                with urllib.request.urlopen(req, timeout=_FETCH_TIMEOUT) as resp:
                    return json.loads(resp.read())
            except Exception as e:
                if attempt < self.max_retries:
                    logger.debug("blockchain.info fetch attempt %d/%d failed: %s", attempt + 1, self.max_retries + 1, e)
                    time.sleep(0.5 * (2 ** attempt))  # exponential backoff: 0.5s, 1s, 2s
                else:
                    logger.warning("blockchain.info fetch failed after %d attempts: %s", self.max_retries + 1, e)
        return None

    def _analyze(self, stats: Optional[dict]) -> OnchainData:
        """blockchain.info 데이터 분석 + Glassnode 보충."""
        if stats is None:
            return OnchainData(
                exchange_flow="NEUTRAL",
                whale_activity="NEUTRAL",
                nvt_signal="N/A",
                hash_rate_change=None,
                tx_volume_usd=None,
                onchain_score=0.0,
                source="unavailable",
            )

        # blockchain.com API에서 사용 가능한 지표 파싱
        # estimated_transaction_volume_usd: 24h 추정 거래량
        tx_vol = stats.get("estimated_transaction_volume_usd")
        hash_rate = stats.get("hash_rate")  # TH/s
        n_tx = stats.get("n_transactions_total")
        market_cap = stats.get("market_cap_usd")

        # NVT proxy (network value to transactions ratio)
        # NVT = market_cap / tx_vol_30d_avg (여기선 단일 일자만 있으므로 proxy)
        nvt_signal = "N/A"
        if tx_vol and market_cap and tx_vol > 0:
            nvt_proxy = market_cap / tx_vol
            if nvt_proxy < 50:
                nvt_signal = "UNDERVALUED"
            elif nvt_proxy > 150:
                nvt_signal = "OVERVALUED"
            else:
                nvt_signal = "FAIR"

        # 해시레이트 변화 (단일 데이터 포인트 → 변화율 추정 불가, N/A로)
        hash_rate_change = None

        # Exchange flow proxy: 거래량 대비 시장 규모로 추정
        # (실제 거래소 inflow/outflow은 Glassnode 유료 데이터)
        exchange_flow = "NEUTRAL"
        whale_activity = "NEUTRAL"

        # Glassnode 키 있으면 더 정확한 데이터
        if self._glassnode_key:
            exchange_flow, whale_activity = self._fetch_glassnode_signals()

        score = self._score_from_fields(exchange_flow, whale_activity, nvt_signal)

        return OnchainData(
            exchange_flow=exchange_flow,
            whale_activity=whale_activity,
            nvt_signal=nvt_signal,
            hash_rate_change=hash_rate_change,
            tx_volume_usd=tx_vol,
            onchain_score=score,
            source="blockchain.info" + ("+glassnode" if self._glassnode_key else ""),
        )

    def _fetch_glassnode_signals(self) -> tuple[str, str]:
        """Glassnode API로 exchange flow + whale 데이터 조회 (부분 실패 허용)."""
        try:
            base = "https://api.glassnode.com/v1/metrics"
            headers = {"User-Agent": "TradingBot/1.0"}

            def _get_with_retry(endpoint: str) -> Optional[dict]:
                """개별 엔드포인트 조회 (재시도 포함)."""
                for attempt in range(self.max_retries + 1):
                    try:
                        url = f"{base}/{endpoint}?a=BTC&api_key={self._glassnode_key}&i=24h&limit=2"
                        req = urllib.request.Request(url, headers=headers)
                        with urllib.request.urlopen(req, timeout=_FETCH_TIMEOUT) as resp:
                            data = json.loads(resp.read())
                        return data[-1] if data else None
                    except Exception as e:
                        if attempt < self.max_retries:
                            logger.debug("Glassnode %s attempt %d/%d failed: %s", endpoint, attempt + 1, self.max_retries + 1, e)
                            time.sleep(0.5 * (2 ** attempt))
                        else:
                            logger.debug("Glassnode %s failed after %d attempts: %s", endpoint, self.max_retries + 1, e)
                return None

            # exchange_net_position_change: 양수 = 유입(매도 신호), 음수 = 유출(매수 신호)
            net_pos = _get_with_retry("distribution/exchange_net_position_change")
            exchange_flow = "NEUTRAL"
            if net_pos and "v" in net_pos:
                v = net_pos["v"]
                if v > 5000:
                    exchange_flow = "INFLOW_SPIKE"
                elif v < -5000:
                    exchange_flow = "OUTFLOW"

            # supply_held_by_whales (1000+ BTC 주소)
            whale_supply = _get_with_retry("supply/supply_held_by_whales")
            whale_activity = "NEUTRAL"
            # 단일 포인트만 있어 변화 감지 어려움 → NEUTRAL 유지

            return exchange_flow, whale_activity

        except Exception as e:
            logger.debug("Glassnode signals extraction failed: %s", e)
            return "NEUTRAL", "NEUTRAL"

    def _score_from_fields(
        self, exchange_flow: str, whale_activity: str, nvt_signal: str
    ) -> float:
        score = 0.0
        if exchange_flow == "INFLOW_SPIKE":
            score -= 1.5
        elif exchange_flow == "OUTFLOW":
            score += 1.0
        if whale_activity == "ACCUMULATING":
            score += 1.5
        elif whale_activity == "DISTRIBUTING":
            score -= 1.5
        if nvt_signal == "UNDERVALUED":
            score += 1.0
        elif nvt_signal == "OVERVALUED":
            score -= 1.0
        return max(-3.0, min(3.0, score))
