# Next Steps

_Last updated: 2026-06-13 (Cycle 307 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 307

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 305 | A+C+F | narrow_range 그리드 확장(trend_regime_filter+atr_trend_max), close_window=60 유지(+1.9 개선) |
| 306 | B+D+F | DrawdownMonitor 재시작 복원 버그 수정, narrow_range trend_regime_filter=True 효과 없음 확인(atr_trend_max=1.4 미트리거), cmf_1h period 상향 |
| 307 | B+D+F | tiered halt roundtrip 테스트 추가, atr_trend_max=1.1도 효과 없음 확정(ATR 필터 포기), cmf_1h 임계값 강화(buy_thresh 0.07→0.10) |

### 🎯 Cycle 308 작업 방향 (308 mod 5 = 3 → C(데이터) + B(리스크) + F(리서치))

#### C(데이터): DataFeed 캐시/Indicator 정확도 점검
- **cmf_1h 임계값 강화 효과 확인**:
  - Cycle 307에서 buy_thresh=[0.07,0.08,0.10], sell_thresh=[-0.10,-0.08,-0.07]로 업데이트
  - paper_simulation 재실행 후 cmf rank 변화 확인
  - 목표: score 48.8 → 55+, trades 75 → 50-60 (신호 감소)
- **또는** enrich_indicators() 점검:
  - cmf_1h에 사용되는 CMF 계산이 1h봉에서 정확한지 확인
  - period=105일 때 warm-up 봉 수 충분한지 검증

#### B(리스크): Kelly Sizer 실효성 점검
- **paper sim 상위 전략(price_cluster, supertrend_multi)의 kelly fraction 검토**:
  - mdd_warn_pct=5% 경고 → size 50% 축소: 너무 빠른 반응 여부 확인
  - 현재 price_cluster(bounce_pct=0.025): MDD=12.2%, 3/8 일관성
  - kelly_reduce_at_mdd=8%일 때 실제 감소 발동 빈도 측정
- **DrawdownMonitor 새 테스트 완료 (Cycle 307)**: 8395 passed

#### F(리서치): narrow_range 대체 필터 방향 탐색
- **ATR/ATR_MA 필터 포기 확정 (Cycle 307)**:
  - BTC 4h에서 ATR_LOOKBACK=20 → ATR/ATR_MA 비율 ~1.003 (1.1도 미트리거)
  - → narrow_range는 BTC 4h 강세장에서 구조적으로 취약
- **다음 실험 후보 (연구만, 전략 파일 수정 불가)**:
  1. EMA slope 필터: EMA20 slope > N% → 추세장 차단
  2. ROC 필터: price change(20봉) > N% → 강한 추세 구간 차단
  3. narrow_range를 Bundle에서 제외 → value_area/elder_impulse로 교체 검토
- **run_bundle_oos.py 현재 상태**: narrow_range atr_trend_max=1.1 (효과 없음 확인됨)

### ⚠️ 주의 사항 (Cycle 308)
- **PAPER_SIM_STRATEGY_PARAMS 현재 설정** (Cycle 307 변동 없음):
  - `value_area: {"vol_filter_mult": 0.5}` ← Cycle 295 A
  - `wick_reversal: {"min_volatility": 0.001, "vol_mult": 0.6}` ← Cycle 295 A
  - `relative_volume: {"rvol_buy_sell": 1.2}` ← Cycle 297 B
  - `momentum_quality: {"quality_score_buy_threshold": 0.8, "consistency_buy_threshold": 0.3}` ← Cycle 295 C
  - `price_cluster: {"bounce_pct": 0.025, "close_window": 60, "vol_regime_filter": True, "vol_use_relative": True, "vol_atr_trend_min": 1.5}` ← Cycle 305 C 확정
  - `order_flow_imbalance_v2: {"trend_span": 20}` ← Cycle 298 F
- **BUNDLE_STRATEGY_INIT_PARAMS 현재 설정** (Cycle 307):
  - `narrow_range: {"trend_regime_filter": True, "atr_trend_max": 1.1}` ← Cycle 307 D(ML, 효과 없음 확정)
    - → Cycle 308에서 narrow_range 필터 방향 재검토
  - `supertrend_multi: {...}` ← 기존 설정 유지
- **walk_forward.py 그리드 Cycle 307 변경사항**:
  - `narrow_range: trend_regime_filter=[False]` 고정, `atr_trend_max` 제거
  - `cmf_1h: period=[90,105]`, `buy_thresh=[0.07,0.08,0.10]`, `sell_thresh=[-0.10,-0.08,-0.07]`
- **Engine adaptive_slippage=True**: paper_simulation에 활성화 (Cycle 299 E)
- **Engine consec_loss_scale_threshold=5**: paper_simulation에 활성화 (Cycle 298 B)
- **신규 전략 파일 생성 금지** — 파라미터 오버라이드로만 접근
- **Bundle OOS 실행 시 --csv-dir data/historical 필수**
- **단독 실험 원칙**: 두 파라미터를 동시에 변경하면 역효과 원인 특정 불가

### 핵심 메트릭 (Cycle 307)
- 테스트: **8395 passed, 23 skipped** (회귀 없음, +1 신규 테스트)
- Paper Sim BTC 1h (8 windows): **0/22 PASS**
  - price_cluster close_window=60: rank1 score=75.7 (Cycle305~307 안정)
  - supertrend_multi: rank2 score=68.3 (안정)
  - cmf: rank15 score=48.8 Sharpe=-1.44 (임계값 강화 효과는 다음 사이클 확인)
- Bundle OOS BTC 4h (5-fold): **2/5 PASS** (cmf=2.508, supertrend_multi=3.674)

### narrow_range ATR 필터 분석 (Cycle 307 확정)
| 실험 | threshold | fold1 트리거 | fold3 트리거 | 결과 |
|------|-----------|------------|------------|------|
| Cycle 306 | 1.4 | 2/341봉 | 0/341봉 | 효과 없음 |
| Cycle 307 | 1.1 | 동일 OOS 결과 | 동일 OOS 결과 | **효과 없음 확정** |
→ ATR_LOOKBACK=20으로는 BTC 4h 점진적 추세 감지 불가
→ trend_regime_filter 접근 포기, narrow_range 대안 필터 연구 필요

### 주요 코드 변경 이력 (Cycle 307)
1. `tests/test_drawdown_monitor.py` — B(리스크) 테스트 추가
   - `test_tiered_halt_roundtrip_recovery`: to_dict→from_dict 후 recovery 동작 검증
2. `scripts/run_bundle_oos.py` — D(ML) atr_trend_max 변경
   - `narrow_range.atr_trend_max: 1.4 → 1.1` (실험, 효과 없음 확정)
3. `src/backtest/walk_forward.py` — 그리드 2건 업데이트
   - narrow_range: trend_regime_filter=[False] 고정 + atr_trend_max 제거
   - cmf_1h: buy_thresh/sell_thresh 강화, period=[90,105]으로 축소

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: real CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows)
- ETH/SOL: synthetic CSV (data/historical/synthetic/)
- Bundle OOS: `--csv-dir data/historical` 필수 (5-fold 4h 구조, 2023~2024 실제 BTC)
- Paper simulation 1h: 22 전략 × 8 windows → 약 8-10분 소요
