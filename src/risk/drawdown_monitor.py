"""
I2. DrawdownMonitor — 실시간 MDD 추적 + 긴급 정지.

Peak equity를 추적하며, 현재 손실이 max_drawdown_pct 초과 시
circuit_breaker 패턴으로 거래 차단.

3층 서킷브레이커:
  - 일일 DD > daily_limit  → WARNING (거래 중단)
  - 주간 DD > weekly_limit → HALT (거래 중단)
  - 월간 DD > monthly_limit → FORCE_LIQUIDATE (강제 청산)

연속 손실 + 시간 기반 쿨다운:
  - 연속 손실 >= loss_streak_threshold → 포지션 사이즈 50% 축소
  - 큰 손실(single_loss_halt_pct 초과) → cooldown_seconds 동안 거래 일시 정지

사용:
    monitor = DrawdownMonitor(max_drawdown_pct=0.15)  # 15% MDD
    monitor.update(current_equity=9500)
    if monitor.is_halted():
        # 거래 중단
"""

import logging
import time
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Deque, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


class AlertLevel(str, Enum):
    NONE = "NONE"
    WARNING = "WARNING"       # 일일 DD 초과 — 경고
    HALT = "HALT"             # 주간 DD 초과 — 거래 중단
    FORCE_LIQUIDATE = "FORCE_LIQUIDATE"  # 월간 DD 초과 — 강제 청산


class MddLevel(str, Enum):
    """단계적 MDD 서킷브레이커 레벨.

    MDD (peak 대비 전체 낙폭) 기준 4단계:
      NORMAL       : MDD < mdd_warn_pct       → 정상 (size_multiplier=1.0)
      WARN         : mdd_warn_pct ≤ MDD < mdd_block_pct → 경고 + 포지션 50% 축소
      BLOCK_ENTRY  : mdd_block_pct ≤ MDD < mdd_liquidate_pct → 신규 진입 차단
      LIQUIDATE    : mdd_liquidate_pct ≤ MDD < mdd_halt_pct → 모든 포지션 청산 권고
      FULL_HALT    : MDD ≥ mdd_halt_pct       → 전체 거래 중단
    """
    NORMAL = "NORMAL"
    WARN = "WARN"
    BLOCK_ENTRY = "BLOCK_ENTRY"
    LIQUIDATE = "LIQUIDATE"
    FULL_HALT = "FULL_HALT"


@dataclass
class DrawdownStatus:
    current_equity: float
    peak_equity: float
    drawdown_pct: float       # 현재 낙폭 (양수, 0~1)
    max_drawdown_pct: float   # 최대 허용 낙폭
    halted: bool
    reason: str
    alert_level: AlertLevel = AlertLevel.NONE
    daily_drawdown_pct: float = 0.0
    weekly_drawdown_pct: float = 0.0
    monthly_drawdown_pct: float = 0.0
    consecutive_losses: int = 0
    size_multiplier: float = 1.0   # 포지션 사이즈 배수 (1.0=정상, 0.5=연속손실 축소)
    cooldown_active: bool = False  # 단일 손실(single_loss_halt_pct 초과) 쿨다운 중 여부만 반영.
    # streak cooldown(is_in_streak_cooldown)은 별도이며 이 필드에 포함되지 않음.
    mdd_level: MddLevel = MddLevel.NORMAL          # 단계적 MDD 레벨
    mdd_size_multiplier: float = 1.0  # MDD 단계별 사이즈 배수 (1.0/0.5/0.0)
    rolling_mdd_pct: float = 0.0   # 롤링 윈도우(50봉) 내 MDD
    rolling_mdd_short_pct: float = 0.0  # 단기 롤링(20봉) MDD — 장기 대비 조기 경보용
    kelly_fraction_multiplier: float = 1.0  # Kelly fraction 축소 배수 (MDD > kelly_reduce_at_mdd 시 0.5)
    atr_vol_multiplier: float = 1.0  # ATR 변동성 필터 배수 (ATR 급등 시 0.5)
    sharpe_decay_multiplier: float = 1.0  # OOS Sharpe decay 필터 배수 (decay 감지 시 0.5)


