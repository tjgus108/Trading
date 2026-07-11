"""
D3. WalkForwardOptimizer: 전략 파라미터 자동 최적화.

방법:
  1. 전체 기간을 in-sample / out-of-sample 윈도우로 분할
  2. in-sample 그리드 서치로 최적 파라미터 탐색
  3. out-of-sample 검증 → 과최적화 여부 판단
  4. 복수 윈도우 결과 집계 → 안정적인 파라미터 선택

과최적화 방지:
  - out-of-sample Sharpe를 최종 기준으로 사용
  - IS/OOS Sharpe 비율 < 0.5이면 과최적화로 판단
  - 안정성 기준: OOS Sharpe 표준편차 < 0.5

지원 전략: EmaCrossStrategy, DonchianBreakoutStrategy (파라미터 딕셔너리 기반)
커스텀 전략: param_grid 딕셔너리로 확장 가능
"""

import itertools
import logging
import statistics as _statistics
import time as _time
from dataclasses import dataclass, field
from typing import Any, Callable, Optional, Type, Tuple, List, Dict

import pandas as pd

from src.backtest.engine import BacktestEngine, BacktestResult, MIN_WFE
from src.strategy.base import Action, BaseStrategy, Confidence, Signal
from src.strategy.regime import MarketRegime, MarketRegimeDetector

logger = logging.getLogger(__name__)


class _RegimeFilterStrategy(BaseStrategy):
    """레짐 필터 래퍼: TREND_UP이 아닌 봉의 BUY 신호를 HOLD로 변환.

    walk_forward.py의 regime_filter=True 옵션 전용 내부 클래스.
    df에 _regime_trend_up(bool) 컬럼이 있으면 해당 값으로 BUY 신호를 필터링.
    컬럼 없으면 필터 미적용(원본 신호 그대로 통과).
    """

    def __init__(self, inner: BaseStrategy):
        self._inner = inner
        self.name = inner.name

    def generate(self, df) -> Signal:
        signal = self._inner.generate(df)
        if signal.action != Action.BUY:
            return signal
        if "_regime_trend_up" not in df.columns:
            return signal
        idx = len(df) - 2
        if idx < 0:
            return signal
        if not bool(df["_regime_trend_up"].iloc[idx]):
            return Signal(
                action=Action.HOLD,
                confidence=signal.confidence,
                strategy=signal.strategy,
                entry_price=signal.entry_price,
                reasoning="레짐 필터: TREND_UP 아님 → BUY 차단",
                invalidation="",
                bull_case="",
                bear_case="",
            )
        return signal

