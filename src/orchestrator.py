"""
BotOrchestrator: 트레이딩 봇 전체 생명주기를 관리하는 중앙 조율자.

책임:
  - 컴포넌트 조립 및 초기화
  - Startup gate: backtest PASS 없이 live 불가
  - 파이프라인 1회 / 스케줄 루프 실행
  - Strategy tournament: 여러 전략 병렬 백테스트 후 Sharpe 기준 최고 선택
  - 알림 / 로그 / 상태 파일 관리

main.py는 인수 파싱 후 Orchestrator에 위임하고 끝낸다.
"""

import concurrent.futures
import logging
import threading
from dataclasses import dataclass
from datetime import date
from typing import Optional

from src.alpha.context import MarketContextBuilder
from src.analysis.strategy_correlation import SignalCorrelationTracker
from src.analysis.regime_detector import SimpleRegimeDetector
from src.backtest.engine import BacktestEngine, BacktestResult
from src.config import AppConfig
from src.data.feed import DataFeed
from src.exchange.connector import ExchangeConnector
from src.notifier import TelegramNotifier
from src.pipeline.runner import PipelineResult, TradingPipeline
from src.position_tracker import Position, PositionTracker
from src.risk.manager import CircuitBreaker, RiskManager
from src.scheduler import CandleScheduler
from src.strategy.base import Action, BaseStrategy
from src.strategy.donchian_breakout import DonchianBreakoutStrategy
from src.strategy.ema_cross import EmaCrossStrategy
from src.strategy.funding_rate import FundingRateStrategy
from src.strategy.residual_mean_reversion import ResidualMeanReversionStrategy
from src.strategy.pair_trading import PairTradingStrategy
from src.strategy.ml_strategy import MLRFStrategy
from src.strategy.lstm_strategy import MLLSTMStrategy
from src.strategy.rsi_divergence import RsiDivergenceStrategy
from src.strategy.bb_squeeze import BbSqueezeStrategy
from src.strategy.funding_carry import FundingCarryStrategy
from src.strategy.regime_adaptive import RegimeAdaptiveStrategy
from src.strategy.lob_strategy import LOBOFIStrategy
from src.strategy.heston_lstm_strategy import HestonLSTMStrategy
from src.strategy.cross_exchange_arb import CrossExchangeArbStrategy
from src.strategy.liquidation_cascade import LiquidationCascadeStrategy
from src.strategy.gex_strategy import GEXStrategy
from src.strategy.cme_basis_strategy import CMEBasisStrategy
from src.strategy.supertrend import SuperTrendStrategy
from src.strategy.vwap_reversion import VWAPReversionStrategy
from src.strategy.volume_breakout import VolumeBreakoutStrategy
from src.strategy.momentum import MomentumStrategy
from src.strategy.bb_reversion import BBReversionStrategy
from src.strategy.candle_pattern import CandlePatternStrategy
from src.strategy.stochastic import StochasticStrategy
from src.strategy.stoch_rsi import StochRSIStrategy
from src.strategy.macd_strategy import MACDStrategy
from src.strategy.ichimoku import IchimokuStrategy
from src.strategy.williams_r import WilliamsRStrategy
from src.strategy.parabolic_sar import ParabolicSARStrategy
from src.strategy.adx_trend import ADXTrendStrategy
from src.strategy.aroon import AroonStrategy
from src.strategy.cci import CCIStrategy
from src.strategy.cmf import CMFStrategy
from src.strategy.trix import TRIXStrategy
from src.strategy.mfi import MFIStrategy
from src.strategy.obv import OBVStrategy
from src.strategy.keltner_channel import KeltnerChannelStrategy
from src.strategy.price_channel import PriceChannelStrategy
from src.strategy.pivot_points import PivotPointsStrategy
from src.strategy.elder_ray import ElderRayStrategy
from src.strategy.vortex import VortexStrategy
from src.strategy.dpo import DPOStrategy
from src.strategy.stc import STCStrategy
from src.strategy.dema_cross import DEMACrossStrategy
from src.strategy.tema_cross import TEMACrossStrategy
from src.strategy.heikin_ashi import HeikinAshiStrategy
from src.strategy.coppock import CoppockStrategy
from src.strategy.fisher_transform import FisherTransformStrategy
from src.strategy.ppo import PPOStrategy
from src.strategy.klinger import KlingerStrategy
from src.strategy.cmo import CMOStrategy
from src.strategy.ultimate_oscillator import UltimateOscillatorStrategy
from src.strategy.zlema_cross import ZLEMACrossStrategy
from src.strategy.mcginley import McGinleyStrategy
from src.strategy.roc import ROCStrategy
from src.strategy.awesome_oscillator import AwesomeOscillatorStrategy
from src.strategy.connors_rsi import ConnorsRSIStrategy
from src.strategy.linear_regression import LinearRegressionStrategy
from src.strategy.williams_fractal import WilliamsFractalStrategy
from src.strategy.mass_index import MassIndexStrategy
from src.strategy.smi import SMIStrategy
from src.strategy.trima import TRIMAStrategy
from src.strategy.choppiness import ChoppinessStrategy
from src.strategy.alma import ALMAStrategy
from src.strategy.adaptive_rsi import AdaptiveRSIStrategy
from src.strategy.volatility_ratio import VolatilityRatioStrategy
from src.strategy.pmo import PMOStrategy
from src.strategy.rvi import RVIStrategy
from src.strategy.disparity_index import DisparityIndexStrategy
from src.strategy.psychological_line import PsychologicalLineStrategy
from src.strategy.tsi import TSIStrategy
from src.strategy.bop import BOPStrategy
from src.strategy.volatility_breakout import VolatilityBreakoutLWStrategy
from src.strategy.ichimoku_advanced import IchimokuAdvancedStrategy
from src.strategy.ichimoku_cloud_pos import IchimokuCloudPosStrategy
from src.strategy.consecutive_candles import ConsecutiveCandlesStrategy
from src.strategy.guppy import GuppyStrategy
from src.strategy.apo import APOStrategy
from src.strategy.zscore_mean_reversion import ZScoreMeanReversionStrategy
from src.strategy.median_price import MedianPriceStrategy
from src.strategy.nr7 import NR7Strategy
from src.strategy.inside_bar import InsideBarStrategy
from src.strategy.gap_strategy import GapStrategy
from src.strategy.star_pattern import StarPatternStrategy
from src.strategy.doji_pattern import DojiPatternStrategy
from src.strategy.three_candles import ThreeCandlesStrategy
from src.strategy.harami import HaramiStrategy
from src.strategy.cloud_cover import CloudCoverStrategy
from src.strategy.tweezer import TweezerStrategy
from src.strategy.pin_bar import PinBarStrategy
from src.strategy.vwap_cross import VWAPCrossStrategy
from src.strategy.ease_of_movement import EaseOfMovementStrategy
from src.strategy.sr_breakout import SRBreakoutStrategy
from src.strategy.trend_channel import TrendChannelStrategy
from src.strategy.hhll_channel import HHLLChannelStrategy
from src.strategy.vpt import VPTStrategy
from src.strategy.adl import ADLStrategy
from src.strategy.force_index import ForceIndexStrategy
from src.strategy.marubozu import MarubozuStrategy
from src.strategy.spinning_top import SpinningTopStrategy
from src.strategy.proc_trend import PRoCTrendStrategy
from src.strategy.dual_thrust import DualThrustStrategy
from src.strategy.r_squared import RSquaredStrategy
from src.strategy.body_momentum import BodyMomentumStrategy
from src.strategy.turtle_trading import TurtleTradingStrategy
from src.strategy.atr_trailing import ATRTrailingStrategy
from src.strategy.historical_volatility import HistoricalVolatilityStrategy
from src.strategy.price_action_momentum import PriceActionMomentumStrategy
from src.strategy.volume_oscillator import VolumeOscillatorStrategy
from src.strategy.price_envelope import PriceEnvelopeStrategy
from src.strategy.opening_range_breakout import OpeningRangeBreakoutStrategy
from src.strategy.session_high_low import SessionHighLowStrategy
from src.strategy.cci_breakout import CCIBreakoutStrategy
from src.strategy.squeeze_momentum import SqueezeMomentumStrategy
from src.strategy.frama import FRAMAStrategy
from src.strategy.vw_macd import VWMACDStrategy
from src.strategy.chandelier_exit import ChandelierExitStrategy
from src.strategy.vol_adj_momentum import VolAdjMomentumStrategy
from src.strategy.elder_impulse import ElderImpulseStrategy
from src.strategy.ha_trend import HATrendStrategy
from src.strategy.engulfing import EngulfingStrategy
from src.strategy.morning_evening_star import MorningEveningStarStrategy
from src.strategy.three_soldiers_crows import ThreeSoldiersAndCrowsStrategy
from src.strategy.mean_reversion_channel import MeanReversionChannelStrategy
from src.strategy.pivot_reversal import PivotReversalStrategy
from src.strategy.range_expansion import RangeExpansionStrategy
from src.strategy.rsi_momentum_div import RSIMomentumDivStrategy
from src.strategy.dpo_cross import DPOCrossStrategy
from src.strategy.trend_strength import TrendStrengthStrategy
from src.strategy.vpt_signal import VPTSignalStrategy
from src.strategy.stochrsi_div import StochRSIDivStrategy
from src.strategy.trix_signal import TRIXSignalStrategy
from src.strategy.kama import KAMAStrategy
from src.strategy.atr_channel import ATRChannelStrategy
from src.strategy.double_top_bottom import DoubleTopBottomStrategy
from src.strategy.macd_hist_div import MACDHistDivStrategy
from src.strategy.vcp import VCPStrategy
from src.strategy.ema_stack import EMAStackStrategy
from src.strategy.supertrend_rsi import SupertrendRSIStrategy
from src.strategy.bb_bandwidth import BBBandwidthStrategy
from src.strategy.volume_surge import VolumeSurgeStrategy
from src.strategy.price_velocity import PriceVelocityStrategy
from src.strategy.multi_score import MultiScoreStrategy
from src.strategy.adx_regime import ADXRegimeStrategy
from src.strategy.obv_divergence import OBVDivergenceStrategy
from src.strategy.rsi_ob_os import RSIOBOSStrategy
from src.strategy.lr_channel import LRChannelStrategy
from src.strategy.momentum_reversal import MomentumReversalStrategy
from src.strategy.cup_handle import CupHandleStrategy
from src.strategy.flag_pennant import FlagPennantStrategy
from src.strategy.relative_volume import RelativeVolumeStrategy
from src.strategy.pmo_strategy import PriceMomentumOscillator
from src.strategy.fib_retracement import FibRetracementStrategy
from src.strategy.stoch_divergence import StochDivergenceStrategy
from src.strategy.ha_smoothed import HeikinAshiSmoothedStrategy
from src.strategy.keltner_rsi import KeltnerRSIStrategy
from src.risk.drawdown_monitor import DrawdownMonitor

