# Next Steps

_Last updated: 2026-06-14 (Cycle 311 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 311

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 309 | D+E+F | cmf buy_thresh=0.10 paper_sim 실험(미미한 개선), 슬리피지 레짐 추적 추가, NR ema_slope 조사 |
| 310 | A+C+F | cmf period=40 역효과 확인(복원), NR ema_slope_min_buy/max_sell 구현, bundle OOS init params 업데이트 |
| 311 | B+D+F | 슬리피지 레짐 리포트 추가(paper_sim), NR ema_slope 버그수정(enrich_indicators 누락), ema_slope 실험 결과 분석 후 기본값 복원 |

### 🎯 Cycle 312 작업 방향 (312 mod 5 = 2 → B(리스크) + D(ML) + F(리서치))

#### B(리스크): KellySizer 및 CircuitBreaker 점검
- **KellySizer `kelly_reduce_at_mdd` 파라미터 최적화**:
  - 현재: kelly_reduce_at_mdd=0.08 (MDD>8% 시 Kelly 50% 축소)
  - price_cluster MDD=12.2%일 때 Kelly 이미 축소 — 이 기준이 적절한지 검토
  - 테스트: `tests/test_risk_kelly.py` 실행하여 kelly_reduce_at_mdd 관련 테스트 확인
- **CircuitBreaker 룰 확장 검토**:
  - 현재 3층 서킷브레이커(일/주/월) 이외에 **연속 FAIL 전략 kill** 로직 미구현
  - DrawdownMonitor.should_kill_strategy() 함수 존재하나 paper_sim/backtest에서 활용 안 됨
  - 백테스트 엔진에서 should_kill_strategy() 연동 가능성 검토 (별도 파라미터)

#### D(ML): narrow_range 저거래 문제 해결 방향 탐색
- **narrow_range 근본 문제**: 4h bar에서 신호 부족 (5-fold 중 60%가 trades<10)
  - ema_slope 필터 → 신호를 더 줄여서 오히려 악화
  - atr_trend_max → 효과 없음 (Cycle307)
  - trend_regime_filter → 효과 없음 (Cycle307)
- **다음 실험 후보**:
  - `nr_lookback` 감소 (5→3): 더 자주 신호 발생 → trades 증가 목표
  - 단독 실험 원칙 유지: nr_lookback만 변경
  - 예상 효과: trades 증가(낮은 threshold), 하지만 PF 저하 가능성
- **BUNDLE_STRATEGY_INIT_PARAMS["narrow_range"] 현재 설정**:
  - `{"trend_regime_filter": False, "ema_slope_min_buy": 0.0, "ema_slope_max_sell": 0.0}` ← Cycle311 복원

#### F(리서치): 1h Walk-Forward 윈도우 축소 실험 설계
- **Train window 축소 가설** (Cycle 311 F 결론):
  - 현재: TRAIN_HOURS=5040h(210일), TEST_HOURS=1440h(60일) → 8 windows
  - 가설 A: TRAIN_HOURS=2016h(84일), TEST_HOURS=1440h(60일) → 더 많은 windows
  - 가설 B: TRAIN_HOURS=5040h, TEST_HOURS=720h(30일) → windows 증가, trades 감소 우려
  - 실험 전 주의: trades≥15 기준이 30일 test에서 충족 어려울 수 있음
  - **권고**: 가설 A 먼저 시도 (train만 줄여 최신 regime 반영도 개선)
  - 단, paper_simulation.py에서 TRAIN_HOURS 상수 변경만 하면 됨 (코드 간단)

### ⚠️ 주의 사항 (Cycle 312)
- **PAPER_SIM_STRATEGY_PARAMS 현재 설정** (Cycle 311 변경 없음):
  - `value_area: {"vol_filter_mult": 0.5}` ← Cycle 295 A
  - `wick_reversal: {"min_volatility": 0.001, "vol_mult": 0.6}` ← Cycle 295 A
  - `relative_volume: {"rvol_buy_sell": 1.2}` ← Cycle 297 B
  - `momentum_quality: {"quality_score_buy_threshold": 0.8, "consistency_buy_threshold": 0.3}` ← Cycle 295 C
  - `price_cluster: {"bounce_pct": 0.025, "close_window": 60, "vol_regime_filter": True, "vol_use_relative": True, "vol_atr_trend_min": 1.5}` ← Cycle 305 C
  - `order_flow_imbalance_v2: {"trend_span": 20}` ← Cycle 298 F
  - `cmf: {"buy_thresh": 0.10}` ← Cycle 309 D (1h: 구조적 FAIL, 4h 전용 확정)
- **BUNDLE_STRATEGY_INIT_PARAMS 현재 설정** (Cycle 311 변경):
  - `narrow_range: {"trend_regime_filter": False, "ema_slope_min_buy": 0.0, "ema_slope_max_sell": 0.0}` ← Cycle311 D(ML) 복원
  - `supertrend_multi: {atr_threshold=0.5, ema_filter=True, cmf_confirm=True, ...}`
- **run_bundle_oos.py enrich_indicators() 수정** (Cycle 311 D):
  - `df["ema20_slope"] = df["ema20"].diff() / df["ema20"]` 추가 — feed.py와 동기화됨
- **paper_simulation.py 슬리피지 레짐 리포트** (Cycle 311 B):
  - window_results에 `slippage_regime_counts` 필드 추가
  - 결과 dict에 `slippage_regime_agg` 추가
  - generate_report()에 "슬리피지 레짐 분포" 섹션 추가
- **Bundle OOS 실행 시 --csv-dir data/historical 필수**
- **단독 실험 원칙**: 두 파라미터를 동시에 변경하면 역효과 원인 특정 불가

### 핵심 메트릭 (Cycle 311)
- 테스트: **8400 passed, 23 skipped** (회귀 없음)
- Paper Sim BTC 1h (8 windows): **0/22 PASS**
  - price_cluster: rank1 score=75.7 (AvgSharpe=0.59, MDD=12.2%, 3/8 consistent)
  - supertrend_multi: rank2 score=68.3 (2/8 consistent)
  - slippage regime: 대부분 전략 ~15% high (정상), dema_cross 79.2% (저거래 노이즈)
- Bundle OOS BTC 4h (5-fold): **2/5 PASS** (cmf=2.508, supertrend_multi=3.674)
  - narrow_range: ema_slope=0.001 실험 → fold2 악화 + 저거래 문제 → 기본값(0.0) 복원
  - cmf: 5/5 ALL PASS (avg OOS Sharpe=2.508, std=1.888) — 안정적 유지
  - value_area: OOS std=2.018 (임계값 초과 FAIL 지속)

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: real CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows)
- ETH/SOL: synthetic CSV (data/historical/synthetic/)
- Bundle OOS: `--csv-dir data/historical` 필수 (5-fold 4h 구조, 2023~2024 실제 BTC)
- Paper simulation 1h: 22 전략 × 8 windows → 약 7-10분 소요
