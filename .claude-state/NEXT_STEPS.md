# Next Steps

_Last updated: 2026-06-15 (Cycle 312 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 312

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 310 | A+C+F | cmf period=40 역효과 확인(복원), NR ema_slope_min_buy/max_sell 구현, bundle OOS init params 업데이트 |
| 311 | B+D+F | 슬리피지 레짐 리포트 추가(paper_sim), NR ema_slope 버그수정(enrich_indicators 누락), ema_slope 실험 결과 분석 후 기본값 복원 |
| 312 | B+D+F | kelly_fraction_multiplier 테스트 추가(4개), NR nr_lookback=4 실험→효과없음(복원), TRAIN_HOURS=84일 실험→역효과(210일 복원) |

### 🎯 Cycle 313 작업 방향 (313 mod 5 = 3 → C(데이터) + B(리스크) + F(리서치))

#### C(데이터): narrow_range 저거래 binding constraint 탐구
- **Cycle 312 D 결론**: nr_lookback 5→4 변경은 효과 없음
  - NR4/NR5 동일 bars에서 최소 range → lookback이 binding constraint 아님
  - **실제 binding constraint**: ATR_THRESHOLD(0.95), VOL_SPIKE_MULT(1.0), NR_SCAN_WINDOW(3)
- **다음 실험 후보** (단독 실험 원칙):
  - `ATR_THRESHOLD` 완화: 0.95→1.05 (ATR 수축 조건 거의 폐기) — trades 증가 기대
  - `VOL_SPIKE_MULT` 제거: 1.0→0.5 (거래량 필터 완화) — trades 대폭 증가 가능
  - `NR_SCAN_WINDOW` 확장: 3→5 (더 먼 NR 이후 돌파도 허용) — trades 증가
  - 권고: NR_SCAN_WINDOW 3→5 먼저 시도 (신호 발생 윈도우 확장, 가장 직접적)
- **주의**: narrow_range 파라미터는 BUNDLE_STRATEGY_INIT_PARAMS에만 영향 (INIT_PARAMS로 고정 실험)
  - 하지만 NR_SCAN_WINDOW는 클래스 레벨 상수 → 직접 코드 수정 필요

#### B(리스크): kelly_reduce_at_mdd 기준 유지 확인
- **Cycle 312 B 결론**: kelly_reduce_at_mdd=0.08 기준 적절함
  - mdd_warn(5%) < kelly_reduce(8%) < mdd_block(10%) 순서 — 2% 안전 마진
  - price_cluster MDD=12.2% → kelly_fraction=0.5 AND mdd_size=0.0 모두 적용 (정상)
  - CircuitBreaker should_kill_strategy()는 manager.py에 이미 구현됨 — 추가 개선 불필요
- **이번 사이클 B 작업**: RiskManager 단위 테스트 확장
  - `manager.py:check_strategy_health()` 테스트 존재 여부 확인 (`tests/test_risk_manager.py`)
  - should_kill_strategy() 레짐별 배수 테스트 추가 가능

#### F(리서치): Walk-Forward 윈도우 실험 결론 도출
- **Cycle 312 F 결론**: 가설 A(84일 train) FAIL
  - 84일 train: price_cluster 3/8→1/12 consistency 폭락
  - 12 windows 생성됐으나 파라미터 과적합 방지 못함 → 210일 복원
- **가설 B 보류**: TEST=30일이면 trades≥15 기준 충족 어려울 것
- **다음 방향 (F 리서치)**:
  - 1h BTC 구조적 FAIL 근본 원인 재분석:
    - `profit_factor < 1.5`가 가장 빈번한 실패 (Cycle 312 12-window 결과에서도 확인)
    - PF 개선 방법: 손절 타이트하게(ATR multiplier 감소), TP 관대하게(ATR multiplier 증가)
    - 현재 atr_multiplier_sl=1.5, atr_multiplier_tp=3.0 — TP 비율 개선 여지 검토
  - 혹은 **1h paper_sim 포기 선언**: 4h BTC Bundle OOS에만 집중하는 전략 채택

### ⚠️ 주의 사항 (Cycle 313)
- **PAPER_SIM_STRATEGY_PARAMS 현재 설정** (Cycle 312 변경 없음):
  - `value_area: {"vol_filter_mult": 0.5}` ← Cycle 295 A
  - `wick_reversal: {"min_volatility": 0.001, "vol_mult": 0.6}` ← Cycle 295 A
  - `relative_volume: {"rvol_buy_sell": 1.2}` ← Cycle 297 B
  - `momentum_quality: {"quality_score_buy_threshold": 0.8, "consistency_buy_threshold": 0.3}` ← Cycle 295 C
  - `price_cluster: {"bounce_pct": 0.025, "close_window": 60, "vol_regime_filter": True, "vol_use_relative": True, "vol_atr_trend_min": 1.5}` ← Cycle 305 C
  - `order_flow_imbalance_v2: {"trend_span": 20}` ← Cycle 298 F
  - `cmf: {"buy_thresh": 0.10}` ← Cycle 309 D (1h: 구조적 FAIL, 4h 전용 확정)
- **BUNDLE_STRATEGY_INIT_PARAMS 현재 설정** (Cycle 312 복원):
  - `narrow_range: {"trend_regime_filter": False, "ema_slope_min_buy": 0.0, "ema_slope_max_sell": 0.0}` ← Cycle311 D(ML) 복원 (nr_lookback 실험 후 명시적 복원)
  - `supertrend_multi: {atr_threshold=0.5, ema_filter=True, cmf_confirm=True, ...}`
- **paper_simulation.py TRAIN_HOURS**: `24 * 210` (84일 실험 후 복원)
- **Bundle OOS 실행 시 --csv-dir data/historical 필수**
- **단독 실험 원칙**: 두 파라미터를 동시에 변경하면 역효과 원인 특정 불가

### 핵심 메트릭 (Cycle 312)
- 테스트: **8404 passed, 23 skipped** (4개 신규 추가, 회귀 없음)
- Paper Sim BTC 1h (12 windows, 84일 train 실험): **0/22 PASS**
  - rank1: supertrend_multi (3/12 consistent, AvgSharpe=0.13) — 84일 train으로 하락
  - rank2: price_cluster (1/12 consistent, AvgSharpe=0.19) — 3/8→1/12 폭락
  - 실험 결론: TRAIN=210일이 최적 (84일 역효과 확정)
- Bundle OOS BTC 4h (5-fold): **2/5 PASS** (cmf=2.508, supertrend_multi=3.674)
  - narrow_range nr_lookback=4: FAIL (avg=-0.194) — nr_lookback=5와 동일 결과
  - cmf: 5/5 ALL PASS (avg=2.508) — 안정적 유지
  - value_area: std=2.018 > 2.0 (불안정 지속)

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: real CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows)
- ETH/SOL: synthetic CSV (data/historical/synthetic/)
- Bundle OOS: `--csv-dir data/historical` 필수 (5-fold 4h 구조, 2023~2024 실제 BTC)
- Paper simulation 1h: 22 전략 × 8 windows (210일 train) → 약 7-10분 소요
