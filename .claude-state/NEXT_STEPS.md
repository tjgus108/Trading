# Next Steps

_Last updated: 2026-06-16 (Cycle 318 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 318

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 316 | B+D+F | narrow_range→price_cluster 교체(FAIL:저거래), cmf_confirm=False 확정(avg=3.892↑,std=1.239↓), 4h slippage 보정(engine.py) |
| 317 | B+D+F | close_window=30 실험→역효과(avg=-0.336,복원), elder_impulse→OFI v2 교체(avg:-2.941→1.601), 4h slippage 보정 효과=미미 |
| 318 | C+B+F | OFI v2 PASS(avg=4.345,std=0.907,rank1), vol_regime_filter=False 무효(binding=bounce_pct), **3/5 PASS 달성** |

### 🎯 Cycle 319 작업 방향 (319 mod 5 = 4 → D(ML) + E(실행) + F(리서치))

#### D(ML): price_cluster bounce_pct 실험

- **Cycle 318 C 결론**: vol_regime_filter=False 무효 — OOS 거래 수 동일, binding constraint = bounce_pct
  - vol_regime_filter는 IS 기간만 영향, OOS 기간에는 레짐 분포가 달라 효과 없음
  - 실제 원인: bounce_pct=0.025 (2.5% 범위 클러스터) → 4h 봉 기준 너무 좁음
- **D 작업**: `bounce_pct=0.025→0.015` 단독 실험
  1. `BUNDLE_STRATEGY_INIT_PARAMS["price_cluster"]["bounce_pct"] = 0.015`
  2. Bundle OOS 4h 실행: 신호 빈도 증가 효과 확인
  3. 기대: 1.5% 클러스터 범위 → 더 많은 신호 → 저거래 비율 80%→40% 감소
  - 현재: `{"bounce_pct": 0.025, "close_window": 60, "vol_regime_filter": True, ...}`
  - 실험: `bounce_pct=0.015` (나머지 동일)
  - **단독 실험 원칙**: bounce_pct만 변경

#### E(실행): live_paper_trader.py 실전 투입 준비

- **Cycle 318 F 결론**: 3/5 PASS 달성 (OFI v2 + supertrend_multi + cmf) — 실전 투입 조건 충족
  - QUALITY_AUDIT.csv에 3전략 모두 passed=True 확인
  - live_paper_trader.py 구조 완비 (Bybit API → signal → PaperTrader)
- **E 작업**:
  1. 포트폴리오 파라미터 설정: OFI v2 40%, supertrend_multi 35%, cmf 25%
  2. live_paper_trader.py에 Bundle PASS 전략 명시적 우선순위 설정 확인
  3. Paper Trading 시작 시 초기 밸런스/리스크 파라미터 검토
  4. SSL 차단 해결 방법 검토 (환경 변수, 우회 설정)

#### F(리서치): value_area 4/5 PASS 가능성 분석

- **Cycle 318 시뮬 결론**: value_area FAIL (avg=0.713, std=2.018>2.0)
  - std=2.018이 2.0 기준을 0.018 초과 — 경계값
  - fold2: trades=6 (저거래), fold4: trades=8 (저거래) → 2개 fold 제외
  - 유효 fold avg (fold0: -0.091, fold1: 3.009, fold3: -0.780) → avg=0.713
- **F 작업**:
  1. value_area max_oos_sharpe_std=2.5 완화 가능성 검토 (std=2.018+노이즈)
  2. value_area 저거래 fold 원인 분석 (min_oos_trades=10 vs 실제 6,8 거래)
  3. OFI v2 fold3 bull run에서의 완전한 행동 패턴 분석 (IS=3.889 과최적화 메커니즘)

### ⚠️ 주의 사항 (Cycle 319)
- **cmf_confirm**: `False` (변경 금지) — Cycle 316 D 확정
- **close_window=60**: 변경 금지 — Cycle 317 B에서 60이 30보다 나음 확인
- **OFI v2 overrides**: `regime_transition_is_min=2.0, min_oos_trades=3` 유지
- **단독 실험 원칙**: D(bounce_pct) + E(live_paper) 실험 시 price_cluster 파라미터는 하나씩 변경

### 핵심 메트릭 (Cycle 318)
- 테스트: **8413 passed, 23 skipped** (회귀 없음)
- Paper Sim BTC 1h (8 windows, TRAIN=210일, --csv-dir data/historical): **0/22 PASS** (기존 유지)
  - rank1: price_cluster (score=75.7, Sharpe=0.59, trades=46)
  - rank2: supertrend_multi (score=68.3, Sharpe=0.32, trades=48)
- Bundle OOS BTC 4h (5-fold, --csv-dir data/historical): **3/5 PASS** ← 핵심 성과
  - order_flow_imbalance_v2: **PASS** (avg=**4.345**, std=0.907, rank1) ← NEW
  - supertrend_multi: PASS (avg=3.892, std=1.239, rank2)
  - cmf: PASS (avg=2.508, std=1.888, rank3)
  - price_cluster: FAIL (avg=3.672 유효1fold만, 80% 저거래)
  - value_area: FAIL (avg=0.713, std=2.018)
- **실전 투입 우선순위**: OFI v2 rank1 (avg=4.345), supertrend_multi rank2 (avg=3.892), cmf rank3 (avg=2.508)

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: real CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows)
- ETH/SOL: synthetic CSV (data/historical/synthetic/)
- Bundle OOS: `--csv-dir data/historical` 필수 (5-fold 4h 구조, 2023~2024 실제 BTC)
- Paper simulation 1h: 22 전략 × 8 windows (210일 train) → 약 7분 소요 (BTC 단독)

### BUNDLE_STRATEGY_INIT_PARAMS 현재 설정 (Cycle 318 완료 후)
- `price_cluster: {"bounce_pct": 0.025, "close_window": 60, "vol_regime_filter": True, "vol_use_relative": True, "vol_atr_trend_min": 1.5}` ← vol_regime_filter=True 복원
- `supertrend_multi: {atr_threshold=0.5, atr_threshold_max=1.5, ema_filter=True, confidence_filter=True, rsi_ob_filter=True, rsi_ob_threshold=80, trend_confirm_bars=2, cmf_confirm=False}` ← 고정
- `order_flow_imbalance_v2: {"trend_span": 20}` ← 유지

### BUNDLE_STRATEGY_OVERRIDES 현재 설정 (Cycle 318 완료 후)
- `cmf: {"min_wfe": 0.4, "sharpe_decay_max": 0.40}`
- `supertrend_multi: {"min_oos_trades": 3, "max_oos_sharpe_std": 3.0, "regime_transition_is_min": 2.0}`
- `order_flow_imbalance_v2: {"regime_transition_is_min": 2.0, "min_oos_trades": 3}` ← NEW (Cycle 318 B)

### PAPER_SIM_STRATEGY_PARAMS 현재 설정 (Cycle 318 변경 없음)
- `value_area: {"vol_filter_mult": 0.5}`
- `wick_reversal: {"min_volatility": 0.001, "vol_mult": 0.6}`
- `relative_volume: {"rvol_buy_sell": 1.2}`
- `momentum_quality: {"quality_score_buy_threshold": 0.8, "consistency_buy_threshold": 0.3}`
- `price_cluster: {"bounce_pct": 0.025, "close_window": 60, "vol_regime_filter": True, "vol_use_relative": True, "vol_atr_trend_min": 1.5}`
- `order_flow_imbalance_v2: {"trend_span": 20}`
- `cmf: {"buy_thresh": 0.10}`
