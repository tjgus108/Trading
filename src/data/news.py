"""
B3. NewsMonitor: 크립토 뉴스/이벤트 리스크 감지.

접근법:
  - CryptoPanic RSS (무료, 인증 불필요)
  - 키워드 기반 HIGH/MEDIUM/LOW 분류
  - HIGH 이벤트: 포지션 50% 축소 권고 → orchestrator에 즉시 전파
  - API 실패 시 level=NONE 반환 — 파이프라인 블록 금지
  - 재시도 로직 + fallback으로 일시적 장애 극복

news-agent가 이 모듈을 사용한다.
"""

import json
import logging
import time
import urllib.request
import urllib.parse
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
import re

logger = logging.getLogger(__name__)

# CryptoPanic RSS (인증 없이 최신 뉴스 20개)
CRYPTOPANIC_RSS = "https://cryptopanic.com/api/free/v1/posts/?auth_token=&metadata=false&regions=en&filter=hot&currencies=BTC,ETH"

_FETCH_TIMEOUT = 8

# 키워드 분류 (대소문자 무관)
HIGH_KEYWORDS = [
    "hack", "exploit", "breach", "stolen", "theft", "rug pull", "exit scam",
    "arrested", "shutdown", "banned", "ban", "seized", "frozen",
    "emergency", "crash", "liquidation", "insolvent", "bankrupt",
    "sec charges", "doj", "criminal", "regulation ban",
]
MEDIUM_KEYWORDS = [
    "etf", "interest rate", "cpi", "fed", "fomc", "rate hike", "rate cut",
    "regulation", "senate", "congress", "hearing", "subpoena",
    "investigation", "warning", "notice", "concern",
    "partnership", "launch", "upgrade", "halving",
]


@dataclass
class NewsEvent:
    """감지된 뉴스 이벤트."""
    level: str              # "HIGH" | "MEDIUM" | "LOW" | "NONE"
    event: str              # 1줄 요약
    action: str             # "REDUCE_POSITION" | "HOLD_NEW_ENTRIES" | "MONITOR" | "NONE"
    expires_at: str         # UTC 시각 (ISO 8601)
    keywords_matched: list[str]
    source: str = "live"    # "live" | "fallback" | "unavailable"

    def is_high_risk(self) -> bool:
        return self.level == "HIGH"

    def summary(self) -> str:
        return (
            f"NEWS_RISK: level={self.level} action={self.action} "
            f"event={self.event[:60]}... expires={self.expires_at} source={self.source}"
        ) if self.event else f"NEWS_RISK: level=NONE source={self.source}"


