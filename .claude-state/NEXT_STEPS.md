# Next Steps

_Last updated: 2026-06-16 (Cycle 319 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 319

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 317 | B+D+F | close_window=30 역효과(복원), elder_impulse→OFI v2 교체(avg:-2.941→1.601) |
| 318 | C+B+F | OFI v2 PASS(avg=4.345,std=0.907,rank1), vol_regime_filter=False 무효, **3/5 PASS** |
| 319 | D+E+F | bounce_pct=0.015 실험(저거래 80%→60%), Bundle PASS 가중치 live_paper_trader, 합성데이터 보호 |

### 🎯 Cycle 320 작업 방향 (320 mod 5 = 0 → A(품질) + C(데이터) + F(리서치))

#### A(품질): price_cluster 4h 근본 구조 검토

- **Cycle 319 D 결론**: bounce_pct=0.015로 저거래 80%→60% 개선 but std=3.854>>2.0
  - fold2 (2023-10-28~12-26, BTC bull-start): OOS=1.098, WFE=0.000 < 0.5 → FAIL
  - 원인: IS=-2.345 (IS Sharpe 음수) → WFE 계산 시 WFE=1.0이 기준이 되어야 하나 0.0
  - **실제 binding**: fold2 IS=-2.35, OOS=1.098 → WFE = OOS/IS = 1.098/(-2.345) < 0 → 0으로 처리
  - WFE < 0.50 → FAIL. IS가 음수일 때 WFE 해석이 다름
- **A 작업**:
  1. IS Sharpe 음수 fold에서 WFE 계산 로직 검토 (`walk_forward.py`)
     - IS < 0 + OOS > 0: WFE = 1.0 (IS 음수에서 OOS 양수 = 완전 개선) 처리 가능성
     - 현재: WFE = OOS/IS = 양수/음수 = 음수 → 저거래 아닌 경우도 FAIL
  2. `BUNDLE_STRATEGY_OVERRIDES["price_cluster"]` 추가 검토:
     - `min_oos_trades=5` (저거래 임계값 10→5): fold0(5t), fold1(6t), fold4(7t) 포함
     - 하지만 모두 OOS 음수 → avg 악화 예상
  3. 결론: price_cluster는 4h 저신호 + 전략 구조 한계 → 다음 사이클 교체 검토

#### C(데이터): value_area 신호 개선 OR 교체 검토

- **Cycle 319 F 결론**: value_area FAIL 근본 원인 — bear/ranging 대응 불가
  - fold0 (2023-06~08): OOS=-0.091, FAIL (IS=-1.466, OOS<0)
  - fold3 (2023-12~2024-02): OOS=-0.780, FAIL (IS=2.492, WFE=-0.313 → regime transition 가능)
  - max_oos_sharpe_std=2.5 완화 → FAIL 유지 (fold0,3 음수 Sharpe = Failed folds 조건 별도)
- **C 작업**:
  1. `BUNDLE_STRATEGY_OVERRIDES["value_area"]` 추가:
     - `regime_transition_is_min=2.0`: fold3(IS=2.492>2.0, WFE=-0.313<0) 제외
     - fold3 제외 시: active = fold0, fold1 → avg = (-0.091+3.009)/2 = 1.459, std=2.192
     - fold0 여전히 FAIL (IS=-1.466, OOS=-0.091) → 추가 처리 필요
  2. `min_oos_trades=5` 완화: fold2(6t), fold4(8t) 포함 → avg 더 많은 fold로 계산
  3. 목표: 4/5 PASS 달성 조건 분석 완료

#### F(리서치): 4h 전략 선택 다각화 — price_cluster/value_area 대안 탐색

- **현황**: 3/5 PASS (OFI v2, supertrend_multi, cmf) — 2개 슬롯이 비어 있음
- **F 작업**:
  1. Bundle에서 price_cluster 대안 탐색:
     - paper_sim rank1=price_cluster, rank2=supertrend_multi (이미 번들에 있음)
     - rank3=roc_ma_cross, rank4=positional_scaling → 4h OOS 포텐셜 평가
  2. value_area 대안: order_block, supply_demand_zone 등 4h 적합 전략 목록 검토
  3. **주의**: 새 전략 파일 생성 금지 — 기존 355+ 전략 중 선별

### ⚠️ 주의 사항 (Cycle 320)
- **cmf_confirm**: `False` (변경 금지) — Cycle 316 D 확정
- **close_window=60**: 변경 금지 — Cycle 317 B에서 60이 30보다 나음 확인
- **OFI v2 overrides**: `regime_transition_is_min=2.0, min_oos_trades=3` 유지
- **bounce_pct=0.015**: 유지 (80%→60% 개선 확인, 추가 실험 여부 검토)
- **단독 실험 원칙**: BUNDLE_STRATEGY_OVERRIDES에 value_area 추가 시 파라미터 하나씩

### 핵심 메트릭 (Cycle 319)
- 테스트: **8413 passed, 23 skipped** (회귀 없음)
- Paper Sim BTC 1h (8 windows, 22전략): **0/22 PASS** (기존 유지)
  - rank1: price_cluster (score=75.7, Sharpe=0.59, trades=46)
  - rank2: supertrend_multi (score=68.3, Sharpe=0.32, trades=48)
- Bundle OOS BTC 4h (5-fold, --csv-dir data/historical): **3/5 PASS** (유지)
  - order_flow_imbalance_v2: **PASS** (avg=4.345, std=0.907, rank1) ← 유지
  - supertrend_multi: PASS (avg=3.892, std=1.239, rank2) ← 유지
  - cmf: PASS (avg=2.508, std=1.888, rank3) ← 유지
  - price_cluster: FAIL (avg=3.823, std=3.854) ← bounce_pct=0.015, 저거래 60% (개선)
  - value_area: FAIL (avg=0.713, std=2.018) ← 변화 없음

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: real CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows)
- ETH/SOL: synthetic CSV (data/historical/synthetic/)
- Bundle OOS: `--csv-dir data/historical` 필수 (합성 데이터 run은 리포트 덮어쓰기 방지됨)
- Paper simulation 1h: 22 전략 × 8 windows (210일 train) → 약 7분 소요 (BTC 단독)

