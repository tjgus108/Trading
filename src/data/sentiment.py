"""
B1. SentimentFetcher: Fear & Greed Index + 펀딩비/Open Interest 수집.

데이터 소스:
  - Fear & Greed: alternative.me (무료, HTTPS GET)
  - 펀딩비/OI: ccxt (거래소 연결 있을 때) 또는 Binance REST API
  - 연결 실패 시 graceful degradation: fallback 데이터 또는 중립 점수 반환

sentiment-agent가 이 모듈을 사용한다.
"""

import logging
import time
import urllib.request
import json
from dataclasses import dataclass
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

FEAR_GREED_URL = "https://api.alternative.me/fng/?limit=1"
BINANCE_FUNDING_URL = "https://fapi.binance.com/fapi/v1/premiumIndex?symbol={symbol}"
BINANCE_OI_URL = "https://fapi.binance.com/fapi/v1/openInterest?symbol={symbol}"

_FETCH_TIMEOUT = 8  # 초


@dataclass
class SentimentData:
    """B1 감성 신호 집계."""
    fear_greed_index: Optional[int]     # 0~100 (0=Extreme Fear, 100=Extreme Greed)
    fear_greed_label: str               # "Extreme Fear" | "Fear" | "Neutral" | "Greed" | "Extreme Greed"
    funding_rate: Optional[float]       # 현재 펀딩비 (소수, e.g. 0.0003 = 0.03%)
    open_interest: Optional[float]      # USD 기준 미체결 약정 잔액
    sentiment_score: float              # [-3, +3]: 종합 감성 점수
    source: str                         # 데이터 소스 기록

    def is_extreme_fear(self) -> bool:
        return self.fear_greed_index is not None and self.fear_greed_index <= 25

    def is_extreme_greed(self) -> bool:
        return self.fear_greed_index is not None and self.fear_greed_index >= 75

    def summary(self) -> str:
        fg = f"FG={self.fear_greed_index}({self.fear_greed_label})" if self.fear_greed_index else "FG=N/A"
        fr = f"FR={self.funding_rate*100:.4f}%" if self.funding_rate is not None else "FR=N/A"
        return f"SENTIMENT: {fg} | {fr} | score={self.sentiment_score:+.1f} | src={self.source}"