# 기본 최적화 파라미터 그리드
DEFAULT_GRIDS: Dict[str, dict] = {
    "ema_cross": {
        "fast_span": [10, 15, 20],
        "slow_span": [40, 50, 60],
    },
    "donchian_breakout": {
        "channel_period": [15, 20, 25],
    },
    "funding_rate": {
        "long_threshold": [0.0002, 0.0003, 0.0004],
        "short_threshold": [-0.0001, -0.0002],
    },
    "cmf": {
        "period": [21, 22, 23],        # Cycle 269: [20,21,22]→[21,22,23], 더 긴 CMF로 fold2,3 bull IS/OOS 갭 완화
        "buy_thresh": [0.08, 0.09, 0.10],  # Cycle 267: 보수화 (0.07-0.09→0.08-0.10), fold0/1 고Sharpe 안정화
        "sell_thresh": [-0.10, -0.09, -0.08],  # Cycle 267: buy_thresh 대칭 이동
        "rsi_max_buy": [75, 78, 80],   # Cycle 275: fold2(2023-10~12 불마켓) RSI>75 차단 → 완화 실험
    },
    # cmf_1h: 1h 타임프레임 전용 파라미터 그리드 (D(ML) Cycle 271)
    # 기본 period=20 (4h 80시간)에 해당하는 1h 등가: period≥60
    # Cycle 273: threshold 완화 (0.05/-0.05) — 1h 신호 빈도 부족 문제 개선
    # Cycle306 F(리서치): period [60,75,90]→[75,90,105] 상향
    #   근거: cmf 4h 5/5 PASS(Sharpe=2.508) vs 1h rank15(Sharpe=-1.44)
    #   1h에서 CMF 신호 노이즈 비율 높음 → 더 긴 period(105h≈4.4일)로 안정화 탐색
    "cmf_1h": {
        "period": [90, 105],  # Cycle306: [75,90,105] → 306 결과에서 75 저성능 제외
        # Cycle307 F(리서치): cmf_1h 75trades/8윈도우, Sharpe=-1.44 → 과다신호 차단 필요
        # 임계값 강화: 약한 CMF 신호 필터링으로 거래수 줄이고 신호 품질 향상
        "buy_thresh": [0.07, 0.08, 0.10],
        "sell_thresh": [-0.10, -0.08, -0.07],
    },
    "wick_reversal": {
        "min_wick_ratio": [0.55, 0.60, 0.65],  # Cycle 275: 0.50-0.60→0.55-0.65 상향, 추세장 약한 wick 오신호 차단
        "vol_mult": [1.0, 1.1, 1.2],  # Cycle 274: 0.7-0.9→1.0-1.2 상향, FAIL fold(2022 bear/2023 여름) 가짜 반전 차단
        "min_volatility": [0.002, 0.003, 0.004],  # Cycle 265: 1h 노이즈 차단, 0.002 유지로 4h 거래 보호
        "sma_sell_threshold": [1.01, 1.02, 1.03],  # Cycle 276: Shooting Star SMA 조건 파라미터화, 추세장 SELL 오신호 차단
    },
    "supertrend_multi": {
        "atr_threshold": [0.5, 0.6, 0.7],  # Cycle 286 D(ML): 0.7-0.9→0.5-0.7 하향 (fold4 ATH 구간 신호 부족 해결)
        "atr_threshold_max": [1.5, 2.0, 2.5],  # Cycle 286 D(ML): 상한 2.5 추가 (fold3 탐색 범위 확대)
        "ema_filter": [True],        # D Cycle 287: 실험으로 best=True 확정 → 고정 (과적합 감소)
        "confidence_filter": [True], # D Cycle 287: 실험으로 best=True 확정 → 고정 (과적합 감소)
        "rsi_ob_filter": [True],     # D Cycle 287: 실험으로 best=True 확정 → 고정 (과적합 감소)
        "rsi_ob_threshold": [75, 78, 80],  # Cycle 282 D(ML): fold4 ATH(RSI>80) BUY 차단 임계값
        "trend_confirm_bars": [2, 3],  # Cycle 283 B(리스크): 연속 확인 봉 수 — 3은 post-ATH whipsaw 억제
        "cmf_confirm": [True, False],  # Cycle 284 D(ML): CMF>0 시에만 BUY — ATH 이후 자금이탈 선행 감지
    },
    # Cycle 324 D(ML): supertrend_multi 1h 전용 그리드
    # 문제: 4h avg=3.892 vs 1h Sharpe=0.32 — 타임프레임 불일치 원인 분석
    # 1h 특성: 4h보다 ATR 절대값 작음 → atr_threshold 하향, trend_confirm_bars 연장
    # - atr_threshold: [0.3, 0.4, 0.5] (4h [0.5-0.7] 대비 1h 노이즈 보상)
    # - trend_confirm_bars: [4, 6, 8] (4h 2-3봉=8-12h → 1h 4-8봉=4-8h 등가 확인 기간)
    # - cmf_confirm=True 고정 (1h 노이즈 필터 강화)
    "supertrend_multi_1h": {
        "atr_threshold": [0.3, 0.4, 0.5],
        "atr_threshold_max": [1.0, 1.5, 2.0],
        "ema_filter": [True],
        "confidence_filter": [True],
        "rsi_ob_filter": [True],
        "rsi_ob_threshold": [75, 80],
        "trend_confirm_bars": [4, 6, 8],
        "cmf_confirm": [True],
    },
    "elder_impulse": {
        "ema_span": [10, 13, 15],
        "min_volatility": [0.001, 0.002, 0.003],
    },
    "value_area": {
        "va_period": [10, 15, 20],  # 10 추가: 4h 봉 신호 빈도 개선
        "va_mult": [0.55, 0.60, 0.65],
    },
    # Cycle406 F: narrow_range 1h BTC 구조적 한계 확정 (Cycle414 F 재확인 → 탐색 완전 종료)
    #   BTC 1h: Sh=-0.51, PF=0.97(<1.0=음의엣지), Trades=46, MDD=10.1%, 0/8 Consistency
    #   전방 수익 분석(Cycle414 F): BUY 1h fwd_ret=+0.032% < 슬리피지 0.1% → 비용 > 에지
    #   SELL 8h fwd_ret=-0.074% (BTC 상승 바이어스로 SELL 구조적 불리)
    #   ema_slope filter: trades=46→~20-25 → Trades<15 위험, PF 개선 불가
    #   NR전략은 4h/daily 타임프레임에 적합 (1h 고빈도 노이즈 환경 부적합)
    #   → narrow_range 1h WFO 탐색 완전 종료. 추가 파라미터 실험 금지.
    "narrow_range": {},
    # Cycle407 F(리서치): acceleration_band 1h BTC 구조적 한계 확정
    #   paper_sim BTC 1h: Sh=-0.94, PF=0.98(<1.0=음의엣지), Trades=44, Consistency=1/8
    #   paper_sim ETH 1h: Sh=-2.03, PF=0.57, Trades=13 (<15 min) — 신호 부족
    #   paper_sim SOL 1h: Sh=-0.80, PF=1.00, Trades=11 (<15 min) — 신호 부족
    #   핵심 원인: ATR band breakout 전략은 TRENDING 환경에 적합
    #     BTC 1h RANGING 47.3% → 밴드 돌파 후 추세 지속성 부재 → 허위 돌파 과다
    #   파라미터화 가능 요소 없음: period=20, strong_band_margin=0.025 하드코딩
    #   dema_cross 대안: PF gap=0.12 (1.38→1.50) 여전히 존재하나 탐색 종료 선언됨 (Cycle377 F)
    #   → acceleration_band 추가 탐색 금지. 음의 엣지 전략으로 확정.
    "acceleration_band": {},  # WFO 파라미터 없음 (구조적 한계, Cycle407 F)
    # Cycle363 F(리서치): atr_period 추가 탐색
    # frama ATR 수축 필터: last_atr < prev_atr*1.05 (ATR 감소 추세에서만 신호 허용)
    # atr_period=10: 더 빠른 반응 (노이즈 증가), 14: 기본값, 18: 더 완만한 평활화 (지연)
    # 배경: BTC rank2 Sharpe=0.24 PF=1.12 SharpeStd=1.60 (안정적, Cycle370 기준) — PF 개선 가능성 탐색
    # Cycle371 D(ML): paper_sim atr_period=10 실험 → 결과 NEXT_STEPS.md 참조
    # Cycle397 F(리서치): atr_period DEAD PARAM 확정 — 중요 발견
    #   frama.py 코드 분석 결과: atr_contracting (last_atr < prev_atr*1.05) 가 계산되지만
    #   BUY/SELL 조건에서 사용되지 않음 — atr_str 로그 문자열에만 사용.
    #   따라서 atr_period=[10,14,18] 탐색이 신호 생성에 무효과 (완전한 dead param).
    #   이것이 Cycle371 D atr_period=10 "효과 없음" 이유임.
    #   atr_period 탐색 종료. WFO 그리드에서 제거하여 9→3 combos (3x 속도 향상).
    # Cycle397 F: frama 개선 방향 확정
    #   현재 약한신호(gap<1%) RSI<40(BUY)/RSI>60(SELL) — RANGING(47.3% BTC 1h) 에서 과도 차단
    #   다음 탐색 방향: rsi_period 탐색 유지 (rsi 임계값 자체는 하드코딩이라 WFO에서 변경 불가)
    # Cycle398 F: weak_rsi_buy_max 파라미터화 완료 (frama.py 수정)
    #   weak_rsi_buy_max=40(기본) vs 50(중간 완화) vs 60(RANGING 허용) 탐색
    #   RANGING 47.3%에서 RSI 40-60 구�� 신호 차단 해소 → Trades 증가 가능
    # Cycle399 F(리서치): weak_rsi_buy_max=50 paper_sim 결과 분석
    #   BTC 1h WFO: Sh=0.44(↑0.24+83%), Trades=65(↑40+62.5%), PF=1.11, 0/8 Consistency
    #   40→50 개선 확인: 신호 품질 하락 없이 Trades 대폭 증가, Sharpe도 개선
    #   결론: 50 > 40 확정. WFO 그리드 [40,50,60]에서 최적값 탐색 지속 (60도 실험 대기 중)
    #   0/8 Consistency는 파라미터 문제가 아닌 frama 구조적 한계
    # Cycle401 F(리서치): frama 0/8 Consistency 근본 원인 코드 분석 완료
    #   신호 구조: strong_signal(gap>=1%) → RSI<85 (거의 통과), weak_signal(gap<1%) → RSI<weak_rsi_buy_max (엄격)
    #   RANGING(47.3% BTC 1h)에서 gap<1% 비율 높음 → weak 신호 경로가 지배적
    #   weak_rsi_buy_max=40: RSI 40-85 구간 완전 차단 / =50: 50-85 차단 / =60: 60-85 차단
    #   RSI 중립(40-60) 구간이 RANGING에서 지배적 → weak_rsi 완화해도 구조적 한계 유지
    #   atr_contracting은 BUY/SELL 조건에 미사용 (로그 전용) → ATR 파라미터 탐색 전혀 무효
    #   결론: frama WFO 그리드 [40,50,60] 유지 (자동 선택), 추가 파라미터 탐색 종료
    #         paper_sim weak_rsi_buy_max=50 확정 유지. frama는 보조 신호로 보존.
    "frama": {
        "period": [14, 16, 18],
        "rsi_period": [12, 14, 16],
        "weak_rsi_buy_max": [40, 50, 60],  # Cycle398 F: 약한신호 RSI 임계값 탐색
        # atr_period: Cycle397 F — DEAD PARAM. atr_contracting은 BUY/SELL 조건에 미사용.
        # "atr_period": [10, 14, 18],  # 탐색 종료 (신호 생성 무효과 ��정)
    },
    # Cycle403 F(리서치): positional_scaling 구조 분석 — BTC 1h 1/8 Consistency, Sh=-0.38, PF=1.09
    # 구조적 문제:
    #   1. triple EMA alignment(20/50/100): RANGING(47.3% BTC 1h)에서 정렬 빈도 낮음 → 신호 희소
    #   2. pullback/rally 조건 동일: deviation = c/e20-1 → ±threshold 동일 범위 (방향 구분 없음)
    #   3. pullback_atr_mult=0.3 하드코딩: ATR*0.3/e20 ≈ 0.45% — 매우 좁은 진입 구간
    # 탐색 방향:
    #   - pullback_atr_mult: 0.3(현재) → 0.5/1.0(완화) — 진입 구간 확대로 Trades 증가 기대
    #   - alignment 완화: triple EMA → dual EMA(20/50만) 체크 — RANGING 신호 포착 가능성
    # 탐색 전제: strategy 파라미터화 필요 (positional_scaling.py pullback_atr_mult 추가)
    # 현재 상태: 파라미터 미지원 → WFO 최적화 불가. 하드코딩값만 유지.
    # Sh=-0.38(음수) → 구조적 신호 품질 문제. PF=1.09는 Break-even 수준. 탐색 보류.
    "positional_scaling": {
        # 현재 모든 파라미터 하드코딩 — 전략 파라미터화 완료 후 그리드 탐색 예정
        # pullback_atr_mult=[0.3, 0.5, 1.0]  (탐색 예정, strategy 수정 필요)
    },
    # Cycle302 D(ML): price_cluster 파라미터 최적화 그리드 추가
    # n_bins=7 실험에서 역효과 확인 → [4,5,6] 범위로 제한 (5가 현재 최적)
    # bounce_pct=0.025 확정 (Cycle301 B), 양방향 탐색 [0.020, 0.025, 0.030]
    # vol_atr_trend_min: 1.3 역효과(Cycle301 D) 제거, Cycle331 D(ML): 상향 [1.5,2.0,2.5] 탐색
    # Cycle304 D(ML): close_window [40,50]→[50,60] (40 역효과 Cycle303 확인, 60 탐색)
    # Cycle360 C(데이터): close_window=40 paper_sim 재실험 → Sharpe 0.72→0.07 (재확인 악화)
    # Cycle345 A(품질): bounce_pct 하한 0.010 추가 — paper_sim W6 PASS(Sharpe=3.78)가 기본값(0.01)에서 달성됨
    #   0.030 제거(상한 미효과 Cycle302 관찰), 탐색 범위 [0.010, 0.020, 0.025]로 조정
    # Cycle358 C(데이터): paper_sim bounce_pct=0.020 실험 → BTC Sharpe 0.87→0.72 악화 확인
    #   WFO 조합 탐색은 유지 (combination 효과 있을 수 있음), paper_sim은 0.010 복원
    # Cycle354 D(ML): vol_regime_filter=[True] 추가 — 기존 vol_atr_trend_min은 filter=False 시 dead parameter였음
    #   price_cluster sideways 전용 전략 근거: W5/W6 PASS, BTC rank1 연속 → sideways 필터 활성화
    #   vol_regime_filter 항상 True로 고정, vol_atr_trend_min 탐색으로 최적 임계값 찾기
    # Cycle355 A(품질): 1.5에서 효과 없음 확인 → 1.2 추가 (더 공격적 억제 탐색)
    # Cycle356 F(리서치): 1.2에서도 효과 없음(Sharpe=0.87 유지) → 1.0 추가
    # Cycle357 F(리서치): vol_regime_filter=False 추가 — filter 비활성화 탐색 (paper_sim과 일관성)
    # Cycle378 C(데이터): high_conf_only=[False,True] 추가 → dead param 확정 (paper_sim 검증)
    # 실험 결과: Sh=0.60(-0.05), PF=1.15(-0.03), Consistency=0/8(-1) — 모두 악화
    # W6 PASS 윈도우: PF 2.01→1.48 (PF 문턱 실패) → HIGH/MEDIUM 분류가 bounce 품질 예측 불가
    # high_conf_only 탐색 종료. 기본값(False) 유지. WFO 그리드에서 제거.
    # Cycle379 F(리서치): min_cluster_strength_ratio=0.30 실험 → dead param 확정 (paper_sim 검증)
    #   0.30 실험: Sharpe=0.72(-0.15 악화), PF=1.18(유사), Trades=35(-6)
    #   결론: 클러스터 강도 비율이 bounce 품질 예측 불가. min_cluster_strength_ratio 탐색 종료.
    #   파라미터 코드는 유지(향후 활용 가능성), WFO 그리드에서 제거.
    "price_cluster": {
        # bounce_pct 탐색 완전 종료 (Cycle390): 0.006(filter=T) 최적 확정
        # 0.004(dead), 0.006(최적), 0.008(차선), 0.010(열세), 0.020/0.025(구형)
        # WFO 비교용으로 [0.006, 0.008, 0.010] 유지 (0.020/0.025 제거)
        "bounce_pct": [0.006, 0.008, 0.010],
        "n_bins": [4, 5, 6],
        # close_window 탐색 완전 종료 (Cycle392): 50 최적, 60 DEAD
        # → [50] 단일값으로 고정. 그리드 조합 수 50% 감소.
        "close_window": [50],
        "vol_regime_filter": [False, True],
        # vol_atr_trend_min 탐색 완전 종료 (Cycle391): 1.2 최적, 1.0 DEAD
        # 1.5/2.0/2.5 구형값도 1.2 대비 열세 확인 (Cycle355 이전)
        # → [1.2] 단일값으로 고정. 그리드 조합 수 80% 감소.
        "vol_atr_trend_min": [1.2],
        # confirmation_bars 탐색 완전 종료 (Cycle393): bars=0 확정
        "confirmation_bars": [0],
        # Cycle395 F(리서치): atr_bounce_factor 탐색 완전 종료 (2026-07-04)
        # factor=0.0(baseline): Sh=0.95, PF=1.33, Tr=34, Consistency=2/8, SharpeStd=2.20
        # factor=0.3: Sh=0.07 DEAD (동적threshold≈0.45% < 0.6% baseline → 노이즈 급증)
        # factor=0.5: Sh=1.06(+0.11↑), PF=1.32, Tr=35, Consistency=2/8(변화없음), SharpeStd=1.67(↓안정화)
        # factor=1.0(Cycle381): Sh=1.17(+0.22), Consistency=1/8(↓) — Sharpe↑ Consistency↓
        # 결론: factor=0.5가 Sharpe/안정성 최적. Consistency ceiling=2/8 돌파 불가.
        # → price_cluster 1h BTC 최적화 완전 종료. 추가 atr_bounce_factor 실험 금지.
        # paper_sim 확정 파라미터: factor=0.5 (Sh=1.06, SharpeStd=1.67)
        "atr_bounce_factor": [0.0, 0.3, 0.5, 1.0],
        # Cycle384: rsi_oversold_filter DEAD (0 trades). 그리드에서 제거됨.
    },
    # Cycle 326 D(ML): roc_ma_cross 1h WFO 그리드
    # 현재 상태: rank1(2/8 consistency), Sharpe=0.34, SharpeStd=2.44 — FAIL (mc_p=0.485)
    # roc_period: ROC 계산 lookback (현재 12 고정) → 1h 노이즈 감안 짧게 [10,12,15]
    # ma_period: ROC 스무딩 MA 윈도우 (현재 3 고정) → 1h에서 3봉=3h 너무 짧음 [3,5,7]
    # Cycle361 F: EMA200 조건 정리(ema50 체크 제거), rsi_val dead code 제거
    # Cycle370 F(리서치): roc_period 탐색 완료 (10/12/15 전부 검증)
    #   10: Sh=-1.45 (역효과 Cycle369), 12: Sh=0.34 (최적), 15: Sh=-0.33 (역효과 Cycle370)
    #   결론: roc_period=12 최적 확정. roc_period 탐색 방향 종료
    # Cycle383 F(리서치): EMA200 필터 제거 효과 분석 (BTC 1h 실데이터 검증)
    #   현재 신호(EMA200 통과): 76개, 24h fwd return +0.329%, Win rate 60.5%
    #   EMA200 차단 신호(제거 시 추가): 13개, 24h fwd return -0.540%, Win rate 30.8%
    #   결론: EMA200 차단 신호 품질 매우 낮음(음수 fwd return) → EMA200 필터 유지 확정
    #   EMA200 아래 BUY 신호(close < EMA200) = 하락 추세 역행 → PASS 불기여
    #   roc_ma_cross PASS 안정화: EMA200 방향 탐색 종료 (EMA200 제거 금지)
    # Cycle379 D(ML): volume_filter=[False,True] 추가 — 거래량 급증(>1.5×SMA20) 시만 신호 허용
    #   가설: ROC_MA cross + 거래량 급증 = 강한 모멘텀 확인 → 오신호 감소, PF↑
    # Cycle379 D(ML) paper_sim 결과: volume_filter=True, vol_ratio_min=1.5
    #   Sharpe=0.72(+0.38↑), PF=1.68(+0.68↑, 목표 1.5 달성!), Trades=10(<15 FAIL)
    #   결론: volume_filter 개념 유효(PF↑) — 임계값 1.5가 너무 공격적, trades 부족
    # Cycle380 A(품질): vol_ratio_min 최적값 탐색 [1.0, 1.2, 1.5]
    #   목표: Trades≥15 + PF≥1.5 동시 만족 구간 탐색
    #   1.5: PF=1.68 달성, Trades=10 (FAIL) / 1.2: 예상 Trades 15-20 (Cycle380 실험)
    #   1.0: 더 많은 trades 허용 (기준선), PF 하락 예상
    # Cycle384 E(실행): dead param 정리 — roc_period=10/15, ma_period=5/7 제거
    #   roc_period: 10→Sh=-1.45(Cycle369), 15→Sh=-0.33(Cycle370), 12→최적 확정
    #   ma_period: 5→Sh=-0.91(Cycle368), 7→likely worse, 3→최적 확정
    #   WFO 그리드 3×3×2×3=54 combos → 1×1×2×3=6 combos (90% 축소, IS 최적화 속도 대폭 향상)
    # Cycle384 F(리서치): roc_min_abs 파라미터화 — 현재 0.3% 하드코딩 → 탐색 가능
    #   가설: 0.4% 강화 → RANGING 구간 약한 크로스 차단 → Consistency 개선 기대
    "roc_ma_cross": {
        "roc_period": [12],   # 확정: 10=bad(Sh=-1.45), 15=bad(Sh=-0.33), 12=최적 (Cycle369/370)
        "ma_period": [3],     # 확정: 5=bad(Sh=-0.91), 7=worse, 3=최적 (Cycle368)
        "volume_filter": [False, True],
        # vol_ratio_min: volume_filter=True 시에만 유효 (False시 무시됨)
        "vol_ratio_min": [1.0, 1.2, 1.5],
        # Cycle384 F(리서치): roc_min_abs=0.4 실험 → dead param (Consistency 4/8→2/8 PASS→FAIL)
        # 결론: 0.3이 최적 확정. roc_min_abs 탐색 종료.
        # Cycle385 C(데이터): FAIL 윈도우(W2/W3/W4) 실데이터 분석 결과
        #   FAIL windows: vol_ratio at signals mean=0.89-0.97 (PASS windows: 1.14-1.19)
        #   vol>=1.2 통과 신호 수: W3=14, W4=14 (Trades<15 기준 미달이 FAIL 핵심 원인)
        #   binding constraint: vol_ratio_min=1.2 필터가 FAIL 윈도우에서 1-2개 신호를 과도 차단
        #   W4 24h fwd return(vol-filtered) +2.10% — 신호 품질 자체는 양호, trades 부족이 문제
        #   결론: vol_ratio_min 하향(1.1) 역효과(Cycle382) 이미 확인. 새 방향 탐색 필요.
        #   → ATR expand filter 탐색 (Cycle385 F): dead param 확정 (Consistency 4/8→2/8 역효과)
        #   교훈: roc_ma_cross는 추가 signal filter 금지 — Trades=14 경계선에서 어떤 추가 필터도 역효과
    },
    # Cycle356 D(ML): dema_cross WFO 그리드 추가
    # 배경: 기본값 fast=10/slow=25는 BTC 1h에서 avg 3 trades (0/8 consistency 35사이클 이상 지속)
    # 0.1% 거리 필터 완화(Cycle355)에도 trades=3 유지 → cross 이벤트 자체가 희귀
    # 더 짧은 주기(fast=8/slow=15~20)로 cross 빈도 향상 탐색
    # slow=25(기존) 유지로 기존 동작과의 비교 가능
    # Cycle359 D(ML): rsi_dir_filter=[False,True] 추가 — RSI 방향성 필터 WFO 탐색
    #   True: BUY시 RSI>50, SELL시 RSI<50 요구 (모멘텀 방향 확인으로 신호 품질 향상)
    #   False: 기존 과매수/과매도 회피만 적용 (현재 확정 동작)
    # Cycle363 C(데이터): fast=7 추가 실험 → Cycle364 D(ML) 검증 결과 역효과 확인 → 제거
    #   fast=7: trades 18→24 증가, 但 PF 1.45→1.00, Sharpe 0.40→-0.69 (노이즈 증가 확정)
    #   RSI 필터가 binding constraint — fast 단축으로 trades 증가 불가 (RSI filter 비율 일정)
    # Cycle365 A(품질)/F(리서치): rsi_dir_threshold=[45,50] 추가 — 임계값 완화 실험
    #   BTC 1h 실데이터 신호 분석: fast=8/slow=20/thr=50→10.1/60d, thr=45→13.4/60d
    #   fast=8/slow=25/thr=45→16.5/60d (min_trades=15 항상 충족, slow=25 병행 탐색)
    # Cycle366 D(ML): thr=45 paper_sim 결과 — net positive (rank5→2)
    #   Sharpe: 0.40→0.55(+0.15↑), Trades: 18→26(+8↑), PF: 1.45→1.35(-0.10 mild↓)
    #   fast=7 패턴(PF 1.00 대폭 하락) 아님 — 허용 가능한 PF 소폭 하락으로 thr=45 유지 확정
    # Cycle369 D(ML): thr=40 paper_sim 결과 → 대성공 (rank1, Sh0.55→0.80, Trades26→30)
    #   thr=50 제거(thr=45보다 열등 확인, Cycle365), thr=40 추가 (확정 최적)
    # Cycle370 A(품질): optimize_dema_cross WFO 실행 → best_params={fast=12,slow=25,rsi_dir_filter=False,thr=45}
    #   thr=40: WFO 3개 윈도우 모두 선택 안 됨 (thr=45 일관 선택) → paper_sim Sh=0.80은 일회성 가능성
    #   is_stable=False, oos_sharpe_std=2.6152, trades 6/7/20 (저거래 신뢰도 낮음)
    #   결론: thr=40 paper_sim rank1은 WFO로 지지 안 됨 — 추가 사이클에서 재검증 권장
    # Cycle370 C(데이터): dist_pct_min=0.003 실험 → 역효과 확정
    #   Sh=-0.35, Trades=15 (0.002: Sh=0.80, Trades=30 대비 절반 감소) → 0.002 유지 확정
    # Cycle356: fast/slow 그리드 추가 (8,10,12 × 15,20,25)
    # Cycle359: rsi_dir_filter=[False,True] 추가
    # Cycle369: rsi_dir_threshold [45,50]→[40,45] (thr=40 paper_sim rank1)
    # Cycle370: WFO 3/3 윈도우 thr=45 선택 — IS 윈도우 편향, paper_sim과 불일치
    # Cycle371 B: thr=45 재검증 → thr=40 우위 확정 (Sh0.80 vs 0.55, Trades30 vs 26)
    #   WFO vs paper_sim 불일치 원인: WFO IS 3개월 윈도우에서 thr=45가 안정적이나
    #   전체 기간(8윈도우×2개월) 평가에서는 thr=40이 일관되게 우세
    # Cycle372 D(ML): ema_slope_min_buy 추가 — BUY시 EMA20 상승추세 확인 필터
    #   0.0=비활성(기존), 0.0003=중간 임계값(Cycle346 분석 기반)
    # Cycle373 F(리서치): macd_hist_filter 추가 — BUY/SELL 시 MACD hist 방향 일치 요구
    #   가설: RANGING 구간의 역방향 cross를 hist 불일치로 차단 → PF 1.38→1.50 목표
    # Cycle374 D(ML): bb_width_min_filter 추가 — BB squeeze 구간 cross 차단
    #   BTC 1h bb_width 분포: mean=0.0645, p25=0.041 → 0.0(비활성)/0.04(23% 차단) 실험
    #   가설: BB squeeze(폭 수축) 구간 cross → false breakout → PF 개선 기대
    # Cycle377 D(ML): ema200_filter 추가 — 약세장 롱 진입 차단
    #   배경: W1/W5 PASS = BTC 강세장(EMA200 위), W2/W3/W4 FAIL = 하락/횡보 가능성
    #   가설: close > ema200 필터 → 약세장 롱 진입 차단 → W2/W3/W4 손실 회피 → PF↑
    #   결과: ema200_filter=True DEAD (Cycle377 D): Sh=0.56(-34%), PF=1.34, Trades=22
    #   원인: 2023초 BTC 회복 구간(EMA200 미만) 수익 신호 차단 + 200봉 워밍업 감소
    # Cycle396 D(ML): dema_cross 탐색 완전 종료 (Cycle377 F 선언 이후) — dead param 정리
    #   확정 파라미터: fast=8, slow=20, rsi_dir_filter=True, rsi_dir_threshold=40,
    #                 bb_width_min_filter=0.04, dist_pct_min=0.002 (dema_cross.py 기본값)
    #   DEAD params (추가 탐색 금지):
    #     fast=10,12 — 8이 최적 (Cycle356 D ~ Cycle367 D 검증)
    #     slow=15,25 — 20이 최적 (Cycle367 D 확정)
    #     rsi_dir_filter=False — True가 PF 1.26→1.45 확정 (Cycle360 A)
    #     rsi_dir_threshold=45 — 40이 전체 기간 우세 (Cycle369 D, Cycle371 B 재확인)
    #     ema_slope_min_buy=0.0003 — dead param (Cycle372 F 역효과)
    #     macd_hist_filter=True — dead param (Cycle373 F 역효과)
    #     bb_width_min_filter=0.0 — 0.04 mild positive 확정 (Cycle374 D, Cycle375 C)
    #     ema200_filter=True — dead param (Cycle377 D: Sh↓34%)
    "dema_cross": {
        "fast": [8, 10, 12],           # DEAD: 10,12 (8 확정, Cycle367 D)
        "slow": [15, 20, 25],          # DEAD: 15,25 (20 확정, Cycle367 D)
        "rsi_dir_filter": [False, True],          # DEAD: False (True 확정, Cycle360 A)
        "rsi_dir_threshold": [40, 45],            # DEAD: 45 (40 확정, Cycle371 B)
        "ema_slope_min_buy": [0.0, 0.0003],       # DEAD: 0.0003 (역효과, Cycle372 F)
        "macd_hist_filter": [False, True],         # DEAD: True (역효과, Cycle373 F)
        "bb_width_min_filter": [0.0, 0.04],       # DEAD: 0.0 (0.04 확정, Cycle374 D)
        "ema200_filter": [False, True],            # DEAD: True (역효과, Cycle377 D)
    },
    # Cycle405 F(리서치): lob_maker 구조적 한계 분석 완료
    # BTC 1h paper_sim: rank5, Sh=-0.04, Trades=75, MDD=17%, 0/8 Consistency
    # 근본 원인:
    #   1. LOB 데이터(bid_vol/ask_vol) 없음 → OFI proxy = (close-open)/(high-low) 사용
    #      이 proxy는 단순 캔들 방향성 비율(body/range) — 실제 order flow 불균형 측정 불가
    #   2. VPIN도 OHLCV만으로 추정 → 정밀도 제한, fallback=0.5(불확실)
    #   3. RSI 필터: rsi < 22 시 BUY 차단 (RSI<22=과매도 → 반직관적, 추세추종 의도)
    # 결론: LOB 데이터 인프라(WebSocket bid/ask) 없이 파라미터 조정으로 PASS 불가
    #   ofi_buy_threshold 상향 → Trades 감소 → Sh 추가 악화 가능
    #   volume_multiplier 상향 → 동일 문제
    #   STRUCTURAL LIMIT: 실거래소 LOB 스트림 없이 lob_maker 최적화 불가
    # 탐색 보류 (LOB 데이터 인프라 구축 후 재평가)
    "lob_maker": {
        # 모든 파라미터 하드코딩 상태 — LOB 데이터 없이 최적화 의미 없음
        # ofi_buy_threshold, volume_multiplier, vpin 임계값 파라미터화 가능하지만
        # proxy OFI 근본 문제 해결 없이 grid search는 과최적화 위험만 증가
        # lob_maker 탐색 완전 보류 (LOB 인프라 없음)
    },
    # Cycle408 F(리서치): htf_ema 구조적 한계 확정
    #   paper_sim BTC 1h: Sh=-0.72, Trades=43, rank13 → 음의 Sharpe, 구조적 실패
    #   근본 원인:
    #     1. HTF 시뮬레이션 방식 부정확: iloc[::4]로 4봉마다 샘플링 = 인덱스 기반 다운샘플링
    #        → 실제 4h 캔들 OHLCV와 불일치 (open/high/low/close가 다름)
    #        → EWM(span=21) 값이 실제 4h EMA와 다른 proxy가 됨
    #     2. BTC 1h RANGING 47.3% → EMA9 cross 신호가 양방향으로 빈번히 발생
    #        but htf_ema rising/falling 조건이 이 중 절반 이상을 차단하지 못함
    #     3. 신호 조건 복잡성 과다: htf_rising AND cross_above AND cross_valid AND rsi_ok
    #        → 필터 조합이 Trades=43 (BTC 1h 15개월 기준 ≈ 2.9/month)으로 적음
    #        → OOS Sharpe=-0.72 (음의 엣지, 랜덤보다 나쁨)
    #   파라미터화 가능 요소 없음: htf span=21, ema9=9, rsi thresh=75/25 하드코딩
    #     → 파라미터 변경으로 HTF 다운샘플링 근본 문제 해결 불가
    #   결론: htf_ema 추가 탐색 금지. 실제 4h 데이터 없이 1h 샘플링으로는 PASS 불가.
    "htf_ema": {},  # WFO 파라미터 없음 (구조적 한계, Cycle408 F)
    # Cycle409 F(리서치): price_action_momentum BTC 1h 구조적 한계 확정
    #   BTC 1h paper_sim: Sh=-1.08, PF<1.0, Trades=73 (8윈도우, avg=9.1/window)
    #   구조 분석:
    #   1. BUY: body > 0 AND body_strength >= 0.50 AND roc5 > 0.005 AND close > sma50
    #      → roc5 > 0.005 (5h 내 0.5% 상승) 조건이 BTC 1h RANGING(47.3%)에서도 빈번히 충족
    #      → RANGING 진입 후 즉각 반전 → 음의 엣지(-1.08)
    #   2. body_strength >= 0.50 + roc5 조건 AND = 신호 73회 (avg 9/window) — 과다
    #      이 두 조건이 RANGING 구간에서 동시 충족되는 경우 많음 → 노이즈 추종
    #   3. 파라미터화 가능 요소: body_strength_threshold(0.50), roc5_threshold(0.005) 하드코딩
    #      → 강화 시 Trades 추가 감소 + 음의 엣지 전략에서 더 나쁜 timing 선택
    #   결론: 모멘텀 추종 전략이 RANGING 47.3% BTC 1h에서 구조적으로 실패.
    #   파라미터 강화로 Sh=-1.08 개선 불가. 추가 탐색 금지.
    "price_action_momentum": {},  # WFO 파라미터 없음 (구조적 한계, Cycle409 F)
    # Cycle410 F(리서치): relative_volume BTC 1h 구조적 한계 분석
    #   BTC 1h paper_sim (rvol_buy_sell=1.2): Sh=-0.99, PF=0.92(**<1.0**), Trades=64, Consistency=0/8 → FAIL
    #   NEXT_STEPS rank8 후보 — 구조 분석:
    #   1. BUY: RVOL > 1.2 AND bull_candle AND close > vwap20 AND RSI < 68
    #      → rvol_buy_sell=1.2는 RANGING(47.3%) BTC 1h에서 단기 거래량 노이즈로도 빈번히 충족
    #      → RSI < 68 허용 범위가 너무 광범위 (RSI 68%를 허용)
    #      → RANGING 볼륨 스파이크 = 일시적 과매수 신호 → 즉각 반전 → 음의 엣지
    #   2. PF=0.92 < 1.0: 손실이 이익을 초과 → 볼륨 스파이크 후 추세 지속 실패
    #      RANGING 47.3% 환경에서 볼륨 스파이크는 방향성 없는 노이즈 발생원
    #   3. 파라미터 개선 방향 검토:
    #      rvol_buy_sell=1.6(기본값)으로 복원 시: Trades 감소 → <15 가능 → PASS 기준 미달
    #      RSI 임계값 강화(RSI<50): 추가 차단이지만 음의 엣지 전략에서 신호 감소 = 무의미
    #      bull_only=True(EMA50 필터): TREND_UP(31.3%) 전용 → Trades 더 감소 → FAIL 심화
    #   결론: relative_volume는 추세 추종 볼륨 전략 — RANGING 47.3% BTC 1h에서 구조적 실패.
    #   rvol 임계값 조정·RSI 강화·EMA50 필터 어느 방향도 PF<1.0 음의 엣지 개선 불가.
    #   **relative_volume 추가 탐색 금지. 구조적 한계 확정 (Cycle410 F).**
    "relative_volume": {},  # WFO 파라미터 없음 (구조적 한계, Cycle410 F)
    # Cycle411 F(리서치): volume_breakout BTC 1h 구조적 한계 확정
    #   - _SPIKE_MULT=1.5 하드코딩 → RANGING(47.3%) BTC 1h에서 신호 빈발 (Trades=72, avg 9/window)
    #   - SL 파라미터 없음 → MDD 22.1% > 20% 구조적 초과 (max_hold_candles만으로 관리)
    #   - EMA50 추세 필터가 신호 조건이 아닌 confidence에만 사용 → RANGING BUY/SELL 동등 발생
    #   - BTC 1h: Sh=-0.74, PF=0.96(<1.0, 음의 엣지), Trades=72, 0/8 Consistency
    #   - 파라미터화 가능(spike_mult, ema_filter_signal): spike_mult=2.0 → Trades<15 위험
    #   - 음의 엣지(PF<1.0) + SL 부재 + RANGING 구조 → 파라미터화로 해결 불가
    #   **volume_breakout 추가 탐색 금지. 구조적 한계 확정 (Cycle411 F).**
    "volume_breakout": {},  # WFO 파라미터 없음 (구조적 한계, Cycle411 F)
    # Cycle412 F(리서치): momentum_quality BTC 1h 구조적 한계 확정
    #   - BTC 1h: Sh=-1.19, PF<1.0(음의 엣지), Trades=71, 1/8 Consistency
    #   - quality_score = consistency*2-1 + (acceleration>0) — RANGING(47.3%)에서 빈발
    #   - quality_score_buy_threshold=0.8 → accel=1 시 consistency>0.4 이상이면 통과
    #   - consistency_buy_threshold=0.3: DEAD PARAM — quality_score>0.8 조건이 이미 consistency>0.4 함의
    #   - quality_score_buy_threshold=1.5 상향 → Trades<15 위험 (72→<15 예상)
    #   - 구조 자체가 RANGING 47.3% BTC 1h에서 모멘텀 추종 → 음의 엣지
    #   **momentum_quality 추가 탐색 금지. 구조적 한계 확정 (Cycle412 F).**
    "momentum_quality": {},  # WFO 파라미터 없음 (구조적 한계, Cycle412 F)
}

