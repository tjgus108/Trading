# Next Steps

_Last updated: 2026-06-13 (Cycle 305 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 305

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 303 | C+B+F | close_window=40 역효과(Sharpe -61%) 확인→50 복원, tiered halt 회복 테스트 2개 추가 |
| 304 | D+E+F | bounce_pct=0.030 역효과(PF-9%) 확인→0.025 복원, NarrowRange trend_regime_filter 추가 |
| 305 | A+C+F | narrow_range 그리드 확장(trend_regime_filter+atr_trend_max), close_window=60 유지(+1.9 개선) |

### 🎯 Cycle 306 작업 방향 (306 mod 5 = 1 → B(리스크) + D(ML) + F(리서치))

#### B(리스크): close_window=60 Bundle OOS 검증
- **Bundle OOS에서 close_window=60 효과 직접 확인**:
  - run_bundle_oos.py에 price_cluster override 추가 또는 PAPER_SIM_STRATEGY_PARAMS를 bundle에 전달
  - 현재 Bundle OOS는 DEFAULT_GRIDS를 사용 (close_window=[50,60] 포함됨)
  - 질문: 4h 기준에서도 close_window=60이 50보다 나은지?

#### D(ML): narrow_range trend_regime_filter walk-forward 실험
- **run_bundle_oos.py narrow_range 재실험**:
  - 새 그리드: nr_lookback=[5,6,7] + trend_regime_filter=[False,True] + atr_trend_max=[1.3,1.4,1.5]
  - 목표: fold1(OOS=-3.828), fold3(OOS=-10.794) 개선
  - 기대: trend_regime_filter=True + atr_trend_max≤1.4가 추세장 진입 억제

#### F(리서치): cmf 1h vs 4h 성능 차이 원인 분석
- **cmf 타임프레임 의존성**:
  - 4h: 5/5 PASS (Sharpe=2.508) — 우수
  - 1h: rank15 (score=48.8, Sharpe=-1.44) — 열등
  - 원인 가설: CMF 신호가 1h에서는 노이즈 비율이 높음 (1h period=60-90이지만 거래량 변동성 큼)
  - 개선 방안: cmf_1h 그리드 주기를 더 보수적으로 (period=90+ 실험)

### ⚠️ 주의 사항 (Cycle 306)
- **PAPER_SIM_STRATEGY_PARAMS 현재 설정** (Cycle 305 최종):
  - `value_area: {"vol_filter_mult": 0.5}` ← Cycle 295 A
  - `wick_reversal: {"min_volatility": 0.001, "vol_mult": 0.6}` ← Cycle 295 A
  - `relative_volume: {"rvol_buy_sell": 1.2}` ← Cycle 297 B
  - `momentum_quality: {"quality_score_buy_threshold": 0.8, "consistency_buy_threshold": 0.3}` ← Cycle 295 C
  - `price_cluster: {"bounce_pct": 0.025, "close_window": 60, "vol_regime_filter": True, "vol_use_relative": True, "vol_atr_trend_min": 1.5}` ← **Cycle 305 C 업데이트** (close_window=60)
  - `order_flow_imbalance_v2: {"trend_span": 20}` ← Cycle 298 F
- **Engine adaptive_slippage=True**: paper_simulation에 활성화 (Cycle 299 E)
- **Engine consec_loss_scale_threshold=5**: paper_simulation에 활성화 (Cycle 298 B)
- **신규 전략 파일 생성 금지** — 파라미터 오버라이드로만 접근
- **Bundle OOS 실행 시 --csv-dir data/historical 필수**
- **단독 실험 원칙**: 두 파라미터를 동시에 변경하면 역효과 원인 특정 불가

### 핵심 메트릭 (Cycle 305)
- 테스트: **8394 passed, 23 skipped** (회귀 없음)
- Paper Sim BTC 1h (8 windows): **0/22 PASS**
  - price_cluster close_window=60: rank1 score=75.7 (Cycle304: 73.8 → +1.9 개선), SharpeStd=1.77
  - rank2: supertrend_multi (score=68.3, AvgSharpe=0.32, PF=1.14, Trades=48)
- Bundle OOS BTC 4h (5-fold): **2/5 PASS** (cmf=2.508, supertrend_multi=3.674) ← 동일

### 주요 코드 변경 이력 (Cycle 305)
1. `src/backtest/walk_forward.py` — narrow_range 그리드 확장 (A(품질))
   - `trend_regime_filter: [False, True]` 추가
   - `atr_trend_max: [1.3, 1.4, 1.5]` 추가
2. `scripts/paper_simulation.py` — price_cluster close_window=60 (C(데이터))
   - score 73.8→75.7 (+1.9), SharpeStd 개선 → 효과 확인, 유지 확정

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: real CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows)
- ETH/SOL: synthetic CSV (data/historical/synthetic/)
- Bundle OOS: `--csv-dir data/historical` 필수 (5-fold 4h 구조, 2023~2024 실제 BTC)
- Paper simulation 1h: 22 전략 × 8 windows → 약 8-10분 소요

### close_window 실험 역사 (price_cluster)
| 실험 | close_window | Score/Sharpe | PF | Trades | 결론 |
|------|-------------|--------------|-----|--------|------|
| 기본 | 50 | score~73.8 | ~2.2 | ~12 | 기준선 |
| Cycle303 C | 40 | Sharpe=1.47 | 1.54 | 12 | 역효과 (Sharpe -61%) |
| Cycle305 C | 60 | score=75.7 | 1.18 | 46 | **소폭 개선** (+1.9), 유지 확정 |

### narrow_range Bundle OOS fold 분석
| Fold | 기간 | OOS Sharpe | 시장 상황 | trend_regime_filter 기대효과 |
|------|------|-----------|---------|--------------------------|
| 0 | 2023-06-30~08-28 | +3.764 | 횡보/소폭 상승 | 필터 불필요 (PASS) |
| 1 | 2023-08-29~10-27 | -3.828 | 완만한 상승 | ATR 보통 → 일부 억제 기대 |
| 2 | 2023-10-28~12-26 | +1.540 | 강세 초입 | 필터 불필요 (PASS) |
| 3 | 2023-12-27~24-02-24 | -10.794 | BTC 급등 | ATR 급등 → **억제 효과 최대 기대** |
| 4 | 2024-02-25~04-24 | -1.573 | ATH 근처 | ATR 혼재 → 일부 억제 기대 |
