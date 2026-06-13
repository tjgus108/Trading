# Next Steps

_Last updated: 2026-06-13 (Cycle 306 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 306

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 304 | D+E+F | bounce_pct=0.030 역효과(PF-9%) 확인→0.025 복원, NarrowRange trend_regime_filter 추가 |
| 305 | A+C+F | narrow_range 그리드 확장(trend_regime_filter+atr_trend_max), close_window=60 유지(+1.9 개선) |
| 306 | B+D+F | DrawdownMonitor 재시작 복원 버그 수정, narrow_range trend_regime_filter=True 효과 없음 확인(atr_trend_max=1.4 미트리거), cmf_1h period 상향 |

### 🎯 Cycle 307 작업 방향 (307 mod 5 = 2 → B(리스크) + D(ML) + F(리서치))

#### B(리스크): DrawdownMonitor 새 직렬화 검증 테스트 추가
- **to_dict/from_dict 재시작 후 tiered halt recovery 정확성 테스트 추가**:
  - 시나리오: tiered halt → to_dict → from_dict → recovery 체크
  - 현재 테스트(`test_tiered_halt_recovery_faster_than_legacy`)는 to_dict 없이만 테스트
  - 새 테스트: `test_tiered_halt_roundtrip_recovery` — 직렬화 후 recovery 검증
- **또는** Kelly Sizer 파라미터 튜닝:
  - paper sim 상위 전략(price_cluster, supertrend_multi)의 kelly fraction 검토
  - mdd_warn_pct 실효성 검증 (현재 5% 경고 → 50% 축소: 너무 빠른 반응?)

#### D(ML): narrow_range atr_trend_max=1.1 실험
- **원인 확인 (Cycle 306)**: atr_trend_max=1.4가 BTC 4h 점진적 추세에서 미트리거
  - fold3 max ATR ratio = 1.236 (1.4 미달)
  - fold1 max ATR ratio = 1.447 (341봉 중 2번만 트리거)
- **Cycle 307 실험**: atr_trend_max=1.1 테스트
  - `run_bundle_oos.py` `BUNDLE_STRATEGY_INIT_PARAMS["narrow_range"]["atr_trend_max"] = 1.1`
  - 예상: fold3에서 ~15-20% 봉 억제 (ATR ratio > 1.1인 구간)
  - 위험: 억제된 신호가 좋은 신호일 수도 있음 (fold2 OOS=1.540 하락 가능성)
- **대안**: ATR_MA 기간 단축 (20→5) — 단기 ATR 급등 감지로 더 민감하게

#### F(리서치): cmf_1h period=105 walk-forward 실험 결과 분석
- Cycle 306에서 cmf_1h grid period [60,75,90]→[75,90,105] 적용
- 다음 paper_simulation.py 1h 결과에서 cmf rank 개선 여부 확인 필요
  - 현재 rank15 (score=48.8, Sharpe=-1.44)
  - 목표: score 55+ (period 105로 노이즈 필터 개선)

### ⚠️ 주의 사항 (Cycle 307)
- **PAPER_SIM_STRATEGY_PARAMS 현재 설정** (Cycle 306 변동 없음):
  - `value_area: {"vol_filter_mult": 0.5}` ← Cycle 295 A
  - `wick_reversal: {"min_volatility": 0.001, "vol_mult": 0.6}` ← Cycle 295 A
  - `relative_volume: {"rvol_buy_sell": 1.2}` ← Cycle 297 B
  - `momentum_quality: {"quality_score_buy_threshold": 0.8, "consistency_buy_threshold": 0.3}` ← Cycle 295 C
  - `price_cluster: {"bounce_pct": 0.025, "close_window": 60, "vol_regime_filter": True, "vol_use_relative": True, "vol_atr_trend_min": 1.5}` ← Cycle 305 C 확정
  - `order_flow_imbalance_v2: {"trend_span": 20}` ← Cycle 298 F
- **BUNDLE_STRATEGY_INIT_PARAMS 현재 설정** (Cycle 306):
  - `narrow_range: {"trend_regime_filter": True, "atr_trend_max": 1.4}` ← Cycle 306 D(ML, 효과 없음 확인)
    - → Cycle 307에서 atr_trend_max=1.1로 변경 예정
  - `supertrend_multi: {...}` ← 기존 설정 유지
- **Engine adaptive_slippage=True**: paper_simulation에 활성화 (Cycle 299 E)
- **Engine consec_loss_scale_threshold=5**: paper_simulation에 활성화 (Cycle 298 B)
- **신규 전략 파일 생성 금지** — 파라미터 오버라이드로만 접근
- **Bundle OOS 실행 시 --csv-dir data/historical 필수**
- **단독 실험 원칙**: 두 파라미터를 동시에 변경하면 역효과 원인 특정 불가

### 핵심 메트릭 (Cycle 306)
- 테스트: **8394 passed, 23 skipped** (회귀 없음)
- Paper Sim BTC 1h (8 windows): **0/22 PASS**
  - price_cluster close_window=60: rank1 score=75.7 (Cycle305와 동일, 안정)
  - supertrend_multi: rank2 score=68.3 (동일)
- Bundle OOS BTC 4h (5-fold): **2/5 PASS** (cmf=2.508, supertrend_multi=3.674) ← 동일

### 주요 코드 변경 이력 (Cycle 306)
1. `src/risk/drawdown_monitor.py` — B(리스크) 버그 수정
   - `to_dict()`: `_tiered_halt`, `_halt_drawdown` 포함
   - `from_dict()`: 두 필드 복원 (backward compatible `.get()` 사용)
2. `scripts/run_bundle_oos.py` — D(ML) 실험
   - `BUNDLE_STRATEGY_INIT_PARAMS["narrow_range"]` 추가: `trend_regime_filter=True, atr_trend_max=1.4`
   - 실험 결과: 효과 없음 (ATR/ATR_MA(20) ratio > 1.4 미트리거)
3. `src/backtest/walk_forward.py` — F(리서치) cmf_1h 그리드 수정
   - `cmf_1h.period`: [60, 75, 90] → [75, 90, 105]

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: real CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows)
- ETH/SOL: synthetic CSV (data/historical/synthetic/)
- Bundle OOS: `--csv-dir data/historical` 필수 (5-fold 4h 구조, 2023~2024 실제 BTC)
- Paper simulation 1h: 22 전략 × 8 windows → 약 8-10분 소요

### narrow_range ATR 필터 분석 (Cycle 306 신규)
| 구분 | fold1 (2023-08~10) | fold3 (2023-12~2024-02) |
|-----|-------------------|----------------------|
| OOS Sharpe | -3.828 | -10.794 |
| ATR ratio max | 1.447 | 1.236 |
| ATR ratio > 1.4 (out of 341) | 2번 | **0번** |
| ATR ratio mean | ~1.0 | ~1.003 |
| 결론 | 거의 미트리거 | **완전 미트리거** |
→ 점진적 추세에서 ATR/ATR_MA(20)은 1.0 근처 유지 → threshold=1.4는 BTC 4h에서 비효율적
→ Cycle 307: threshold=1.1 실험 (341봉 중 ~50-70봉 트리거 예상)