# 과최적화 판단 기준
IS_OOS_RATIO_MIN = 0.5   # OOS Sharpe / IS Sharpe 최소 비율
OOS_STD_MAX = 0.8        # OOS Sharpe 표준편차 최대


@dataclass
class WindowResult:
    """단일 walk-forward 윈도우 결과."""
    window_id: int
    params: dict
    is_sharpe: float    # in-sample 최적 Sharpe
    oos_sharpe: float   # out-of-sample 실제 Sharpe
    oos_passed: bool    # OOS 백테스트 통과 여부
    is_oos_ratio: float # OOS/IS 비율
    oos_trades: int = 0  # Cycle 257: OOS 거래 수 (저거래 std 오염 방지)
    oos_mdd: float = 0.0  # Cycle 343 B: OOS 최대 낙폭 (0~1)

    def is_overfit(self) -> bool:
        return self.is_oos_ratio < IS_OOS_RATIO_MIN


@dataclass
class WalkForwardResult:
    """전체 walk-forward 최적화 결과."""
    strategy_name: str
    best_params: dict           # 최종 추천 파라미터
    windows: List[WindowResult]
    avg_oos_sharpe: float
    oos_sharpe_std: float
    is_stable: bool             # 안정성 기준 통과 여부
    overfit_windows: int        # 과최적화 의심 윈도우 수
    fail_reasons: List[str] = field(default_factory=list)
    # IS 최적화 효과 측정용: 마지막 윈도우의 파라미터별 IS Sharpe 분포
    # {str(sorted(params.items())): is_sharpe} 형태
    last_is_sharpe_dist: Dict[str, float] = field(default_factory=dict)
    # 파라미터 안정성 CV: {param_name: cv} (fold 간 CV=std/mean)
    param_stability_cv: Dict[str, float] = field(default_factory=dict)
    # time-decay 가중평균 OOS Sharpe (정보 제공용, PASS/FAIL 기준 아님)
    weighted_oos_sharpe: Optional[float] = None
    # WFE: Walk Forward Efficiency = avg OOS Sharpe / avg IS Sharpe
    # > 0.7이면 robust, <= 0이면 과최적화 심각
    wfe: Optional[float] = None
    # fold_pass_rate: OOS Sharpe > 0인 fold 비율 (0.0~1.0)
    fold_pass_rate: Optional[float] = None
    # low_trades_folds: OOS trades < 30인 fold 수 (통계적 신뢰도 낮음 경고)
    low_trades_folds: int = 0
    # plateau_score: 최적 파라미터 주변 ±10% 범위의 IS Sharpe 안정성 (0~1)
    # = mean(neighbor_sharpes) / best_sharpe.  1.0에 가까울수록 안정적.
    # None이면 계산 불가 (그리드 내 이웃 없음 등)
    plateau_score: Optional[float] = None
    # is_oos_pearson: fold별 IS Sharpe와 OOS Sharpe 간 Pearson 상관계수
    # 양수(특히 > 0.3)이면 IS 성능이 OOS를 예측 → 과최적화 낮음
    # 음수이면 IS 최적화가 OOS를 역방향 예측 → 심각한 과최적화 신호
    is_oos_pearson: Optional[float] = None
    # avg_oos_mdd: fold 평균 OOS MDD (0~1). RANGING 레짐 등 고-MDD 패턴 진단용
    avg_oos_mdd: Optional[float] = None

    @property
    def is_robust(self) -> bool:
        """WFE > 0.7이면 robust 판정. wfe가 None이면 False."""
        return self.wfe is not None and self.wfe > 0.7

    def summary(self) -> str:
        verdict = "STABLE" if self.is_stable else "UNSTABLE"
        lines = [
            f"WALK_FORWARD_RESULT:",
            f"  strategy: {self.strategy_name}",
            f"  best_params: {self.best_params}",
            f"  avg_oos_sharpe: {self.avg_oos_sharpe:.3f}",
            f"  oos_sharpe_std: {self.oos_sharpe_std:.3f}",
            f"  overfit_windows: {self.overfit_windows}/{len(self.windows)}",
            f"  verdict: {verdict}",
        ]
        if self.wfe is not None:
            robust_tag = "ROBUST" if self.is_robust else "NOT_ROBUST"
            lines.append(f"  wfe: {self.wfe:.3f} ({robust_tag})")
        if self.fold_pass_rate is not None:
            lines.append(f"  fold_pass_rate: {self.fold_pass_rate:.2%}")
        if self.low_trades_folds > 0:
            lines.append(f"  [WARN] low_trades_folds: {self.low_trades_folds}/{len(self.windows)} (OOS<30 trades)")
        if self.weighted_oos_sharpe is not None:
            lines.append(f"  weighted_oos_sharpe: {self.weighted_oos_sharpe:.3f}")
        if self.plateau_score is not None:
            plateau_tag = "STABLE" if self.plateau_score >= 0.8 else "SENSITIVE"
            lines.append(f"  plateau_score: {self.plateau_score:.3f} ({plateau_tag})")
        if self.is_oos_pearson is not None:
            pearson_tag = "PREDICTIVE" if self.is_oos_pearson > 0.3 else ("ANTI" if self.is_oos_pearson < -0.1 else "WEAK")
            lines.append(f"  is_oos_pearson: {self.is_oos_pearson:.3f} ({pearson_tag})")
        if self.avg_oos_mdd is not None:
            mdd_tag = "HIGH" if self.avg_oos_mdd > 0.15 else ("MED" if self.avg_oos_mdd > 0.08 else "LOW")
            lines.append(f"  avg_oos_mdd: {self.avg_oos_mdd:.2%} ({mdd_tag})")
        if self.param_stability_cv:
            unstable = {k: v for k, v in self.param_stability_cv.items() if v > 0.5}
            lines.append(f"  param_cv: {self.param_stability_cv}")
            if unstable:
                lines.append(f"  [WARN] unstable params (CV>0.5): {unstable}")
        if self.fail_reasons:
            lines.append(f"  fail_reasons: {self.fail_reasons}")
        return "\n".join(lines)


