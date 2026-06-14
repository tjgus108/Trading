# Next Steps

_Last updated: 2026-06-14 (Cycle 308 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 308

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 306 | B+D+F | DrawdownMonitor 재시작 복원 버그 수정, narrow_range trend_regime_filter=True 효과 없음 확인 |
| 307 | B+D+F | tiered halt roundtrip 테스트 추가, atr_trend_max=1.1도 효과 없음 확정(ATR 필터 포기), cmf_1h 임계값 강화 |
| 308 | C+B+F | CMFStrategy warmup 버그 수정(period 기반 min_rows), DrawdownMonitor WARN 히스테리시스 추가 |

### 🎯 Cycle 309 작업 방향 (309 mod 5 = 4 → D(ML) + E(실행) + F(리서치))

#### D(ML): cmf_1h 임계값 강화 효과 검증
- **paper_sim에서 cmf threshold 효과 미확인 (Cycle 308 분석)**:
  - paper_simulation.py는 cmf default params(period=20, buy_thresh=0.08) 사용
  - walk_forward.py cmf_1h 그리드([0.07,0.08,0.10]) 변경은 optimizer에만 영향
  - **검증 방법**: `PAPER_SIM_STRATEGY_PARAMS["cmf"] = {"buy_thresh": 0.10}` 추가 후 재실행
  - 목표: cmf trades 75→50-60, Sharpe -1.44→개선
  - **단독 실험 원칙**: buy_thresh만 변경, period는 기본값(20) 유지
- **또는** narrow_range 대체 필터 연구:
  - fold3 OOS=-10.794 극단 손실 원인: 2023-12~2024-02 BTC 급등(+150%) 구간
  - EMA slope 필터: `EMA20_slope > N% (e.g., 0.5%/봉)` → 추세장 신호 차단
  - ROC 필터: `price change(20봉) > 15%` → 강한 추세 구간 차단
  - **코드 수정 불가** (전략 파일 금지) → walk_forward.py grids에만 파라미터 추가

#### E(실행): Paper Trading 실전 검증
- **supertrend_multi + cmf 조합 실전 성능 점검**:
  - Bundle OOS cmf: 5/5 PASS, avg Sharpe=2.508 (매우 안정적)
  - Bundle OOS supertrend_multi: 3/5 PASS, avg Sharpe=3.674
  - paper_sim rank2: supertrend_multi Sharpe=0.32 (4h 최강 but 1h 부진)
  - 분석: 4h 성능 우수 → paper_sim(1h) 부진의 원인 파악 필요
- **슬리피지 모델 검증**: 현재 DEFAULT_SLIPPAGE=0.05%, adaptive_slippage=True
  - price_cluster MDD=12.2%에서 adaptive_slippage 실제 비용 측정

#### F(리서치): narrow_range 대안 방향 + value_area 교체 검토
- **narrow_range EMA slope 실험 (연구만, 코드는 grids만)**:
  - 현재 fold3 OOS=-10.794 구조적 문제
  - EMA slope filter를 `DEFAULT_GRIDS["narrow_range"]`에 추가:
    - `"ema_slope_min": [0.0, 0.003, 0.005]` — EMA20 slope > N시 신호 차단 (추세 차단)
  - NarrowRangeStrategy에 `ema_slope_min` 파라미터 지원 여부 확인 필요
- **value_area 교체 검토**:
  - OOS std=2.018 (임계값 2.0 극소 초과) → fold0 OOS=-0.091, fold3 OOS=-0.780
  - elder_impulse와 교체 시 std=3.117 더 나쁨 → 차라리 value_area 유지
  - 또는 가중 평균 앙상블 (cmf + supertrend_multi 2전략만으로 Bundle 구성)

### ⚠️ 주의 사항 (Cycle 309)
- **PAPER_SIM_STRATEGY_PARAMS 현재 설정** (Cycle 308 변동 없음):
  - `value_area: {"vol_filter_mult": 0.5}` ← Cycle 295 A
  - `wick_reversal: {"min_volatility": 0.001, "vol_mult": 0.6}` ← Cycle 295 A
  - `relative_volume: {"rvol_buy_sell": 1.2}` ← Cycle 297 B
  - `momentum_quality: {"quality_score_buy_threshold": 0.8, "consistency_buy_threshold": 0.3}` ← Cycle 295 C
  - `price_cluster: {"bounce_pct": 0.025, "close_window": 60, "vol_regime_filter": True, "vol_use_relative": True, "vol_atr_trend_min": 1.5}` ← Cycle 305 C 확정
  - `order_flow_imbalance_v2: {"trend_span": 20}` ← Cycle 298 F
- **BUNDLE_STRATEGY_INIT_PARAMS 현재 설정** (Cycle 308 변동 없음):
  - `narrow_range: {"trend_regime_filter": True, "atr_trend_max": 1.1}` ← 효과 없음 확정
  - `supertrend_multi: {atr_threshold=0.5, ema_filter=True, cmf_confirm=True, ...}`
- **walk_forward.py 그리드 Cycle 308 변경사항 없음** (Cycle 307 상태 유지):
  - `narrow_range: trend_regime_filter=[False]` 고정
  - `cmf_1h: period=[90,105], buy_thresh=[0.07,0.08,0.10], sell_thresh=[-0.10,-0.08,-0.07]`
- **CMFStrategy 변경 (Cycle 308)**:
  - `min_rows = max(25, self.period + 5)` — period=90/105에서 warmup 방어
  - 기존 cmf(period=20) 동작 변화 없음 (max(25,25)=25)
- **DrawdownMonitor 변경 (Cycle 308)**:
  - `mdd_warn_hysteresis_pct=0.015` (기본 1.5%) — WARN→NORMAL 복귀 버퍼
  - BLOCK_ENTRY 이상에서 직접 mdd_warn_pct 이하로 회복 시 히스테리시스 미적용
- **Bundle OOS 실행 시 --csv-dir data/historical 필수**
- **단독 실험 원칙**: 두 파라미터를 동시에 변경하면 역효과 원인 특정 불가

### 핵심 메트릭 (Cycle 308)
- 테스트: **8400 passed, 23 skipped** (+5 신규 테스트, 회귀 없음)
- Paper Sim BTC 1h (8 windows): **0/22 PASS**
  - price_cluster close_window=60: rank1 score=75.7 (안정)
  - supertrend_multi: rank2 score=68.3 (안정)
  - cmf: rank15 score=48.8 Sharpe=-1.44 (동일, default params 사용)
- Bundle OOS BTC 4h (5-fold): **2/5 PASS** (cmf=2.508, supertrend_multi=3.674)
  - cmf 5/5 ALL PASS 달성 (avg OOS Sharpe=2.508, std=1.888)
  - narrow_range fold3 OOS=-10.794 지속 (ATR 필터 포기 확정)
  - value_area OOS std=2.018 (임계값 0.018 초과 FAIL 지속)

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: real CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows)
- ETH/SOL: synthetic CSV (data/historical/synthetic/)
- Bundle OOS: `--csv-dir data/historical` 필수 (5-fold 4h 구조, 2023~2024 실제 BTC)
- Paper simulation 1h: 22 전략 × 8 windows → 약 7-10분 소요
