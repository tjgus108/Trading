# Next Steps

_Last updated: 2026-06-12 (Cycle 301 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 301

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 299 | D+E+F | vol_regime_filter 파라미터(코드), adaptive_slippage 활성화, delta_window 파라미터화 |
| 300 | A+C+F | 상대적 ATR vol_regime_filter 구현 (score +3.3), buy_thresh=0.30 실험→역효과 복원 |
| 301 | B+D+F | bounce_pct 0.025 (Sharpe+10%/PF+11%), ATR 동적 bounce_pct 기능 추가, 두 D실험 역효과 복원 |

### 🎯 Cycle 302 작업 방향 (302 mod 5 = 2 → B(리스크) + D(ML) + F(리서치))

#### B(리스크): 리스크 관리 개선
- **핵심 이슈**: price_cluster trades=12 < 15 (most windows에서 MIN_TRADES 미달)
  - bounce_pct=0.025 설정 후에도 trades=12 변화 없음 → trades 부족의 근본 원인은 bounce_pct가 아님
  - 근본 원인 분석: cluster 구조 자체 (5-bin 50봉) — 가격이 cluster 경계를 자주 왕래하지 않음
  - 다음 시도: n_bins=7 실험 (더 세밀한 cluster, bounce 기회 증가 가능)
  - 또는 close_window 축소: 50→40봉 (더 민감한 cluster 업데이트)
  - 단, PF/Sharpe 유지 조건으로 실험

#### D(ML): ML 신호 개선
- **결과 정리**: 두 D(ML) 실험 모두 역효과
  - vol_atr_trend_min=1.3: SharpeStd 2.41→2.52 악화 → 1.5 유지
  - quality_score_buy_threshold=0.85: PF 1.48→1.33 → 0.80 유지
- **다음 방향**: price_cluster SharpeStd=2.41~2.52 감소 방법 재탐색
  - n_bins 변경 (5→7): 더 세밀한 지지/저항 구간 → 신호 품질 향상 가능
  - W8(bull, trades=8, Sharpe=-0.11): W8 기간 시장 특성 더 분석 필요
- order_flow_imbalance_v2: 3/8 PASS 복원 완료 (Cycle 301 시뮬에서 rank8 확인)

#### F(리서치): 최신 연구 기반 개선
- **ATR 동적 bounce_pct 기능 구현 완료** (atr_bounce_factor 파라미터)
  - 다음 실험: atr_bounce_factor=1.5~2.0 실험 (ATR 기반 동적 threshold)
  - 기대: 고변동성 시장에서 threshold 자동 확대 → 불필요한 HOLD 감소
- **narrow_range fold3 극단 손실 분석 완료**
  - 2023-12-27~2024-02-24 (BTC 급등 30k→52k): NR 패턴 오작동 확인
  - 해결책: 상대적 ATR 필터 추가 (price_cluster 방식: ATR/ATR_MA > 1.4 시 억제)
  - 구현: 다음 A(품질) 사이클에서 `narrow_range.py`에 `trend_regime_filter` 추가 검토
- **가격 bin 실험 근거 (리서치)**:
  - 5-bin → 7-bin: market microstructure 연구에서 7-10 지지/저항 레벨 유효성 확인
  - 더 세밀한 bin = 더 정확한 cluster 특정 → 신호 진입 정확도 향상

### ⚠️ 주의 사항 (Cycle 302)
- **PAPER_SIM_STRATEGY_PARAMS 현재 설정** (Cycle 301 최종):
  - `value_area: {"vol_filter_mult": 0.5}` ← Cycle 295 A
  - `wick_reversal: {"min_volatility": 0.001, "vol_mult": 0.6}` ← Cycle 295 A
  - `relative_volume: {"rvol_buy_sell": 1.2}` ← Cycle 297 B
  - `momentum_quality: {"quality_score_buy_threshold": 0.8, "consistency_buy_threshold": 0.3}` ← Cycle 295 C (0.85 역효과 복원)
  - `price_cluster: {"bounce_pct": 0.025, "vol_regime_filter": True, "vol_use_relative": True, "vol_atr_trend_min": 1.5}` ← Cycle 301 B (bounce_pct 0.02→0.025, 1.3→1.5 복원)
  - `order_flow_imbalance_v2: {"trend_span": 20}` ← Cycle 298 F
- **Engine adaptive_slippage=True**: paper_simulation에 활성화 (Cycle 299 E)
- **Engine consec_loss_scale_threshold=5**: paper_simulation에 활성화 (Cycle 298 B)
- **신규 전략 파일 생성 금지** — 파라미터 오버라이드로만 접근
- **Bundle OOS 실행 시 --csv-dir data/historical 필수**

### 핵심 메트릭 (Cycle 301)
- 테스트: **8392 passed, 23 skipped** (전체 스위트) ← 회귀 없음
- Paper Sim BTC 4h (8 windows, adaptive_slippage=True): 0/22 PASS
  - rank1: price_cluster (score=72.1, Sharpe=3.76→+10%, PF=2.28→+11%, SharpeStd=2.52, trades=12, **2/8 PASS**) ← bounce_pct=0.025 효과
  - rank2: momentum_quality (score=61.3, Sharpe=1.48, PF=1.33, trades=22) ← threshold=0.85 역효과 → 0.80 복원
  - rank3: cmf (score=54.9, Sharpe=0.59, trades=23)
  - rank8: order_flow_imbalance_v2 (3/8 PASS, 복원 확인)
- Bundle OOS BTC 4h (5-fold, real CSV 2023~2024):
  - cmf: **PASS** avg=2.508, std=1.888, WFE=1.136
  - supertrend_multi: **PASS** avg=3.674, std=1.860, WFE=2.116
  - **총 PASS: 2/5** (Cycle 299와 동일)

### 주요 코드 변경 이력 (Cycle 301)
1. `src/strategy/price_cluster.py` — ATR 기반 동적 bounce_pct 기능 추가 (F 리서치)
   - `atr_bounce_factor` 파라미터 (기본값=0.0, 비활성)
   - atr_bounce_factor>0 시: effective_bounce_pct = ATR(14)/close × factor
   - 향후 실험: factor=1.5~2.0 시도 예정
2. `scripts/paper_simulation.py` — bounce_pct 0.02→0.025, 실험 역효과 복원 (B+D)
   - bounce_pct=0.025: Sharpe +10% (3.41→3.76), PF +11% (2.05→2.28) 개선
   - vol_atr_trend_min=1.3 실험: SharpeStd 2.41→2.52 → 1.5 복원
   - quality_score_buy_threshold=0.85 실험: PF 1.48→1.33 → 0.80 복원

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: real CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows)
- ETH/SOL: synthetic CSV (data/historical/synthetic/)
- Bundle OOS: `--csv-dir data/historical` 필수 (5-fold 4h 구조, 2023~2024 실제 BTC)
- Paper simulation 4h: 22 전략 × 8 windows → 약 1-2분 소요 (BTC 단일)
