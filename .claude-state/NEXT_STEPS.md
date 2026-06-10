# Next Steps

_Last updated: 2026-06-10 (Cycle 294 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 294

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 292 | B+D+F | supertrend_multi std threshold 2.5→3.0, --start-date 옵션, Bundle OOS 0→2 PASS |
| 293 | C+B+F | --verbose-windows 옵션, VolTargeting.for_timeframe(), Paper Sim FAIL 원인 분석 완료 |
| 294 | D+E+F | compute_ensemble_weight_regime_aware(), trades_regularization_scale 추가, 레짐별 전략 할당 분석 |

### 🎯 Cycle 295 작업 방향 (295 mod 5 = 0 → A(품질) + C(데이터) + F(리서치))

#### A(품질): 저거래 전략 거래 빈도 개선
- **핵심 이슈**: Paper Sim 전체 FAIL 원인 1위 = "trades X < 15" (22개 중 대부분)
  - 특히: value_area(avg=12), htf_ema(avg=11), wick_reversal(avg=10), relative_volume(avg=13)
  - 이들은 Sharpe/PF가 양호하나 거래 수만 부족 → 조건 완화로 PASS 가능성 있음
  - `scripts/paper_simulation.py` PAPER_SIM_STRATEGY_PARAMS에 조건 완화 오버라이드 추가
  - 예: value_area의 va_period 축소, htf_ema lookback 조정
  - 테스트 실행 후 거래 수 개선 확인

#### C(데이터): SIDEWAYS 레짐 전략 탐색
- **핵심 이슈**: Paper Sim W5-W6(sideways) 구간에서 모든 전략 0~2 PASS
  - cmf: W5 Sharpe=-2.41, W6 Sharpe=-0.50 — sideways에서 완전 실패
  - supertrend_multi: W5-W7 모두 0 trades
  - 분석: momentum_quality (W6: Sharpe=2.51, PF=1.45), price_cluster (W5: Sharpe=3.40, PF=1.68) — sideways 후보
  - `momentum_quality`: sideways에서 가장 유망, PF 0.05 gap이 최소
  - `data/historical` CSV로 sideways 구간(W5-W6, 2023-12~2024-03) 집중 분석
  - 해당 구간 전략 파라미터 튜닝 (기존 전략 파일 수정)

#### F(리서치): 거래 빈도 개선 패턴 조사
- Cycle 294 분석 결론:
  - 거래 빈도가 공통 병목: trades < 15가 전체 FAIL 원인의 70%+
  - PASS 기준 15 trades는 4h 60일 구간에서 상당히 높음 (2.5 trades/week)
  - 제안: PAPER_SIM_STRATEGY_PARAMS에 거래 빈도 개선 파라미터 추가
    - value_area: va_period 하향 (20→15), va_mult 상향 (0.60→0.65)
    - htf_ema: lookback 단축, 신호 조건 완화
    - relative_volume: vol_threshold 하향 (더 자주 신호)
  - Bundle OOS와 Paper Sim 불일치 계속: 다음 사이클 평가 기준 통합 검토

### ⚠️ 주의 사항 (Cycle 295)
- **Bundle OOS 실행 시 --csv-dir data/historical 필수**
- **trades_regularization_scale=0.1**: optimize_supertrend_multi에만 적용, 다른 전략 기본값 0.0 유지
- **compute_ensemble_weight_regime_aware()**: 실제 배포 시 레짐 감지 파이프라인과 연동 필요
- **신규 전략 파일 생성 금지** — 기존 파라미터 오버라이드로만 접근

### 핵심 메트릭 (Cycle 294)
- 테스트: **8392 passed** — 회귀 없음 (목표)
- Paper Sim BTC 4h (8 windows, --verbose-windows): 0/22 PASS (Cycle 293과 동일)
  - rank1: cmf (score=68.3, Sharpe=1.25, PF=1.24, trades=23)
  - rank5: supertrend_multi (score=54.6, Sharpe=2.14, PF=1.22, trades=8)
- Bundle OOS BTC 4h (5-fold, real CSV 2023~2024):
  - cmf: **PASS** avg=2.508, std=1.888, WFE=1.136
  - supertrend_multi: **PASS** avg=3.674, std=1.860, WFE=2.116
  - **총 PASS: 2/5** (Cycle 293과 동일 유지)

### 주요 코드 변경 이력 (Cycle 294)
1. `src/ml/trainer.py` — `compute_ensemble_weight_regime_aware()` 추가 (D ML)
   - 레짐별 전략 패널티 계수 딕셔너리: BULL/SIDEWAYS/BEAR/HIGH_VOL
   - SIDEWAYS: cmf=0.3, supertrend_multi=0.2 (강한 패널티)
   - Bundle OOS Sharpe 배율 옵션 포함
2. `src/backtest/walk_forward.py` — IS 거래 수 기반 타이브레이커 추가 (E 실행)
   - `WalkForwardOptimizer.trades_regularization_scale` 파라미터 추가
   - `_optimize_in_sample()`: IS trades 저장 + Score += scale * min(1, trades/30)
   - `optimize_supertrend_multi()`: `trades_regularization_scale=0.1` 적용

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: real CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows)
- ETH/SOL: synthetic CSV (data/historical/synthetic/)
- Bundle OOS: `--csv-dir data/historical` 필수 (5-fold 4h 구조, 2023~2024 실제 BTC)
- Paper simulation 4h: 22 전략 × 8 windows → 약 8-10분 소요
- Paper simulation 4h + --verbose-windows: 상위 5 전략 윈도우별 분석 포함
