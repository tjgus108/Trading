"""
B3. NewsMonitor: 크립토 뉴스/이벤트 리스크 감지.

접근법:
  - CryptoPanic RSS (무료, 인증 불필요)
  - 키워드 기반 HIGH/MEDIUM/LOW 분류
  - HIGH 이벤트: 포지션 50% 축소 권고 → orchestrator에 즉시 전파
  - API 실패 시 level=NONE 반환 — 파이프라인 블록 금지

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

    def is_high_risk(self) -> bool:
        return self.level == "HIGH"

    def summary(self) -> str:
        return (
            f"NEWS_RISK: level={self.level} action={self.action} "
            f"event={self.event[:60]}... expires={self.expires_at}"
        ) if self.event else f"NEWS_RISK: level=NONE"


class NewsMonitor:
    """
    뉴스 이벤트 모니터.

    fetch()로 최신 24h 뉴스 리스크 반환.
    HIGH 이벤트 콜백: on_high_risk_callback(event) 설정 가능.
    """

    def __init__(self, use_cache_seconds: int = 300):
        self.use_cache_seconds = use_cache_seconds
        self._cache: Optional[NewsEvent] = None
        self._cache_time: float = 0.0
        self.on_high_risk_callback = None  # orchestrator가 설정

    def fetch(self) -> NewsEvent:
        now = time.time()
        if self._cache and (now - self._cache_time) < self.use_cache_seconds:
            return self._cache

        headlines = self._fetch_headlines()
        event = self._classify(headlines)

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
        )

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _fetch_headlines(self) -> list[str]:
        """CryptoPanic API에서 최신 뉴스 헤드라인 반환."""
        try:
            req = urllib.request.Request(
                CRYPTOPANIC_RSS,
                headers={"User-Agent": "TradingBot/1.0"},
            )
            with urllib.request.urlopen(req, timeout=_FETCH_TIMEOUT) as resp:
                data = json.loads(resp.read())
            results = data.get("results", [])
            return [r.get("title", "") for r in results[:30]]
        except Exception as e:
            logger.debug("CryptoPanic fetch failed: %s", e)
            return []

    def _classify(self, headlines: list[str]) -> NewsEvent:
        """헤드라인 리스트를 키워드 분류 → NewsEvent 반환."""
        if not headlines:
            return NewsEvent(
                level="NONE", event="none",
                action="NONE", expires_at="", keywords_matched=[],
            )

        all_text = " ".join(headlines).lower()
        high_hits = [kw for kw in HIGH_KEYWORDS if kw in all_text]
        medium_hits = [kw for kw in MEDIUM_KEYWORDS if kw in all_text]

        # HIGH 이벤트
        if high_hits:
            # 가장 많이 언급된 헤드라인 찾기
            best = self._best_headline(headlines, high_hits)
            return NewsEvent(
                level="HIGH",
                event=best[:150],
                action="REDUCE_POSITION",
                expires_at=self._expires_utc(hours=6),
                keywords_matched=high_hits[:5],
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
            )

        # 뉴스 있지만 분류 안 됨
        return NewsEvent(
            level="LOW",
            event=headlines[0][:150] if headlines else "general news",
            action="MONITOR",
            expires_at=self._expires_utc(hours=1),
            keywords_matched=[],
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