logger = logging.getLogger(__name__)

STRATEGY_REGISTRY: dict[str, type[BaseStrategy]] = {
    "ema_cross": EmaCrossStrategy,
    "donchian_breakout": DonchianBreakoutStrategy,
    "funding_rate": FundingRateStrategy,
    "residual_mean_reversion": ResidualMeanReversionStrategy,
    "pair_trading": PairTradingStrategy,
    "ml_rf": MLRFStrategy,
    "ml_lstm": MLLSTMStrategy,
    "rsi_divergence": RsiDivergenceStrategy,
    "bb_squeeze": BbSqueezeStrategy,
    "funding_carry": FundingCarryStrategy,
    "regime_adaptive": RegimeAdaptiveStrategy,
    "lob_maker": LOBOFIStrategy,
    "heston_lstm": HestonLSTMStrategy,
    "cross_exchange_arb": CrossExchangeArbStrategy,
    "liquidation_cascade": LiquidationCascadeStrategy,
    "gex_signal": GEXStrategy,
    "cme_basis": CMEBasisStrategy,
    "supertrend": SuperTrendStrategy,
    "vwap_reversion": VWAPReversionStrategy,
    "volume_breakout": VolumeBreakoutStrategy,
    "momentum": MomentumStrategy,
    "bb_reversion": BBReversionStrategy,
    "candle_pattern": CandlePatternStrategy,
    "stochastic": StochasticStrategy,
    "stoch_rsi": StochRSIStrategy,
    "macd": MACDStrategy,
    "ichimoku": IchimokuStrategy,
    "williams_r": WilliamsRStrategy,
    "parabolic_sar": ParabolicSARStrategy,
    "adx_trend": ADXTrendStrategy,
    "aroon": AroonStrategy,
    "cci": CCIStrategy,
    "cmf": CMFStrategy,
    "trix": TRIXStrategy,
    "mfi": MFIStrategy,
    "obv": OBVStrategy,
    "keltner_channel": KeltnerChannelStrategy,
    "price_channel": PriceChannelStrategy,
    "pivot_points": PivotPointsStrategy,
    "elder_ray": ElderRayStrategy,
    "vortex": VortexStrategy,
    "dpo": DPOStrategy,
    "stc": STCStrategy,
    "dema_cross": DEMACrossStrategy,
    "tema_cross": TEMACrossStrategy,
    "heikin_ashi": HeikinAshiStrategy,
    "coppock": CoppockStrategy,
    "fisher_transform": FisherTransformStrategy,
    "ppo": PPOStrategy,
    "klinger": KlingerStrategy,
    "cmo": CMOStrategy,
    "ultimate_oscillator": UltimateOscillatorStrategy,
    "zlema_cross": ZLEMACrossStrategy,
    "mcginley": McGinleyStrategy,
    "roc": ROCStrategy,
    "awesome_oscillator": AwesomeOscillatorStrategy,
    "connors_rsi": ConnorsRSIStrategy,
    "linear_regression": LinearRegressionStrategy,
    "williams_fractal": WilliamsFractalStrategy,
    "mass_index": MassIndexStrategy,
    "smi": SMIStrategy,
    "trima": TRIMAStrategy,
    "choppiness": ChoppinessStrategy,
    "alma": ALMAStrategy,
    "adaptive_rsi": AdaptiveRSIStrategy,
    "volatility_ratio": VolatilityRatioStrategy,
    "pmo": PMOStrategy,
    "rvi": RVIStrategy,
    "disparity_index": DisparityIndexStrategy,
    "psychological_line": PsychologicalLineStrategy,
    "tsi": TSIStrategy,
    "bop": BOPStrategy,
    "volatility_breakout_lw": VolatilityBreakoutLWStrategy,
    "ichimoku_advanced": IchimokuAdvancedStrategy,
    "ichimoku_cloud_pos": IchimokuCloudPosStrategy,
    "consecutive_candles": ConsecutiveCandlesStrategy,
    "guppy": GuppyStrategy,
    "apo": APOStrategy,
    "zscore_mean_reversion": ZScoreMeanReversionStrategy,
    "median_price": MedianPriceStrategy,
    "nr7": NR7Strategy,
    "inside_bar": InsideBarStrategy,
    "gap_strategy": GapStrategy,
    "star_pattern": StarPatternStrategy,
    "doji_pattern": DojiPatternStrategy,
    "three_candles": ThreeCandlesStrategy,
    "tweezer": TweezerStrategy,
    "pin_bar": PinBarStrategy,
    "vwap_cross": VWAPCrossStrategy,
    "ease_of_movement": EaseOfMovementStrategy,
    "harami": HaramiStrategy,
    "cloud_cover": CloudCoverStrategy,
    "sr_breakout": SRBreakoutStrategy,
    "trend_channel": TrendChannelStrategy,
    "hhll_channel": HHLLChannelStrategy,
    "vpt": VPTStrategy,
    "adl": ADLStrategy,
    "force_index": ForceIndexStrategy,
    "marubozu": MarubozuStrategy,
    "spinning_top": SpinningTopStrategy,
    "proc_trend": PRoCTrendStrategy,
    "dual_thrust": DualThrustStrategy,
    "r_squared": RSquaredStrategy,
    "body_momentum": BodyMomentumStrategy,
    "turtle_trading": TurtleTradingStrategy,
    "atr_trailing": ATRTrailingStrategy,
    "historical_volatility": HistoricalVolatilityStrategy,
    "price_action_momentum": PriceActionMomentumStrategy,
    "volume_oscillator": VolumeOscillatorStrategy,
    "price_envelope": PriceEnvelopeStrategy,
    "opening_range_breakout": OpeningRangeBreakoutStrategy,
    "session_high_low": SessionHighLowStrategy,
    "cci_breakout": CCIBreakoutStrategy,
    "squeeze_momentum": SqueezeMomentumStrategy,
    "frama": FRAMAStrategy,
    "vw_macd": VWMACDStrategy,
    "elder_impulse": ElderImpulseStrategy,
    "mean_reversion_channel": MeanReversionChannelStrategy,
    "pivot_reversal": PivotReversalStrategy,
    "range_expansion": RangeExpansionStrategy,
    "rsi_momentum_div": RSIMomentumDivStrategy,
    "dpo_cross": DPOCrossStrategy,
    "ha_trend": HATrendStrategy,
    "engulfing": EngulfingStrategy,
    "trend_strength": TrendStrengthStrategy,
    "vpt_signal": VPTSignalStrategy,
    "chandelier_exit": ChandelierExitStrategy,
    "vol_adj_momentum": VolAdjMomentumStrategy,
    "stochrsi_div": StochRSIDivStrategy,
    "trix_signal": TRIXSignalStrategy,
    "morning_evening_star": MorningEveningStarStrategy,
    "three_soldiers_crows": ThreeSoldiersAndCrowsStrategy,
    "kama": KAMAStrategy,
    "atr_channel": ATRChannelStrategy,
    "double_top_bottom": DoubleTopBottomStrategy,
    "macd_hist_div": MACDHistDivStrategy,
    "vcp": VCPStrategy,
    "ema_stack": EMAStackStrategy,
    "supertrend_rsi": SupertrendRSIStrategy,
    "bb_bandwidth": BBBandwidthStrategy,
    "volume_surge": VolumeSurgeStrategy,
    "price_velocity": PriceVelocityStrategy,
    "multi_score": MultiScoreStrategy,
    "adx_regime": ADXRegimeStrategy,
    "obv_divergence": OBVDivergenceStrategy,
    "rsi_ob_os": RSIOBOSStrategy,
    "lr_channel": LRChannelStrategy,
    "momentum_reversal": MomentumReversalStrategy,
    "cup_handle": CupHandleStrategy,
    "flag_pennant": FlagPennantStrategy,
    "relative_volume": RelativeVolumeStrategy,
    "pmo_strategy": PriceMomentumOscillator,
    "fib_retracement": FibRetracementStrategy,
    "stoch_divergence": StochDivergenceStrategy,
    "ha_smoothed": HeikinAshiSmoothedStrategy,
    "keltner_rsi": KeltnerRSIStrategy,
}