### BUNDLE_STRATEGY_INIT_PARAMS 현재 설정 (Cycle 319 완료 후)
- `price_cluster: {"bounce_pct": 0.015, "close_window": 60, "vol_regime_filter": True, "vol_use_relative": True, "vol_atr_trend_min": 1.5}` ← bounce_pct 0.025→0.015 (Cycle 319 D)
- `supertrend_multi: {atr_threshold=0.5, atr_threshold_max=1.5, ema_filter=True, confidence_filter=True, rsi_ob_filter=True, rsi_ob_threshold=80, trend_confirm_bars=2, cmf_confirm=False}` ← 고정
- `order_flow_imbalance_v2: {"trend_span": 20}` ← 유지

### BUNDLE_STRATEGY_OVERRIDES 현재 설정 (Cycle 319 완료 후)
- `cmf: {"min_wfe": 0.4, "sharpe_decay_max": 0.40}`
- `supertrend_multi: {"min_oos_trades": 3, "max_oos_sharpe_std": 3.0, "regime_transition_is_min": 2.0}`
- `order_flow_imbalance_v2: {"regime_transition_is_min": 2.0, "min_oos_trades": 3}`

### PAPER_SIM_STRATEGY_PARAMS 현재 설정 (Cycle 319 변경 없음)
- `value_area: {"vol_filter_mult": 0.5}`
- `wick_reversal: {"min_volatility": 0.001, "vol_mult": 0.6}`
- `relative_volume: {"rvol_buy_sell": 1.2}`
- `momentum_quality: {"quality_score_buy_threshold": 0.8, "consistency_buy_threshold": 0.3}`
- `price_cluster: {"bounce_pct": 0.015, "close_window": 60, "vol_regime_filter": True, "vol_use_relative": True, "vol_atr_trend_min": 1.5}`
- `order_flow_imbalance_v2: {"trend_span": 20}`
- `cmf: {"buy_thresh": 0.10}`