class SentimentFetcher:
    """
    감성 데이터 수집기 (재시도 + fallback 지원).

    fetch()로 최신 SentimentData 반환.
    - API 성공 시: 실제 데이터 반환
    - 일부 API 실패: 성공한 API 데이터 사용
    - 모든 API 실패: fallback(이전 성공 데이터) 또는 중립 데이터 반환
    
    파이프라인 블록 절대 금지.
    """

    def __init__(self, symbol: str = "BTCUSDT", use_cache_seconds: int = 300, max_retries: int = 2):
        self.symbol = symbol.replace("/", "")  # BTC/USDT → BTCUSDT
        self.use_cache_seconds = use_cache_seconds
        self.max_retries = max_retries  # 각 API별 최대 재시도 횟수
        self._cache: Optional[SentimentData] = None
        self._cache_time: float = 0.0
        self._last_successful: Optional[SentimentData] = None  # 이전 성공한 데이터

    def fetch(self) -> SentimentData:
        """최신 감성 데이터 반환. cache_seconds 내 재호출 시 캐시 반환.
        
        모든 API 실패 시:
        1. 이전 성공한 데이터 반환 (fallback)
        2. 그것도 없으면 중립 데이터 반환 (score=0)
        """
        now = time.time()
        if self._cache and (now - self._cache_time) < self.use_cache_seconds:
            return self._cache

        fear_greed, fg_label = self._fetch_fear_greed()
        funding_rate = self._fetch_funding_rate()
        open_interest = self._fetch_open_interest()

        score = self._compute_score(fear_greed, funding_rate)
        source_parts = []
        if fear_greed is not None:
            source_parts.append("alternative.me")
        if funding_rate is not None:
            source_parts.append("binance_futures")
        
        if source_parts:
            # 최소 하나의 API 성공
            source = ",".join(source_parts)
            data = SentimentData(
                fear_greed_index=fear_greed,
                fear_greed_label=fg_label,
                funding_rate=funding_rate,
                open_interest=open_interest,
                sentiment_score=score,
                source=source,
            )
            self._last_successful = data  # 성공한 데이터 저장
        else:
            # 모든 API 실패 - fallback 사용
            if self._last_successful:
                logger.warning("All sentiment APIs failed, using fallback data from %s", self._last_successful.source)
                data = self._last_successful
            else:
                logger.warning("All sentiment APIs failed, no fallback available. Returning neutral.")
                data = SentimentData(
                    fear_greed_index=None,
                    fear_greed_label="N/A",
                    funding_rate=None,
                    open_interest=None,
                    sentiment_score=0.0,
                    source="unavailable",
                )
        
        self._cache = data
        self._cache_time = now
        logger.info(data.summary())
        return data

    def mock(self, fear_greed: int = 50, funding_rate: float = 0.0001) -> SentimentData:
        """테스트/데모용 mock 데이터 반환."""
        score = self._compute_score(fear_greed, funding_rate)
        label = self._fg_label(fear_greed)
        return SentimentData(
            fear_greed_index=fear_greed,
            fear_greed_label=label,
            funding_rate=funding_rate,
            open_interest=None,
            sentiment_score=score,
            source="mock",
        )

    # ------------------------------------------------------------------
    # Internal fetchers (각각 독립 실패 처리 + 재시도)
    # ------------------------------------------------------------------

    def _fetch_fear_greed(self) -> Tuple[Optional[int], str]:
        for attempt in range(self.max_retries + 1):
            try:
                req = urllib.request.Request(
                    FEAR_GREED_URL,
                    headers={"User-Agent": "TradingBot/1.0"},
                )
                with urllib.request.urlopen(req, timeout=_FETCH_TIMEOUT) as resp:
                    data = json.loads(resp.read())
                value = int(data["data"][0]["value"])
                label = data["data"][0]["value_classification"]
                return value, label
            except Exception as e:
                if attempt < self.max_retries:
                    logger.debug("Fear&Greed fetch attempt %d/%d failed: %s", attempt + 1, self.max_retries + 1, e)
                    time.sleep(0.5 * (2 ** attempt))  # exponential backoff: 0.5s, 1s, 2s
                else:
                    logger.warning("Fear&Greed fetch failed after %d attempts: %s", self.max_retries + 1, e)
        return None, "N/A"

    def _fetch_funding_rate(self) -> Optional[float]:
        for attempt in range(self.max_retries + 1):
            try:
                url = BINANCE_FUNDING_URL.format(symbol=self.symbol)
                req = urllib.request.Request(url, headers={"User-Agent": "TradingBot/1.0"})
                with urllib.request.urlopen(req, timeout=_FETCH_TIMEOUT) as resp:
                    data = json.loads(resp.read())
                return float(data.get("lastFundingRate", 0))
            except Exception as e:
                if attempt < self.max_retries:
                    logger.debug("Funding rate fetch attempt %d/%d failed: %s", attempt + 1, self.max_retries + 1, e)
                    time.sleep(0.5 * (2 ** attempt))
                else:
                    logger.warning("Funding rate fetch failed after %d attempts: %s", self.max_retries + 1, e)
        return None

    def _fetch_open_interest(self) -> Optional[float]:
        for attempt in range(self.max_retries + 1):
            try:
                url = BINANCE_OI_URL.format(symbol=self.symbol)
                req = urllib.request.Request(url, headers={"User-Agent": "TradingBot/1.0"})
                with urllib.request.urlopen(req, timeout=_FETCH_TIMEOUT) as resp:
                    data = json.loads(resp.read())
                return float(data.get("openInterest", 0))
            except Exception as e:
                if attempt < self.max_retries:
                    logger.debug("Open Interest fetch attempt %d/%d failed: %s", attempt + 1, self.max_retries + 1, e)
                    time.sleep(0.5 * (2 ** attempt))
                else:
                    logger.warning("Open Interest fetch failed after %d attempts: %s", self.max_retries + 1, e)
        return None

    def _compute_score(self, fg: Optional[int], fr: Optional[float]) -> float:
        """종합 감성 점수 [-3, +3]. 높을수록 강세."""
        score = 0.0

        if fg is not None:
            # Fear & Greed: 역추세 관점 (극단 공포 = 매수 기회)
            if fg <= 10:
                score += 2.0    # Extreme Fear → 강한 매수 신호
            elif fg <= 25:
                score += 1.0    # Fear → 약한 매수 신호
            elif fg >= 90:
                score -= 2.0    # Extreme Greed → 강한 매도 신호
            elif fg >= 75:
                score -= 1.0    # Greed → 약한 매도 신호
            # 25~75 중립

        if fr is not None:
            # 펀딩비 역추세
            if fr >= 0.0005:
                score -= 2.0    # 극단적 롱 과밀 → 매도
            elif fr >= 0.0003:
                score -= 1.0    # 롱 과밀
            elif fr <= -0.0002:
                score += 2.0    # 극단적 숏 과밀 → 매수
            elif fr <= -0.0001:
                score += 1.0    # 숏 과밀

        return max(-3.0, min(3.0, score))

    def _fg_label(self, value: int) -> str:
        if value <= 20:
            return "Extreme Fear"
        if value <= 40:
            return "Fear"
        if value <= 60:
            return "Neutral"
        if value <= 80:
            return "Greed"
        return "Extreme Greed"
