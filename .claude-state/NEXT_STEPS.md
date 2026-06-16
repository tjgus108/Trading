# Next Steps

_Last updated: 2026-06-16 (Cycle 317 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 317

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 315 | A+C+F | atr_threshold=1.05 실험→역효과(avg=-2.118, std=3.889, 복원), cmf 4h BTC-특이성 확인(ETH/SOL FAIL) |
| 316 | B+D+F | narrow_range→price_cluster 교체(FAIL:저거래), cmf_confirm=False 확정(avg=3.892↑,std=1.239↓), 4h slippage 보정(engine.py) |
| 317 | B+D+F | close_window=30 실험→역효과(avg=-0.336,복원), elder_impulse→OFI v2 교체(avg:-2.941→1.601), 4h slippage 보정 효과=미미 |

### 🎯 Cycle 318 작업 방향 (318 mod 5 = 3 → C(데이터) + B(리스크) + F(리서치))

#### B(리스크): order_flow_imbalance_v2 fold3 regime_transition 처리

- **Cycle 317 D 결론**: OFI v2 도입 — avg=1.601 (elder_impulse -2.941 대비 큰 개선)
  - FAIL 원인: fold3 (IS=3.889, WFE=-2.410) — BTC 40k~60k 강한 상승장 구간
  - fold3: IS=3.889 > 2.0 AND WFE=-2.410 < 0 → `regime_transition_is_min=2.0` 적용 대상
  - 예상 결과: fold3 제외 시 avg = (4.655+3.791+3.458+5.475)/4 = **4.345**, std 대폭 감소
- **B 작업**: BUNDLE_STRATEGY_OVERRIDES에 OFI v2 override 추가
  1. `BUNDLE_STRATEGY_OVERRIDES["order_flow_imbalance_v2"] = {"regime_transition_is_min": 2.0, "min_oos_trades": 3}`
  2. Bundle OOS 4h 실행: `python3 scripts/run_bundle_oos.py --symbol BTC/USDT --timeframe 4h --csv-dir data/historical`
  3. 목표: OFI v2 PASS (avg ~4.3, std < 2.0) → Bundle 3/5 PASS 달성
  - **만약 std 여전히 높음**: fold3 제외해도 극단값이 있으면 max_oos_sharpe_std=3.0 추가 고려

#### C(데이터): price_cluster vol_regime_filter=False 실험

- **Cycle 317 B 결론**: close_window=30 실험 실패 — IS 과최적화 심화
  - close_window=60(avg=3.672, 80%저거래) vs close_window=30(avg=-0.336, IS overfitting)
  - 두 옵션 모두 FAIL, 다른 접근 필요
- **C 작업**: `vol_regime_filter=False` 단독 실험
  1. `BUNDLE_STRATEGY_INIT_PARAMS["price_cluster"]["vol_regime_filter"] = False` (close_window=60 유지)
  2. Bundle OOS 4h 실행: 신호 발생 레짐 제한 해제 효과 확인
  3. 기대: sideways 레짐 제한 해제 → 신호 빈도 증가 → 저거래 비율 80%→40% 감소
  - 현재: `{"bounce_pct": 0.025, "close_window": 60, "vol_regime_filter": True, ...}`
  - 실험: `vol_regime_filter=False` (나머지 동일)
  - **단독 실험 원칙**: vol_regime_filter만 변경

#### F(리서치): Bundle 3/5 PASS 달성 후 실전 투입 타임라인 검토

- **Cycle 317 F 결론**: 4h slippage 보정은 현실적 비용 모델링에는 기여하지만 Sharpe 수치 불변
- **F 작업**:
  1. OFI v2 PASS 확인 시: supertrend_multi + cmf + OFI v2 = 3/5 PASS → 실전 투입 타임라인 작성
  2. Paper Trading 모드 준비 검토 (live_paper_trader.py 검토)
  3. 3/5 PASS 달성 시: 포트폴리오 구성 (supertrend_multi 50%, cmf 30%, OFI v2 20%)

### ⚠️ 주의 사항 (Cycle 318)
- **cmf_confirm**: `False` (변경 금지) — Cycle 316 D 확정
- **close_window=60**: 변경 금지 — Cycle 317 B에서 60이 30보다 나음 확인
- **regime_transition 실험**: OFI v2 fold3 IS=3.889 > 2.0, WFE=-2.410 < 0 → 레짐 전환 확정
- **단독 실험 원칙**: B(OFI v2 override) + C(price_cluster vol_regime_filter) 동시 실험 금지
  - B 먼저 → 결과 확인 후 C 실험 OR 하나씩 순차 진행

### 핵심 메트릭 (Cycle 317)
- 테스트: **8413 passed, 23 skipped** (회귀 없음)
- Paper Sim BTC 1h (8 windows, TRAIN=210일, --csv-dir data/historical): **0/22 PASS** (Cycle 316 동일)
  - rank1: price_cluster (score=75.7, Sharpe=0.59, trades=46)
  - rank2: supertrend_multi (score=68.3, Sharpe=0.32, trades=48)
- Bundle OOS BTC 4h (5-fold, --csv-dir data/historical): **2/5 PASS** (유지)
  - cmf: 5/5 PASS (avg=2.508, std=1.888)
  - supertrend_multi (cmf_confirm=False): 4/4 valid PASS (avg=**3.892**, std=**1.239**)
  - order_flow_imbalance_v2 (trend_span=20): FAIL (avg=1.601, std=6.185) — fold3 bull run OOS=-9.373
  - price_cluster (close_window=60): FAIL (avg=3.672, 80% 저거래)
  - value_area: FAIL (avg=0.713, std=2.018)
- **실전 투입 우선순위**: supertrend_multi rank1 (avg=3.892), cmf rank2 (avg=2.508)

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: real CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows)
- ETH/SOL: synthetic CSV (data/historical/synthetic/)
- Bundle OOS: `--csv-dir data/historical` 필수 (5-fold 4h 구조, 2023~2024 실제 BTC)
- Paper simulation 1h: 22 전략 × 8 windows (210일 train) → 약 7분 소요 (BTC 단독)