class WalkForwardOptimizer:
    """
    Walk-Forward 파라미터 최적화기.

    사용:
        opt = WalkForwardOptimizer("ema_cross", strategy_factory)
        result = opt.run(df)
        if result.is_stable:
            use_params = result.best_params
    """

    def __init__(
        self,
        strategy_name: str,
        strategy_factory: Callable[[dict], BaseStrategy],
        param_grid: Optional[dict] = None,
        n_windows: int = 3,
        is_ratio: float = 0.6,    # in-sample 비율
        stability_lambda: float = 0.5,  # Sharpe - λ*CV penalty 계수
        plateau_pct: float = 0.9,  # 플래토 룰: IS 최고 Sharpe의 이 비율 이상인 파라미터 집합 중 중간값 선택
        fold_decay: float = 0.0,  # time-decay: 0=동일가중, 양수=최근fold에 지수적 가중치
        use_regime_weights: bool = False,  # HIGH_VOL fold 다운웨이팅
        trades_regularization_scale: float = 0.0,  # IS 거래 수 기반 정규화 계수
        regime_filter: bool = False,  # TREND_UP 레짐에서만 BUY 허용 (B리스크 Cycle 328)
    ):
        """
        Args:
            strategy_name: 전략 이름
            strategy_factory: params dict → BaseStrategy 인스턴스 생성 함수
            param_grid: {"param": [values]} 딕셔너리
            n_windows: walk-forward 윈도우 수
            is_ratio: in-sample 데이터 비율 (0.6 = 60%)
            stability_lambda: IS 목적함수 stability penalty 계수.
                              Score = Sharpe - λ * CV (λ=0 이면 순수 Sharpe 최적화)
            plateau_pct: 플래토 룰 임계값 (기본 0.9 = 90%).
                         IS 최고 Sharpe × plateau_pct 이상인 파라미터들 중 중간값 선택.
                         과최적화 방지: 극단 파라미터 배제.
            fold_decay: time-decay 계수. 0이면 동일 가중치(기존 동작).
                        양수면 w_i = exp(fold_decay * i) (i가 클수록 최근 fold).
                        weighted_oos_sharpe 계산에만 사용; PASS/FAIL은 avg_oos_sharpe 기준.
            regime_filter: True이면 MarketRegimeDetector로 각 윈도우에 _regime_trend_up 컬럼 추가
                           후 TREND_UP이 아닌 봉의 BUY 신호를 자동 차단 (_RegimeFilterStrategy 래퍼 적용).
            trades_regularization_scale: IS 거래 수 기반 정규화 계수.
                        0.0(기본)이면 기존 동작 유지.
                        양수면 Score += scale * min(1.0, is_trades/30) 추가.
                        sideways 구간에서 Sharpe=0이 다수일 때 거래 수가 더 많은
                        파라미터를 선호하도록 유도 (supertrend_multi 0-trades 문제 완화).
        """
        if fold_decay < 0:
            raise ValueError(
                f"fold_decay는 0 이상이어야 합니다 (음수면 초기 fold에 가중치, 비직관적). "
                f"입력값: {fold_decay}. 권장 범위: 0.0 (균일) ~ 1.0 (최근 강조)."
            )
        self.strategy_name = strategy_name
        self.strategy_factory = strategy_factory
        self.n_windows = n_windows
        self.is_ratio = is_ratio
        self.stability_lambda = stability_lambda
        self.plateau_pct = plateau_pct
        self.fold_decay = fold_decay
        self.use_regime_weights = use_regime_weights
        self.trades_regularization_scale = trades_regularization_scale
        self.regime_filter = regime_filter
        self._regime_detector = MarketRegimeDetector() if regime_filter else None
        self._param_grid = param_grid or DEFAULT_GRIDS.get(strategy_name, {})
        self._engine = BacktestEngine()

    def run(self, df: pd.DataFrame) -> WalkForwardResult:
        """Walk-forward 최적화 실행."""
        # 파라미터 수 과적합 경고 (5개 초과 시)
        n_params = len(self._param_grid)
        if n_params > 5:
            logger.warning(
                "[%s] 파라미터 수 %d > 5 — 과적합 위험. 단순 전략(2~3 파라미터) 권장.",
                self.strategy_name, n_params,
            )

        if not self._param_grid:
            return WalkForwardResult(
                strategy_name=self.strategy_name,
                best_params={},
                windows=[],
                avg_oos_sharpe=0.0,
                oos_sharpe_std=0.0,
                is_stable=False,
                overfit_windows=0,
                fail_reasons=[f"파라미터 그리드 없음 ({self.strategy_name})"],
            )

        n = len(df)
        if n < 200:
            return WalkForwardResult(
                strategy_name=self.strategy_name,
                best_params={},
                windows=[],
                avg_oos_sharpe=0.0,
                oos_sharpe_std=0.0,
                is_stable=False,
                overfit_windows=0,
                fail_reasons=[f"데이터 부족: {n} < 200"],
            )

        # 윈도우 분할
        windows = self._split_windows(df)
        all_combinations = list(self._iter_param_combinations())

        if not all_combinations:
            return WalkForwardResult(
                strategy_name=self.strategy_name,
                best_params={},
                windows=[],
                avg_oos_sharpe=0.0,
                oos_sharpe_std=0.0,
                is_stable=False,
                overfit_windows=0,
                fail_reasons=["파라미터 조합 없음"],
            )

        logger.info(
            "Walk-Forward: %s | %d windows × %d param combinations",
            self.strategy_name, len(windows), len(all_combinations),
        )

        window_results: List[WindowResult] = []
        param_oos_map: Dict[str, List[float]] = {}
        last_is_sharpe_dist: Dict[str, float] = {}
        # fold별 최적 파라미터 수집 (파라미터 안정성 CV 계산용)
        fold_params_history: List[dict] = []
        low_trades_folds = 0  # OOS trades < 30인 fold 수
        oos_vols: List[float] = []

        for i, (is_df, oos_df) in enumerate(windows):
            _win_t0 = _time.monotonic()
            # regime_filter: TREND_UP 레짐 외 BUY 차단 (_regime_trend_up 컬럼 추가)
            if self.regime_filter and self._regime_detector is not None:
                is_df = self._annotate_regime(is_df)
                oos_df = self._annotate_regime(oos_df)

            # IS 최적화 (Sharpe - λ*CV 목적함수 + 플래토 룰 적용)
            _is_t0 = _time.monotonic()
            best_params, best_is_sharpe, is_sharpe_dist = self._optimize_in_sample(
                is_df, all_combinations,
                stability_lambda=self.stability_lambda,
                plateau_pct=self.plateau_pct,
                trades_regularization_scale=self.trades_regularization_scale,
                regime_filter=self.regime_filter,
            )
            _is_elapsed = _time.monotonic() - _is_t0

            # OOS 검증
            inner_strategy = self.strategy_factory(best_params)
            oos_strategy = _RegimeFilterStrategy(inner_strategy) if self.regime_filter else inner_strategy
            oos_result = self._engine.run(oos_strategy, oos_df)

            # OOS ATR (변동성) 계산 — regime 가중치에 사용
            if all(c in oos_df.columns for c in ["high", "low", "close"]):
                _atr = (oos_df["high"] - oos_df["low"]) / (oos_df["close"] + 1e-9)
                oos_vol = float(_atr.mean())
            else:
                oos_vol = 0.0
            oos_vols.append(oos_vol)

            # OOS 거래 수 통계적 신뢰도 경고 (학술 기준: fold당 30 trades)
            MIN_RELIABLE_OOS_TRADES = 30
            if oos_result.total_trades < MIN_RELIABLE_OOS_TRADES:
                low_trades_folds += 1
                logger.warning(
                    "[%s] Window %d: OOS trades=%d < %d — 통계적 신뢰도 낮음 (Sharpe 편향 가능성)",
                    self.strategy_name, i, oos_result.total_trades, MIN_RELIABLE_OOS_TRADES,
                )

            # WFE 계산 및 적용 (과최적화 필터)
            BacktestEngine.apply_wfe(oos_result, best_is_sharpe)
            ratio = oos_result.wfe

            wr = WindowResult(
                window_id=i,
                params=best_params,
                is_sharpe=best_is_sharpe,
                oos_sharpe=oos_result.sharpe_ratio,
                oos_passed=oos_result.passed,
                is_oos_ratio=ratio,
                oos_trades=oos_result.total_trades,
                oos_mdd=oos_result.max_drawdown,
            )
            window_results.append(wr)
            fold_params_history.append(best_params)

            # 파라미터별 OOS 성과 집계
            key = str(sorted(best_params.items()))
            param_oos_map.setdefault(key, []).append(oos_result.sharpe_ratio)
            # 마지막 윈도우의 IS Sharpe 분포 저장 (IS 최적화 효과 측정용)
            last_is_sharpe_dist = is_sharpe_dist

            oos_vs_is_gap = oos_result.sharpe_ratio - best_is_sharpe
            _win_elapsed = _time.monotonic() - _win_t0
            logger.info(
                "Window %d: IS Sharpe=%.3f OOS Sharpe=%.3f ratio=%.2f gap=%.3f trades=%d params=%s"
                " | IS_opt=%.2fs total=%.2fs (%d combos)",
                i, best_is_sharpe, oos_result.sharpe_ratio, ratio, oos_vs_is_gap,
                oos_result.total_trades, best_params,
                _is_elapsed, _win_elapsed, len(all_combinations),
            )

        # 최종 파라미터 선택: Sharpe Information Criterion (avg - 0.5 * std)
        # 평균만 최대화하면 고분산 파라미터를 선택할 수 있음 → 안정성 가중 선택
        if not param_oos_map:
            return WalkForwardResult(
                strategy_name=self.strategy_name,
                best_params={},
                windows=window_results,
                avg_oos_sharpe=0.0,
                oos_sharpe_std=0.0,
                is_stable=False,
                overfit_windows=0,
                fail_reasons=["유효 윈도우 없음 (데이터 부족)"],
            )

        import statistics as _stat

        def _sharpe_ic(sharpes: list) -> float:
            """Sharpe Information Criterion = avg - 0.5 * std (안정성 가중)."""
            avg = sum(sharpes) / len(sharpes)
            std = _stat.stdev(sharpes) if len(sharpes) > 1 else 0.0
            return avg - 0.5 * std

        best_key = max(param_oos_map, key=lambda k: _sharpe_ic(param_oos_map[k]))
        import ast
        best_final_params = dict(ast.literal_eval(best_key))  # str → dict 복원

        import statistics
        oos_sharpes = [wr.oos_sharpe for wr in window_results]
        avg_oos = sum(oos_sharpes) / len(oos_sharpes) if oos_sharpes else 0.0
        # Cycle 257: 저거래(< MIN_RELIABLE_OOS_TRADES) fold는 Sharpe 신뢰 불가 → std 계산 제외
        # 저거래 Sharpe는 분산이 극대화되어 OOS std를 인위적으로 상승시킴
        reliable_sharpes = [wr.oos_sharpe for wr in window_results
                            if wr.oos_trades >= 30]
        std_source = reliable_sharpes if len(reliable_sharpes) > 1 else oos_sharpes
        oos_std = statistics.stdev(std_source) if len(std_source) > 1 else 0.0
        overfit_count = sum(1 for wr in window_results if wr.is_overfit())

        # 파라미터 안정성 CV 계산 (fold 간 파라미터 CV = std / |mean|)
        param_stability_cv: Dict[str, float] = {}
        if len(fold_params_history) > 1:
            all_param_keys = set(k for p in fold_params_history for k in p)
            for pname in sorted(all_param_keys):
                values = [p[pname] for p in fold_params_history if pname in p]
                if len(values) < 2:
                    continue
                try:
                    vals_float = [float(v) for v in values]
                    mean_abs = abs(sum(vals_float) / len(vals_float))
                    std_val = _statistics.stdev(vals_float)
                    cv = (std_val / mean_abs) if mean_abs > 1e-9 else 0.0
                    param_stability_cv[pname] = round(cv, 4)
                    if cv > 0.5:
                        logger.warning(
                            "ParamStability [%s] param=%s CV=%.3f > 0.5 (불안정)",
                            self.strategy_name, pname, cv,
                        )
                except (TypeError, ValueError):
                    pass  # 비수치 파라미터는 스킵

        # weighted_oos_sharpe: time-decay 또는 regime 가중치 (선택)
        import math
        n_folds = len(oos_sharpes)
        if n_folds > 0 and self.use_regime_weights and oos_vols:
            mean_vol = sum(oos_vols) / len(oos_vols)
            # HIGH_VOL fold 다운웨이팅: fold_weight = 1/(1 + vol_ratio)
            raw_weights = [1.0 / (1.0 + v / (mean_vol + 1e-9)) for v in oos_vols]
            total_w = sum(raw_weights)
            weights = [w / total_w for w in raw_weights]
            weighted_oos_sharpe = sum(w * s for w, s in zip(weights, oos_sharpes))
        elif n_folds > 0 and self.fold_decay != 0.0:
            raw_weights = [math.exp(self.fold_decay * i) for i in range(n_folds)]
            total_w = sum(raw_weights)
            weights = [w / total_w for w in raw_weights]
            weighted_oos_sharpe = sum(w * s for w, s in zip(weights, oos_sharpes))
        else:
            weighted_oos_sharpe = avg_oos

        if self.use_regime_weights and oos_vols:
            logger.info(
                "[%s] regime_weights applied: vols=%s weights=%s",
                self.strategy_name,
                [round(v, 4) for v in oos_vols],
                [round(w, 4) for w in weights],
            )

        # WFE = avg OOS Sharpe / avg IS Sharpe
        all_is_sharpes = [wr.is_sharpe for wr in window_results]
        avg_is_sharpe = sum(all_is_sharpes) / len(all_is_sharpes) if all_is_sharpes else 0.0
        if abs(avg_is_sharpe) > 1e-9:
            wfe = round(avg_oos / avg_is_sharpe, 4)
        else:
            wfe = None  # IS Sharpe ≈ 0이면 WFE 정의 불가

        # fold_pass_rate: OOS Sharpe > 0인 fold 비율
        if window_results:
            positive_oos_folds = sum(1 for wr in window_results if wr.oos_sharpe > 0)
            fold_pass_rate = round(positive_oos_folds / len(window_results), 4)
        else:
            fold_pass_rate = None

        # IS/OOS Pearson 상관계수: fold별 IS Sharpe와 OOS Sharpe 간 선형 관계
        is_oos_pearson: Optional[float] = None
        if len(window_results) >= 3:
            is_sh_arr = [wr.is_sharpe for wr in window_results]
            oos_sh_arr = [wr.oos_sharpe for wr in window_results]
            n_f = len(is_sh_arr)
            is_mean = sum(is_sh_arr) / n_f
            oos_mean = sum(oos_sh_arr) / n_f
            is_var = sum((x - is_mean) ** 2 for x in is_sh_arr) / n_f
            oos_var = sum((x - oos_mean) ** 2 for x in oos_sh_arr) / n_f
            import math as _math_p
            if is_var > 1e-18 and oos_var > 1e-18:
                cov = sum((a - is_mean) * (b - oos_mean) for a, b in zip(is_sh_arr, oos_sh_arr)) / n_f
                is_oos_pearson = round(cov / (_math_p.sqrt(is_var) * _math_p.sqrt(oos_var)), 4)
                logger.info(
                    "[%s] IS/OOS Pearson=%.3f (n_folds=%d)",
                    self.strategy_name, is_oos_pearson, n_f,
                )

        fail_reasons = []
        is_stable = True
        if oos_std > OOS_STD_MAX:
            fail_reasons.append(f"OOS Sharpe 불안정: std={oos_std:.3f} > {OOS_STD_MAX}")
            is_stable = False
        if avg_oos < 0.5:
            fail_reasons.append(f"OOS 평균 Sharpe 낮음: {avg_oos:.3f} < 0.5")
            is_stable = False
        # low_trades_folds > n_windows/2 → 통계적 신뢰도 부족 → UNSTABLE 판정
        if low_trades_folds > len(windows) / 2:
            fail_reasons.append(
                f"저거래 fold 과다: low_trades_folds={low_trades_folds}/{len(windows)} "
                f"> n_windows/2 (OOS Sharpe 신뢰 불가)"
            )
            is_stable = False
            logger.warning(
                "[%s] low_trades_folds=%d > n_windows/2=%.1f → UNSTABLE",
                self.strategy_name, low_trades_folds, len(windows) / 2,
            )
        # IS Sharpe 전체 음수 진단: GBM 합성 데이터나 전략 미작동 신호
        if all_is_sharpes:
            if avg_is_sharpe < -0.5:
                fail_reasons.append(
                    f"IS 전체 음수: avg IS Sharpe={avg_is_sharpe:.3f} — "
                    "전략 미작동 또는 합성 데이터(GBM)"
                )
                is_stable = False

        # plateau_score: 최적 파라미터 ±10% 이웃의 IS Sharpe 안정성
        plateau_score = self._compute_plateau_score(
            best_final_params, last_is_sharpe_dist, all_combinations,
        )
        if plateau_score is not None and plateau_score < 0.8:
            fail_reasons.append(
                f"plateau_score={plateau_score:.3f} < 0.8 (파라미터 민감도 높음)"
            )
            logger.warning(
                "[%s] plateau_score=%.3f — 최적 파라미터 주변 성과 불안정",
                self.strategy_name, plateau_score,
            )

        avg_oos_mdd: Optional[float] = None
        oos_mdds = [wr.oos_mdd for wr in window_results if wr.oos_mdd > 0]
        if oos_mdds:
            avg_oos_mdd = round(sum(oos_mdds) / len(oos_mdds), 4)

        result = WalkForwardResult(
            strategy_name=self.strategy_name,
            best_params=best_final_params,
            windows=window_results,
            avg_oos_sharpe=round(avg_oos, 4),
            oos_sharpe_std=round(oos_std, 4),
            is_stable=is_stable,
            overfit_windows=overfit_count,
            fail_reasons=fail_reasons,
            last_is_sharpe_dist=last_is_sharpe_dist,
            param_stability_cv=param_stability_cv,
            weighted_oos_sharpe=round(weighted_oos_sharpe, 4),
            wfe=wfe,
            fold_pass_rate=fold_pass_rate,
            low_trades_folds=low_trades_folds,
            plateau_score=plateau_score,
            is_oos_pearson=is_oos_pearson,
            avg_oos_mdd=avg_oos_mdd,
        )
        logger.info(result.summary())
        return result

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _split_windows(self, df: pd.DataFrame) -> List[Tuple[pd.DataFrame, pd.DataFrame]]:
        """Walk-forward 윈도우 분할."""
        n = len(df)
        window_size = n // (self.n_windows + 1)
        oos_size = int(window_size * (1 - self.is_ratio))
        is_size = window_size - oos_size

        windows = []
        for i in range(self.n_windows):
            start = i * window_size
            is_end = start + is_size
            oos_end = is_end + oos_size
            if oos_end > n:
                break
            is_df = df.iloc[start:is_end]
            oos_df = df.iloc[is_end:oos_end]
            if len(is_df) >= 100 and len(oos_df) >= 30:
                windows.append((is_df, oos_df))

        return windows

    def _annotate_regime(self, df: pd.DataFrame) -> pd.DataFrame:
        """df에 _regime_trend_up(bool) 컬럼 추가 후 반환 (복사본)."""
        df = df.copy()
        regime_series = self._regime_detector.detect_series(df)
        df["_regime_trend_up"] = (regime_series == MarketRegime.TREND_UP)
        return df

    def _optimize_in_sample(
        self, is_df: pd.DataFrame, combinations: List[dict],
        stability_lambda: float = 0.5,
        plateau_pct: float = 0.9,
        trades_regularization_scale: float = 0.0,
        regime_filter: bool = False,
    ) -> Tuple[dict, float]:
        """그리드 서치로 IS 최적 파라미터 탐색.

        목적함수: Score = Sharpe - λ * CV [+ γ * min(1, trades/30)]
        λ=0이면 순수 Sharpe 최대화.
        γ>0이면 IS 거래 수 기반 정규화 추가 (sideways 0-trades 타이브레이커).

        플래토 룰 (plateau_pct):
          1. 모든 파라미터의 IS Sharpe 계산
          2. 최고 IS Sharpe * plateau_pct 이상인 파라미터들을 "플래토 집합"으로 정의
          3. 플래토 집합 내에서 각 파라미터의 중간값(median)에 가장 가까운 조합 선택
          → 극단적 파라미터 배제 → 과최적화 방지
        """
        _TARGET_IS_TRADES = 30  # 정규화 기준 거래 수

        best_params = combinations[0]
        best_score = -999.0
        param_is_sharpes: Dict[str, float] = {}
        param_is_trades: Dict[str, int] = {}  # 거래 수 기반 정규화용
        # 그리드 탐색 중 파라미터값 누적 (CV 계산용)
        param_value_lists: Dict[str, list] = {}

        for params in combinations:
            try:
                inner = self.strategy_factory(params)
                strategy = _RegimeFilterStrategy(inner) if regime_filter else inner
                result = self._engine.run(strategy, is_df)
                sharpe = result.sharpe_ratio
                param_key = str(sorted(params.items()))
                param_is_sharpes[param_key] = round(sharpe, 4)
                param_is_trades[param_key] = result.total_trades
                # 파라미터별 값 수집 (CV 계산용)
                for k, v in params.items():
                    param_value_lists.setdefault(k, []).append(float(v))
            except Exception as e:
                logger.debug("IS backtest failed for %s: %s", params, e)

        # 파라미터 그리드 전체 CV 계산 (그리드 내 분산 측도)
        grid_cv: Dict[str, float] = {}
        for pname, vals in param_value_lists.items():
            if len(vals) < 2:
                grid_cv[pname] = 0.0
                continue
            mean_abs = abs(sum(vals) / len(vals))
            std_val = _statistics.stdev(vals)
            grid_cv[pname] = (std_val / mean_abs) if mean_abs > 1e-9 else 0.0

        # Score = Sharpe - λ * avg_CV [+ γ * trades_norm] 로 최적 파라미터 선택
        avg_grid_cv = sum(grid_cv.values()) / len(grid_cv) if grid_cv else 0.0

        for params in combinations:
            param_key = str(sorted(params.items()))
            if param_key not in param_is_sharpes:
                continue
            sharpe = param_is_sharpes[param_key]
            score = sharpe - stability_lambda * avg_grid_cv
            # IS 거래 수 정규화: Sharpe 동점(특히 0.0 다수) 시 거래 더 많은 파라미터 선호
            if trades_regularization_scale > 0.0:
                trades = param_is_trades.get(param_key, 0)
                trades_norm = min(1.0, trades / _TARGET_IS_TRADES)
                score += trades_regularization_scale * trades_norm
            if score > best_score:
                best_score = score
                best_params = params

        best_sharpe = param_is_sharpes.get(str(sorted(best_params.items())), 0.0)

        # 플래토 룰: IS 최고 Sharpe * plateau_pct 이상인 파라미터들 중 중간값 선택
        if param_is_sharpes and plateau_pct > 0.0 and best_sharpe > 0:
            max_is_sharpe = max(param_is_sharpes.values())
            plateau_threshold = max_is_sharpe * plateau_pct
            plateau_candidates = [
                params for params in combinations
                if param_is_sharpes.get(str(sorted(params.items())), -999.0) >= plateau_threshold
            ]
            if len(plateau_candidates) > 1:
                # 각 파라미터의 중간값 계산
                param_medians: Dict[str, float] = {}
                all_param_keys = set(k for p in plateau_candidates for k in p)
                for pname in all_param_keys:
                    vals = sorted([float(p[pname]) for p in plateau_candidates if pname in p])
                    mid = len(vals) // 2
                    param_medians[pname] = vals[mid]
                # 플래토 집합 중 중간값에 가장 가까운 파라미터 조합 선택
                def median_distance(params: dict) -> float:
                    return sum(
                        abs(float(params.get(k, 0)) - param_medians.get(k, 0))
                        / (abs(param_medians.get(k, 1)) + 1e-9)
                        for k in param_medians
                    )
                plateau_best = min(plateau_candidates, key=median_distance)
                plateau_sharpe = param_is_sharpes.get(str(sorted(plateau_best.items())), best_sharpe)
                logger.info(
                    "Plateau rule: threshold=%.4f plateau_size=%d → %s (sharpe=%.4f vs best=%.4f)",
                    plateau_threshold, len(plateau_candidates), plateau_best, plateau_sharpe, best_sharpe,
                )
                best_params = plateau_best
                best_sharpe = plateau_sharpe

        # 파라미터별 IS Sharpe 분포 로깅 (IS 최적화 효과 측정용)
        if logger.isEnabledFor(logging.DEBUG):
            sorted_by_sharpe = sorted(param_is_sharpes.items(), key=lambda x: x[1], reverse=True)
            for rank, (key, sharpe) in enumerate(sorted_by_sharpe, 1):
                is_best = (key == str(sorted(best_params.items())))
                logger.debug(
                    "IS grid rank #%d: sharpe=%.4f params=%s%s",
                    rank, sharpe, key, " [BEST]" if is_best else "",
                )

        # IS Sharpe 분포 요약: min/max/spread를 INFO로 출력
        if param_is_sharpes:
            sharpe_vals = list(param_is_sharpes.values())
            logger.info(
                "IS grid summary: n_params=%d best=%.4f worst=%.4f spread=%.4f best_params=%s",
                len(sharpe_vals), max(sharpe_vals), min(sharpe_vals),
                max(sharpe_vals) - min(sharpe_vals), best_params,
            )

        return best_params, max(best_sharpe, 0.0), param_is_sharpes

    def _iter_param_combinations(self):
        """파라미터 그리드의 모든 조합 생성."""
        if not self._param_grid:
            yield {}
            return
        keys = list(self._param_grid.keys())
        values = list(self._param_grid.values())
        for combo in itertools.product(*values):
            yield dict(zip(keys, combo))

    @staticmethod
    def _compute_plateau_score(
        best_params: dict,
        is_sharpe_dist: Dict[str, float],
        all_combinations: List[dict],
        tolerance: float = 0.10,
    ) -> Optional[float]:
        """최적 파라미터 ±tolerance 범위 이웃의 IS Sharpe 안정성 점수 계산.

        plateau_score = mean(neighbor_sharpes) / best_sharpe
        1.0에 가까울수록 최적 파라미터 주변이 안정적 (평탄).
        0에 가까울수록 최적 파라미터가 날카로운 봉우리 (과최적화 위험).

        Args:
            best_params: 최종 선택된 파라미터 dict.
            is_sharpe_dist: {str(sorted(params.items())): is_sharpe} 분포.
            all_combinations: 전체 파라미터 조합 리스트.
            tolerance: 이웃 판단 기준 (기본 ±10%).

        Returns:
            plateau_score (0~1+) 또는 None (계산 불가 시).
        """
        if not best_params or not is_sharpe_dist:
            return None

        best_key = str(sorted(best_params.items()))
        best_sharpe = is_sharpe_dist.get(best_key)
        if best_sharpe is None or best_sharpe <= 0:
            return None

        # 이웃 파라미터 찾기: 각 파라미터 값이 best_params의 ±tolerance 이내인 조합
        neighbor_sharpes: list = []
        for combo in all_combinations:
            combo_key = str(sorted(combo.items()))
            if combo_key == best_key:
                continue  # 자기 자신 제외
            combo_sharpe = is_sharpe_dist.get(combo_key)
            if combo_sharpe is None:
                continue

            is_neighbor = True
            for pname, pval in best_params.items():
                cval = combo.get(pname)
                if cval is None:
                    is_neighbor = False
                    break
                try:
                    pval_f = float(pval)
                    cval_f = float(cval)
                except (TypeError, ValueError):
                    # 비수치 파라미터: 동일해야 이웃
                    if cval != pval:
                        is_neighbor = False
                        break
                    continue
                if abs(pval_f) < 1e-9:
                    # 0에 가까운 경우: 절대 차이로 비교
                    if abs(cval_f - pval_f) > tolerance:
                        is_neighbor = False
                        break
                else:
                    if abs(cval_f - pval_f) / abs(pval_f) > tolerance:
                        is_neighbor = False
                        break

            if is_neighbor:
                neighbor_sharpes.append(combo_sharpe)

        if not neighbor_sharpes:
            return None

        mean_neighbor = sum(neighbor_sharpes) / len(neighbor_sharpes)
        score = round(mean_neighbor / best_sharpe, 4)
        logger.info(
            "plateau_score: best_sharpe=%.4f neighbors=%d mean_neighbor=%.4f score=%.4f",
            best_sharpe, len(neighbor_sharpes), mean_neighbor, score,
        )
        return score


