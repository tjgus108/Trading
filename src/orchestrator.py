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
from typing import List, Optional

from src.alpha.context import MarketContextBuilder
from src.analysis.strategy_correlation import SignalCorrelationTracker
from src.analysis.regime_detector import SimpleRegimeDetector
from src.backtest.engine import BacktestEngine, BacktestResult
from src.config import AppConfig
from src.data.feed import DataFeed
from src.data.health_check import DataFeedsHealthCheck
from src.exchange.connector import ExchangeConnector
from src.notifier import TelegramNotifier
from src.pipeline.runner import PipelineResult, TradingPipeline
from src.position_tracker import Position, PositionTracker
from src.risk.manager import CircuitBreaker, RiskManager
from src.scheduler import CandleScheduler
from src.strategy.base import Action, BaseStrategy
from src.strategy.wick_analysis import WickAnalysisStrategy
from src.strategy.price_flow_index import PriceFlowIndexStrategy
from src.strategy.scalping_signal import ScalpingSignalStrategy
from src.strategy.swing_momentum import SwingMomentumStrategy
from src.strategy.order_flow_imbalance_v2 import OrderFlowImbalanceV2Strategy
from src.strategy.market_microstructure import MarketMicrostructureStrategy
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
from src.strategy.parabolic_sar_trend import ParabolicSARTrendStrategy
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
from src.strategy.pivot_point import PivotPointStrategy
from src.strategy.vortex import VortexStrategy
from src.strategy.dpo import DPOStrategy
from src.strategy.stc import STCStrategy
from src.strategy.dema_cross import DEMACrossStrategy
from src.strategy.trend_slope_filter import TrendSlopeFilterStrategy
from src.strategy.tema_cross import TEMACrossStrategy
from src.strategy.heikin_ashi import HeikinAshiStrategy
from src.strategy.coppock import CoppockStrategy
from src.strategy.fisher_transform import FisherTransformStrategy
from src.strategy.ppo import PPOStrategy
from src.strategy.cmo import CMOStrategy
from src.strategy.chande_momentum import ChandeMomentumStrategy
from src.strategy.zlema_cross import ZLEMACrossStrategy
from src.strategy.mcginley import McGinleyStrategy
from src.strategy.roc import ROCStrategy
from src.strategy.awesome_oscillator import AwesomeOscillatorStrategy
from src.strategy.connors_rsi import ConnorsRSIStrategy
from src.strategy.linear_regression import LinearRegressionStrategy
from src.strategy.williams_fractal import WilliamsFractalStrategy
from src.strategy.smi import SMIStrategy
from src.strategy.trima import TRIMAStrategy
from src.strategy.choppiness import ChoppinessStrategy
from src.strategy.alma import ALMAStrategy
from src.strategy.adaptive_rsi import AdaptiveRSIStrategy
from src.strategy.volatility_ratio import VolatilityRatioStrategy
from src.strategy.pmo import PMOStrategy
from src.strategy.rvi import RVIStrategy
from src.strategy.disparity_index import DisparityIndexStrategy
from src.strategy.tsi import TSIStrategy
from src.strategy.bop import BOPStrategy
from src.strategy.volatility_breakout import VolatilityBreakoutStrategy
from src.strategy.ichimoku_advanced import IchimokuAdvancedStrategy
from src.strategy.ichimoku_cloud_pos import IchimokuCloudPosStrategy
from src.strategy.guppy import GuppyStrategy
from src.strategy.apo import APOStrategy
from src.strategy.zscore_mean_reversion import ZScoreMeanReversionStrategy
from src.strategy.median_price import MedianPriceStrategy
from src.strategy.inside_bar import InsideBarStrategy
from src.strategy.gap_strategy import GapStrategy
from src.strategy.star_pattern import StarPatternStrategy
from src.strategy.doji_pattern import DojiPatternStrategy
from src.strategy.three_candles import ThreeCandlesStrategy
from src.strategy.harami import HaramiStrategy
from src.strategy.tweezer import TweezerStrategy
from src.strategy.pin_bar import PinBarStrategy
from src.strategy.vwap_cross import VWAPCrossStrategy
from src.strategy.ease_of_movement import EaseOfMovementStrategy
from src.strategy.sr_breakout import SRBreakoutStrategy
from src.strategy.hhll_channel import HHLLChannelStrategy
from src.strategy.vpt import VPTStrategy
from src.strategy.adl import ADLStrategy
from src.strategy.force_index import ForceIndexStrategy
from src.strategy.marubozu import MarubozuStrategy
from src.strategy.spinning_top import SpinningTopStrategy
from src.strategy.proc_trend import PRoCTrendStrategy
from src.strategy.r_squared import RSquaredStrategy
from src.strategy.body_momentum import BodyMomentumStrategy
from src.strategy.turtle_trading import TurtleTradingStrategy
from src.strategy.atr_trailing import ATRTrailingStrategy
from src.strategy.historical_volatility import HistoricalVolatilityStrategy
from src.strategy.price_action_momentum import PriceActionMomentumStrategy
from src.strategy.volume_oscillator import VolumeOscillatorStrategy
from src.strategy.price_range_breakout import PriceRangeBreakoutStrategy
from src.strategy.volume_oscillator_v2 import VolumeOscillatorV2Strategy
from src.strategy.price_envelope import PriceEnvelopeStrategy
from src.strategy.opening_range_breakout import OpeningRangeBreakoutStrategy
from src.strategy.session_high_low import SessionHighLowStrategy
from src.strategy.cci_breakout import CCIBreakoutStrategy
from src.strategy.frama import FRAMAStrategy
from src.strategy.vw_macd import VWMACDStrategy
from src.strategy.chandelier_exit import ChandelierExitStrategy
from src.strategy.vwap_band import VWAPBandStrategy
from src.strategy.vol_adj_momentum import VolAdjMomentumStrategy
from src.strategy.elder_impulse import ElderImpulseStrategy
from src.strategy.ha_trend import HATrendStrategy
from src.strategy.morning_evening_star import MorningEveningStarStrategy
from src.strategy.three_soldiers_crows import ThreeSoldiersAndCrowsStrategy
from src.strategy.laguerre_rsi import LaguerreRSIStrategy
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
from src.strategy.price_velocity import PriceVelocityStrategy
from src.strategy.multi_score import MultiScoreStrategy
from src.strategy.adx_regime import ADXRegimeStrategy
from src.strategy.obv_divergence import OBVDivergenceStrategy
from src.strategy.lr_channel import LRChannelStrategy
from src.strategy.momentum_reversal import MomentumReversalStrategy
from src.strategy.cup_handle import CupHandleStrategy
from src.strategy.relative_volume import RelativeVolumeStrategy
from src.strategy.pmo_strategy import PriceMomentumOscillator
from src.strategy.fib_retracement import FibRetracementStrategy
from src.strategy.ha_smoothed import HeikinAshiSmoothedStrategy
from src.strategy.keltner_rsi import KeltnerRSIStrategy
from src.strategy.chaikin_osc import ChaikinOscillatorStrategy
from src.strategy.alligator import AlligatorStrategy
from src.strategy.anchored_vwap import AnchoredVWAPStrategy
from src.strategy.zlmacd import ZeroLagMACDStrategy
from src.strategy.adaptive_stop import AdaptiveStopStrategy
from src.strategy.engulfing_zone import BullishEngulfingZoneStrategy
from src.strategy.tii_strategy import TrendIntensityIndexStrategy
from src.strategy.htf_ema import HigherTimeframeEMAStrategy
from src.strategy.donchian_midline import DonchianMidlineStrategy
from src.strategy.poc_strategy import POCStrategy
from src.strategy.bid_ask_imbalance import BidAskImbalanceStrategy
from src.strategy.gann_swing import GannSwingStrategy
from src.strategy.elder_force import ElderForceIndexStrategy
from src.risk.drawdown_monitor import AlertLevel, DrawdownMonitor
from src.strategy.price_deviation import PriceDeviationStrategy
from src.strategy.acceleration_band import AccelerationBandStrategy
from src.strategy.supertrend_multi import SupertrendMultiStrategy
from src.strategy.narrow_range import NarrowRangeStrategy
from src.strategy.failed_breakout import FailedBreakoutStrategy
from src.strategy.coppock_enhanced import CoppockEnhancedStrategy
from src.strategy.cumulative_delta import CumulativeDeltaStrategy
from src.strategy.volume_price_trend_v2 import VolumePriceTrendV2Strategy
from src.strategy.spread_analysis import SpreadAnalysisStrategy
from src.strategy.vwrsi import VolumeWeightedRSIStrategy
from src.strategy.hurst_strategy import HurstExponentStrategy
from src.strategy.entropy_strategy import ApproximateEntropyStrategy
from src.strategy.sr_bounce import SRBounceStrategy
from src.strategy.candle_score import CandleScoreStrategy
from src.strategy.momentum_div import MomentumDivergenceStrategy
from src.strategy.roc_ma_cross import ROCMACrossStrategy
from src.strategy.vpt_confirm import VolumePriceTrendConfirmStrategy
from src.strategy.gap_fill import GapFillStrategy
from src.strategy.opening_momentum import OpeningMomentumStrategy
from src.strategy.renko_trend import RenkoTrendStrategy
from src.strategy.wick_reversal import WickReversalStrategy
from src.strategy.ichimoku_breakout import IchimokuBreakoutStrategy
from src.strategy.macd_slope import MACDSlopeStrategy
from src.strategy.ema_ribbon import EMARibbonStrategy
from src.strategy.price_channel_break import PriceChannelBreakStrategy
from src.strategy.bb_keltner_squeeze import BBKeltnerSqueezeStrategy
from src.strategy.rsi_trend_filter import RSITrendFilterStrategy
from src.strategy.vol_adj_trend import VolAdjustedTrendStrategy
from src.strategy.dual_ema_cross import DualEMACrossStrategy
from src.strategy.breakout_confirm import BreakoutConfirmationStrategy
from src.strategy.linear_channel_rev import LinearChannelReversionStrategy
from src.strategy.price_rsi_div import PriceRSIDivergenceStrategy
from src.strategy.momentum_accel import MomentumAccelerationStrategy
from src.strategy.parabolic_momentum import ParabolicMomentumStrategy
from src.strategy.exhaustion_reversal import ExhaustionReversalStrategy
from src.strategy.swing_point import SwingPointStrategy
from src.strategy.confluence_zone import ConfluenceZoneStrategy
from src.strategy.adaptive_ma_cross import AdaptiveMACrossStrategy
from src.strategy.bull_bear_power import BullBearPowerStrategy
from src.strategy.absolute_strength_hist import AbsoluteStrengthHistStrategy
from src.strategy.overextension import OverextensionStrategy
from src.strategy.fvg_strategy import FairValueGapStrategy
from src.strategy.gartley_pattern import SimplifiedGartleyStrategy
from src.strategy.price_cluster import PriceClusterStrategy
from src.strategy.liquidity_sweep import LiquiditySweepStrategy
from src.strategy.market_maker_sig import MarketMakerStrategy
from src.strategy.ema_dynamic_support import EMADynamicSupportStrategy
from src.strategy.autocorr_strategy import AutoCorrelationStrategy
from src.strategy.adaptive_rsi_thresh import AdaptiveRSIThresholdStrategy
from src.strategy.mr_entry import MeanReversionEntryStrategy
from src.strategy.kijun_bounce import KijunBounceStrategy
from src.strategy.vol_price_confirm import VolumePriceConfirmStrategy
from src.strategy.trend_strength_filter import TrendStrengthFilterStrategy
from src.strategy.vol_spread_analysis import VolSpreadAnalysisStrategy
from src.strategy.crossover_confluence import CrossoverConfluenceStrategy
from src.strategy.breakout_retest import BreakoutRetestStrategy
from src.strategy.volatility_expansion import VolatilityExpansionStrategy
from src.strategy.cci_divergence import CCIDivergenceStrategy
from src.strategy.hybrid_trend_rev import HybridTrendReversionStrategy
from src.strategy.multi_factor import MultiFactorScoreStrategy
from src.strategy.stoch_momentum import StochasticMomentumStrategy
from src.strategy.volume_roc import VolumeROCStrategy
from src.strategy.smc_strategy import SmartMoneyConceptStrategy
from src.strategy.positional_scaling import PositionalScalingStrategy
from src.strategy.relative_strength import RelativeStrengthStrategy
from src.strategy.momentum_breadth import MomentumBreadthStrategy
from src.strategy.price_squeeze import PriceSqueezeStrategy
from src.strategy.inverse_fisher_rsi import InverseFisherRSIStrategy
from src.strategy.value_area import ValueAreaStrategy
from src.strategy.divergence_score import DivergenceScoreStrategy
from src.strategy.seasonal_cycle import SeasonalCycleStrategy
from src.strategy.trend_follow_break import TrendFollowBreakStrategy
from src.strategy.adaptive_threshold import AdaptiveThresholdStrategy
from src.strategy.volatility_cluster import VolatilityClusterStrategy
from src.strategy.volume_profile import VolumeProfileStrategy
from src.strategy.order_flow_imbalance import OrderFlowImbalanceStrategy
from src.strategy.mean_rev_zscore import MeanRevZScoreStrategy
from src.strategy.momentum_persistence import MomentumPersistenceStrategy
from src.strategy.fractal_break import FractalBreakStrategy
from src.strategy.market_structure_break import MarketStructureBreakStrategy
from src.strategy.regime_filter import RegimeFilterStrategy
from src.strategy.candle_pattern_score import CandlePatternScoreStrategy
from src.strategy.multi_tf_trend import MultiTFTrendStrategy
from src.strategy.keltner_breakout import KeltnerBreakoutStrategy
from src.strategy.acc_dist import AccDistStrategy
from src.strategy.price_momentum_osc import PriceMomentumOscStrategy
from src.strategy.channel_midline import ChannelMidlineStrategy
from src.strategy.breakout_confirm_v2 import BreakoutConfirmV2Strategy
from src.strategy.trendline_break import TrendlineBreakStrategy
from src.strategy.sr_flip import SRFlipStrategy
from src.strategy.volume_weighted_rsi import VolumeWeightedRSIStrategy as VolumeWeightedRSINewStrategy
from src.strategy.adaptive_momentum import AdaptiveMomentumStrategy
from src.strategy.pivot_point_rev import PivotPointRevStrategy
from src.strategy.heiken_ashi_trend import HeikenAshiTrendStrategy
from src.strategy.roc_divergence import ROCDivergenceStrategy
from src.strategy.tema_strategy import TEMAStrategy
from src.strategy.vwap_deviation import VWAPDeviationStrategy
from src.strategy.balance_of_power import BalanceOfPowerStrategy
from src.strategy.money_flow_index import MoneyFlowIndexStrategy
from src.strategy.trend_strength_index import TrendStrengthIndexStrategy
from src.strategy.wavetrend_osc import WaveTrendOscStrategy
from src.strategy.cyber_cycle import CyberCycleStrategy
from src.strategy.gaussian_channel import GaussianChannelStrategy
from src.strategy.ehlers_fisher import EhlersFisherStrategy
from src.strategy.sine_wave import SineWaveStrategy
from src.strategy.adaptive_cycle import AdaptiveCycleStrategy
from src.strategy.demarker import DeMarkerStrategy
from src.strategy.trend_exhaustion import TrendExhaustionStrategy
from src.strategy.high_low_channel import HighLowChannelStrategy
from src.strategy.trend_intensity_index import TrendIntensityIndexV2Strategy
from src.strategy.price_cycle_detector import PriceCycleDetectorStrategy
from src.strategy.momentum_quality import MomentumQualityStrategy
from src.strategy.normalized_price_osc import NormalizedPriceOscStrategy
from src.strategy.ema_envelope import EMAEnvelopeStrategy
from src.strategy.volatility_breakout_v2 import VolatilityBreakoutV2Strategy
from src.strategy.velocity_entry import VelocityEntryStrategy
from src.strategy.range_bias import RangeBiasStrategy
from src.strategy.composite_momentum import CompositeMomentumStrategy
from src.strategy.signal_line_cross import SignalLineCrossStrategy
from src.strategy.breakout_vol_ratio import BreakoutVolRatioStrategy
from src.strategy.mean_rev_band_v2 import MeanRevBandV2Strategy
from src.strategy.price_impact import PriceImpactStrategy
from src.strategy.smart_money_flow import SmartMoneyFlowStrategy
from src.strategy.micro_trend import MicroTrendStrategy
from src.strategy.ema_dynamic_band import EMADynamicBandStrategy
from src.strategy.oscillator_band import OscillatorBandStrategy
from src.strategy.price_action_filter import PriceActionFilterStrategy
from src.strategy.trend_momentum_blend import TrendMomentumBlendStrategy
from src.strategy.ema_cloud import EMACloudStrategy
from src.strategy.trend_strength_composite import TrendStrengthCompositeStrategy
from src.strategy.tick_volume import TickVolumeStrategy
from src.strategy.market_breadth_proxy import MarketBreadthProxyStrategy
from src.strategy.divergence_confirmation import DivergenceConfirmationStrategy
from src.strategy.dual_momentum import DualMomentumStrategy
from src.strategy.carry_strategy import CarryStrategy
from src.strategy.intraday_momentum import IntradayMomentumStrategy
from src.strategy.volatility_surface import VolatilitySurfaceStrategy
from src.strategy.regime_momentum import RegimeMomentumStrategy
from src.strategy.liquidity_score import LiquidityScoreStrategy
from src.strategy.trend_consistency import TrendConsistencyStrategy
from src.strategy.volume_weighted_momentum import VolumeWeightedMomentumStrategy
from src.strategy.price_velocity_filter import PriceVelocityFilterStrategy
from src.strategy.momentum_quality_v2 import MomentumQualityV2Strategy
from src.strategy.multi_timeframe_momentum import MultiTimeframeMomentumStrategy
from src.strategy.smart_beta import SmartBetaStrategy
from src.strategy.adaptive_trend import AdaptiveTrendStrategy
from src.strategy.price_compression_signal import PriceCompressionSignalStrategy
from src.strategy.keltner_channel_v2 import KeltnerChannelV2Strategy
from src.strategy.rsi_band import RSIBandStrategy
from src.strategy.breakout_pullback import BreakoutPullbackStrategy
from src.strategy.trend_follow_filter import TrendFollowFilterStrategy
from src.strategy.price_action_scorer import PriceActionScorerStrategy
from src.strategy.volatility_trend import VolatilityTrendStrategy
from src.strategy.momentum_divergence_v2 import MomentumDivergenceV2Strategy
from src.strategy.volume_spread_analysis_v2 import VolumeSpreadAnalysisV2Strategy
from src.strategy.gap_momentum import GapMomentumStrategy
from src.strategy.consolidation_break import ConsolidationBreakStrategy
from src.strategy.range_trading import RangeTradingStrategy
from src.strategy.trend_acceleration import TrendAccelerationStrategy
from src.strategy.candle_body_filter import CandleBodyFilterStrategy
from src.strategy.ema_fan import EMAFanStrategy
from src.strategy.entropy_momentum import EntropyMomentumStrategy
from src.strategy.fractal_dimension import FractalDimensionStrategy
from src.strategy.tail_risk_filter import TailRiskFilterStrategy
from src.strategy.price_path_efficiency import PricePathEfficiencyStrategy
from src.strategy.bollinger_squeeze import BollingerSqueezeStrategy
from src.strategy.relative_momentum_index import RelativeMomentumIndexStrategy
from src.strategy.market_pressure import MarketPressureStrategy
from src.strategy.trend_quality_filter import TrendQualityFilterStrategy
from src.strategy.cyclic_momentum import CyclicMomentumStrategy
from src.strategy.price_rhythm import PriceRhythmStrategy
from src.strategy.trend_fibonacci import TrendFibonacciStrategy
from src.strategy.mean_reversion_score import MeanReversionScoreStrategy
from src.strategy.stochastic_momentum import StochasticMomentumStrategy
from src.strategy.price_channel_filter import PriceChannelFilterStrategy
from src.strategy.volume_momentum_break import VolumeMomentumBreakStrategy
from src.strategy.price_structure_analysis import PriceStructureAnalysisStrategy
from src.strategy.adaptive_volatility import AdaptiveVolatilityStrategy
from src.strategy.trend_persistence import TrendPersistenceStrategy
from src.strategy.price_divergence_index import PriceDivergenceIndexStrategy
from src.strategy.trend_momentum_score import TrendMomentumScoreStrategy
from src.strategy.impulse_system import ImpulseSystemStrategy
from src.strategy.colored_candles import ColoredCandlesStrategy
from src.strategy.trend_break_confirm import TrendBreakConfirmStrategy
from src.strategy.momentum_mean_rev import MomentumMeanRevStrategy
from src.strategy.spread_momentum import SpreadMomentumStrategy
from src.strategy.higher_high_momentum import HigherHighMomentumStrategy
from src.strategy.mean_rev_bounce import MeanRevBounceStrategy

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
    "parabolic_sar_trend": ParabolicSARTrendStrategy,
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
    "vortex": VortexStrategy,
    "dpo": DPOStrategy,
    "stc": STCStrategy,
    "dema_cross": DEMACrossStrategy,
    "trend_slope_filter": TrendSlopeFilterStrategy,
    "tema_cross": TEMACrossStrategy,
    "heikin_ashi": HeikinAshiStrategy,
    "coppock": CoppockStrategy,
    "fisher_transform": FisherTransformStrategy,
    "ppo": PPOStrategy,
    "cmo": CMOStrategy,
    "chande_momentum": ChandeMomentumStrategy,
    "zlema_cross": ZLEMACrossStrategy,
    "mcginley": McGinleyStrategy,
    "roc": ROCStrategy,
    "awesome_oscillator": AwesomeOscillatorStrategy,
    "connors_rsi": ConnorsRSIStrategy,
    "demarker": DeMarkerStrategy,
    "linear_regression": LinearRegressionStrategy,
    "williams_fractal": WilliamsFractalStrategy,
    "smi": SMIStrategy,
    "trima": TRIMAStrategy,
    "choppiness": ChoppinessStrategy,
    "alma": ALMAStrategy,
    "adaptive_rsi": AdaptiveRSIStrategy,
    "volatility_ratio": VolatilityRatioStrategy,
    "pmo": PMOStrategy,
    "rvi": RVIStrategy,
    "disparity_index": DisparityIndexStrategy,
    "tsi": TSIStrategy,
    "bop": BOPStrategy,
    "volatility_breakout": VolatilityBreakoutStrategy,
    "ichimoku_advanced": IchimokuAdvancedStrategy,
    "ichimoku_cloud_pos": IchimokuCloudPosStrategy,
    "guppy": GuppyStrategy,
    "apo": APOStrategy,
    "zscore_mean_reversion": ZScoreMeanReversionStrategy,
    "median_price": MedianPriceStrategy,
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
    "sr_breakout": SRBreakoutStrategy,
    "hhll_channel": HHLLChannelStrategy,
    "vpt": VPTStrategy,
    "adl": ADLStrategy,
    "force_index": ForceIndexStrategy,
    "marubozu": MarubozuStrategy,
    "spinning_top": SpinningTopStrategy,
    "proc_trend": PRoCTrendStrategy,
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
    "frama": FRAMAStrategy,
    "vw_macd": VWMACDStrategy,
    "elder_impulse": ElderImpulseStrategy,
    "mean_reversion_channel": MeanReversionChannelStrategy,
    "pivot_reversal": PivotReversalStrategy,
    "range_expansion": RangeExpansionStrategy,
    "rsi_momentum_div": RSIMomentumDivStrategy,
    "dpo_cross": DPOCrossStrategy,
    "ha_trend": HATrendStrategy,
    "trend_strength": TrendStrengthStrategy,
    "vpt_signal": VPTSignalStrategy,
    "chandelier_exit": ChandelierExitStrategy,
    "vwap_band": VWAPBandStrategy,
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
    "price_velocity": PriceVelocityStrategy,
    "multi_score": MultiScoreStrategy,
    "adx_regime": ADXRegimeStrategy,
    "obv_divergence": OBVDivergenceStrategy,
    "lr_channel": LRChannelStrategy,
    "momentum_reversal": MomentumReversalStrategy,
    "cup_handle": CupHandleStrategy,
    "relative_volume": RelativeVolumeStrategy,
    "pmo_strategy": PriceMomentumOscillator,
    "fib_retracement": FibRetracementStrategy,
    "ha_smoothed": HeikinAshiSmoothedStrategy,
    "keltner_rsi": KeltnerRSIStrategy,
    "chaikin_osc": ChaikinOscillatorStrategy,
    "alligator": AlligatorStrategy,
    "anchored_vwap": AnchoredVWAPStrategy,
    "zlmacd": ZeroLagMACDStrategy,
    "adaptive_stop": AdaptiveStopStrategy,
    "engulfing_zone": BullishEngulfingZoneStrategy,
    "tii_strategy": TrendIntensityIndexStrategy,
    "htf_ema": HigherTimeframeEMAStrategy,
    "donchian_midline": DonchianMidlineStrategy,
    "price_deviation": PriceDeviationStrategy,
    "acceleration_band": AccelerationBandStrategy,
    "poc_strategy": POCStrategy,
    "bid_ask_imbalance": BidAskImbalanceStrategy,
    "supertrend_multi": SupertrendMultiStrategy,
    "narrow_range": NarrowRangeStrategy,
    "gann_swing": GannSwingStrategy,
    "elder_force": ElderForceIndexStrategy,
    "failed_breakout": FailedBreakoutStrategy,
    "coppock_enhanced": CoppockEnhancedStrategy,
    "vwrsi": VolumeWeightedRSIStrategy,
    "hurst_strategy": HurstExponentStrategy,
    "entropy_strategy": ApproximateEntropyStrategy,
    "sr_bounce": SRBounceStrategy,
    "candle_score": CandleScoreStrategy,
    "momentum_div": MomentumDivergenceStrategy,
    "roc_ma_cross": ROCMACrossStrategy,
    "vpt_confirm": VolumePriceTrendConfirmStrategy,
    "gap_fill": GapFillStrategy,
    "opening_momentum": OpeningMomentumStrategy,
    "renko_trend": RenkoTrendStrategy,
    "wick_reversal": WickReversalStrategy,
    "ichimoku_breakout": IchimokuBreakoutStrategy,
    "macd_slope": MACDSlopeStrategy,
    "ema_ribbon": EMARibbonStrategy,
    "price_channel_break": PriceChannelBreakStrategy,
    "bb_keltner_squeeze": BBKeltnerSqueezeStrategy,
    "rsi_trend_filter": RSITrendFilterStrategy,
    "vol_adj_trend": VolAdjustedTrendStrategy,
    "dual_ema_cross": DualEMACrossStrategy,
    "breakout_confirm": BreakoutConfirmationStrategy,
    "linear_channel_rev": LinearChannelReversionStrategy,
    "price_rsi_div": PriceRSIDivergenceStrategy,
    "momentum_accel": MomentumAccelerationStrategy,
    "swing_point": SwingPointStrategy,
    "confluence_zone": ConfluenceZoneStrategy,
    "adaptive_ma_cross": AdaptiveMACrossStrategy,
    "bull_bear_power": BullBearPowerStrategy,
    "absolute_strength_hist": AbsoluteStrengthHistStrategy,
    "overextension": OverextensionStrategy,
    "fvg_strategy": FairValueGapStrategy,
    "gartley_pattern": SimplifiedGartleyStrategy,
    "price_cluster": PriceClusterStrategy,
    "liquidity_sweep": LiquiditySweepStrategy,
    "market_maker_sig": MarketMakerStrategy,
    "ema_dynamic_support": EMADynamicSupportStrategy,
    "autocorr_strategy": AutoCorrelationStrategy,
    "adaptive_rsi_thresh": AdaptiveRSIThresholdStrategy,
    "mr_entry": MeanReversionEntryStrategy,
    "kijun_bounce": KijunBounceStrategy,
    "vol_price_confirm": VolumePriceConfirmStrategy,
    "trend_strength_filter": TrendStrengthFilterStrategy,
    "vol_spread_analysis": VolSpreadAnalysisStrategy,
    "crossover_confluence": CrossoverConfluenceStrategy,
    "breakout_retest": BreakoutRetestStrategy,
    "volatility_expansion": VolatilityExpansionStrategy,
    "cci_divergence": CCIDivergenceStrategy,
    "hybrid_trend_rev": HybridTrendReversionStrategy,
    "multi_factor": MultiFactorScoreStrategy,
    "stoch_momentum": StochasticMomentumStrategy,
    "volume_roc": VolumeROCStrategy,
    "smc_strategy": SmartMoneyConceptStrategy,
    "positional_scaling": PositionalScalingStrategy,
    "relative_strength": RelativeStrengthStrategy,
    "momentum_breadth": MomentumBreadthStrategy,
    "price_squeeze": PriceSqueezeStrategy,
    "inverse_fisher_rsi": InverseFisherRSIStrategy,
    "value_area": ValueAreaStrategy,
    "divergence_score": DivergenceScoreStrategy,
    "adaptive_threshold": AdaptiveThresholdStrategy,
    "volatility_cluster": VolatilityClusterStrategy,
    "seasonal_cycle": SeasonalCycleStrategy,
    "trend_follow_break": TrendFollowBreakStrategy,
    "volume_profile": VolumeProfileStrategy,
    "order_flow_imbalance": OrderFlowImbalanceStrategy,
    "mean_rev_zscore": MeanRevZScoreStrategy,
    "momentum_persistence": MomentumPersistenceStrategy,
    "fractal_break": FractalBreakStrategy,
    "market_structure_break": MarketStructureBreakStrategy,
    "regime_filter": RegimeFilterStrategy,
    "candle_pattern_score": CandlePatternScoreStrategy,
    "multi_tf_trend": MultiTFTrendStrategy,
    "keltner_breakout": KeltnerBreakoutStrategy,
    "acc_dist": AccDistStrategy,
    "price_momentum_osc": PriceMomentumOscStrategy,
    "channel_midline": ChannelMidlineStrategy,
    "breakout_confirm_v2": BreakoutConfirmV2Strategy,
    "trendline_break": TrendlineBreakStrategy,
    "sr_flip": SRFlipStrategy,
    "volume_weighted_rsi": VolumeWeightedRSINewStrategy,
    "adaptive_momentum": AdaptiveMomentumStrategy,
    "pivot_point_rev": PivotPointRevStrategy,
    "heiken_ashi_trend": HeikenAshiTrendStrategy,
    "roc_divergence": ROCDivergenceStrategy,
    "tema_strategy": TEMAStrategy,
    "vwap_deviation": VWAPDeviationStrategy,
    "balance_of_power": BalanceOfPowerStrategy,
    "money_flow_index": MoneyFlowIndexStrategy,
    "trend_strength_index": TrendStrengthIndexStrategy,
    "wavetrend_osc": WaveTrendOscStrategy,
    "cyber_cycle": CyberCycleStrategy,
    "laguerre_rsi": LaguerreRSIStrategy,
    "gaussian_channel": GaussianChannelStrategy,
    "ehlers_fisher": EhlersFisherStrategy,
    "sine_wave": SineWaveStrategy,
    "adaptive_cycle": AdaptiveCycleStrategy,
    "trend_exhaustion": TrendExhaustionStrategy,
    "high_low_channel": HighLowChannelStrategy,
    "trend_intensity_index": TrendIntensityIndexV2Strategy,
    "price_cycle_detector": PriceCycleDetectorStrategy,
    "momentum_quality": MomentumQualityStrategy,
    "normalized_price_osc": NormalizedPriceOscStrategy,
    "ema_envelope": EMAEnvelopeStrategy,
    "volatility_breakout_v2": VolatilityBreakoutV2Strategy,
    "cumulative_delta": CumulativeDeltaStrategy,
    "volume_price_trend_v2": VolumePriceTrendV2Strategy,
    "spread_analysis": SpreadAnalysisStrategy,
    "velocity_entry": VelocityEntryStrategy,
    "range_bias": RangeBiasStrategy,
    "composite_momentum": CompositeMomentumStrategy,
    "signal_line_cross": SignalLineCrossStrategy,
    "breakout_vol_ratio": BreakoutVolRatioStrategy,
    "mean_rev_band_v2": MeanRevBandV2Strategy,
    "price_impact": PriceImpactStrategy,
    "smart_money_flow": SmartMoneyFlowStrategy,
    "micro_trend": MicroTrendStrategy,
    "ema_dynamic_band": EMADynamicBandStrategy,
    "oscillator_band": OscillatorBandStrategy,
    "price_action_filter": PriceActionFilterStrategy,
    "trend_momentum_blend": TrendMomentumBlendStrategy,
    "tick_volume": TickVolumeStrategy,
    "market_breadth_proxy": MarketBreadthProxyStrategy,
    "divergence_confirmation": DivergenceConfirmationStrategy,
    "parabolic_momentum": ParabolicMomentumStrategy,
    "exhaustion_reversal": ExhaustionReversalStrategy,
    "dual_momentum": DualMomentumStrategy,
    "carry_strategy": CarryStrategy,
    "ema_cloud": EMACloudStrategy,
    "trend_strength_composite": TrendStrengthCompositeStrategy,
    "intraday_momentum": IntradayMomentumStrategy,
    "volatility_surface": VolatilitySurfaceStrategy,
    "regime_momentum": RegimeMomentumStrategy,
    "liquidity_score": LiquidityScoreStrategy,
    "price_velocity_filter": PriceVelocityFilterStrategy,
    "momentum_quality_v2": MomentumQualityV2Strategy,
    "trend_consistency": TrendConsistencyStrategy,
    "volume_weighted_momentum": VolumeWeightedMomentumStrategy,
    "pivot_point": PivotPointStrategy,
    "price_range_breakout": PriceRangeBreakoutStrategy,
    "volume_oscillator_v2": VolumeOscillatorV2Strategy,
    "multi_timeframe_momentum": MultiTimeframeMomentumStrategy,
    "smart_beta": SmartBetaStrategy,
    "keltner_channel_v2": KeltnerChannelV2Strategy,
    "rsi_band": RSIBandStrategy,
    "breakout_pullback": BreakoutPullbackStrategy,
    "trend_follow_filter": TrendFollowFilterStrategy,
    "price_action_scorer": PriceActionScorerStrategy,
    "volatility_trend": VolatilityTrendStrategy,
    "adaptive_trend": AdaptiveTrendStrategy,
    "price_compression_signal": PriceCompressionSignalStrategy,
    "momentum_divergence_v2": MomentumDivergenceV2Strategy,
    "volume_spread_analysis_v2": VolumeSpreadAnalysisV2Strategy,
    "gap_momentum": GapMomentumStrategy,
    "consolidation_break": ConsolidationBreakStrategy,
    "scalping_signal": ScalpingSignalStrategy,
    "swing_momentum": SwingMomentumStrategy,
    "order_flow_imbalance_v2": OrderFlowImbalanceV2Strategy,
    "market_microstructure": MarketMicrostructureStrategy,
    "range_trading": RangeTradingStrategy,
    "trend_acceleration": TrendAccelerationStrategy,
    "candle_body_filter": CandleBodyFilterStrategy,
    "ema_fan": EMAFanStrategy,
    "entropy_momentum": EntropyMomentumStrategy,
    "fractal_dimension": FractalDimensionStrategy,
    "wick_analysis": WickAnalysisStrategy,
    "price_flow_index": PriceFlowIndexStrategy,
    "tail_risk_filter": TailRiskFilterStrategy,
    "price_path_efficiency": PricePathEfficiencyStrategy,
    "bollinger_squeeze": BollingerSqueezeStrategy,
    "relative_momentum_index": RelativeMomentumIndexStrategy,
    "market_pressure": MarketPressureStrategy,
    "trend_quality_filter": TrendQualityFilterStrategy,
    "cyclic_momentum": CyclicMomentumStrategy,
    "price_rhythm": PriceRhythmStrategy,
    "trend_fibonacci": TrendFibonacciStrategy,
    "mean_reversion_score": MeanReversionScoreStrategy,
    "stochastic_momentum": StochasticMomentumStrategy,
    "price_channel_filter": PriceChannelFilterStrategy,
    "volume_momentum_break": VolumeMomentumBreakStrategy,
    "price_structure_analysis": PriceStructureAnalysisStrategy,
    "adaptive_volatility": AdaptiveVolatilityStrategy,
    "trend_persistence": TrendPersistenceStrategy,
    "price_divergence_index": PriceDivergenceIndexStrategy,
    "trend_momentum_score": TrendMomentumScoreStrategy,
    "impulse_system": ImpulseSystemStrategy,
    "colored_candles": ColoredCandlesStrategy,
    "trend_break_confirm": TrendBreakConfirmStrategy,
    "momentum_mean_rev": MomentumMeanRevStrategy,
    "spread_momentum": SpreadMomentumStrategy,
    "higher_high_momentum": HigherHighMomentumStrategy,
    "mean_rev_bounce": MeanRevBounceStrategy,
}