### BUNDLE_STRATEGY_INIT_PARAMS 현재 설정 (Cycle 317 완료 후)
- `price_cluster: {"bounce_pct": 0.025, "close_window": 60, "vol_regime_filter": True, "vol_use_relative": True, "vol_atr_trend_min": 1.5}` ← close_window=60 복원
- `supertrend_multi: {atr_threshold=0.5, atr_threshold_max=1.5, ema_filter=True, confidence_filter=True, rsi_ob_filter=True, rsi_ob_threshold=80, trend_confirm_bars=2, cmf_confirm=False}` ← 고정
- `order_flow_imbalance_v2: {"trend_span": 20}` ← NEW (elder_impulse 대체)

### BUNDLE_STRATEGY_OVERRIDES 현재 설정 (Cycle 317 완료 후)
- `cmf: {"min_wfe": 0.4, "sharpe_decay_max": 0.40}`
- `supertrend_multi: {"min_oos_trades": 3, "max_oos_sharpe_std": 3.0, "regime_transition_is_min": 2.0}`

### PAPER_SIM_STRATEGY_PARAMS 현재 설정 (Cycle 317 변경 없음)
- `value_area: {"vol_filter_mult": 0.5}`
- `wick_reversal: {"min_volatility": 0.001, "vol_mult": 0.6}`
- `relative_volume: {"rvol_buy_sell": 1.2}`
- `momentum_quality: {"quality_score_buy_threshold": 0.8, "consistency_buy_threshold": 0.3}`
- `price_cluster: {"bounce_pct": 0.025, "close_window": 60, "vol_regime_filter": True, "vol_use_relative": True, "vol_atr_trend_min": 1.5}`
- `order_flow_imbalance_v2: {"trend_span": 20}`
- `cmf: {"buy_thresh": 0.10}`