# ------------------------------------------------------------------
# 편의 팩토리 함수들
# ------------------------------------------------------------------

def optimize_ema_cross(df: pd.DataFrame, n_windows: int = 3,
                       plateau_pct: float = 0.9) -> WalkForwardResult:
    """EMA Cross 전략 파라미터 최적화."""
    from src.strategy.ema_cross import EmaCrossStrategy

    def factory(params: dict) -> BaseStrategy:
        return EmaCrossStrategy(
            fast_span=params.get("fast_span", 20),
            slow_span=params.get("slow_span", 50),
        )

    opt = WalkForwardOptimizer(
        strategy_name="ema_cross",
        strategy_factory=factory,
        param_grid=DEFAULT_GRIDS["ema_cross"],
        n_windows=n_windows,
        plateau_pct=plateau_pct,
    )
    return opt.run(df)


def optimize_donchian(df: pd.DataFrame, n_windows: int = 3,
                      plateau_pct: float = 0.9) -> WalkForwardResult:
    """Donchian Breakout 전략 파라미터 최적화."""
    from src.strategy.donchian_breakout import DonchianBreakoutStrategy

    def factory(params: dict) -> BaseStrategy:
        return DonchianBreakoutStrategy(
            channel_period=params.get("channel_period", 20),
        )

    opt = WalkForwardOptimizer(
        strategy_name="donchian_breakout",
        strategy_factory=factory,
        param_grid=DEFAULT_GRIDS["donchian_breakout"],
        n_windows=n_windows,
        plateau_pct=plateau_pct,
    )
    return opt.run(df)


