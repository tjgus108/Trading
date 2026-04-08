"""
G2. 옵션 시장 데이터 피드.

GEX (Gamma Exposure):
  - Deribit 공개 API: https://www.deribit.com/api/v2/public/get_book_summary_by_currency
  - 응답에서 gamma, open_interest, mark_price 추출
  - Net GEX = sum(gamma * open_interest * spot^2 / 100) for calls - puts
  - Positive GEX → 딜러 헤지로 변동성 억제 (mean-revert)
  - Negative GEX → 추세 가속 구간

CME Basis:
  - Binance 현물 가격 vs CME 선물 가격 차이
  - basis_pct = (futures_price - spot_price) / spot_price * 100
  - 연환산: basis_annual = basis_pct * (365 / days_to_expiry)
  - Binance 선물 API: https://fapi.binance.com/fapi/v1/premiumIndex

두 피드 모두 실패 시 mock 반환 (예외 전파 금지).
"""

import logging
import time
from datetime import datetime, timezone
from typing import Optional
from urllib.request import urlopen
import json

logger = logging.getLogger(__name__)

_GEX_SCORE_SCALE = 3.0  # max abs score


class GEXFeed:
    """Deribit 옵션 데이터로 Net GEX 계산."""

    DERIBIT_URL = (
        "https://www.deribit.com/api/v2/public/get_book_summary_by_currency"
        "?currency={symbol}&kind=option"
    )

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self._mock_data: Optional[dict] = None

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def get_gex(self, symbol: str = "BTC") -> dict:
        """
        Returns:
            {"net_gex": float, "positive": bool, "score": float(-3~+3)}
        API 실패 시 {"net_gex": 0.0, "positive": True, "score": 0.0}
        """
        if self._mock_data is not None:
            return self._mock_data

        try:
            url = self.DERIBIT_URL.format(symbol=symbol.upper())
            with urlopen(url, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode())
            return self._parse_gex(data)
        except Exception as exc:
            logger.warning("GEXFeed.get_gex failed: %s", exc)
            return {"net_gex": 0.0, "positive": True, "score": 0.0}

    @classmethod
    def mock(cls, net_gex: float = 1e9, positive: bool = True) -> "GEXFeed":
        """테스트용 mock 인스턴스."""
        instance = cls()
        score = min(_GEX_SCORE_SCALE, abs(net_gex) / 1e9)
        if not positive:
            score = -score
        instance._mock_data = {
            "net_gex": net_gex if positive else -net_gex,
            "positive": positive,
            "score": score,
        }
        return instance

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _parse_gex(self, data: dict) -> dict:
        summaries = data.get("result", [])
        call_gex = 0.0
        put_gex = 0.0

        for item in summaries:
            instrument = item.get("instrument_name", "")
            gamma = item.get("gamma", 0.0) or 0.0
            oi = item.get("open_interest", 0.0) or 0.0
            spot = item.get("mark_price", 0.0) or 0.0

            if gamma == 0.0 or oi == 0.0 or spot == 0.0:
                continue

            gex_val = gamma * oi * (spot ** 2) / 100.0

            # 마지막 문자로 call/put 구분: ...-C / ...-P
            if instrument.endswith("-C"):
                call_gex += gex_val
            elif instrument.endswith("-P"):
                put_gex += gex_val

        net_gex = call_gex - put_gex
        positive = net_gex >= 0.0

        # score: -3 ~ +3 (1e9 단위 스케일)
        raw_score = net_gex / 1e9
        score = max(-_GEX_SCORE_SCALE, min(_GEX_SCORE_SCALE, raw_score))

        return {"net_gex": net_gex, "positive": positive, "score": score}


class CMEBasisFeed:
    """Binance 선물 premiumIndex로 CME basis 추정."""

    BINANCE_URL = (
        "https://fapi.binance.com/fapi/v1/premiumIndex?symbol={symbol}"
    )
    BINANCE_FUTURES_URL = (
        "https://fapi.binance.com/fapi/v1/ticker/price?symbol={symbol}"
    )

    # score 임계값
    HIGH_BASIS_THRESHOLD = 15.0   # annual %
    LOW_BASIS_THRESHOLD = 3.0

    def __init__(self, timeout: int = 10, days_to_expiry: int = 30):
        self.timeout = timeout
        self.days_to_expiry = days_to_expiry
        self._mock_data: Optional[dict] = None

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def get_basis(self, symbol: str = "BTCUSDT") -> dict:
        """
        Returns:
            {"basis_pct": float, "basis_annual": float, "score": float(-3~+3)}
        score: basis_annual > 15% → +2 (carry 매력), < 5% → -1
        API 실패 시 {"basis_pct": 0.0, "basis_annual": 0.0, "score": 0.0}
        """
        if self._mock_data is not None:
            return self._mock_data

        try:
            url = self.BINANCE_URL.format(symbol=symbol.upper())
            with urlopen(url, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode())
            return self._parse_basis(data)
        except Exception as exc:
            logger.warning("CMEBasisFeed.get_basis failed: %s", exc)
            return {"basis_pct": 0.0, "basis_annual": 0.0, "score": 0.0}

    @classmethod
    def mock(cls, basis_annual: float = 10.0) -> "CMEBasisFeed":
        """테스트용 mock 인스턴스."""
        instance = cls()
        # basis_pct 역산 (days_to_expiry=30 기준)
        basis_pct = basis_annual * (30 / 365)
        score = instance._calc_score(basis_annual)
        instance._mock_data = {
            "basis_pct": basis_pct,
            "basis_annual": basis_annual,
            "score": score,
        }
        return instance

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _parse_basis(self, data: dict) -> dict:
        mark_price = float(data.get("markPrice", 0.0))
        index_price = float(data.get("indexPrice", 0.0))

        if index_price == 0.0:
            return {"basis_pct": 0.0, "basis_annual": 0.0, "score": 0.0}

        basis_pct = (mark_price - index_price) / index_price * 100.0
        days = max(1, self.days_to_expiry)
        basis_annual = basis_pct * (365.0 / days)
        score = self._calc_score(basis_annual)

        return {
            "basis_pct": basis_pct,
            "basis_annual": basis_annual,
            "score": score,
        }

    @staticmethod
    def _calc_score(basis_annual: float) -> float:
        """
        basis_annual > 15% → +2
        basis_annual < 5%  → -1
        else               →  0
        """
        if basis_annual > 15.0:
            return 2.0
        if basis_annual < 5.0:
            return -1.0
        return 0.0