class NewsMonitor:
    """
    뉴스 이벤트 모니터.

    fetch()로 최신 24h 뉴스 리스크 반환.
    HIGH 이벤트 콜백: on_high_risk_callback(event) 설정 가능.
    API 실패 시 fallback → neutral 반환으로 graceful degradation.
    """

    def __init__(self, use_cache_seconds: int = 300, max_retries: int = 2):
        self.use_cache_seconds = use_cache_seconds
        self.max_retries = max_retries
        self._cache: Optional[NewsEvent] = None
        self._cache_time: float = 0.0
        self._last_successful: Optional[NewsEvent] = None  # fallback 데이터
        self.on_high_risk_callback = None  # orchestrator가 설정

    def fetch(self) -> NewsEvent:
        """최신 뉴스 리스크 반환. API 실패 시 graceful degradation."""
        now = time.time()
        if self._cache and (now - self._cache_time) < self.use_cache_seconds:
            return self._cache

        # 재시도 로직으로 API 호출
        headlines = self._fetch_headlines_with_retry()
        
        try:
            event = self._classify(headlines)
        except Exception as e:
            logger.warning("_classify failed: %s, using fallback", e)
            event = self._get_fallback_or_neutral()

        # 성공한 live 데이터만 저장 (fallback 제외)
        if event.source == "live":
            self._last_successful = event

        if event.is_high_risk() and self.on_high_risk_callback:
            try:
                self.on_high_risk_callback(event)
            except Exception as e:
                logger.error("High risk callback failed: %s", e)

        self._cache = event
        self._cache_time = now
        logger.info(event.summary())
        return event

    def mock(self, level: str = "NONE", event_text: str = "") -> NewsEvent:
        """테스트/데모용 mock."""
        action_map = {
            "HIGH": "REDUCE_POSITION",
            "MEDIUM": "HOLD_NEW_ENTRIES",
            "LOW": "MONITOR",
            "NONE": "NONE",
        }
        expires = self._expires_utc(hours=4 if level == "HIGH" else 2)
        return NewsEvent(
            level=level,
            event=event_text or ("none" if level == "NONE" else "mock event"),
            action=action_map.get(level, "NONE"),
            expires_at=expires,
            keywords_matched=[],
            source="live",
        )

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _fetch_headlines_with_retry(self) -> list[str]:
        """CryptoPanic API에서 최신 뉴스 헤드라인 반환. 재시도 포함."""
        for attempt in range(self.max_retries):
            try:
                return self._fetch_headlines()
            except Exception as e:
                logger.debug(f"Fetch attempt {attempt + 1}/{self.max_retries} failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(0.5 * (2 ** attempt))  # exponential backoff
        
        logger.warning("CryptoPanic API failed after %d retries", self.max_retries)
        return []

    def _fetch_headlines(self) -> list[str]:
        """CryptoPanic API에서 최신 뉴스 헤드라인 반환."""
        req = urllib.request.Request(
            CRYPTOPANIC_RSS,
            headers={"User-Agent": "TradingBot/1.0"},
        )
        with urllib.request.urlopen(req, timeout=_FETCH_TIMEOUT) as resp:
            data = json.loads(resp.read())
        results = data.get("results", [])
        return [r.get("title", "") for r in results[:30]]

    def _classify(self, headlines: list[str]) -> NewsEvent:
        """헤드라인 리스트를 키워드 분류 → NewsEvent 반환."""
        if not headlines:
            return NewsEvent(
                level="NONE", event="none",
                action="NONE", expires_at=self._expires_utc(hours=1),
                keywords_matched=[], source="live",
            )

        all_text = " ".join(headlines).lower()
        high_hits = [kw for kw in HIGH_KEYWORDS if kw in all_text]
        medium_hits = [kw for kw in MEDIUM_KEYWORDS if kw in all_text]

        # HIGH 이벤트
        if high_hits:
            best = self._best_headline(headlines, high_hits)
            return NewsEvent(
                level="HIGH",
                event=best[:150],
                action="REDUCE_POSITION",
                expires_at=self._expires_utc(hours=6),
                keywords_matched=high_hits[:5],
                source="live",
            )

        # MEDIUM 이벤트
        if medium_hits:
            best = self._best_headline(headlines, medium_hits)
            return NewsEvent(
                level="MEDIUM",
                event=best[:150],
                action="HOLD_NEW_ENTRIES",
                expires_at=self._expires_utc(hours=3),
                keywords_matched=medium_hits[:5],
                source="live",
            )

        # 뉴스 있지만 분류 안 됨
        return NewsEvent(
            level="LOW",
            event=headlines[0][:150] if headlines else "general news",
            action="MONITOR",
            expires_at=self._expires_utc(hours=1),
            keywords_matched=[],
            source="live",
        )

    def _get_fallback_or_neutral(self) -> NewsEvent:
        """Fallback 데이터 반환. 없으면 중립 데이터."""
        if self._last_successful:
            logger.info("Using fallback news data from previous successful fetch")
            # 복사본 반환하되 source만 변경
            fb = NewsEvent(
                level=self._last_successful.level,
                event=self._last_successful.event,
                action=self._last_successful.action,
                expires_at=self._last_successful.expires_at,
                keywords_matched=self._last_successful.keywords_matched[:],
                source="fallback",
            )
            return fb
        
        # fallback도 없으면 중립
        logger.warning("No fallback available, returning unavailable event")
        return NewsEvent(
            level="NONE",
            event="news unavailable",
            action="NONE",
            expires_at=self._expires_utc(hours=1),
            keywords_matched=[],
            source="unavailable",
        )

    def _best_headline(self, headlines: list[str], keywords: list[str]) -> str:
        """키워드 가장 많이 포함된 헤드라인 반환."""
        best, best_count = headlines[0], 0
        for h in headlines:
            h_lower = h.lower()
            count = sum(1 for kw in keywords if kw in h_lower)
            if count > best_count:
                best, best_count = h, count
        return best

    def _expires_utc(self, hours: int = 4) -> str:
        from datetime import timedelta
        now = datetime.now(timezone.utc)
        expires = now + timedelta(hours=hours)
        return expires.strftime("%Y-%m-%dT%H:%M:%SZ")