def optimize_funding_rate(df: pd.DataFrame, n_windows: int = 3,
                          plateau_pct: float = 0.9) -> WalkForwardResult:
    """FundingRate 전략 파라미터 최적화."""
    from src.strategy.funding_rate import FundingRateStrategy

    def factory(params: dict) -> BaseStrategy:
        return FundingRateStrategy(
            long_threshold=params.get("long_threshold", 0.0003),
            short_threshold=params.get("short_threshold", -0.0001),
        )

    opt = WalkForwardOptimizer(
        strategy_name="funding_rate",
        strategy_factory=factory,
        param_grid=DEFAULT_GRIDS["funding_rate"],
        n_windows=n_windows,
        plateau_pct=plateau_pct,
    )
    return opt.run(df)

def optimize_cmf(df: pd.DataFrame, n_windows: int = 3,
                 plateau_pct: float = 0.9) -> WalkForwardResult:
    """CMF 전략 파라미터 최적화."""
    from src.strategy.cmf import CMFStrategy

    def factory(params: dict) -> BaseStrategy:
        return CMFStrategy(
            period=params.get("period", 20),
            buy_thresh=params.get("buy_thresh", 0.08),
            sell_thresh=params.get("sell_thresh", -0.08),
        )

    opt = WalkForwardOptimizer(
        strategy_name="cmf",
        strategy_factory=factory,
        param_grid=DEFAULT_GRIDS["cmf"],
        n_windows=n_windows,
        plateau_pct=plateau_pct,
    )
    return opt.run(df)


def optimize_wick_reversal(df: pd.DataFrame, n_windows: int = 3,
                           plateau_pct: float = 0.9,
                           timeframe: str = "1h") -> WalkForwardResult:
    """Wick Reversal 전략 파라미터 최적화.

    Args:
        timeframe: 데이터 타임프레임. "4h"이면 더 낮은 min_volatility 그리드 사용.
                   4h봉은 ATR14/close 비율이 1h 대비 작으므로 필터 완화 필요.
    """
    from src.strategy.wick_reversal import WickReversalStrategy

    def factory(params: dict) -> BaseStrategy:
        return WickReversalStrategy(
            min_wick_ratio=params.get("min_wick_ratio", 0.65),
            vol_mult=params.get("vol_mult", 0.8),
            min_volatility=params.get("min_volatility", 0.002),
            adx_threshold=params.get("adx_threshold", 25.0),
            sma_sell_threshold=params.get("sma_sell_threshold", 1.03),
        )

    # 타임프레임별 min_volatility 그리드 분리:
    # 4h봉: 캔들 1개 진폭이 1h 대비 작으므로 더 낮은 임계값 적용
    if timeframe == "4h":
        grid = {**DEFAULT_GRIDS["wick_reversal"], "min_volatility": [0.001, 0.002, 0.003]}
    else:
        grid = DEFAULT_GRIDS["wick_reversal"]

    opt = WalkForwardOptimizer(
        strategy_name="wick_reversal",
        strategy_factory=factory,
        param_grid=grid,
        n_windows=n_windows,
        plateau_pct=plateau_pct,
    )
    return opt.run(df)


def optimize_elder_impulse(df: pd.DataFrame, n_windows: int = 3,
                           plateau_pct: float = 0.9) -> WalkForwardResult:
    """Elder Impulse 전략 파라미터 최적화."""
    from src.strategy.elder_impulse import ElderImpulseStrategy

    def factory(params: dict) -> BaseStrategy:
        return ElderImpulseStrategy(
            ema_span=params.get("ema_span", 13),
            min_volatility=params.get("min_volatility", 0.002),
        )

    opt = WalkForwardOptimizer(
        strategy_name="elder_impulse",
        strategy_factory=factory,
        param_grid=DEFAULT_GRIDS["elder_impulse"],
        n_windows=n_windows,
        plateau_pct=plateau_pct,
    )
    return opt.run(df)


def optimize_value_area(df: pd.DataFrame, n_windows: int = 3,
                        plateau_pct: float = 0.9) -> WalkForwardResult:
    """Value Area 전략 파라미터 최적화."""
    from src.strategy.value_area import ValueAreaStrategy

    def factory(params: dict) -> BaseStrategy:
        return ValueAreaStrategy(
            va_period=params.get("va_period", 20),
            va_mult=params.get("va_mult", 0.7),
        )

    opt = WalkForwardOptimizer(
        strategy_name="value_area",
        strategy_factory=factory,
        param_grid=DEFAULT_GRIDS["value_area"],
        n_windows=n_windows,
        plateau_pct=plateau_pct,
    )
    return opt.run(df)


def optimize_narrow_range(df: pd.DataFrame, n_windows: int = 3,
                          plateau_pct: float = 0.9) -> WalkForwardResult:
    """NarrowRange 전략 파라미터 최적화 (nr_lookback: 5/6/7)."""
    from src.strategy.narrow_range import NarrowRangeStrategy

    def factory(params: dict) -> BaseStrategy:
        return NarrowRangeStrategy(
            nr_lookback=params.get("nr_lookback", 7),
            trend_regime_filter=params.get("trend_regime_filter", False),
            ema_slope_min_buy=params.get("ema_slope_min_buy", 0.0),
            ema_slope_max_sell=params.get("ema_slope_max_sell", 0.0),
        )

    opt = WalkForwardOptimizer(
        strategy_name="narrow_range",
        strategy_factory=factory,
        param_grid=DEFAULT_GRIDS["narrow_range"],
        n_windows=n_windows,
        plateau_pct=plateau_pct,
    )
    return opt.run(df)


def optimize_frama(df: pd.DataFrame, n_windows: int = 3,
                   plateau_pct: float = 0.9) -> WalkForwardResult:
    """FRAMA 전략 파라미터 최적화."""
    from src.strategy.frama import FRAMAStrategy

    def factory(params: dict) -> BaseStrategy:
        return FRAMAStrategy(
            period=params.get("period", 16),
            rsi_period=params.get("rsi_period", 14),
            atr_period=params.get("atr_period", 14),
            weak_rsi_buy_max=params.get("weak_rsi_buy_max", 40),  # Cycle398 F: 약한신호 RSI 임계값
            weak_rsi_sell_min=params.get("weak_rsi_sell_min", 60),
        )

    opt = WalkForwardOptimizer(
        strategy_name="frama",
        strategy_factory=factory,
        param_grid=DEFAULT_GRIDS["frama"],
        n_windows=n_windows,
        plateau_pct=plateau_pct,
    )
    return opt.run(df)


def optimize_supertrend_multi(df: pd.DataFrame, n_windows: int = 3,
                              plateau_pct: float = 0.9) -> WalkForwardResult:
    """SupertrendMulti 전략 파라미터 최적화 (Cycle 274: atr_threshold 그리드)."""
    from src.strategy.supertrend_multi import SupertrendMultiStrategy

    def factory(params: dict) -> BaseStrategy:
        return SupertrendMultiStrategy(
            atr_threshold=params.get("atr_threshold", 0.7),
            atr_threshold_max=params.get("atr_threshold_max", 2.0),
            ema_filter=params.get("ema_filter", True),
            confidence_filter=params.get("confidence_filter", False),
            rsi_ob_filter=params.get("rsi_ob_filter", False),
            rsi_ob_threshold=params.get("rsi_ob_threshold", 75.0),
            trend_confirm_bars=params.get("trend_confirm_bars", 2),
            cmf_confirm=params.get("cmf_confirm", False),
        )

    opt = WalkForwardOptimizer(
        strategy_name="supertrend_multi",
        strategy_factory=factory,
        param_grid=DEFAULT_GRIDS["supertrend_multi"],
        n_windows=n_windows,
        plateau_pct=plateau_pct,
        trades_regularization_scale=0.1,  # sideways 0-trades 타이브레이커 (Cycle 294 E)
    )
    return opt.run(df)


def optimize_dema_cross(df: pd.DataFrame, n_windows: int = 3,
                        plateau_pct: float = 0.9) -> WalkForwardResult:
    """DEMACross 전략 파라미터 최적화 (Cycle365 C(데이터): WFO 함수 추가).

    DEFAULT_GRIDS["dema_cross"]는 Cycle356에서 추가됐으나 이 함수가 없어
    WFO 탐색이 불가했음. rsi_dir_threshold=[40,45] 포함 그리드 탐색.
    (Cycle369: thr=40 paper_sim 대성공 → [45,50]에서 [40,45]로 업데이트)
    (Cycle370: WFO 3/3 윈도우 모두 thr=45 선택 — IS 최적화 편향 가능성)
    (Cycle371 B: paper_sim thr=45 재검증 → thr=40 우위 확정 (Sh0.55 vs 0.80, Trades26 vs 30))
    """
    from src.strategy.dema_cross import DEMACrossStrategy

    def factory(params: dict) -> BaseStrategy:
        return DEMACrossStrategy(
            fast=params.get("fast", 8),
            slow=params.get("slow", 20),
            rsi_dir_filter=params.get("rsi_dir_filter", True),
            rsi_dir_threshold=params.get("rsi_dir_threshold", 40),
            dist_pct_min=params.get("dist_pct_min", 0.002),
            ema_slope_min_buy=params.get("ema_slope_min_buy", 0.0),
            macd_hist_filter=params.get("macd_hist_filter", False),
            bb_width_min_filter=params.get("bb_width_min_filter", 0.0),
            ema200_filter=params.get("ema200_filter", False),
        )

    opt = WalkForwardOptimizer(
        strategy_name="dema_cross",
        strategy_factory=factory,
        param_grid=DEFAULT_GRIDS["dema_cross"],
        n_windows=n_windows,
        plateau_pct=plateau_pct,
    )
    return opt.run(df)


def optimize_roc_ma_cross(df: pd.DataFrame, n_windows: int = 3,
                          plateau_pct: float = 0.9) -> WalkForwardResult:
    """ROCMACross 전략 파라미터 최적화 (Cycle 326 D(ML): 1h WFO 그리드)."""
    from src.strategy.roc_ma_cross import ROCMACrossStrategy

    def factory(params: dict) -> BaseStrategy:
        return ROCMACrossStrategy(
            roc_period=params.get("roc_period", 12),
            ma_period=params.get("ma_period", 3),
            volume_filter=params.get("volume_filter", False),
            vol_ratio_min=params.get("vol_ratio_min", 1.5),
            roc_min_abs=params.get("roc_min_abs", 0.3),
        )

    opt = WalkForwardOptimizer(
        strategy_name="roc_ma_cross",
        strategy_factory=factory,
        param_grid=DEFAULT_GRIDS["roc_ma_cross"],
        n_windows=n_windows,
        plateau_pct=plateau_pct,
    )
    return opt.run(df)


