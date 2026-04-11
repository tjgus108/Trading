"""
B3. NewsMonitor: 크립토 뉴스/이벤트 리스크 감지.

접근법:
  - CryptoPanic RSS (무료, 인증 불필요)
  - 키워드 기반 HIGH/MEDIUM/LOW 분류
  - HIGH 이벤트: 포지션 50% 축소 권고 → orchestrator에 즉시 전파
  - API 실패 시 level=NONE 반환 — 파이프라인 블록 금지
  - 재시도 로직 + fallback으로 일시적 장애 극복
  - 중복 감지: title hash로 동일 뉴스 이벤트 필터링

news-agent가 이 모듈을 사용한다.
"""

import hashlib
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


def _get_title_hash(title: str) -> str:
    """제목의 hash 값 반환. 중복 감지용."""
    return hashlib.md5(title.lower().strip().encode()).hexdigest()


@dataclass
class NewsEvent:
    """감지된 뉴스 이벤트."""
    level: str              # "HIGH" | "MEDIUM" | "LOW" | "NONE"
    event: str              # 1줄 요약
    action: str             # "REDUCE_POSITION" | "HOLD_NEW_ENTRIES" | "MONITOR" | "NONE"
    expires_at: str         # UTC 시각 (ISO 8601)
    keywords_matched: list[str]
    source: str = "live"    # "live" | "fallback" | "unavailable"
    title_hash: str = ""    # 중복 감지용

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
    중복 감지: title hash로 동일 이벤트 필터링.
    """

    def __init__(self, use_cache_seconds: int = 300, max_retries: int = 2, duplicate_window_hours: int = 24):
        self.use_cache_seconds = use_cache_seconds
        self.max_retries = max_retries
        self.duplicate_window_hours = duplicate_window_hours
        self._cache: Optional[NewsEvent] = None
        self._cache_time: float = 0.0
        self._last_successful: Optional[NewsEvent] = None  # fallback 데이터
        self._seen_hashes: dict[str, float] = {}  # title_hash -> timestamp
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

        # 중복 확인
        if event.source == "live" and self._is_duplicate(event.title_hash):
            logger.debug(f"Duplicate news detected: {event.event[:50]}... Using fallback")
            event = self._get_fallback_or_neutral()
        else:
            # 새로운 해시 기록
            if event.source == "live":
                self._seen_hashes[event.title_hash] = now
                self._cleanup_old_hashes(now)

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
        title_hash = _get_title_hash(event_text) if event_text else ""
        return NewsEvent(
            level=level,
            event=event_text or ("none" if level == "NONE" else "mock event"),
            action=action_map.get(level, "NONE"),
            expires_at=expires,
            keywords_matched=[],
            source="live",
            title_hash=title_hash,
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
                keywords_matched=[], source="live", title_hash="",
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
                title_hash=_get_title_hash(best),
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
                title_hash=_get_title_hash(best),
            )

        # 뉴스 있지만 분류 안 됨
        headline = headlines[0][:150] if headlines else "general news"
        return NewsEvent(
            level="LOW",
            event=headline,
            action="MONITOR",
            expires_at=self._expires_utc(hours=1),
            keywords_matched=[],
            source="live",
            title_hash=_get_title_hash(headlines[0]) if headlines else "",
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
                title_hash=self._last_successful.title_hash,
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
            title_hash="",
        )

    def _is_duplicate(self, title_hash: str) -> bool:
        """Title hash가 최근 윈도우에 있으면 중복."""
        if not title_hash:
            return False
        now = time.time()
        window_secs = self.duplicate_window_hours * 3600
        return title_hash in self._seen_hashes and (now - self._seen_hashes[title_hash]) < window_secs

    def _cleanup_old_hashes(self, now: float):
        """오래된 hash 제거."""
        window_secs = self.duplicate_window_hours * 3600
        expired = [h for h, ts in self._seen_hashes.items() if (now - ts) >= window_secs]
        for h in expired:
            del self._seen_hashes[h]
        if expired:
            logger.debug(f"Cleaned up {len(expired)} old news hashes")

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
