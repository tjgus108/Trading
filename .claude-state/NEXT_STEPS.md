# Next Steps

_Last updated: 2026-06-11 (Cycle 299 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 299

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 297 | B+D+F | apply_wfe 불일치 수정, rvol_buy_sell 1.3→1.2, n_bins/bull_only 실험 실패 → 복원 |
| 298 | C+B+F | bounce_pct 0.015→0.02 (2/8 sideways PASS), consec_loss_scale 엔진 추가, trend_span 실험 |
| 299 | D+E+F | vol_regime_filter 파라미터(코드), adaptive_slippage 활성화, delta_window 파라미터화 |

### 🎯 Cycle 300 작업 방향 (300 mod 5 = 0 → A(품질) + C(데이터) + F(리서치))

#### A(품질): 전략 백테스트 품질 재검증
- **핵심 이슈**: price_cluster 2/8 PASS (sideways만), SharpeStd=2.41 높음
  - vol_regime_filter 코드 기능 존재 → 상대적 ATR 방식으로 개선 검토
  - 상대 ATR: ATR < ATR_MA*1.0 → sideways, ATR > ATR_MA*1.5 → trending
  - 현재 절대값 thresh(0.025) 대신 ATR_MA 대비 비율 사용 시 더 효과적일 수 있음
- momentum_quality SharpeStd=3.81 여전히 높음 — 어떤 윈도우에서 FAIL하는지 분석 필요

#### C(데이터): 데이터 품질 개선
- **핵심 이슈**: ETH/SOL synthetic CSV로 인한 제약
  - BTC 전략 결과가 전체 판단을 지배
  - ETH 1h real CSV 수집 가능 여부 재확인 (SSL 차단 환경)
- order_flow_imbalance_v2 극단 손실 (SharpeStd=6.24 원인) 윈도우 분석
  - 어떤 마켓 레짐(fold)에서 극단 손실 발생하는지 확인

#### F(리서치): price_cluster vol_regime_filter 개선 방향
- **핵심 이슈**: 절대값 thresh(0.025) → 역효과 확인 (trades 12→5)
  - 개선: 상대적 ATR (ATR/ATR_MA 비율) 사용
  - ATR_MA(20) 대비 ATR < 1.0 → ranging/sideways → 신호 허용
  - ATR_MA(20) 대비 ATR > 1.5 → trending → 신호 억제
  - 이 방식이면 BTC 4h에서 더 안정적인 필터 가능
- order_flow_imbalance_v2 BUY_THRESH 강화 검토 (0.25→0.30)
  - 극단 손실 윈도우의 노이즈 신호 억제 목적

### ⚠️ 주의 사항 (Cycle 300)
- **PAPER_SIM_STRATEGY_PARAMS 현재 설정** (Cycle 299 최종):
  - `value_area: {"vol_filter_mult": 0.5}` ← Cycle 295 A
  - `wick_reversal: {"min_volatility": 0.001, "vol_mult": 0.6}` ← Cycle 295 A
  - `relative_volume: {"rvol_buy_sell": 1.2}` ← Cycle 297 B
  - `momentum_quality: {"quality_score_buy_threshold": 0.8, "consistency_buy_threshold": 0.3}` ← Cycle 295 C
  - `price_cluster: {"bounce_pct": 0.02}` ← Cycle 298 C (vol_regime_filter 비활성)
  - `order_flow_imbalance_v2: {"trend_span": 20}` ← Cycle 298 F
- **Engine adaptive_slippage=True**: paper_simulation에 활성화 (Cycle 299 E) ← 신규
- **Engine consec_loss_scale_threshold=5**: paper_simulation에 활성화 (Cycle 298 B)
- **신규 전략 파일 생성 금지** — 파라미터 오버라이드로만 접근
- **Bundle OOS 실행 시 --csv-dir data/historical 필수**

### 핵심 메트릭 (Cycle 299)
- 테스트: **8392 passed, 23 skipped** (전체 스위트) + 262 passed (관련 테스트 단독)
- Paper Sim BTC 4h (8 windows, adaptive_slippage=True): 0/22 PASS
  - rank1: price_cluster (score=71.5, Sharpe=3.41, SharpeStd=2.41, PF=2.05, trades=12, **2/8 PASS**) ← bounce_pct=0.02
  - rank2: momentum_quality (score=63.6, Sharpe=1.48, SharpeStd=3.81, trades=22)
  - rank3: cmf (score=56.9, Sharpe=0.59, adaptive slippage 페널티)
  - rank8: order_flow_imbalance_v2 (trend_span=20, 3/8 PASS 복원)
- Bundle OOS BTC 4h (5-fold, real CSV 2023~2024):
  - cmf: **PASS** avg=2.508, std=1.888, WFE=1.136
  - supertrend_multi: **PASS** avg=3.674, std=1.860, WFE=2.116
  - **총 PASS: 2/5** (Cycle 298와 동일 유지)

### 주요 코드 변경 이력 (Cycle 299)
1. `src/strategy/price_cluster.py` — vol_regime_filter 파라미터 추가 (D ML)
   - ATR(14)/close 비율로 변동성 레짐 판별 (`_atr_ratio()` 메서드)
   - thresh=0.025 역효과 확인 → PAPER_SIM 비활성, 향후 상대적 ATR 방식 검토
2. `src/strategy/order_flow_imbalance_v2.py` — delta_window 파라미터화 (F 리서치)
   - 기본값=10 유지, delta_window=7 역효과 확인 후 기본값 복원
3. `scripts/paper_simulation.py` — adaptive_slippage=True (E 실행)
   - ATR 기반 레짐별 슬리피지 (low/normal/high = 0.02/0.05/0.15%)
   - 현실적 시장 충격 반영, 고변동성 전략 성과 보수적 추정

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: real CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows)
- ETH/SOL: synthetic CSV (data/historical/synthetic/)
- Bundle OOS: `--csv-dir data/historical` 필수 (5-fold 4h 구조, 2023~2024 실제 BTC)
- Paper simulation 4h: 22 전략 × 8 windows → 약 1-2분 소요 (BTC 단일)