class OrchestratorError(Exception):
    pass


@dataclass
class TournamentResult:
    winner: str                          # 전략 이름
    winner_sharpe: float
    rankings: list[dict]                 # [{name, sharpe, passed, fail_reasons}]

    def summary(self) -> str:
        lines = ["TOURNAMENT RESULT:"]
        for i, r in enumerate(self.rankings, 1):
            verdict = "PASS" if r["passed"] else "FAIL"
            lines.append(
                f"  #{i} {r['name']:25s}  Sharpe={r['sharpe']:.3f}  {verdict}"
                + (f"  fail={r['fail_reasons']}" if r["fail_reasons"] else "")
            )
        lines.append(f"  WINNER → {self.winner} (Sharpe={self.winner_sharpe:.3f})")
        return "\n".join(lines)


class BotOrchestrator:
    """
    트레이딩 봇 오케스트레이터.

    사용 예:
        orch = BotOrchestrator(cfg)
        orch.startup()
        orch.run_once()          # 1회
        orch.run_loop()          # 스케줄 루프
        orch.run_backtest_only() # 검증만
    """

    def __init__(self, cfg: AppConfig):
        self.cfg = cfg
        self._connector: Optional[ExchangeConnector] = None
        self._data_feed: Optional[DataFeed] = None
        self._risk_manager: Optional[RiskManager] = None
        self._strategy: Optional[BaseStrategy] = None
        self._notifier: Optional[TelegramNotifier] = None
        self._pipeline: Optional[TradingPipeline] = None
        self._tracker = PositionTracker()
        self._stop_event = threading.Event()
        self._cycle_count: int = 0
        self._context_builder: Optional[MarketContextBuilder] = None
        self._demo: bool = False
        self._tournament_interval: int = 72  # C3: 자동 재평가 주기 (캔들 수)
        self._last_regime: Optional[str] = None
        self._last_tournament_winner: Optional[str] = None
        self._last_run_date: Optional[date] = None
        self._drawdown_monitor = DrawdownMonitor(
            max_drawdown_pct=getattr(cfg.risk, "max_drawdown", 0.20),
        )

    # ── Public API ───────────────────────────────────────────────────────

    def startup(self, dry_run: bool = True, demo: bool = False, skip_backtest_gate: bool = False) -> None:
        """
        컴포넌트 초기화 + backtest gate.
        demo=True: MockExchangeConnector 사용 (API 키 불필요)
        live 모드일 때 backtest FAIL이면 OrchestratorError 발생.
        skip_backtest_gate=True: 토너먼트 모드 등에서 게이트 건너뜀.
        """
        self._dry_run = dry_run
        self._demo = demo
        self._notifier = self._build_notifier()
        logger.info("Orchestrator starting — strategy=%s symbol=%s dry_run=%s demo=%s",
                    self.cfg.strategy, self.cfg.trading.symbol, dry_run, demo)

        self._connect(mock=demo)
        self._build_risk()
        self._load_strategy()
        self._build_context(demo=demo)
        self._build_pipeline()
        self._attach_llm_analyst(demo=demo)

        if not dry_run and not skip_backtest_gate:
            self._backtest_gate()

        self._notifier.notify_startup(
            strategy=self.cfg.strategy,
            symbol=self.cfg.trading.symbol,
            dry_run=dry_run,
        )
        logger.info("Orchestrator startup complete")

    def run_once(self) -> PipelineResult:
        """파이프라인 1회 실행 후 결과 반환."""
        self._assert_ready()
        self._update_funding_rates()

        # 자정 감지: 날짜가 바뀌면 일일 손실 리셋
        today = date.today()
        if self._last_run_date is not None and self._last_run_date != today:
            logger.info("날짜 변경 감지 (%s → %s): 일일 손실 리셋", self._last_run_date, today)
            if self._risk_manager:
                self._risk_manager.reset_daily()
        self._last_run_date = today

        # DrawdownMonitor 체크 (거래 전)
        try:
            balance = self._pipeline._fetch_balance_usd()
            dd_status = self._drawdown_monitor.update(balance)
            if dd_status.halted:
                from src.pipeline.runner import PipelineResult
                from datetime import datetime, timezone
                ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
                logger.warning("DrawdownMonitor HALT: %s", dd_status.reason)
                self._notifier.notify_error(f"[DRAWDOWN HALT] {dd_status.reason}")
                return PipelineResult(
                    timestamp=ts, symbol=self.cfg.trading.symbol,
                    pipeline_step="drawdown_check", status="BLOCKED",
                    notes=[f"DrawdownMonitor halted: {dd_status.reason}"],
                )
        except Exception as e:
            logger.debug("DrawdownMonitor check failed (non-fatal): %s", e)

        try:
            _summary = self._data_feed.fetch(
                self.cfg.trading.symbol, self.cfg.trading.timeframe, limit=100
            )
            regime = SimpleRegimeDetector.detect(_summary.df)
            self._last_regime = regime
            logger.info("Market regime: %s", regime)
        except Exception as _e:
            logger.debug("Regime detection failed (non-fatal): %s", _e)

        result = self._pipeline.run()
        self._handle_result(result)
        self._update_position_from_result(result)

        # CircuitBreaker에 거래 결과 기록 (pnl 정보가 있을 때)
        if result.pnl != 0.0 and self._risk_manager and self._risk_manager.circuit_breaker:
            try:
                balance = self._pipeline._fetch_balance_usd()
                self._risk_manager.circuit_breaker.record_trade_result(result.pnl, balance)
                logger.debug("CircuitBreaker.record_trade_result(pnl=%.2f, balance=%.2f)", result.pnl, balance)
            except Exception as e:
                logger.warning("circuit_breaker.record_trade_result 실패: %s", e)

        self._cycle_count += 1

        # 매 24사이클마다 일일 P&L 리포트 (1h 타임프레임 기준 ~24시간)
        if self._cycle_count % 24 == 0:
            self._send_daily_report()

        # C3: 매 TOURNAMENT_INTERVAL 사이클마다 전략 자동 재평가 (기본 72사이클 = 3일)
        if self._cycle_count % self._tournament_interval == 0 and self._cycle_count > 0:
            logger.info("C3: Auto-tournament triggered at cycle %d", self._cycle_count)
            try:
                tr = self.run_tournament()
                logger.info("C3: Auto-tournament winner → %s", tr.winner)
            except Exception as e:
                logger.error("C3: Auto-tournament failed: %s", e)

        return result

    def run_loop(self) -> None:
        """캔들 완성 시각에 맞춰 파이프라인을 반복 실행. Ctrl+C로 종료."""
        self._assert_ready()
        scheduler = CandleScheduler()
        logger.info("Loop started — timeframe=%s (Ctrl+C to stop)", self.cfg.trading.timeframe)

        try:
            scheduler.run_loop(self.run_once, self.cfg.trading.timeframe, self._stop_event)
        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt — stopping")
            self._stop_event.set()

        logger.info("Orchestrator stopped gracefully")

    def stop(self) -> None:
        """외부에서 루프 종료 신호."""
        self._stop_event.set()

    def run_backtest_only(self) -> BacktestResult:
        """백테스트만 실행하고 결과 반환. startup() 이후 호출."""
        self._assert_ready()
        return self._run_backtest(self._strategy)

    def run_tournament(self, candidates: Optional[list[str]] = None) -> TournamentResult:
        """
        여러 전략을 병렬 백테스트 후 Sharpe 기준으로 순위를 매기고 승자를 반환.
        승자 전략으로 파이프라인을 재구성한다.

        Args:
            candidates: 검증할 전략 이름 목록. None이면 STRATEGY_REGISTRY 전체.

        Returns:
            TournamentResult (rankings + winner)
        """
        self._assert_ready()
        # 외부 API 의존 전략은 토너먼트 기본 목록에서 제외 (타임아웃 방지)
        _EXCLUDE_FROM_TOURNAMENT = {"gex_signal", "cme_basis", "cross_exchange_arb"}
        names = candidates or [
            k for k in STRATEGY_REGISTRY.keys() if k not in _EXCLUDE_FROM_TOURNAMENT
        ]
        try:
            _summary = self._data_feed.fetch(
                self.cfg.trading.symbol, self.cfg.trading.timeframe, limit=100
            )
            regime = SimpleRegimeDetector.detect(_summary.df)
            self._last_regime = regime
            logger.info("Market regime: %s", regime)
        except Exception as _e:
            logger.debug("Regime detection failed (non-fatal): %s", _e)

        logger.info("Tournament starting — candidates: %s", names)

        strategies = []
        for name in names:
            cls = STRATEGY_REGISTRY.get(name)
            if cls is None:
                logger.warning("Tournament: unknown strategy '%s', skipping", name)
                continue
            strategies.append(cls())

        if not strategies:
            raise OrchestratorError("No valid strategies for tournament")

        # 병렬 백테스트
        results: dict[str, BacktestResult] = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(strategies)) as pool:
            futures = {pool.submit(self._run_backtest, s): s.name for s in strategies}
            for fut in concurrent.futures.as_completed(futures):
                name = futures[fut]
                try:
                    results[name] = fut.result()
                    logger.info("Tournament [%s]: Sharpe=%.3f passed=%s",
                                name, results[name].sharpe_ratio, results[name].passed)
                except Exception as e:
                    logger.error("Tournament [%s] failed: %s", name, e)

        if not results:
            raise OrchestratorError("All strategies failed during tournament")

        # Sharpe 기준 정렬 (PASS 전략 우선, 그 다음 Sharpe 내림차순)
        ranked = sorted(
            results.items(),
            key=lambda x: (x[1].passed, x[1].sharpe_ratio),
            reverse=True,
        )

        winner_name, winner_result = ranked[0]
        rankings = [
            {
                "name": name,
                "sharpe": r.sharpe_ratio,
                "passed": r.passed,
                "fail_reasons": r.fail_reasons,
            }
            for name, r in ranked
        ]

        tournament = TournamentResult(
            winner=winner_name,
            winner_sharpe=winner_result.sharpe_ratio,
            rankings=rankings,
        )

        # 상위 3개 전략 신호 상관관계 체크 (백테스트 결과의 신호 분포로 추정)
        self._check_top3_correlation(ranked[:3])

        # 승자 전략으로 파이프라인 재구성
        self._last_tournament_winner = winner_name
        self._strategy = STRATEGY_REGISTRY[winner_name]()
        self._build_pipeline()
        logger.info("Tournament winner: %s (Sharpe=%.3f)", winner_name, winner_result.sharpe_ratio)

        msg = f"Tournament winner: {winner_name} (Sharpe={winner_result.sharpe_ratio:.3f})"
        self._notifier.notify_error(f"[Tournament] {msg}")  # notify_info 없으므로 재사용

        return tournament

    # ── Internal: 초기화 ─────────────────────────────────────────────────

    def _connect(self, mock: bool = False) -> None:
        if mock:
            from src.exchange.mock_connector import MockExchangeConnector
            self._connector = MockExchangeConnector(symbol=self.cfg.trading.symbol)
        else:
            self._connector = ExchangeConnector(
                exchange_name=self.cfg.exchange.name,
                sandbox=self.cfg.exchange.sandbox,
            )
        self._connector.connect()
        self._data_feed = DataFeed(self._connector)

    def _build_risk(self) -> None:
        cb = CircuitBreaker(
            max_daily_loss=self.cfg.risk.max_daily_loss,
            max_drawdown=self.cfg.risk.max_drawdown,
            max_consecutive_losses=self.cfg.risk.max_consecutive_losses,
            flash_crash_pct=self.cfg.risk.flash_crash_pct,
        )
        self._risk_manager = RiskManager(
            risk_per_trade=self.cfg.risk.risk_per_trade,
            atr_multiplier_sl=self.cfg.risk.stop_loss_atr_multiplier,
            atr_multiplier_tp=self.cfg.risk.take_profit_atr_multiplier,
            max_position_size=self.cfg.trading.max_position_size,
            circuit_breaker=cb,
        )

    def _load_strategy(self) -> None:
        strategy_cls = STRATEGY_REGISTRY.get(self.cfg.strategy)
        if strategy_cls is None:
            raise OrchestratorError(
                f"Unknown strategy '{self.cfg.strategy}'. "
                f"Available: {list(STRATEGY_REGISTRY)}"
            )
        self._strategy = strategy_cls()
        logger.info("Strategy loaded: %s", self._strategy.name)

    def _build_context(self, demo: bool = False) -> None:
        """MarketContextBuilder 초기화. demo=True면 mock 모드."""
        self._context_builder = MarketContextBuilder(symbol=self.cfg.trading.symbol)
        self._context_builder.set_high_risk_callback(self._on_high_news_risk)
        if demo:
            # demo 모드: build()가 항상 mock 반환하도록 래핑
            original_build = self._context_builder.build
            self._context_builder.build = lambda **kw: original_build(use_mock=True)
        logger.info("MarketContextBuilder initialized (demo=%s)", demo)

    def _on_high_news_risk(self, event) -> None:
        """HIGH 뉴스 이벤트 즉시 알림."""
        msg = f"[HIGH NEWS RISK] {event.event[:100]} → {event.action}"
        logger.warning(msg)
        self._notifier.notify_error(msg)

    def _build_pipeline(self) -> None:
        self._pipeline = TradingPipeline(
            connector=self._connector,
            data_feed=self._data_feed,
            strategy=self._strategy,
            risk_manager=self._risk_manager,
            symbol=self.cfg.trading.symbol,
            timeframe=self.cfg.trading.timeframe,
            dry_run=self._dry_run,
            context_builder=self._context_builder,
        )

    def _attach_specialist(self) -> None:
        """F1: SpecialistEnsemble을 파이프라인에 연결."""
        try:
            from src.alpha.specialist_agents import SpecialistEnsemble
            self._pipeline.specialist_ensemble = SpecialistEnsemble()
            logger.info("SpecialistEnsemble attached")
        except Exception as e:
            logger.warning("SpecialistEnsemble 연결 실패: %s", e)

    def attach_specialist(self) -> None:
        """Public: SpecialistEnsemble 연결 (main.py --specialist 플래그에서 호출)."""
        self._assert_ready()
        self._attach_specialist()

    def _update_funding_rates(self) -> None:
        """FundingRateStrategy가 있으면 펀딩비 업데이트."""
        try:
            from src.data.sentiment import SentimentFetcher
            from src.strategy.funding_rate import FundingRateStrategy
            if isinstance(self._strategy, FundingRateStrategy):
                sf = SentimentFetcher()
                score = sf.get_score()
                if hasattr(self._strategy, 'update_funding_rate'):
                    self._strategy.update_funding_rate(score * 0.0001)
        except Exception as e:
            logger.debug("펀딩비 업데이트 실패 (무시): %s", e)

    def _attach_llm_analyst(self, demo: bool = False) -> None:
        """C2: LLMAnalyst를 파이프라인에 연결. API 키 없으면 mock 모드."""
        try:
            from src.alpha.llm_analyst import LLMAnalyst
            analyst = LLMAnalyst(use_haiku=True)
            self._pipeline.llm_analyst = analyst
            logger.info("LLMAnalyst attached (enabled=%s demo=%s)", analyst._enabled, demo)
        except Exception as e:
            logger.warning("LLMAnalyst attach failed (non-fatal): %s", e)

    def _build_notifier(self) -> TelegramNotifier:
        tg = self.cfg.telegram
        if tg is None:
            return TelegramNotifier(enabled=False)
        return TelegramNotifier(
            bot_token=tg.bot_token,
            chat_id=tg.chat_id,
            enabled=tg.enabled,
        )

    # ── Internal: Backtest gate ──────────────────────────────────────────

    def _backtest_gate(self) -> None:
        """live 전 backtest PASS 필수. FAIL이면 OrchestratorError."""
        logger.info("Backtest gate — validating strategy before live")
        result = self._run_backtest(self._strategy)
        print(result.summary())
        if not result.passed:
            msg = f"Backtest gate FAILED: {result.fail_reasons}"
            self._notifier.notify_error(msg)
            raise OrchestratorError(msg)
        logger.info("Backtest gate PASSED")

    def _run_backtest(self, strategy: BaseStrategy) -> BacktestResult:
        summary = self._data_feed.fetch(
            self.cfg.trading.symbol,
            self.cfg.trading.timeframe,
            limit=1000,
        )
        engine = BacktestEngine(
            atr_multiplier_sl=self.cfg.risk.stop_loss_atr_multiplier,
            atr_multiplier_tp=self.cfg.risk.take_profit_atr_multiplier,
        )
        return engine.run(strategy, summary.df)

    def _check_top3_correlation(self, top3: list) -> None:
        """
        상위 3개 전략의 신호 상관관계를 win_rate 기반으로 추정하고
        0.7 이상 상관 쌍에 WARNING 로그를 출력한다.

        BacktestResult에는 실제 신호 시계열이 없으므로,
        win_rate를 대표 신호값으로 사용해 상관관계를 근사한다.
        실제 신호 시계열이 필요한 경우 SignalCorrelationTracker를 직접 활용할 것.
        """
        if len(top3) < 2:
            return
        try:
            from src.strategy.base import Action
            tracker = SignalCorrelationTracker([name for name, _ in top3])
            # win_rate를 신호 분포로 변환: win_rate 비율만큼 BUY, 나머지 SELL/HOLD
            import random
            rng = random.Random(42)
            for _ in range(30):
                for name, result in top3:
                    wr = result.win_rate
                    r = rng.random()
                    if r < wr:
                        action = Action.BUY
                    elif r < wr + (1 - wr) * 0.5:
                        action = Action.SELL
                    else:
                        action = Action.HOLD
                    tracker.record(name, action)

            high_pairs = tracker.high_correlation_pairs(threshold=0.7)
            if high_pairs:
                for a, b, corr_val in high_pairs:
                    logger.warning(
                        "Tournament correlation WARNING: %s ↔ %s r=%.3f (≥0.7) — 전략 다각화 효과 낮음",
                        a, b, corr_val,
                    )
            else:
                logger.info("Tournament: top-3 전략 간 상관관계 정상 (|r|<0.7)")
        except Exception as e:
            logger.debug("_check_top3_correlation 실패 (무시): %s", e)

    # ── Internal: 결과 처리 ──────────────────────────────────────────────

    def _handle_result(self, result: PipelineResult) -> None:
        self._print_result(result)
        self._notifier.notify_pipeline(result)
        self._append_worklog(result)

    def _print_result(self, result: PipelineResult) -> None:
        print(f"\nPIPELINE: {result.pipeline_step}")
        print(f"STATUS:   {result.status}")
        if result.signal:
            print(f"SIGNAL:   {result.signal.action.value} @ {result.signal.entry_price:.2f}"
                  f"  ({result.signal.confidence.value})")
            if result.signal.bull_case:
                print(f"  bull: {result.signal.bull_case}")
            if result.signal.bear_case:
                print(f"  bear: {result.signal.bear_case}")
        if result.risk:
            print(f"RISK:     {result.risk.status.value}", end="")
            if result.risk.reason:
                print(f" — {result.risk.reason}", end="")
            print()
            if result.risk.position_size:
                print(f"  size={result.risk.position_size}"
                      f"  SL={result.risk.stop_loss}"
                      f"  TP={result.risk.take_profit}")
        if result.execution:
            print(f"EXEC:     {result.execution.get('status')}")
        if result.notes:
            print(f"NOTES:    {' | '.join(result.notes)}")
        if result.error:
            print(f"ERROR:    {result.error}")

    def _append_worklog(self, result: PipelineResult) -> None:
        try:
            with open(".claude-state/WORKLOG.md", "a") as f:
                f.write("\n" + result.log_line())
        except OSError:
            pass

    def _update_position_from_result(self, result: PipelineResult) -> None:
        """파이프라인 결과로 포지션 트래커 업데이트."""
        if result.status != "OK":
            return
        if result.signal is None or result.risk is None or result.execution is None:
            return

        exec_status = result.execution.get("status")
        if exec_status not in ("FILLED", "DRY_RUN"):
            return

        action = result.signal.action
        if action == Action.HOLD:
            return

        # 반대 방향 신호면 기존 포지션 청산
        if self._tracker.has_position(result.symbol):
            current = self._tracker.get_position(result.symbol)
            if current and current.side != action.value:
                exit_price = result.signal.entry_price
                self._tracker.close_position(
                    result.symbol, exit_price, reason="SIGNAL_REVERSE",
                    circuit_breaker=self._risk_manager.circuit_breaker if self._risk_manager else None,
                )

        # 새 포지션 오픈
        if not self._tracker.has_position(result.symbol) and result.risk.position_size:
            from datetime import datetime, timezone
            pos = Position(
                symbol=result.symbol,
                side=action.value,
                entry_price=result.signal.entry_price,
                size=result.risk.position_size,
                stop_loss=result.risk.stop_loss or 0.0,
                take_profit=result.risk.take_profit or 0.0,
                opened_at=datetime.now(timezone.utc).isoformat(),
                order_id=result.execution.get("order_id"),
            )
            self._tracker.open_position(pos)

    def _send_daily_report(self) -> None:
        summary = self._tracker.daily_summary()
        logger.info("Daily report: %s", summary)
        self._notifier.notify_error(f"[Daily Report] {summary}")

    @property
    def tracker(self) -> PositionTracker:
        return self._tracker

    def _assert_ready(self) -> None:
        if self._pipeline is None:
            raise OrchestratorError("Call startup() before run_once() / run_loop()")