class DrawdownMonitor:
    """실시간 MDD 추적 및 긴급 정지 모듈.

    3층 서킷브레이커:
      daily_limit  (기본 0.03): 일일 DD 초과 → WARNING + 거래 중단
      weekly_limit (기본 0.07): 주간 DD 초과 → HALT + 거래 중단
      monthly_limit(기본 0.15): 월간 DD 초과 → FORCE_LIQUIDATE

    단계적 MDD 서킷브레이커 (peak 대비 전체 낙폭 기준):
      mdd_warn_pct      (기본 0.05): MDD ≥ 5%  → 경고 + 포지션 사이즈 50% 축소
      mdd_block_pct     (기본 0.10): MDD ≥ 10% → 신규 진입 차단
      mdd_liquidate_pct (기본 0.15): MDD ≥ 15% → 모든 포지션 청산 권고
      mdd_halt_pct      (기본 0.20): MDD ≥ 20% → 전체 거래 중단

    연속 손실 관리:
      loss_streak_threshold    (기본 3): N회 연속 손실 시 size_multiplier=0.5 적용 + streak 쿨다운 시작
      single_loss_halt_pct     (기본 0.02): 단일 거래 손실이 계좌의 N% 초과 시 쿨다운 시작
      cooldown_seconds         (기본 3600): 단일 큰 손실 쿨다운 지속 시간 (초)
      streak_cooldown_seconds  (기본 14400): 연속 손실 N회 도달 시 쿨다운 지속 시간 (4시간)
    """

    # 레짐별 cooldown 배수 (기본 cooldown_seconds * 배수)
    # detect_regime() 반환값("bull","bear","crisis") 별칭 포함
    REGIME_COOLDOWN_MULTIPLIERS: dict = {
        'TREND_UP': 0.5,     # 상승 추세: 짧은 cooldown
        'TREND_DOWN': 1.5,   # 하락 추세: 긴 cooldown
        'RANGING': 1.2,      # 횡보: 기본보다 20% 연장 (손실 빈도 높음, Cycle 343 B)
        'HIGH_VOL': 2.0,     # 고변동성: 가장 긴 cooldown
        # detect_regime() 별칭
        'BULL': 0.5,
        'BEAR': 1.5,
        'CRISIS': 2.0,
    }

    # RANGING 매크로 방향성별 cooldown 배수 (Cycle 346 B)
    # 분석: RANGING+neutral macro(W6 sideways) → mean-reversion PASS
    #        RANGING+directional macro(W2-W5 bull/bear) → mean-reversion FAIL
    # neutral(|ema50_slope| <= threshold): mean-reversion 유리 → cooldown 단축
    # directional(|ema50_slope| > threshold): mean-reversion 불리 → cooldown 연장
    _RANGING_MACRO_NEUTRAL_MULT: float = 0.9   # neutral macro + RANGING: 기본 cooldown 단축
    _RANGING_MACRO_DIRECTIONAL_MULT: float = 1.5  # directional macro + RANGING: cooldown 연장

    def __init__(
        self,
        max_drawdown_pct: float = 0.15,
        recovery_pct: float = 0.05,
        daily_limit: float = 0.03,
        weekly_limit: float = 0.07,
        monthly_limit: float = 0.15,
        loss_streak_threshold: int = 3,
        single_loss_halt_pct: float = 0.02,
        cooldown_seconds: float = 3600.0,
        streak_cooldown_seconds: float = 14400.0,
        streak_recovery_grace_seconds: float = 0.0,
        mdd_warn_pct: float = 0.05,
        mdd_block_pct: float = 0.10,
        mdd_liquidate_pct: float = 0.15,
        mdd_halt_pct: float = 0.20,
        mdd_warn_hysteresis_pct: float = 0.015,
        rolling_window: int = 50,
        kelly_reduce_at_mdd: float = 0.08,
        transition_cushion_enabled: bool = False,
        transition_cushion_threshold: float = 0.70,
    ) -> None:
        """
        Args:
            max_drawdown_pct: 전체 MDD 한계 (legacy). 초과 시 거래 차단.
            recovery_pct: 차단 해제 기준 (낙폭이 max - recovery 이하로 회복 시 재개).
            daily_limit:   일일 낙폭 한계 (기본 3%).
            weekly_limit:  주간 낙폭 한계 (기본 7%).
            monthly_limit: 월간 낙폭 한계 (기본 15%).
            loss_streak_threshold: 연속 손실 N회 시 size_multiplier 0.5로 축소.
                                   이 횟수에 도달하면 streak_cooldown_seconds 쿨다운도 시작.
            single_loss_halt_pct:  단일 손실이 계좌 대비 이 비율 초과 시 쿨다운 시작.
            cooldown_seconds:      단일 큰 손실 후 쿨다운 지속 시간 (초). 기본 1시간.
            streak_cooldown_seconds: 연속 손실(loss_streak_threshold 도달) 후 쿨다운 지속 시간 (초).
                                     기본 4시간. 0으로 설정 시 연속 손실 쿨다운 비활성화.
            streak_recovery_grace_seconds: 마지막 손실 이후 이 시간이 경과하면 consecutive_losses 자동 초기화.
                                     하이브리드(실적+시간) 회복 지원. 0이면 비활성(기본, 실적 기반만).
                                     예) streak_cooldown_seconds와 동일 값(4h) 설정 시: 마지막 손실 4시간 후 자동 복원.
            mdd_warn_pct:      MDD 경고 기준 (기본 5%). 포지션 50% 축소.
            mdd_block_pct:     MDD 진입 차단 기준 (기본 10%). 신규 진입 차단.
            mdd_liquidate_pct: MDD 청산 권고 기준 (기본 15%). 모든 포지션 청산 권고.
            mdd_halt_pct:      MDD 완전 중단 기준 (기본 20%). 전체 거래 중단.
            mdd_warn_hysteresis_pct: WARN→NORMAL 복귀 시 필요한 추가 회복폭 (기본 1.5%).
                                     WARN 진입: MDD ≥ mdd_warn_pct (5%)
                                     NORMAL 복귀: MDD < mdd_warn_pct - mdd_warn_hysteresis_pct (3.5%)
                                     BTC처럼 MDD가 5% 경계를 반복 교차할 때 사이즈 배수 oscillation 방지.
            rolling_window:    rolling_mdd() 기본 윈도우 크기 (equity 업데이트 횟수, 기본 50).
            kelly_reduce_at_mdd: MDD가 이 값을 초과하면 Kelly fraction을 0.5x 축소 신호 반환
                                 (DrawdownStatus.kelly_fraction_multiplier = 0.5).
                                 mdd_size_multiplier와 독립적으로 작동 — 포트폴리오 배분 레이어용.
                                 기본 0.08 (8%): mdd_warn_pct(5%)보다 엄격, mdd_block_pct(10%)보다 완화.
        """
        self.max_drawdown_pct = max_drawdown_pct
        self.recovery_pct = recovery_pct
        self.daily_limit = daily_limit
        self.weekly_limit = weekly_limit
        self.monthly_limit = monthly_limit
        self.loss_streak_threshold = loss_streak_threshold
        self.single_loss_halt_pct = single_loss_halt_pct
        self.cooldown_seconds = cooldown_seconds
        self.streak_cooldown_seconds = streak_cooldown_seconds
        self.streak_recovery_grace_seconds = streak_recovery_grace_seconds
        self.mdd_warn_pct = mdd_warn_pct
        self.mdd_block_pct = mdd_block_pct
        self.mdd_liquidate_pct = mdd_liquidate_pct
        self.mdd_halt_pct = mdd_halt_pct
        self.mdd_warn_hysteresis_pct = float(mdd_warn_hysteresis_pct)
        self.kelly_reduce_at_mdd = float(kelly_reduce_at_mdd)
        # WARN 히스테리시스 상태: True면 mdd_warn_pct를 넘어 WARN 진입한 상태
        self._in_warn_mode: bool = False
        self.transition_cushion_enabled = transition_cushion_enabled
        self.transition_cushion_threshold = transition_cushion_threshold
        self._high_vol_daily_limit: float = 0.02   # HIGH_VOL 레짐 일일 DD 한도 (2%)
        self._current_regime: str = ''             # 현재 레짐 (빈 문자열 = 기본)
        self._rolling_window: int = rolling_window  # 롤링 MDD 윈도우 크기 (equity 업데이트 횟수)
        self._equity_history: Deque[float] = deque(maxlen=self._rolling_window)
        # ATR 변동성 필터 상태
        self._atr_vol_elevated: bool = False       # ATR 급등 여부
        self._atr_vol_mult: float = 1.0            # ATR 필터 배수 (정상=1.0, 급등=0.5)
        # OOS Sharpe decay 필터: OOS/IS Sharpe 비율이 threshold 미만이면 0.5x 적용
        self._sharpe_decay_mult: float = 1.0
        # RANGING 매크로 방향성 중립 상태 (Cycle 346 B)
        # None=정보 없음(기본 1.2x), True=neutral macro(0.9x), False=directional macro(1.5x)
        self._ranging_macro_neutral: Optional[bool] = None

        self._peak: Optional[float] = None
        self._current: float = 0.0
        self._halted: bool = False
        self._halt_reason: str = ""
        self._alert_level: AlertLevel = AlertLevel.NONE

        # 3층 서킷브레이커용 기준 잔고
        self._daily_start: Optional[float] = None
        self._weekly_start: Optional[float] = None
        self._monthly_start: Optional[float] = None

        # 연속 손실 + 쿨다운 상태
        self._consecutive_losses: int = 0
        self._cooldown_until: float = 0.0   # epoch seconds; 0=쿨다운 없음
        self._single_loss_cooldown_until: float = 0.0  # 단일 손실로 인한 쿨다운
        self._last_loss_at: float = 0.0     # 마지막 손실 시각 (하이브리드 회복용)
        # tiered halt 추적: True이면 tiered(일간/주간/월간) 조건으로 halt된 것
        # → tiered 조건 해소 시 legacy MDD 체크 없이 즉시 회복 허용
        self._tiered_halt: bool = False
        # halt 당시 낙폭 기록: tiered 회복 임계값 = _halt_drawdown - recovery_pct
        self._halt_drawdown: float = 0.0

    # ── 기준 잔고 설정 ─────────────────────────────────────────

    def set_daily_start(self, equity: float) -> None:
        """일일 기준 잔고 설정 (매일 자정 호출)."""
        self._daily_start = equity
        logger.info("DrawdownMonitor: daily_start=%.2f", equity)

    def set_weekly_start(self, equity: float) -> None:
        """주간 기준 잔고 설정 (매주 월요일 호출)."""
        self._weekly_start = equity
        logger.info("DrawdownMonitor: weekly_start=%.2f", equity)

    def set_monthly_start(self, equity: float) -> None:
        """월간 기준 잔고 설정 (매월 1일 호출)."""
        self._monthly_start = equity
        logger.info("DrawdownMonitor: monthly_start=%.2f", equity)

    def set_regime(self, regime: str) -> None:
        """현재 시장 레짐 설정. HIGH_VOL 시 일일 DD 한도를 강화한다.

        Args:
            regime: 레짐 문자열 — 'TREND_UP', 'TREND_DOWN', 'RANGING', 'HIGH_VOL'
        """
        self._current_regime = regime.upper() if regime else ''
        if self._current_regime in ('HIGH_VOL', 'CRISIS'):
            logger.info(
                'DrawdownMonitor: %s 레짐 — 일일 DD 한도 %.1f%% → %.1f%% 강화',
                self._current_regime, self.daily_limit * 100, self._high_vol_daily_limit * 100,
            )
        else:
            logger.debug('DrawdownMonitor: regime=%s (일일 한도=%.1f%%)', self._current_regime, self.daily_limit * 100)

    def set_ranging_macro_neutral(self, ema50_slope: float, threshold: float = 0.0005) -> None:
        """RANGING 레짐 내 매크로 방향성 중립 여부 설정.

        RANGING micro 레짐에서 ema50 slope의 절댓값이 threshold 이하이면 중립 매크로로 판정.
        중립 매크로 + RANGING → mean-reversion 전략 유리 → cooldown 단축 (0.9x).
        방향성 매크로 + RANGING → mean-reversion 전략 불리 → cooldown 연장 (1.5x).

        Cycle 346 B 분석 근거:
          - BTC 1h RANGING 창에서 |ema50_slope| < 0.0005: 45.1%의 캔들 (중립 구간)
          - W6 PASS (mkt=sideways): 중립 매크로 + RANGING → Sharpe 3.78
          - W2-W5 FAIL (mkt=bull/bear): 방향성 매크로 + RANGING → Sharpe < 1.0

        Args:
            ema50_slope: 현재 EMA50 기울기 (close 대비 비율). `ema50.diff() / ema50` 계산값.
            threshold:   중립 판정 절댓값 임계값 (기본 0.0005). BTC 1h EMA50 분포 기준 보수적 설정.
        """
        is_neutral = abs(ema50_slope) <= threshold
        if is_neutral != self._ranging_macro_neutral:
            tag = "중립" if is_neutral else "방향성"
            mult = self._RANGING_MACRO_NEUTRAL_MULT if is_neutral else self._RANGING_MACRO_DIRECTIONAL_MULT
            logger.info(
                "DrawdownMonitor: RANGING 매크로 %s 전환 — |ema50_slope|=%.6f %s %.6f → cooldown %.1fx",
                tag, abs(ema50_slope), "≤" if is_neutral else ">", threshold, mult,
            )
        self._ranging_macro_neutral = is_neutral

    def set_atr_state(self, atr: float, atr_ma: float, threshold: float = 1.5,
                      atr_pct: float = 0.0, atr_pct_threshold: float = 0.06) -> None:
        """ATR 변동성 상태 설정. ATR > ATR_MA * threshold이면 포지션 사이즈를 0.5로 축소.

        Args:
            atr:               현재 ATR 값.
            atr_ma:            ATR 이동평균 값.
            threshold:         상대 급등 판정 배수 (기본 1.5 — ATR이 MA의 1.5배 초과 시 급등).
            atr_pct:           현재 ATR/close 비율 (0~1). 0이면 절댓값 체크 비활성.
                               SOL 4h처럼 avg ATR이 높아 상대 배수로는 HIGH 슬리피지 레짐이
                               감지되지 않을 때, 절댓값 임계값으로 보완한다.
                               예) ATR=0.065, close=1.0 → atr_pct=0.065.
            atr_pct_threshold: 절댓값 ATR% 임계값 (기본 0.06 = 6%).
                               atr_pct > atr_pct_threshold이면 elevated로 판정.
                               Cycle352 D(ML): SOL 4h HIGH 슬리피지 임계값(6%)과 일치.
        """
        if atr_ma <= 0 or atr <= 0:
            self._atr_vol_elevated = False
            self._atr_vol_mult = 1.0
            return
        ratio = atr / atr_ma
        # 상대 배수 OR 절댓값 ATR% 중 하나라도 초과 시 elevated 판정
        abs_elevated = (atr_pct > 0 and atr_pct > atr_pct_threshold)
        elevated = ratio >= threshold or abs_elevated
        if elevated != self._atr_vol_elevated:
            if elevated:
                if abs_elevated:
                    logger.info(
                        "DrawdownMonitor: ATR 급등 감지 (절댓값) — atr_pct=%.3f > %.3f → size_mult 0.5 적용",
                        atr_pct, atr_pct_threshold,
                    )
                else:
                    logger.info(
                        "DrawdownMonitor: ATR 급등 감지 — ratio=%.2fx ≥ %.1fx → size_mult 0.5 적용",
                        ratio, threshold,
                    )
            else:
                logger.info(
                    "DrawdownMonitor: ATR 정상화 — ratio=%.2fx < %.1fx, atr_pct=%.3f → size_mult 복원",
                    ratio, threshold, atr_pct,
                )
        self._atr_vol_elevated = elevated
        self._atr_vol_mult = 0.5 if elevated else 1.0

    def get_atr_vol_multiplier(self) -> float:
        """ATR 변동성 필터 배수 반환 (정상=1.0, 급등=0.5)."""
        return self._atr_vol_mult

    def set_sharpe_decay(
        self,
        recent_sharpe: float,
        historical_sharpe: float,
        threshold: float = 0.50,
    ) -> None:
        """OOS Sharpe decay 필터 설정.

        OOS Sharpe / IS Sharpe 비율이 threshold 미만이면 포지션 사이즈를 50% 축소.
        IS_OOS_RATIO_MIN=0.50 기준과 동일하게 맞춤.
        IS Sharpe가 0 이하이거나 recent_sharpe도 양수이면 정상으로 간주.

        Args:
            recent_sharpe:     최근 OOS 구간 Sharpe (또는 최근 롤링 Sharpe).
            historical_sharpe: 기준 IS Sharpe (또는 이전 장기 Sharpe).
            threshold:         OOS/IS 최소 비율. 기본 0.40 (IS_OOS_RATIO_MIN과 동일).
        """
        if historical_sharpe <= 0:
            self._sharpe_decay_mult = 1.0
            return
        ratio = recent_sharpe / historical_sharpe
        decayed = ratio < threshold
        if decayed != (self._sharpe_decay_mult < 1.0):
            if decayed:
                logger.info(
                    "DrawdownMonitor: OOS Sharpe decay 감지 — ratio=%.3f < %.2f → size_mult 0.5 적용",
                    ratio, threshold,
                )
            else:
                logger.info(
                    "DrawdownMonitor: OOS Sharpe decay 해소 — ratio=%.3f ≥ %.2f → size_mult 복원",
                    ratio, threshold,
                )
        self._sharpe_decay_mult = 0.5 if decayed else 1.0

    def get_sharpe_decay_multiplier(self) -> float:
        """Sharpe decay 필터 배수 반환 (정상=1.0, decay=0.5)."""
        return self._sharpe_decay_mult

    def _effective_daily_limit(self) -> float:
        """현재 레짐에 따른 실효 일일 DD 한도 반환."""
        if self._current_regime in ('HIGH_VOL', 'CRISIS'):
            return self._high_vol_daily_limit
        return self.daily_limit

    def _regime_cooldown_multiplier(self) -> float:
        """현재 레짐에 따른 cooldown 배수 반환. 레짐 미설정 시 1.0.

        RANGING 레짐 + 매크로 방향성 정보가 있으면 세분화 배수 적용:
          - neutral macro (_ranging_macro_neutral=True): _RANGING_MACRO_NEUTRAL_MULT (0.9x)
          - directional macro (_ranging_macro_neutral=False): _RANGING_MACRO_DIRECTIONAL_MULT (1.5x)
          - 정보 없음 (_ranging_macro_neutral=None): 기본 RANGING 배수 1.2x
        """
        if self._current_regime == 'RANGING' and self._ranging_macro_neutral is not None:
            if self._ranging_macro_neutral:
                return self._RANGING_MACRO_NEUTRAL_MULT
            return self._RANGING_MACRO_DIRECTIONAL_MULT
        return self.REGIME_COOLDOWN_MULTIPLIERS.get(self._current_regime, 1.0)

    def _effective_cooldown_seconds(self) -> float:
        """레짐 반영된 단일 손실 cooldown 초."""
        return self.cooldown_seconds * self._regime_cooldown_multiplier()

    def _effective_streak_cooldown_seconds(self) -> float:
        """레짐 반영된 연속 손실 streak cooldown 초."""
        return self.streak_cooldown_seconds * self._regime_cooldown_multiplier()

    # ── 낙폭 계산 헬퍼 ────────────────────────────────────────

    def _dd(self, start: Optional[float], current: float) -> float:
        if start is None or start <= 0:
            return 0.0
        return max(0.0, (start - current) / start)

    # ── 연속 손실 + 쿨다운 관리 ───────────────────────────────

    def record_trade_result(self, pnl: float, equity: float) -> None:
        """거래 결과 기록.

        Args:
            pnl:    거래 손익 (음수=손실, 양수=수익).
            equity: 거래 후 계좌 잔고.
        """
        if pnl >= 0:
            if self._consecutive_losses > 0:
                logger.info(
                    "DrawdownMonitor: 연속 손실 초기화 (이전 %d회)", self._consecutive_losses
                )
            self._consecutive_losses = 0
            return

        # 손실 처리
        self._consecutive_losses += 1
        self._last_loss_at = time.monotonic()
        logger.info(
            "DrawdownMonitor: 연속 손실 %d회 (threshold=%d)",
            self._consecutive_losses, self.loss_streak_threshold,
        )

        # 단일 손실 비율이 single_loss_halt_pct 초과 → 쿨다운 시작
        if equity > 0:
            loss_pct = abs(pnl) / equity
            if loss_pct >= self.single_loss_halt_pct:
                eff_cd = self._effective_cooldown_seconds()
                self._single_loss_cooldown_until = time.monotonic() + eff_cd
                logger.warning(
                    "DrawdownMonitor: 쿨다운 시작 — 단일 손실 %.2f%% ≥ %.2f%% "
                    "(%.0f초 동안 거래 정지, 레짐=%s, 배수=%.1fx)",
                    loss_pct * 100, self.single_loss_halt_pct * 100, eff_cd,
                    self._current_regime or 'DEFAULT',
                    self._regime_cooldown_multiplier(),
                )

        # 연속 손실이 threshold에 정확히 도달 → streak 쿨다운 시작 (size reduction만, 완전 블록 아님)
        # (streak_cooldown_seconds=0 이면 스킵)
        if (
            self._consecutive_losses == self.loss_streak_threshold
            and self.streak_cooldown_seconds > 0
        ):
            eff_streak_cd = self._effective_streak_cooldown_seconds()
            self._cooldown_until = time.monotonic() + eff_streak_cd
            logger.warning(
                "DrawdownMonitor: 연속 손실 쿨다운 시작 — %d회 연속 손실 "
                "(%.0f초 = %.1f시간 동안 거래 정지, 레짐=%s, 배수=%.1fx)",
                self._consecutive_losses,
                eff_streak_cd,
                eff_streak_cd / 3600,
                self._current_regime or 'DEFAULT',
                self._regime_cooldown_multiplier(),
            )

    def is_in_cooldown(self) -> bool:
        """현재 시간 기반 쿨다운 중인지 여부 (단일 손실로 인한 완전 블록만)."""
        return time.monotonic() < self._single_loss_cooldown_until
    
    def is_in_streak_cooldown(self) -> bool:
        """연속 손실로 인한 쿨다운 (size reduction 적용됨)."""
        return time.monotonic() < self._cooldown_until

    def get_size_multiplier(self) -> float:
        """포지션 사이즈 배수 반환.

        여러 조건의 최소값을 적용:
        - 단일 손실 쿨다운 중: 0.0 (완전 차단)
        - 연속 손실 >= threshold: 0.5 (50% 축소, streak_cooldown 중에도 유지)
        - MDD 단계별: get_mdd_size_multiplier() 결과
        - 정상: 1.0

        Note: streak cooldown(_cooldown_until) 만료 후에도 consecutive_losses가
        loss_streak_threshold 이상이면 0.5 유지. size 복원은 오직 win 발생 시
        record_trade() → consecutive_losses 초기화를 통해서만 이루어짐.
        (의도적 보수적 설계 — 시간 경과가 아닌 실적으로 신뢰 회복)
        """
        if self.is_in_cooldown():
            return 0.0
        # 하이브리드 streak 회복: grace_seconds 설정 시 마지막 손실 이후 충분한 시간이
        # 경과하면 consecutive_losses 자동 초기화 (실적+시간 혼합 방식)
        if (
            self.streak_recovery_grace_seconds > 0
            and self._consecutive_losses >= self.loss_streak_threshold
            and self._last_loss_at > 0
            and time.monotonic() - self._last_loss_at >= self.streak_recovery_grace_seconds
        ):
            logger.info(
                "DrawdownMonitor: 하이브리드 streak 회복 — %.1f초 무손실 경과, consecutive_losses %d 초기화",
                time.monotonic() - self._last_loss_at,
                self._consecutive_losses,
            )
            self._consecutive_losses = 0
        streak_mult = 0.5 if self._consecutive_losses >= self.loss_streak_threshold else 1.0
        mdd_mult = self.get_mdd_size_multiplier()
        return min(streak_mult, mdd_mult, self._atr_vol_mult, self._sharpe_decay_mult)

    # ── 단계적 MDD 서킷브레이커 ─────────────────────────────────

    def get_mdd_level(self) -> MddLevel:
        """현재 peak 대비 전체 낙폭 기준 MDD 단계 반환.

        MDD 단계:
          NORMAL      : MDD < mdd_warn_pct (히스테리시스 적용 복귀 기준)
          WARN        : mdd_warn_pct ≤ MDD < mdd_block_pct
          BLOCK_ENTRY : mdd_block_pct ≤ MDD < mdd_liquidate_pct
          LIQUIDATE   : mdd_liquidate_pct ≤ MDD < mdd_halt_pct
          FULL_HALT   : MDD ≥ mdd_halt_pct

        WARN 히스테리시스:
          진입 조건: MDD ≥ mdd_warn_pct (5%)
          복귀 조건: MDD < mdd_warn_pct - mdd_warn_hysteresis_pct (기본 3.5%)
          → MDD가 5% 경계를 반복 교차할 때 size_multiplier oscillation 방지
        """
        dd = self.current_drawdown()
        if dd >= self.mdd_halt_pct:
            self._in_warn_mode = False  # 상위 레벨 진입 → 히스테리시스 초기화
            return MddLevel.FULL_HALT
        if dd >= self.mdd_liquidate_pct:
            self._in_warn_mode = False
            return MddLevel.LIQUIDATE
        if dd >= self.mdd_block_pct:
            self._in_warn_mode = False
            return MddLevel.BLOCK_ENTRY
        if dd >= self.mdd_warn_pct:
            self._in_warn_mode = True   # WARN 진입: 히스테리시스 활성화
            return MddLevel.WARN
        # mdd_warn_pct 이하 — WARN 히스테리시스 확인
        # BLOCK_ENTRY 이상에서 직접 내려올 때(_in_warn_mode=False)는 히스테리시스 없이 NORMAL
        if self._in_warn_mode:
            recovery_threshold = self.mdd_warn_pct - self.mdd_warn_hysteresis_pct
            if dd > recovery_threshold:
                return MddLevel.WARN  # 완전 회복 전까지 WARN 유지
        self._in_warn_mode = False
        return MddLevel.NORMAL

    def get_mdd_size_multiplier(self) -> float:
        """MDD 단계에 따른 포지션 사이즈 배수 반환.

        NORMAL      → 1.0  (정상)
        WARN        → 0.5  (50% 축소)
        BLOCK_ENTRY → 0.0  (신규 진입 차단)
        LIQUIDATE   → 0.0  (청산 권고, 진입 불가)
        FULL_HALT   → 0.0  (전체 중단)
        """
        level = self.get_mdd_level()
        if level == MddLevel.NORMAL:
            return 1.0
        if level == MddLevel.WARN:
            return 0.5
        # BLOCK_ENTRY, LIQUIDATE, FULL_HALT → 0.0
        return 0.0

    def get_kelly_fraction_multiplier(self) -> float:
        """Kelly fraction 축소 배수 반환.

        MDD가 kelly_reduce_at_mdd(기본 8%)를 초과하면 0.5를 반환하여
        KellySizer의 fraction을 절반으로 줄이도록 신호를 제공한다.
        mdd_size_multiplier(개별 거래 포지션 사이즈 제어)와 별개로 동작하며
        포트폴리오 배분 레이어에서 전략의 자본 할당을 조정하는 데 사용한다.

        Returns:
            0.5 if current_drawdown() > kelly_reduce_at_mdd, else 1.0
        """
        if self.current_drawdown() > self.kelly_reduce_at_mdd:
            return 0.5
        return 1.0

    def get_transition_cushion_multiplier(self, regime_confidence: float) -> float:
        """레짐 확률이 낮으면 전환 쿠션 적용 (0.5x 축소).

        레짐 전환 구간에서 whipsaw 방지를 위해 포지션을 반으로 줄인다.
        transition_cushion_enabled=False(기본)이면 항상 1.0 반환.
        """
        if not self.transition_cushion_enabled:
            return 1.0
        if regime_confidence < self.transition_cushion_threshold:
            logger.info(
                "Transition cushion: regime_confidence=%.2f < threshold=%.2f → 0.5x",
                regime_confidence, self.transition_cushion_threshold,
            )
            return 0.5
        return 1.0

    def should_liquidate_all(self) -> bool:
        """MDD LIQUIDATE 이상 단계 시 True — 모든 포지션 청산 권고."""
        level = self.get_mdd_level()
        return level in (MddLevel.LIQUIDATE, MddLevel.FULL_HALT)

    def trailing_stop_signal(self, accel_threshold: float = 1.5) -> bool:
        """단기 MDD 속도가 장기 MDD 속도보다 accel_threshold배 이상이면 True.

        (short_mdd / 20봉) vs (long_mdd / 50봉) 비교.
        최근 낙폭 속도가 장기 평균보다 빠르면 trailing stop 강화 신호.
        초기(데이터 부족)에는 항상 False.

        Args:
            accel_threshold: 단기/장기 MDD 속도 비율 임계값 (기본 1.5).
        """
        long_window = self._rolling_window
        short_window = min(20, long_window // 2)
        long_mdd = self.rolling_mdd()
        short_mdd = self.rolling_mdd(window=short_window)
        if long_mdd <= 0 or long_window <= 0:
            return False
        short_rate = short_mdd / short_window
        long_rate = long_mdd / long_window
        return short_rate >= long_rate * accel_threshold

    def rolling_mdd(self, window: Optional[int] = None) -> float:
        """롤링 윈도우 내 MDD 계산.

        전체 기간 peak 대비 낙폭이 아닌 최근 N개 equity 업데이트 내의
        peak → trough 낙폭을 반환한다. 단기 성과 모니터링에 유용.

        Args:
            window: 사용할 윈도우 크기. None이면 self._rolling_window 사용.

        Returns:
            롤링 MDD (0~1). 데이터 부족 시 0.0.
        """
        history = list(self._equity_history)
        if window is not None and window < len(history):
            history = history[-window:]
        if len(history) < 2:
            return 0.0
        peak = history[0]
        max_dd = 0.0
        for eq in history:
            if eq > peak:
                peak = eq
            if peak > 0:
                dd = (peak - eq) / peak
                if dd > max_dd:
                    max_dd = dd
        return max_dd

    @property
    def mdd_level(self) -> MddLevel:
        """현재 MDD 단계 (프로퍼티)."""
        return self.get_mdd_level()

    @property
    def consecutive_losses(self) -> int:
        return self._consecutive_losses

    # ── 메인 업데이트 ──────────────────────────────────────────

    def update(self, current_equity: float) -> DrawdownStatus:
        """현재 자본금으로 상태 업데이트. DrawdownStatus 반환."""
        self._current = current_equity
        self._equity_history.append(current_equity)

        if self._peak is None or current_equity > self._peak:
            self._peak = current_equity

        drawdown = (self._peak - current_equity) / self._peak if self._peak > 0 else 0.0

        # 3층 낙폭 계산
        daily_dd = self._dd(self._daily_start, current_equity)
        weekly_dd = self._dd(self._weekly_start, current_equity)
        monthly_dd = self._dd(self._monthly_start, current_equity)

        # 3층 서킷브레이커 체크 (우선순위: 월간 > 주간 > 일일)
        new_level, new_reason = self._check_tiered(
            daily_dd, weekly_dd, monthly_dd, drawdown
        )

        # ── 티어드 서킷브레이커: 항상 적용 (이미 halted여도 심각도 상향 가능) ──
        _severity = {AlertLevel.NONE: 0, AlertLevel.WARNING: 1,
                     AlertLevel.HALT: 2, AlertLevel.FORCE_LIQUIDATE: 3}
        if new_level != AlertLevel.NONE:
            if _severity[new_level] > _severity[self._alert_level]:
                # 새 레벨이 더 심각 → 즉시 적용 (신규 halt 또는 에스컬레이션)
                self._halted = True
                self._alert_level = new_level
                self._halt_reason = new_reason
                self._tiered_halt = True
                self._halt_drawdown = drawdown
                logger.warning(
                    "DrawdownMonitor: HALTED [%s] — %s", new_level.value, new_reason
                )
            elif not self._halted:
                # 동일 심각도, 아직 미halt → halt 시작
                self._halted = True
                self._alert_level = new_level
                self._halt_reason = new_reason
                self._tiered_halt = True
                self._halt_drawdown = drawdown
                logger.warning(
                    "DrawdownMonitor: HALTED [%s] — %s", new_level.value, new_reason
                )
            # 이미 halt + 동일/더 낮은 레벨 → 유지 (no change)

        # legacy MDD 체크 (기준 잔고 미설정 시 폴백)
        elif not self._halted and drawdown >= self.max_drawdown_pct:
            self._halted = True
            self._tiered_halt = False
            self._halt_drawdown = drawdown
            self._alert_level = AlertLevel.HALT
            self._halt_reason = (
                f"MDD {drawdown:.1%} ≥ 한계 {self.max_drawdown_pct:.1%} "
                f"(peak={self._peak:.2f}, current={current_equity:.2f})"
            )
            logger.warning("DrawdownMonitor: HALTED — %s", self._halt_reason)

        # 차단 해제 체크: tiered 조건 해소 후 재개
        # FORCE_LIQUIDATE는 수동 해제(force_resume)만 허용
        elif self._halted and self._alert_level != AlertLevel.FORCE_LIQUIDATE:
            # tiered halt(일간/주간) → tiered 조건이 해소됐으면(new_level==NONE)
            #   halt_drawdown 대비 recovery_pct만큼 회복했거나, 혹은
            #   legacy 회복 기준(max_drawdown_pct - recovery_pct) 달성 시 재개.
            #   방어 목적: 단순 주간/일간 리셋으로 인한 조기 재개 방지.
            # legacy MDD halt → 기존 기준(max_drawdown_pct - recovery_pct) 그대로 사용.
            if self._tiered_halt:
                tiered_recovery_threshold = self._halt_drawdown - self.recovery_pct
                legacy_threshold = self.max_drawdown_pct - self.recovery_pct
                should_resume = drawdown < max(tiered_recovery_threshold, 0.0) or \
                                drawdown < legacy_threshold
            else:
                should_resume = drawdown < (self.max_drawdown_pct - self.recovery_pct)
            if should_resume:
                self._halted = False
                self._tiered_halt = False
                self._halt_drawdown = 0.0
                self._alert_level = AlertLevel.NONE
                self._halt_reason = ""
                logger.info(
                    "DrawdownMonitor: RESUMED — drawdown=%.2f%% peak=%.2f",
                    drawdown * 100, self._peak,
                )

        # 단계적 MDD 레벨 계산
        cur_mdd_level = self.get_mdd_level()
        cur_mdd_size_mult = self.get_mdd_size_multiplier()

        # MDD 단계 로깅 (NORMAL 제외)
        if cur_mdd_level != MddLevel.NORMAL:
            logger.info(
                "DrawdownMonitor: MDD 단계 [%s] — drawdown=%.2f%% (size_mult=%.1f)",
                cur_mdd_level.value, drawdown * 100, cur_mdd_size_mult,
            )

        return DrawdownStatus(
            current_equity=current_equity,
            peak_equity=self._peak,
            drawdown_pct=drawdown,
            max_drawdown_pct=self.max_drawdown_pct,
            halted=self._halted,
            reason=self._halt_reason,
            alert_level=self._alert_level,
            daily_drawdown_pct=daily_dd,
            weekly_drawdown_pct=weekly_dd,
            monthly_drawdown_pct=monthly_dd,
            consecutive_losses=self._consecutive_losses,
            size_multiplier=self.get_size_multiplier(),
            cooldown_active=self.is_in_cooldown(),
            mdd_level=cur_mdd_level,
            mdd_size_multiplier=cur_mdd_size_mult,
            rolling_mdd_pct=self.rolling_mdd(),
            rolling_mdd_short_pct=self.rolling_mdd(window=20),
            kelly_fraction_multiplier=self.get_kelly_fraction_multiplier(),
            atr_vol_multiplier=self._atr_vol_mult,
            sharpe_decay_multiplier=self._sharpe_decay_mult,
        )

    def _check_tiered(
        self,
        daily_dd: float,
        weekly_dd: float,
        monthly_dd: float,
        total_dd: float,
    ) -> Tuple[AlertLevel, str]:
        """3층 서킷브레이커 체크. 가장 심각한 레벨 반환."""
        if monthly_dd >= self.monthly_limit:
            return (
                AlertLevel.FORCE_LIQUIDATE,
                f"월간 낙폭 {monthly_dd:.1%} ≥ 한계 {self.monthly_limit:.1%} — 강제 청산",
            )
        if weekly_dd >= self.weekly_limit:
            return (
                AlertLevel.HALT,
                f"주간 낙폭 {weekly_dd:.1%} ≥ 한계 {self.weekly_limit:.1%} — 거래 중단",
            )
        if daily_dd >= self._effective_daily_limit():
            return (
                AlertLevel.WARNING,
                f"일일 낙폭 {daily_dd:.1%} ≥ 한계 {self._effective_daily_limit():.1%} — 경고",
            )
        return AlertLevel.NONE, ""

    # ── 상태 조회 ──────────────────────────────────────────────

    def is_halted(self) -> bool:
        return self._halted

    def alert_level(self) -> AlertLevel:
        return self._alert_level

    def current_drawdown(self) -> float:
        """현재 낙폭 비율 (0~1)."""
        if self._peak is None or self._peak <= 0:
            return 0.0
        return max(0.0, (self._peak - self._current) / self._peak)

    # ── 리셋 ──────────────────────────────────────────────────

    def reset(self) -> None:
        """상태 초기화 (새 거래 세션 시작 시)."""
        self._peak = None
        self._current = 0.0
        self._halted = False
        self._halt_reason = ""
        self._alert_level = AlertLevel.NONE
        self._daily_start = None
        self._weekly_start = None
        self._monthly_start = None
        self._consecutive_losses = 0
        self._cooldown_until = 0.0
        self._single_loss_cooldown_until = 0.0
        self._last_loss_at = 0.0
        self._equity_history.clear()
        self._atr_vol_elevated = False
        self._tiered_halt = False
        self._halt_drawdown = 0.0
        self._atr_vol_mult = 1.0
        self._sharpe_decay_mult = 1.0
        self._ranging_macro_neutral = None
        logger.info("DrawdownMonitor: reset")

    def reset_daily(self, equity: float) -> None:
        """일일 기준 잔고 리셋. WARNING 레벨 해제."""
        self._daily_start = equity
        if self._halted and self._alert_level == AlertLevel.WARNING:
            self._halted = False
            self._alert_level = AlertLevel.NONE
            self._halt_reason = ""
            logger.info("DrawdownMonitor: daily reset — WARNING cleared")

    def reset_weekly(self, equity: float) -> None:
        """주간 기준 잔고 리셋. HALT 레벨 해제.

        새 주 시작 시 호출. weekly_start를 갱신하고, 주간 DD 초과로 인한
        HALT 상태를 해제한다. FORCE_LIQUIDATE(월간)는 해제하지 않는다.
        """
        self._weekly_start = equity
        if self._halted and self._alert_level == AlertLevel.HALT:
            self._halted = False
            self._alert_level = AlertLevel.NONE
            self._halt_reason = ""
            logger.info("DrawdownMonitor: weekly reset — HALT cleared")

    def reset_monthly(self, equity: float) -> None:
        """월간 기준 잔고 리셋. monthly_start 갱신만 수행.

        새 월 시작 시 호출. FORCE_LIQUIDATE는 자동 해제하지 않는다.
        월간 DD로 인한 FORCE_LIQUIDATE 해제는 force_resume()을 사용할 것.
        """
        self._monthly_start = equity
        logger.info("DrawdownMonitor: monthly reset — monthly_start=%.2f", equity)

    # ── 수동 제어 ──────────────────────────────────────────────

    # ── MDD Kill Switch ────────────────────────────────────────

    # 레짐별 kill multiplier 상한 — bear/crisis 구간에서 더 빨리 kill
    _REGIME_KILL_MULTIPLIER_MAX: dict = {
        'TREND_UP':   1.5,   # 상승장: 기본 multiplier 유지
        'RANGING':    1.2,   # 횡보: 추세추종 전략 구조적 실패 → 빠른 kill (Cycle 343 B)
        'TREND_DOWN': 1.2,   # 하락장: 1.2x까지 축소 (더 빠른 kill)
        'HIGH_VOL':   1.0,   # 고변동성: backtest MDD 초과 즉시 kill
        'BULL':       1.5,
        'BEAR':       1.2,
        'CRISIS':     1.0,
    }

    def _effective_kill_multiplier(self, multiplier: float, regime: Optional[str] = None) -> float:
        """레짐을 반영한 실효 kill multiplier 반환."""
        if regime is None:
            return multiplier
        cap = self._REGIME_KILL_MULTIPLIER_MAX.get(regime.upper(), multiplier)
        return min(multiplier, cap)

    def should_kill_strategy(
        self,
        current_mdd: float,
        backtest_mdd: float,
        multiplier: float = 1.5,
        regime: Optional[str] = None,
    ) -> bool:
        """현재 MDD가 백테스트 MDD의 multiplier배를 초과하면 전략 kill 권장.

        Args:
            current_mdd: 현재 실시간 MDD (0~1 비율). 음수이면 abs() 처리.
            backtest_mdd: 백테스트에서 관측된 MDD (0~1 비율). 음수이면 abs() 처리.
            multiplier: 초과 배수 기준 (기본 1.5).
            regime: 현재 시장 레짐 (선택). BEAR/CRISIS/HIGH_VOL 시 multiplier를 축소.
                    None이면 레짐 무관 (multiplier 그대로 사용).

        Returns:
            True이면 전략 kill 권장.
        """
        current_mdd = abs(current_mdd)
        backtest_mdd = abs(backtest_mdd)
        eff_mult = self._effective_kill_multiplier(multiplier, regime)
        threshold = backtest_mdd * eff_mult
        return current_mdd > threshold

    def get_kill_switch_status(
        self,
        current_mdd: float,
        backtest_mdd: float,
        multiplier: float = 1.5,
        regime: Optional[str] = None,
    ) -> dict:
        """Kill switch 상태를 dict로 반환.

        Args:
            current_mdd: 현재 실시간 MDD (0~1 비율). 음수이면 abs() 처리.
            backtest_mdd: 백테스트에서 관측된 MDD (0~1 비율). 음수이면 abs() 처리.
            multiplier: 초과 배수 기준 (기본 1.5).
            regime: 현재 시장 레짐 (선택). BEAR/CRISIS/HIGH_VOL 시 multiplier를 축소.

        Returns:
            {
                "should_kill": bool,
                "current_mdd": float,
                "threshold": float,
                "effective_multiplier": float,  # 레짐 반영 후 실제 적용 배수
                "ratio": float,   # current_mdd / backtest_mdd (backtest_mdd=0이면 inf 또는 0)
            }
        """
        current_mdd = abs(current_mdd)
        backtest_mdd = abs(backtest_mdd)
        eff_mult = self._effective_kill_multiplier(multiplier, regime)
        threshold = backtest_mdd * eff_mult
        if backtest_mdd > 0:
            ratio = current_mdd / backtest_mdd
        else:
            ratio = float('inf') if current_mdd > 0 else 0.0
        return {
            "should_kill": current_mdd > threshold,
            "current_mdd": current_mdd,
            "threshold": threshold,
            "effective_multiplier": eff_mult,
            "ratio": ratio,
        }

    # ── 수동 제어 ──────────────────────────────────────────────

    def force_halt(self, reason: str = "Manual halt") -> None:
        """수동으로 거래 차단."""
        self._halted = True
        self._halt_reason = reason
        logger.warning("DrawdownMonitor: force halt — %s", reason)

    def force_resume(self) -> None:
        """수동으로 거래 재개 (FORCE_LIQUIDATE 포함 해제)."""
        self._halted = False
        self._alert_level = AlertLevel.NONE
        self._halt_reason = ""
        logger.info("DrawdownMonitor: force resume")

    # ── 직렬화 ────────────────────────────────────────────────

    def to_dict(self) -> dict:
        """런타임 상태를 dict로 직렬화 (재시작 복원용)."""
        return {
            "max_drawdown_pct": self.max_drawdown_pct,
            "recovery_pct": self.recovery_pct,
            "daily_limit": self.daily_limit,
            "weekly_limit": self.weekly_limit,
            "monthly_limit": self.monthly_limit,
            "loss_streak_threshold": self.loss_streak_threshold,
            "single_loss_halt_pct": self.single_loss_halt_pct,
            "cooldown_seconds": self.cooldown_seconds,
            "streak_cooldown_seconds": self.streak_cooldown_seconds,
            "streak_recovery_grace_seconds": self.streak_recovery_grace_seconds,
            "mdd_warn_pct": self.mdd_warn_pct,
            "mdd_block_pct": self.mdd_block_pct,
            "mdd_liquidate_pct": self.mdd_liquidate_pct,
            "mdd_halt_pct": self.mdd_halt_pct,
            "mdd_warn_hysteresis_pct": self.mdd_warn_hysteresis_pct,
            "kelly_reduce_at_mdd": self.kelly_reduce_at_mdd,
            "rolling_window": self._rolling_window,
            "_in_warn_mode": self._in_warn_mode,
            "_peak": self._peak,
            "_current": self._current,
            "_halted": self._halted,
            "_halt_reason": self._halt_reason,
            "_alert_level": self._alert_level.value,
            "_daily_start": self._daily_start,
            "_weekly_start": self._weekly_start,
            "_monthly_start": self._monthly_start,
            "_consecutive_losses": self._consecutive_losses,
            "_cooldown_until": self._cooldown_until,
            "_single_loss_cooldown_until": self._single_loss_cooldown_until,
            "_last_loss_at": self._last_loss_at,
            "_equity_history": list(self._equity_history),
            "_tiered_halt": self._tiered_halt,
            "_halt_drawdown": self._halt_drawdown,
            "_atr_vol_elevated": self._atr_vol_elevated,
            "_atr_vol_mult": self._atr_vol_mult,
            "_sharpe_decay_mult": self._sharpe_decay_mult,
            "_ranging_macro_neutral": self._ranging_macro_neutral,
            "_current_regime": self._current_regime,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DrawdownMonitor":
        """to_dict() 결과로 인스턴스 복원."""
        obj = cls(
            max_drawdown_pct=data["max_drawdown_pct"],
            recovery_pct=data["recovery_pct"],
            daily_limit=data["daily_limit"],
            weekly_limit=data["weekly_limit"],
            monthly_limit=data["monthly_limit"],
            loss_streak_threshold=data.get("loss_streak_threshold", 3),
            single_loss_halt_pct=data.get("single_loss_halt_pct", 0.02),
            cooldown_seconds=data.get("cooldown_seconds", 3600.0),
            streak_cooldown_seconds=data.get("streak_cooldown_seconds", 14400.0),
            streak_recovery_grace_seconds=data.get("streak_recovery_grace_seconds", 0.0),
            mdd_warn_pct=data.get("mdd_warn_pct", 0.05),
            mdd_block_pct=data.get("mdd_block_pct", 0.10),
            mdd_liquidate_pct=data.get("mdd_liquidate_pct", 0.15),
            mdd_halt_pct=data.get("mdd_halt_pct", 0.20),
            mdd_warn_hysteresis_pct=data.get("mdd_warn_hysteresis_pct", 0.015),
            rolling_window=data.get("rolling_window", 50),
            kelly_reduce_at_mdd=data.get("kelly_reduce_at_mdd", 0.08),
        )
        obj._in_warn_mode = data.get("_in_warn_mode", False)
        obj._peak = data["_peak"]
        obj._current = data["_current"]
        obj._halted = data["_halted"]
        obj._halt_reason = data["_halt_reason"]
        obj._alert_level = AlertLevel(data["_alert_level"])
        obj._daily_start = data["_daily_start"]
        obj._weekly_start = data["_weekly_start"]
        obj._monthly_start = data["_monthly_start"]
        obj._consecutive_losses = data.get("_consecutive_losses", 0)
        obj._cooldown_until = data.get("_cooldown_until", 0.0)
        obj._single_loss_cooldown_until = data.get("_single_loss_cooldown_until", 0.0)
        obj._last_loss_at = data.get("_last_loss_at", 0.0)
        obj._tiered_halt = data.get("_tiered_halt", False)
        obj._halt_drawdown = data.get("_halt_drawdown", 0.0)
        obj._atr_vol_elevated = data.get("_atr_vol_elevated", False)
        obj._atr_vol_mult = data.get("_atr_vol_mult", 1.0)
        obj._sharpe_decay_mult = data.get("_sharpe_decay_mult", 1.0)
        obj._ranging_macro_neutral = data.get("_ranging_macro_neutral", None)
        obj._current_regime = data.get("_current_regime", "")
        for eq in data.get("_equity_history", []):
            obj._equity_history.append(float(eq))
        return obj


# ────────────────────────────────────────────────────────────────────────────────
# DriftMonitor: Page-Hinkley 기반 수익률 분포 변화(concept drift) 감지
# ────────────────────────────────────────────────────────────────────────────────

class DriftState(str, Enum):
    NORMAL = "NORMAL"      # 드리프트 없음
    WARNING = "WARNING"    # 경고 (드리프트 후보)
    DRIFT = "DRIFT"        # 드리프트 확정 → CB 연동 트리거


class DriftMonitor:
    """Page-Hinkley 테스트 기반 수익률 분포 변화 감지기.

    거래 수익률(pnl_pct)을 스트리밍으로 입력받아 분포의 평균 또는 분산이
    통계적으로 유의미하게 변화했는지 감지한다.

    Page-Hinkley Test (양방향):
        m_t = x_t - mu_ref + delta        (delta: 감도 조절)
        M_t = sum(m_0..m_t)               (누적합)
        ph_t = max(M_0..M_t) - M_t        (Page-Hinkley 통계량, 하락 감지)
        drift if ph_t > lambda_            (lambda_: 감지 한계)

    상승 감지: m_t = mu_ref - x_t + delta 로 동일 구조 적용.

    분산 감지:
        rolling 분산이 warm-up 기간 분산의 var_ratio_threshold 배 초과 시 WARNING.

    Args:
        window:              분산 감지용 롤링 윈도우 크기 (기본 30).
        warm_up:             기준 통계 수집 기간 (기본 50). warm-up 전에는 감지 안 함.
        delta:               PH 최소 감지 임계값 (기본 0.001). 작을수록 민감.
        lambda_:             PH 감지 한계 (기본 50). 클수록 false positive 감소.
        var_ratio_threshold: 분산 배율 임계값 (기본 2.0). warm-up 분산 대비 N배 초과 시 WARNING.
        on_drift:            드리프트 감지 시 호출할 콜백 함수 (optional).
                             signature: (state: DriftState, reason: str) -> None
    """

    def __init__(
        self,
        window: int = 30,
        warm_up: int = 50,
        delta: float = 0.001,
        lambda_: float = 50.0,
        var_ratio_threshold: float = 2.0,
        on_drift: Optional[Callable[["DriftState", str], None]] = None,
    ) -> None:
        self.window = window
        self.warm_up = warm_up
        self.delta = delta
        self.lambda_ = lambda_
        self.var_ratio_threshold = var_ratio_threshold
        self.on_drift = on_drift

        self._returns: Deque[float] = deque(maxlen=max(window, warm_up) * 2)
        self._n: int = 0
        self._state: DriftState = DriftState.NORMAL

        # PH 통계량 (하락 감지)
        self._ph_sum_down: float = 0.0
        self._ph_max_down: float = 0.0  # max(M_t) for downward shift detection
        # PH 통계량 (상승 감지)
        self._ph_sum_up: float = 0.0
        self._ph_max_up: float = 0.0

        # warm-up 기간 참조 통계
        self._mu_ref: float = 0.0
        self._var_ref: float = 0.0
        self._warm_up_done: bool = False

    # ── 내부 헬퍼 ─────────────────────────────────────────────────

    def _update_ph(self, x: float) -> Tuple[float, float]:
        """Page-Hinkley 통계량 업데이트. (ph_down, ph_up) 반환.

        표준 PH 공식 (하락 감지):
            m_t = (x_t - mu_ref + delta)   — 평균 하락 시 m_t < 0
            M_t = sum(m)                    — 누적합, 하락 시 감소
            ph_t = max(M) - M_t             — M이 하락할수록 증가
        """
        # 하락 감지: x가 mu_ref 아래로 이동 → ph_down 증가
        m_down = x - self._mu_ref + self.delta
        self._ph_sum_down += m_down
        self._ph_max_down = max(self._ph_max_down, self._ph_sum_down)
        ph_down = self._ph_max_down - self._ph_sum_down

        # 상승 감지: x가 mu_ref 위로 이동 → ph_up 증가
        m_up = self._mu_ref - x + self.delta
        self._ph_sum_up += m_up
        self._ph_max_up = max(self._ph_max_up, self._ph_sum_up)
        ph_up = self._ph_max_up - self._ph_sum_up

        return ph_down, ph_up

    def _rolling_variance(self) -> float:
        """최근 window 기간 수익률 분산."""
        recent = list(self._returns)[-self.window:]
        if len(recent) < 2:
            return 0.0
        return float(np.var(recent, ddof=1))

    # ── 메인 업데이트 ──────────────────────────────────────────────

    def update(self, pnl_pct: float) -> "DriftState":
        """수익률(pnl_pct) 한 건 입력. 현재 DriftState 반환.

        Args:
            pnl_pct: 거래 손익 비율. 예) -0.02 = -2% 손실, 0.015 = +1.5% 수익.

        Returns:
            DriftState: NORMAL / WARNING / DRIFT
        """
        self._returns.append(pnl_pct)
        self._n += 1

        # warm-up 완료 판정
        if not self._warm_up_done and self._n >= self.warm_up:
            warm_data = list(self._returns)[:self.warm_up]
            self._mu_ref = float(np.mean(warm_data))
            self._var_ref = float(np.var(warm_data, ddof=1))
            # PH 통계량 초기화
            self._ph_sum_down = 0.0
            self._ph_max_down = 0.0
            self._ph_sum_up = 0.0
            self._ph_max_up = 0.0
            self._warm_up_done = True
            logger.debug(
                "DriftMonitor: warm-up 완료 — mu_ref=%.5f, var_ref=%.8f",
                self._mu_ref, self._var_ref,
            )

        if not self._warm_up_done:
            return self._state

        # Page-Hinkley 업데이트
        ph_down, ph_up = self._update_ph(pnl_pct)

        # 분산 감지
        rolling_var = self._rolling_variance()
        var_ratio = (rolling_var / self._var_ref) if self._var_ref > 0 else 1.0

        # 감지 판정
        new_state = DriftState.NORMAL
        reason = ""

        if ph_down > self.lambda_:
            new_state = DriftState.DRIFT
            reason = (
                f"PH(하락) {ph_down:.1f} > lambda {self.lambda_:.1f} "
                f"(mu_ref={self._mu_ref:.5f})"
            )
        elif ph_up > self.lambda_:
            new_state = DriftState.DRIFT
            reason = (
                f"PH(상승) {ph_up:.1f} > lambda {self.lambda_:.1f} "
                f"(mu_ref={self._mu_ref:.5f})"
            )
        elif var_ratio >= self.var_ratio_threshold:
            new_state = DriftState.WARNING
            reason = (
                f"분산 {var_ratio:.2f}x 급등 "
                f"(rolling={rolling_var:.8f}, ref={self._var_ref:.8f})"
            )

        # 상태 전이 + 콜백
        if new_state != DriftState.NORMAL:
            if new_state == DriftState.DRIFT:
                logger.warning(
                    "DriftMonitor: DRIFT 감지 — %s [n=%d]", reason, self._n
                )
            else:
                logger.warning(
                    "DriftMonitor: WARNING — %s [n=%d]", reason, self._n
                )
            self._state = new_state
            if self.on_drift is not None:
                try:
                    self.on_drift(new_state, reason)
                except Exception as exc:  # noqa: BLE001
                    logger.error("DriftMonitor: on_drift 콜백 오류 — %s", exc)
        elif self._state != DriftState.NORMAL:
            # 드리프트 감지 후 정상화 — PH 리셋 (새 기준점)
            logger.info(
                "DriftMonitor: 정상화 감지 — 참조 통계 갱신 [n=%d]", self._n
            )
            self._reset_ph_and_ref()
            self._state = DriftState.NORMAL

        return self._state

    def _reset_ph_and_ref(self) -> None:
        """PH 통계량과 참조 평균을 최근 window 데이터 기준으로 갱신."""
        recent = list(self._returns)[-self.window:]
        if len(recent) >= 2:
            self._mu_ref = float(np.mean(recent))
            self._var_ref = float(np.var(recent, ddof=1))
        self._ph_sum_down = 0.0
        self._ph_max_down = 0.0
        self._ph_sum_up = 0.0
        self._ph_max_up = 0.0

    # ── 상태 조회 ──────────────────────────────────────────────────

    @property
    def state(self) -> "DriftState":
        return self._state

    @property
    def n_samples(self) -> int:
        return self._n

    @property
    def is_drift(self) -> bool:
        return self._state == DriftState.DRIFT

    @property
    def is_warning(self) -> bool:
        return self._state in (DriftState.WARNING, DriftState.DRIFT)

    def reset(self) -> None:
        """전체 상태 초기화 (새 세션 시작 시)."""
        self._returns.clear()
        self._n = 0
        self._state = DriftState.NORMAL
        self._ph_sum_down = 0.0
        self._ph_max_down = 0.0
        self._ph_sum_up = 0.0
        self._ph_max_up = 0.0
        self._mu_ref = 0.0
        self._var_ref = 0.0
        self._warm_up_done = False
        logger.info("DriftMonitor: reset")