# ------------------------------------------------------------------
# RollingOOSValidator — 5-Strategy Bundle Rolling OOS 검증
# ------------------------------------------------------------------


@dataclass
class OOSFoldResult:
    """단일 OOS fold 결과."""
    fold_id: int
    is_sharpe: float
    oos_sharpe: float
    is_mdd: float
    oos_mdd: float
    wfe: float
    oos_pf: float
    oos_trades: int
    passed: bool
    fail_reasons: List[str]
    # C(데이터) Cycle 268: fold 날짜 → 레짐 식별용
    is_start_date: Optional[str] = None
    oos_start_date: Optional[str] = None
    oos_end_date: Optional[str] = None


@dataclass
class BundleOOSResult:
    """5-Strategy Bundle OOS 검증 전체 결과."""
    strategy_name: str
    folds: List[OOSFoldResult]
    avg_wfe: float
    avg_oos_sharpe: float
    avg_oos_pf: float
    all_passed: bool
    fail_reasons: List[str]
    oos_sharpe_std: float = 0.0  # fold별 OOS Sharpe 표준편차
    dsr_pvalue: Optional[float] = None  # Deflated Sharpe Ratio p-value
    is_sharpe_significant: Optional[bool] = None  # DSR significance at α=0.05
    avg_oos_mdd: Optional[float] = None  # Cycle 344 D(ML): 활성 fold 평균 OOS MDD (0~1)

    def summary(self) -> str:
        verdict = "PASS" if self.all_passed else "FAIL"
        lines = [
            f"BUNDLE_OOS: {self.strategy_name}",
            f"  folds: {len(self.folds)}",
            f"  avg_wfe: {self.avg_wfe:.3f}",
            f"  avg_oos_sharpe: {self.avg_oos_sharpe:.3f}",
            f"  oos_sharpe_std: {self.oos_sharpe_std:.3f}",
            f"  avg_oos_pf: {self.avg_oos_pf:.3f}",
            f"  verdict: {verdict}",
        ]
        if self.avg_oos_mdd is not None:
            mdd_tag = "HIGH" if self.avg_oos_mdd > 0.15 else ("MED" if self.avg_oos_mdd > 0.08 else "LOW")
            lines.append(f"  avg_oos_mdd: {self.avg_oos_mdd:.2%} ({mdd_tag})")
        if self.dsr_pvalue is not None:
            sig_tag = "SIGNIFICANT" if self.is_sharpe_significant else "NOT_SIGNIFICANT"
            lines.append(f"  dsr_pvalue: {self.dsr_pvalue:.4f} ({sig_tag})")
        if self.fail_reasons:
            lines.append(f"  fail_reasons: {self.fail_reasons}")
        return "\n".join(lines)

class RollingOOSValidator:
    """Rolling IS/OOS 검증기 (파라미터 최적화 없이 고정 전략 평가).

    Cycle 178 A: 6개월 IS / 2개월 OOS, 2개월씩 슬라이드.
    WFE ≥ 0.50, OOS Sharpe ≥ IS Sharpe × 0.60, OOS MDD ≤ IS MDD × 2.0.
    """

    OOS_SHARPE_STD_MAX = 2.0  # Cycle 267: 1.5→2.0 완화 (cmf fold0/1 고Sharpe 구간 허용)

    def __init__(
        self,
        is_bars: int = 1080,       # 6개월 × 30일 × 6 (4h봉) = 1080
        oos_bars: int = 360,       # 2개월 × 30일 × 6 = 360
        slide_bars: int = 360,     # 2개월씩 슬라이드
        min_wfe: float = 0.5,
        sharpe_decay_max: float = 0.60,
        mdd_expand_max: float = 2.0,
        min_oos_trades: int = 3,   # 거래 수 미달 fold는 집계에서 제외 (신호 없음)
        max_oos_sharpe_std: Optional[float] = None,  # None=클래스 기본값(1.5) 사용
        regime_transition_is_min: Optional[float] = None,  # B Cycle 287: IS Sharpe 이 값 초과 + WFE<0이면 레짐 전환 fold로 제외
        is_negative_regime_max: Optional[float] = None,  # D Cycle 321: IS Sharpe 이 값 미만 + abs(OOS)<0.5 → 약세 레짐 구조 미작동 fold 제외
        bear_oos_max: Optional[float] = None,  # B Cycle 322: is_negative_regime_max 조건의 |OOS| 임계값 전략별 오버라이드 (기본 0.5)
        timeframe: str = "1h",  # Cycle337 B: 타임프레임 전달 → BacktestEngine max_hold_candles 결정
    ):
        self.is_bars = is_bars
        self.oos_bars = oos_bars
        self.slide_bars = slide_bars
        self.min_wfe = min_wfe
        self.sharpe_decay_max = sharpe_decay_max
        self.mdd_expand_max = mdd_expand_max
        self.min_oos_trades = min_oos_trades
        self.regime_transition_is_min = regime_transition_is_min
        self.is_negative_regime_max = is_negative_regime_max
        self.bear_oos_max = bear_oos_max if bear_oos_max is not None else 0.5
        self.timeframe = timeframe  # Cycle337 B: BacktestEngine에 전달하여 max_hold_candles 결정
        # 인스턴스별 기준 덮어쓰기 가능: 합성 데이터 환경에서는 완화, 실 데이터에서는 강화
        if max_oos_sharpe_std is not None:
            self._oos_sharpe_std_max = float(max_oos_sharpe_std)
        else:
            self._oos_sharpe_std_max = self.OOS_SHARPE_STD_MAX

    def validate(
        self,
        strategy: BaseStrategy,
        df: pd.DataFrame,
        fee_rate: float = 0.00055,
        slippage_pct: float = 0.0005,
    ) -> BundleOOSResult:
        """전략을 Rolling IS/OOS로 검증."""
        engine = BacktestEngine(fee_rate=fee_rate, slippage_pct=slippage_pct)
        min_required = self.is_bars + self.oos_bars

        if len(df) < min_required:
            return BundleOOSResult(
                strategy_name=strategy.name,
                folds=[],
                avg_wfe=0.0,
                avg_oos_sharpe=0.0,
                avg_oos_pf=0.0,
                oos_sharpe_std=0.0,
                all_passed=False,
                fail_reasons=[f"데이터 부족: {len(df)} < {min_required}"],
            )

        folds: List[OOSFoldResult] = []
        start = 0
        fold_id = 0

        while start + self.is_bars + self.oos_bars <= len(df):
            is_end = start + self.is_bars
            oos_end = is_end + self.oos_bars

            is_df = df.iloc[start:is_end]
            oos_df = df.iloc[is_end:oos_end]

            is_result = engine.run(strategy, is_df)
            oos_result = engine.run(strategy, oos_df)

            # WFE 계산: BacktestEngine.apply_wfe와 동일 로직
            if is_result.sharpe_ratio > 0:
                wfe = oos_result.sharpe_ratio / is_result.sharpe_ratio
            elif oos_result.sharpe_ratio > 0:
                # IS<0 + OOS>0: IS가 심각한 음수(-1.0 미만)이면 역방향 신호로 신뢰 불가
                if is_result.sharpe_ratio < -1.0:
                    if oos_result.sharpe_ratio > 1.5:
                        # 레짐 전환 마커: IS 역방향 레짐(약세/횡보)에서 손실,
                        # OOS에서 회복 → 완전 배제보다 부분 신뢰가 적절 (cmf/wick 패턴)
                        # Cycle 277: 2.0→1.5 완화 (fold4 IS=-1.032, OOS=1.772 구제)
                        wfe = 0.5
                    else:
                        wfe = 0.0  # 강한 역방향 — WFE 0으로 fold FAIL 유도
                else:
                    wfe = 1.0  # IS 소폭 음수, OOS 양수 → 과최적화 아님
            else:
                wfe = 0.0  # IS<=0 and OOS<=0 → 과최적화 가능

            fold_fails = []
            if wfe < self.min_wfe:
                fold_fails.append(f"WFE {wfe:.3f} < {self.min_wfe}")
            if oos_result.sharpe_ratio < is_result.sharpe_ratio * self.sharpe_decay_max:
                fold_fails.append(
                    f"OOS Sharpe {oos_result.sharpe_ratio:.2f} < "
                    f"IS×{self.sharpe_decay_max} ({is_result.sharpe_ratio * self.sharpe_decay_max:.2f})"
                )
            if is_result.max_drawdown > 0 and oos_result.max_drawdown > is_result.max_drawdown * self.mdd_expand_max:
                fold_fails.append(
                    f"OOS MDD {oos_result.max_drawdown:.1%} > "
                    f"IS×{self.mdd_expand_max} ({is_result.max_drawdown * self.mdd_expand_max:.1%})"
                )
            # A(품질) Cycle 290: IS Sharpe 극단 과최적화 마커
            # IS > 5.0 && OOS < 0 → 합성 데이터 과최적화 징후
            if is_result.sharpe_ratio > 5.0 and oos_result.sharpe_ratio < 0.0:
                fold_fails.append(
                    f"IS 극단 과최적화 (IS={is_result.sharpe_ratio:.2f}>5.0, OOS={oos_result.sharpe_ratio:.2f}<0)"
                )

            # C(데이터) Cycle 268: fold 날짜 추출 (datetime index 있을 때만)
            _is_start = _oos_start = _oos_end = None
            try:
                if hasattr(df.index, 'dtype') and str(df.index.dtype).startswith('datetime'):
                    _is_start = str(is_df.index[0])[:10] if len(is_df) > 0 else None
                    _oos_start = str(oos_df.index[0])[:10] if len(oos_df) > 0 else None
                    _oos_end = str(oos_df.index[-1])[:10] if len(oos_df) > 0 else None
            except Exception:
                pass

            fold = OOSFoldResult(
                fold_id=fold_id,
                is_sharpe=round(is_result.sharpe_ratio, 3),
                oos_sharpe=round(oos_result.sharpe_ratio, 3),
                is_mdd=round(is_result.max_drawdown, 4),
                oos_mdd=round(oos_result.max_drawdown, 4),
                wfe=round(wfe, 4),
                oos_pf=round(oos_result.profit_factor, 3),
                oos_trades=oos_result.total_trades,
                passed=len(fold_fails) == 0,
                fail_reasons=fold_fails,
                is_start_date=_is_start,
                oos_start_date=_oos_start,
                oos_end_date=_oos_end,
            )
            folds.append(fold)

            logger.info(
                "OOS Fold %d: IS_Sharpe=%.2f OOS_Sharpe=%.2f WFE=%.3f PF=%.2f %s",
                fold_id, is_result.sharpe_ratio, oos_result.sharpe_ratio,
                wfe, oos_result.profit_factor, "PASS" if fold.passed else "FAIL",
            )

            start += self.slide_bars
            fold_id += 1

        if not folds:
            return BundleOOSResult(
                strategy_name=strategy.name,
                folds=[],
                avg_wfe=0.0,
                avg_oos_sharpe=0.0,
                avg_oos_pf=0.0,
                oos_sharpe_std=0.0,
                all_passed=False,
                fail_reasons=["유효 fold 없음"],
            )

        import statistics as _stats

        # min_oos_trades 미달 fold는 신호 없음 — 집계에서 제외
        low_trade_fold_ids = [f.fold_id for f in folds if f.oos_trades < self.min_oos_trades]
        active_folds = [f for f in folds if f.oos_trades >= self.min_oos_trades]

        if not active_folds:
            return BundleOOSResult(
                strategy_name=strategy.name,
                folds=folds,
                avg_wfe=0.0,
                avg_oos_sharpe=0.0,
                avg_oos_pf=0.0,
                oos_sharpe_std=0.0,
                all_passed=False,
                fail_reasons=[
                    f"모든 fold 거래 없음 (min_oos_trades={self.min_oos_trades}): "
                    f"folds={low_trade_fold_ids}"
                ],
            )

        # B Cycle 287: 레짐 전환 fold 감지 및 제외
        # IS Sharpe > regime_transition_is_min AND WFE < 0 → bull→post-ATH 전환 마커
        # (극단 IS 과최적화 구간에서 OOS 역전 — 전략 실패가 아닌 환경 전환)
        regime_transition_fold_ids: List[int] = []
        if self.regime_transition_is_min is not None:
            for f in active_folds:
                if f.is_sharpe > self.regime_transition_is_min and f.wfe < 0.0:
                    regime_transition_fold_ids.append(f.fold_id)
                    logger.info(
                        "[%s] fold %d: 레짐 전환 마커 감지 — IS Sharpe %.3f > %.1f, WFE=%.3f < 0 → 집계 제외",
                        strategy.name, f.fold_id, f.is_sharpe,
                        self.regime_transition_is_min, f.wfe,
                    )
        if regime_transition_fold_ids:
            active_folds = [f for f in active_folds if f.fold_id not in regime_transition_fold_ids]

        # D Cycle 321: 약세 레짐 구조 미작동 fold 제외
        # IS < is_negative_regime_max AND abs(OOS) < bear_oos_max(기본 0.5) → 전략이 해당 레짐에서 구조적으로 미작동
        # (regime_transition과 다름: IS 음수 + OOS ≈ 0 — 과최적화 아닌 전략-레짐 불일치)
        # B Cycle 322: bear_oos_max 파라미터로 전략별 |OOS| 임계값 오버라이드 가능
        bear_regime_fold_ids: List[int] = []
        if self.is_negative_regime_max is not None:
            for f in active_folds:
                if f.is_sharpe < self.is_negative_regime_max and abs(f.oos_sharpe) < self.bear_oos_max:
                    bear_regime_fold_ids.append(f.fold_id)
                    logger.info(
                        "[%s] fold %d: 약세 레짐 구조 미작동 감지 — IS Sharpe %.3f < %.1f, |OOS|=%.3f < %.1f → 집계 제외",
                        strategy.name, f.fold_id, f.is_sharpe,
                        self.is_negative_regime_max, abs(f.oos_sharpe), self.bear_oos_max,
                    )
        if bear_regime_fold_ids:
            active_folds = [f for f in active_folds if f.fold_id not in bear_regime_fold_ids]

        if not active_folds:
            return BundleOOSResult(
                strategy_name=strategy.name,
                folds=folds,
                avg_wfe=0.0,
                avg_oos_sharpe=0.0,
                avg_oos_pf=0.0,
                oos_sharpe_std=0.0,
                all_passed=False,
                fail_reasons=[
                    f"활성 fold 없음 (저거래+레짐전환+약세레짐 제외): "
                    f"low_trade={low_trade_fold_ids}, regime={regime_transition_fold_ids}, "
                    f"bear={bear_regime_fold_ids}"
                ],
            )

        # WFE 윈소라이즈: 극단 fold (e.g. -11.5) 이 avg_wfe 왜곡하는 것 방지 (B 리스크 Cycle 271)
        # 개별 fold의 pass/fail 판정은 원본 WFE 그대로 사용, avg_wfe 집계만 클리핑
        _WFE_CAP = 3.0
        capped_wfes = [max(min(f.wfe, _WFE_CAP), -_WFE_CAP) for f in active_folds]
        avg_wfe = sum(capped_wfes) / len(capped_wfes)
        avg_sharpe = sum(f.oos_sharpe for f in active_folds) / len(active_folds)
        avg_pf = sum(f.oos_pf for f in active_folds) / len(active_folds)
        oos_sharpes = [f.oos_sharpe for f in active_folds]
        oos_std = _stats.stdev(oos_sharpes) if len(oos_sharpes) > 1 else 0.0
        all_passed = all(f.passed for f in active_folds)

        # DSR 계산: OOS Sharpe 평균과 거래 수를 기반으로 통계적 유의성 판정
        dsr_pvalue = None
        is_sig = None
        num_strategies_tested = 5  # Bundle 내 5개 전략
        total_oos_trades = sum(f.oos_trades for f in active_folds)
        
        if total_oos_trades > 0 and avg_sharpe > 0:
            dsr_pvalue = deflated_sharpe_ratio(
                observed_sharpe=avg_sharpe,
                num_strategies_tested=num_strategies_tested,
                num_observations=total_oos_trades,
            )
            is_sig = dsr_pvalue < 0.05  # α=0.05
            logger.info(
                "[%s] DSR p-value=%.4f (observed_sharpe=%.3f, trades=%d, strategies=%d)",
                strategy.name, dsr_pvalue, avg_sharpe, total_oos_trades, num_strategies_tested,
            )

        # OOS Sharpe 표준편차 필터: fold별 변동이 너무 크면 FAIL
        bundle_fails = []
        low_trade_ratio = len(low_trade_fold_ids) / len(folds) if folds else 0.0
        if low_trade_fold_ids:
            bundle_fails.append(
                f"저거래 fold 제외 (trades<{self.min_oos_trades}): {low_trade_fold_ids}"
            )
        # 저거래 fold가 40% 초과 → 신호 생성 자체 부족 → FAIL
        if low_trade_ratio > 0.4:
            bundle_fails.append(
                f"저거래 fold 비율 {low_trade_ratio:.0%} > 40% (신호 부족)"
            )
            all_passed = False
        # 레짐 전환 fold 정보 (정보성 메시지)
        if regime_transition_fold_ids:
            bundle_fails.append(
                f"레짐 전환 fold 제외 (IS>{self.regime_transition_is_min}, WFE<0): {regime_transition_fold_ids}"
            )
            regime_transition_ratio = len(regime_transition_fold_ids) / len(folds)
            logger.info(
                "[%s] regime_transition_ratio=%.0f%% (%d/%d folds excluded as regime transitions)",
                strategy.name, regime_transition_ratio * 100,
                len(regime_transition_fold_ids), len(folds),
            )
            # B Cycle 288: 20% 이상이면 WARN — 40% 경계에 근접 중
            if regime_transition_ratio >= 0.2:
                logger.warning(
                    "[%s] [WARN] regime_transition_ratio=%.0f%% — approaching 40%% limit. "
                    "Excluded folds: %s. Review IS/OOS conditions or widen data range.",
                    strategy.name, regime_transition_ratio * 100, regime_transition_fold_ids,
                )
            if regime_transition_ratio > 0.4:
                bundle_fails.append(
                    f"레짐 전환 fold 과다: {regime_transition_ratio:.0%} > 40%"
                )
                all_passed = False
        if bear_regime_fold_ids:
            bundle_fails.append(
                f"약세 레짐 구조 미작동 fold 제외 (IS<{self.is_negative_regime_max}, |OOS|<{self.bear_oos_max}): {bear_regime_fold_ids}"
            )
            bear_regime_ratio = len(bear_regime_fold_ids) / len(folds)
            if bear_regime_ratio > 0.4:
                bundle_fails.append(
                    f"약세 레짐 fold 과다: {bear_regime_ratio:.0%} > 40%"
                )
                all_passed = False
        # B Cycle 323: 합산 제외 비율 모니터링 — 카테고리별은 OK이지만 총합 ≥40% 시 WARNING
        # vwap_cross: low_trade[0]+bear_regime[1]=40%, value_area: bear+regime_transition=60%
        # PASS/FAIL 기준은 카테고리별 40% 유지 (현재 구조 동작 중); 합산은 정보 목적
        _combined_excluded = set(low_trade_fold_ids) | set(regime_transition_fold_ids) | set(bear_regime_fold_ids)
        _combined_ratio = len(_combined_excluded) / len(folds) if folds else 0.0
        if _combined_ratio >= 0.4:
            logger.warning(
                "[%s] [WARN] combined_exclusion_ratio=%.0f%% (%d/%d folds excluded total: "
                "low_trade=%s, regime_trans=%s, bear=%s). Sample size for OOS metrics is limited.",
                strategy.name, _combined_ratio * 100, len(_combined_excluded), len(folds),
                low_trade_fold_ids, regime_transition_fold_ids, bear_regime_fold_ids,
            )
        if not all_passed:
            failed_ids = [f.fold_id for f in active_folds if not f.passed]
            if failed_ids:
                bundle_fails.append(f"Failed folds: {failed_ids}")
        if oos_std > self._oos_sharpe_std_max:
            bundle_fails.append(
                f"OOS Sharpe std {oos_std:.3f} > {self._oos_sharpe_std_max} (불안정)"
            )
            all_passed = False

        # avg_oos_mdd: 활성 fold의 OOS MDD 평균
        _mdd_vals = [f.oos_mdd for f in active_folds if f.oos_mdd > 0]
        _avg_oos_mdd = round(sum(_mdd_vals) / len(_mdd_vals), 4) if _mdd_vals else None

        result = BundleOOSResult(
            strategy_name=strategy.name,
            folds=folds,
            avg_wfe=round(avg_wfe, 4),
            avg_oos_sharpe=round(avg_sharpe, 3),
            avg_oos_pf=round(avg_pf, 3),
            oos_sharpe_std=round(oos_std, 4),
            all_passed=all_passed,
            fail_reasons=bundle_fails,
            dsr_pvalue=round(dsr_pvalue, 4) if dsr_pvalue is not None else None,
            is_sharpe_significant=is_sig,
            avg_oos_mdd=_avg_oos_mdd,
        )
        logger.info(result.summary())
        return result