class OrchestratorError(Exception):
    pass


@dataclass
class TournamentResult:
    winner: str                          # 전략 이름
    winner_sharpe: float
    rankings: list[dict]                 # [{name, sharpe, passed, fail_reasons}]
    wf_stable: Optional[bool] = None    # Walk-Forward 안정성 (None=미실행)
    wf_fallback: bool = False            # True면 1위 불안정 → 2위로 fallback

    def summary(self) -> str:
        lines = ["TOURNAMENT RESULT:"]
        for i, r in enumerate(self.rankings, 1):
            verdict = "PASS" if r["passed"] else "FAIL"
            lines.append(
                f"  #{i} {r['name']:25s}  Sharpe={r['sharpe']:.3f}  {verdict}"
                + (f"  fail={r['fail_reasons']}" if r["fail_reasons"] else "")
            )
        wf_tag = ""
        if self.wf_stable is not None:
            wf_tag = f"  WF={'STABLE' if self.wf_stable else 'UNSTABLE'}"
        if self.wf_fallback:
            wf_tag += "  (fallback to #2)"
        lines.append(f"  WINNER → {self.winner} (Sharpe={self.winner_sharpe:.3f}){wf_tag}")
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
        # Implementation Shortfall 누적 메트릭
        self._impl_shortfall_samples: List[float] = []
        self._drawdown_monitor = DrawdownMonitor(
            max_drawdown_pct=getattr(cfg.risk, "max_drawdown", 0.20),
        )
        self._health_checker = DataFeedsHealthCheck()

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
                from datetime import datetime, timezone
                ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
                if dd_status.alert_level == AlertLevel.FORCE_LIQUIDATE:
                    logger.critical(
                        "DrawdownMonitor FORCE_LIQUIDATE: %s — stopping bot loop",
                        dd_status.reason,
                    )
                    self._notifier.notify_error(
                        f"[FORCE_LIQUIDATE] {dd_status.reason} — 봇 루프 정지"
                    )
                    self._stop_event.set()
                else:
                    logger.warning("DrawdownMonitor HALT: %s", dd_status.reason)
                    self._notifier.notify_error(f"[DRAWDOWN HALT] {dd_status.reason}")
                return PipelineResult(
                    timestamp=ts, symbol=self.cfg.trading.symbol,
                    pipeline_step="drawdown_check", status="BLOCKED",
                    notes=[f"DrawdownMonitor halted [{dd_status.alert_level.value}]: {dd_status.reason}"],
                )
        except Exception as e:
            logger.debug("DrawdownMonitor check failed (non-fatal): %s", e)

        # DataFeeds health check
        try:
            if self._data_feed is not None:
                self._health_checker.register_feed("primary_rest", self._data_feed, feed_type="rest")
            _hc = self._health_checker.check_all()
            if "all_feeds_disconnected" in _hc.anomalies:
                from datetime import datetime, timezone
                _ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
                logger.critical("DataFeeds all_disconnected — skipping pipeline")
                self._notifier.notify_error("[DATA FEED] 모든 피드 연결 끊김 — 파이프라인 스킵")
                return PipelineResult(
                    timestamp=_ts, symbol=self.cfg.trading.symbol,
                    pipeline_step="health_check", status="BLOCKED",
                    notes=["all_feeds_disconnected"],
                )
            if "operating_in_degraded_mode" in _hc.anomalies:
                logger.warning("DataFeeds degraded_mode: %s", _hc)
        except Exception as _hce:
            logger.debug("DataFeeds health check failed (non-fatal): %s", _hce)

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

        # Implementation Shortfall 누적 추적
        if result.impl_shortfall_bps is not None:
            self._impl_shortfall_samples.append(result.impl_shortfall_bps)
            avg_sf = sum(self._impl_shortfall_samples) / len(self._impl_shortfall_samples)
            logger.info(
                "[metrics] impl_shortfall cycle=%d value=%.2fbps avg=%.2fbps n=%d",
                self._cycle_count,
                result.impl_shortfall_bps,
                avg_sf,
                len(self._impl_shortfall_samples),
            )

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
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(strategies), 6)) as pool:
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

        # Walk-Forward 검증: 1위 전략의 안정성 확인, 불안정하면 2위로 fallback
        wf_stable: Optional[bool] = None
        wf_fallback = False
        final_winner_name = winner_name
        final_winner_result = winner_result

        try:
            from src.backtest.walk_forward import WalkForwardValidator
            wf_data = self._data_feed.fetch(
                self.cfg.trading.symbol, self.cfg.trading.timeframe, limit=1000
            )
            if len(wf_data.df) >= 250:
                wf_validator = WalkForwardValidator(
                    train_window=200, test_window=50, step_size=50
                )
                wf_result = wf_validator.validate(wf_data.df, STRATEGY_REGISTRY[winner_name]())
                wf_stable = wf_result.consistency_score >= 0.5
                logger.info(
                    "WalkForward [%s]: consistency=%.2f windows=%d → %s",
                    winner_name,
                    wf_result.consistency_score,
                    wf_result.windows,
                    "STABLE" if wf_stable else "UNSTABLE",
                )
                if not wf_stable and len(ranked) >= 2:
                    fallback_name, fallback_result = ranked[1]
                    logger.warning(
                        "WalkForward: winner '%s' is UNSTABLE → falling back to '%s'",
                        winner_name, fallback_name,
                    )
                    final_winner_name = fallback_name
                    final_winner_result = fallback_result
                    wf_fallback = True
            else:
                logger.debug(
                    "WalkForward skipped: insufficient data (%d < 250)", len(wf_data.df)
                )
        except Exception as _wf_err:
            logger.warning("WalkForward validation failed (non-fatal): %s", _wf_err)

        tournament = TournamentResult(
            winner=final_winner_name,
            winner_sharpe=final_winner_result.sharpe_ratio,
            rankings=rankings,
            wf_stable=wf_stable,
            wf_fallback=wf_fallback,
        )

        # 상위 3개 전략 신호 상관관계 체크 (백테스트 결과의 신호 분포로 추정)
        self._check_top3_correlation(ranked[:3])

        # 승자 전략으로 파이프라인 재구성
        self._last_tournament_winner = final_winner_name
        self._strategy = STRATEGY_REGISTRY[final_winner_name]()
        self._build_pipeline()
        logger.info(
            "Tournament winner: %s (Sharpe=%.3f)%s",
            final_winner_name,
            final_winner_result.sharpe_ratio,
            " [WF-fallback]" if wf_fallback else "",
        )

        msg = (
            f"Tournament winner: {final_winner_name}"
            f" (Sharpe={final_winner_result.sharpe_ratio:.3f})"
            + (" [WF-fallback]" if wf_fallback else "")
        )
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
        if result.impl_shortfall_bps is not None:
            print(f"IMPL_SF:  {result.impl_shortfall_bps:+.2f}bps")
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
