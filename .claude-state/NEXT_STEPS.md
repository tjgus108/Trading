# Next Steps

_Last updated: 2026-06-12 (Cycle 300 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 300

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 298 | C+B+F | bounce_pct 0.015→0.02 (2/8 sideways PASS), consec_loss_scale 엔진 추가, trend_span 실험 |
| 299 | D+E+F | vol_regime_filter 파라미터(코드), adaptive_slippage 활성화, delta_window 파라미터화 |
| 300 | A+C+F | 상대적 ATR vol_regime_filter 구현 (score +3.3), buy_thresh=0.30 실험→역효과 복원 |

### 🎯 Cycle 301 작업 방향 (301 mod 5 = 1 → B(리스크) + D(ML) + F(리서치))

#### B(리스크): 리스크 관리 개선
- **핵심 이슈**: price_cluster trades=12 < 15 (most windows에서 MIN_TRADES 미달)
  - 거래 수 부족의 근본 원인 분석 필요
  - bounce_pct 더 완화 시도: 0.02→0.025 (trades 증가 목표)
  - 또는 threshold 완화: `min(cluster_low * bounce_pct, cluster_low * 0.005)` 형태 하한 제거
  - 주의: 거래 수 증가 vs PF 유지 트레이드오프 확인 필요
- momentum_quality PF < 1.5 (1.27~1.48): 약한 신호 필터링 강화 검토
  - quality_score_buy_threshold 0.8 → 0.85 시도 (고품질 신호만 허용)

#### D(ML): ML 신호 개선
- **핵심 이슈**: price_cluster SharpeStd=2.41 여전히 높음
  - W8(bull, trades=8, Sharpe=-0.11) 분석: ATR/ATR_MA가 1.5 미만인데도 FAIL
  - vol_atr_trend_min=1.5 → 1.3으로 더 공격적 필터링 검토 (trades 8→더 감소 가능성)
  - 상충: 더 강한 필터 → trades 더 감소 vs 품질 향상
- order_flow_imbalance_v2 3/8 PASS 복원 확인
  - buy_thresh 기본값(0.25) 복원 → 다음 시뮬에서 3/8 복원 확인 필요

#### F(리서치): 최신 연구 기반 개선
- **횡보시장 전략 품질 향상**: price_cluster의 구조적 한계 분석
  - 50봉 cluster: 다양한 bin 수(3/5/7) 실험 검토
  - bounce_pct 동적 설정: ATR 기반 자동 조정 (현재 고정 2%)
- narrow_range fold3 극단 손실 (OOS=-10.79) 분석
  - fold3 기간: 2023-12-27~2024-02-24 (BTC 급등 구간)
  - 급등 시 narrow range 패턴이 오작동 → BTC 급등 감지 후 일시 중지 로직 필요

### ⚠️ 주의 사항 (Cycle 301)
- **PAPER_SIM_STRATEGY_PARAMS 현재 설정** (Cycle 300 최종):
  - `value_area: {"vol_filter_mult": 0.5}` ← Cycle 295 A
  - `wick_reversal: {"min_volatility": 0.001, "vol_mult": 0.6}` ← Cycle 295 A
  - `relative_volume: {"rvol_buy_sell": 1.2}` ← Cycle 297 B
  - `momentum_quality: {"quality_score_buy_threshold": 0.8, "consistency_buy_threshold": 0.3}` ← Cycle 295 C
  - `price_cluster: {"bounce_pct": 0.02, "vol_regime_filter": True, "vol_use_relative": True, "vol_atr_trend_min": 1.5}` ← Cycle 300 A+F (신규)
  - `order_flow_imbalance_v2: {"trend_span": 20}` ← Cycle 298 F (buy_thresh=0.30 역효과 복원)
- **Engine adaptive_slippage=True**: paper_simulation에 활성화 (Cycle 299 E)
- **Engine consec_loss_scale_threshold=5**: paper_simulation에 활성화 (Cycle 298 B)
- **신규 전략 파일 생성 금지** — 파라미터 오버라이드로만 접근
- **Bundle OOS 실행 시 --csv-dir data/historical 필수**

### 핵심 메트릭 (Cycle 300)
- 테스트: **8392 passed, 23 skipped** (전체 스위트) ← 회귀 없음
- Paper Sim BTC 4h (8 windows, adaptive_slippage=True): 0/22 PASS
  - rank1: price_cluster (score=74.8, Sharpe=3.41, SharpeStd=2.41, PF=2.05, trades=12, **2/8 PASS**) ← 상대 ATR 효과 score +3.3
  - rank2: momentum_quality (score=65.3, Sharpe=1.48, SharpeStd=3.81, trades=22)
  - rank3: cmf (score=58.5, Sharpe=0.59, trades=23)
  - rank11: order_flow_imbalance_v2 (buy_thresh=0.30 역효과 복원 필요, 1/8→3/8 복원 목표)
- Bundle OOS BTC 4h (5-fold, real CSV 2023~2024):
  - cmf: **PASS** avg=2.508, std=1.888, WFE=1.136
  - supertrend_multi: **PASS** avg=3.674, std=1.860, WFE=2.116
  - **총 PASS: 2/5** (Cycle 299와 동일)

### 주요 코드 변경 이력 (Cycle 300)
1. `src/strategy/price_cluster.py` — 상대적 ATR vol_regime_filter 추가 (A+F 품질+리서치)
   - `_atr_ratio_relative()` 메서드: ATR(14)/ATR_MA(20) 비율
   - 데이터 부족 시 1.0 중립 반환 (suppress 안함)
   - 새 파라미터: vol_use_relative=True, vol_atr_ma_period=20, vol_atr_trend_min=1.5
   - ATR/ATR_MA > 1.5 → 추세 → 신호 억제; < 1.5 → 허용
2. `src/strategy/order_flow_imbalance_v2.py` — buy_thresh/sell_thresh 파라미터화 (C 데이터)
   - 생성자에 buy_thresh=0.25, sell_thresh=-0.25 추가 (기본값=모듈 상수 유지)
   - buy_thresh=0.30 실험: 3/8→1/8 PASS 역효과 (mc_p_value 실패 증가) → 기본값 복원
3. `scripts/paper_simulation.py` — price_cluster 상대 ATR 활성화, order_flow buy_thresh 복원

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: real CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows)
- ETH/SOL: synthetic CSV (data/historical/synthetic/)
- Bundle OOS: `--csv-dir data/historical` 필수 (5-fold 4h 구조, 2023~2024 실제 BTC)
- Paper simulation 4h: 22 전략 × 8 windows → 약 1-2분 소요 (BTC 단일)