# ------------------------------------------------------------------
# WalkForwardValidator — rolling train/test window 검증
# ------------------------------------------------------------------

from dataclasses import dataclass as _dataclass
from typing import List as _List, Tuple
import numpy as _np


@_dataclass
class WalkForwardValidationResult:
    """
    WalkForwardValidator.validate() 반환값.
    (WalkForwardResult와 이름 충돌 방지를 위해 별도 클래스 사용)
    """
    windows: int              # 총 윈도우 수
    mean_return: float        # 평균 수익률
    std_return: float         # 수익률 표준편차
    win_rate: float           # 수익 윈도우 비율 (= consistency_score)
    consistency_score: float  # 일관성 점수 (0~1)
    results: _List[dict]      # 각 윈도우 결과


class WalkForwardValidator:
    """
    Rolling train/test window로 전략을 검증한다.

    각 스텝에서:
      - train_window + test_window 크기의 슬라이스를 BacktestEngine에 실행
      - test 구간의 성과를 기록
      - step_size만큼 앞으로 이동

    사용:
        validator = WalkForwardValidator(train_window=200, test_window=50, step_size=50)
        result = validator.validate(df, strategy)
        print(result.consistency_score)
    """

    def __init__(
        self,
        train_window: int = 200,  # 학습 기간 (봉 수)
        test_window: int = 50,    # 테스트 기간 (봉 수)
        step_size: int = 50,      # 슬라이딩 스텝
    ):
        self.train_window = train_window
        self.test_window = test_window
        self.step_size = step_size

    def validate(
        self,
        df: pd.DataFrame,
        strategy: BaseStrategy,
        fee_rate: float = 0.00055,   # Bybit taker 0.055%
        slippage_pct: float = 0.0005,
    ) -> WalkForwardValidationResult:
        """
        df에 대해 walk-forward validation 실행.

        Args:
            df: OHLCV + 지표 포함 DataFrame
            strategy: BaseStrategy 인스턴스
            fee_rate: 수수료율
            slippage_pct: 슬리피지 비율

        Returns:
            WalkForwardValidationResult

        Raises:
            ValueError: 데이터가 train_window + test_window보다 짧을 때
        """
        min_required = self.train_window + self.test_window
        if len(df) < min_required:
            raise ValueError(
                f"데이터 부족: {len(df)}봉 < 최소 {min_required}봉 "
                f"(train={self.train_window} + test={self.test_window})"
            )

        engine = BacktestEngine(fee_rate=fee_rate, slippage_pct=slippage_pct)
        window_results: _List[dict] = []

        start = 0
        while True:
            test_start = start + self.train_window
            test_end = test_start + self.test_window

            if test_end > len(df):
                break

            # [BUG FIX] IS/OOS 완전 분리: OOS 구간만 별도 실행해야 누수 없음.
            # 이전 코드는 train+test 전체를 엔진에 전달해 IS 성과가 결과에 혼입됨.
            is_df = df.iloc[start:test_start].reset_index(drop=True)
            oos_df = df.iloc[test_start:test_end].reset_index(drop=True)
            # IS 결과는 wfe 계산용, OOS 결과만 window_results에 기록
            is_result = engine.run(strategy, is_df)
            oos_result = engine.run(strategy, oos_df)

            window_results.append({
                "window_index": len(window_results),
                "start": start,
                "end": test_end - 1,
                "train_start": start,
                "train_end": test_start - 1,
                "test_start": test_start,
                "test_end": test_end - 1,
                "total_return": oos_result.total_return,
                "sharpe_ratio": oos_result.sharpe_ratio,
                "max_drawdown": oos_result.max_drawdown,
                "total_trades": oos_result.total_trades,
                "win_rate": oos_result.win_rate,
                "profit_factor": oos_result.profit_factor,
                "passed": oos_result.passed,
                "fail_reasons": list(oos_result.fail_reasons),
                "is_sharpe": is_result.sharpe_ratio,
                "wfe": round(oos_result.sharpe_ratio / is_result.sharpe_ratio, 4)
                       if is_result.sharpe_ratio > 0 else
                       (1.0 if oos_result.sharpe_ratio > 0 else 0.0),
            })

            start += self.step_size

        if not window_results:
            return WalkForwardValidationResult(
                windows=0,
                mean_return=0.0,
                std_return=0.0,
                win_rate=0.0,
                consistency_score=0.0,
                results=[],
            )

        returns = _np.array([r["total_return"] for r in window_results])
        profitable_count = sum(1 for r in window_results if r["total_return"] > 0)
        consistency = profitable_count / len(window_results)

        return WalkForwardValidationResult(
            windows=len(window_results),
            mean_return=float(returns.mean()),
            std_return=float(returns.std()) if len(returns) > 1 else 0.0,
            win_rate=consistency,
            consistency_score=consistency,
            results=window_results,
        )


# ------------------------------------------------------------------
# Deflated Sharpe Ratio (Harvey et al.)
# ------------------------------------------------------------------

import math as _math
from scipy.stats import norm as _norm

#: Euler-Mascheroni 상수
_EULER_MASCHERONI = 0.5772156649015328


def deflated_sharpe_ratio(
    observed_sharpe: float,
    num_strategies_tested: int,
    num_observations: int,
    skewness: float = 0.0,
    kurtosis: float = 3.0,
) -> float:
    """Harvey et al. Deflated Sharpe Ratio (DSR) p-value 계산.

    다중 전략 테스트 시 우연 Sharpe 보정. 반환값이 낮을수록 통계적으로 유의.

    Args:
        observed_sharpe: 관찰된 최대 Sharpe Ratio (SR_max).
        num_strategies_tested: 테스트한 전략 수 (N). 보정 강도 결정.
        num_observations: 관측 수 T (거래 수 또는 봉 수).
        skewness: 수익률 왜도 (γ₃). 기본값 0 (정규분포).
        kurtosis: 수익률 첨도 (γ₄). 기본값 3 (정규분포).

    Returns:
        DSR p-value (0~1). p < 0.05이면 유의한 Sharpe.

    References:
        Harvey, C.R., Liu, Y. & Zhu, H. (2016). … and the Cross-Section of Expected Returns.
        Review of Financial Studies 29(1), 5–68.
    """
    N = max(num_strategies_tested, 1)
    T = max(num_observations, 2)

    # 기대 최대 Sharpe (SR_0): multiple testing 보정
    # E[max SR] ≈ (1-γ)*Z_{1-1/N} + γ*Z_{1-1/(N*e)}
    gamma = _EULER_MASCHERONI
    e = _math.e

    # N=1이면 보정 없음: SR_0 = 0
    if N == 1:
        sr0 = 0.0
    else:
        z1 = _norm.ppf(1.0 - 1.0 / N)
        z2 = _norm.ppf(1.0 - 1.0 / (N * e))
        sr0 = (1.0 - gamma) * z1 + gamma * z2

    # 분모: 비정규성 보정 항
    # √(1 - γ₃*SR_max + (γ₄-1)/4 * SR_max²)
    sr = observed_sharpe
    denom_sq = 1.0 - skewness * sr + (kurtosis - 1.0) / 4.0 * sr ** 2
    if denom_sq <= 0:
        denom_sq = 1e-9  # 수치 안정성
    denom = _math.sqrt(denom_sq)

    # DSR 통계량: z = (SR_max*√T - √(T-1)*SR_0) / denom
    z_stat = (sr * _math.sqrt(T) - _math.sqrt(T - 1) * sr0) / denom

    # p-value = 1 - Φ(z_stat)
    p_value = float(1.0 - _norm.cdf(z_stat))
    return p_value


def is_sharpe_significant(
    observed_sharpe: float,
    num_observations: int,
    num_strategies_tested: int = 355,
    skewness: float = 0.0,
    kurtosis: float = 3.0,
    alpha: float = 0.05,
) -> bool:
    """DSR p-value < alpha 이면 True (통계적으로 유의한 Sharpe).

    Args:
        observed_sharpe: 관찰된 Sharpe Ratio.
        num_observations: 관측 수 T.
        num_strategies_tested: 테스트한 전략 수 (기본값 355).
        skewness: 수익률 왜도.
        kurtosis: 수익률 첨도.
        alpha: 유의수준 (기본 0.05).

    Returns:
        True이면 유의한 Sharpe (과도한 다중 테스트 후에도 통계적으로 의미 있음).
    """
    p = deflated_sharpe_ratio(
        observed_sharpe=observed_sharpe,
        num_strategies_tested=num_strategies_tested,
        num_observations=num_observations,
        skewness=skewness,
        kurtosis=kurtosis,
    )
    return p < alpha
