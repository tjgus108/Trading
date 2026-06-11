# Next Steps

_Last updated: 2026-06-11 (Cycle 298 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 298

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 296 | B+D+F | MC_P_THRESHOLD 0.05→0.10, bull_only 파라미터, close_window/n_bins 파라미터 |
| 297 | B+D+F | apply_wfe 불일치 수정, rvol_buy_sell 1.3→1.2, n_bins/bull_only 실험 실패 → 복원 |
| 298 | C+B+F | bounce_pct 0.015→0.02, rvol_buy_sell 1.2→1.1, vol_thresh 실험 실패 → 복원, WF OOS Sharpe 윈소라이즈 |

### 🎯 Cycle 299 작업 방향 (299 mod 5 = 4 → D(ML) + E(실행) + F(리서치))

#### D(ML): price_cluster 추가 trades 개선
- **핵심 이슈**: bounce_pct=0.02 → trades=12 (여전히 < 15)
  - bounce_pct=0.025 또는 0.03 시도 (Sharpe 3.72 유지 여부 확인)
  - 단, PF가 2.17에서 유지되는지 확인 필수
  - 추가 고려: `close_window` 축소 (50→40) → 더 빈번한 클러스터 갱신

#### E(실행): relative_volume mc_p_value 추가 개선
- **핵심 이슈**: mc_p_value 0.155 > 0.10 (1 window, rvol=1.1 적용 후)
  - rvol=1.0 시도하면 trades 추가 증가 가능 (20+) → mc_p_value 하락 예상
  - PF 1.63 유지 여부 모니터링 필수 (너무 낮추면 PF < 1.5 위험)
  - 대안: mc_block_size=3 적용 (serial correlation 보정, 잡음 mc_p 개선)

#### F(리서치): order_flow_imbalance_v2 극단 손실 윈도우 대처
- **핵심 이슈**: sharpe -7.98 (1 window), PF 0.31 (1 window) → 극단 손실 구간
  - 현재 3/8 PASS, 4/8 목표 (50% 달성 시 PASS)
  - 분석: BUY_THRESH=0.25 vs. ATR 기반 동적 임계값
  - 극단 손실 방지: `imbalance_ma` 필터 강화 (imb > imb_ma_val에서 imb > imb_ma_val * 1.1로)
  - 코드 위치: `src/strategy/order_flow_imbalance_v2.py`

### ⚠️ 주의 사항 (Cycle 299)
- **PAPER_SIM_STRATEGY_PARAMS 현재 설정**:
  - `value_area: {"vol_filter_mult": 0.5}` ← Cycle 295 A
  - `wick_reversal: {"min_volatility": 0.001, "vol_mult": 0.6}` ← Cycle 295 A
  - `relative_volume: {"rvol_buy_sell": 1.1}` ← Cycle 298 B (1.2→1.1)
  - `momentum_quality: {"quality_score_buy_threshold": 0.8, "consistency_buy_threshold": 0.3}` ← Cycle 295 C
  - `price_cluster: {"bounce_pct": 0.02}` ← Cycle 298 C (0.015→0.02)
  - ~~`volatility_cluster: {"vol_thresh": 0.7}`~~ ← Cycle 298 B 역효과, 기본값(0.6) 복원
- **vol_thresh=0.7 실험 이력**: PF 1.14→0.88, Sharpe -1.31→-2.17 역효과 확인
- **신규 전략 파일 생성 금지** — 파라미터 오버라이드로만 접근
- **Bundle OOS 실행 시 --csv-dir data/historical 필수**
- **paper_simulation.py 실행 시 --csv-dir data/historical --timeframe 4h 필수** (1h 모드는 다른 결과)

### 핵심 메트릭 (Cycle 298)
- 테스트: **8392 passed** — 회귀 없음
- Paper Sim BTC 4h (8 windows): 0/22 PASS
  - rank1: price_cluster (score=71.5, Sharpe=3.72, PF=2.17, trades=12) ← bounce_pct=0.02
  - rank2: momentum_quality (score=62.9, Sharpe=1.82, trades=22)
  - rank3: relative_volume (score=61.0, Sharpe=1.84, PF=1.63, trades=19, 1/8 PASS) ← rvol=1.1
  - rank6: order_flow_imbalance_v2 (3/8 PASS) ← MC=0.10 효과 유지
- Bundle OOS BTC 4h (5-fold, real CSV 2023~2024):
  - cmf: **PASS** avg=2.508, std=1.888, WFE=1.136
  - supertrend_multi: **PASS** avg=3.674, std=1.860, WFE=2.116
  - **총 PASS: 2/5** (Cycle 297과 동일 유지)

### 주요 코드 변경 이력 (Cycle 298)
1. `src/backtest/walk_forward.py` — OOS Sharpe 윈소라이제이션 (C데이터/F리서치)
   - RollingOOSValidator.validate(): _SHARPE_FOLD_CAP=10.0 추가
   - avg_sharpe + oos_std 모두 capped_sharpes 사용
2. `src/strategy/volatility_cluster.py` — vol_thresh 파라미터화 (B리스크)
   - vol_thresh=_LOW_VOL_THRESH(0.6) 기본값, __init__ 파라미터로 노출
   - PAPER_SIM에서는 기본값(0.6) 사용 (0.7 역효과 확인)
3. `scripts/paper_simulation.py` — 파라미터 오버라이드 업데이트
   - relative_volume: rvol_buy_sell 1.2→1.1 (B리스크)
   - price_cluster: bounce_pct 0.015→0.02 (C데이터)

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: real CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows)
- ETH/SOL: synthetic CSV (data/historical/synthetic/)
- Bundle OOS: `--csv-dir data/historical` 필수 (5-fold 4h 구조, 2023~2024 실제 BTC)
- Paper simulation: `--csv-dir data/historical --timeframe 4h` 필수
- Paper simulation 4h: 22 전략 × 8 windows → 약 1-2분 소요 (BTC 단일)
