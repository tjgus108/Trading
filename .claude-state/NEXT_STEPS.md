# Next Steps

_Last updated: 2026-06-12 (Cycle 302 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 302

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 300 | A+C+F | 상대적 ATR vol_regime_filter 구현 (score +3.3), buy_thresh=0.30 실험→역효과 복원 |
| 301 | B+D+F | bounce_pct 0.025 (Sharpe+10%/PF+11%), ATR 동적 bounce_pct 기능 추가, 두 D실험 역효과 복원 |
| 302 | B+D+F | n_bins=7+atr_bounce_factor=1.5 역효과(Sharpe 3.76→-1.76) 확인 후 복원, DrawdownMonitor tiered halt 회복 개선, price_cluster 최적화 그리드 추가 |

### 🎯 Cycle 303 작업 방향 (303 mod 5 = 3 → C(데이터) + B(리스크) + F(리서치))

#### C(데이터): 데이터/인프라 개선
- **close_window 40봉 단독 실험**: n_bins=5 유지하면서 업데이트 빈도만 증가
  - 현재: close_window=50 → 40으로 축소 (더 반응적인 cluster 업데이트)
  - 기대: trades 12→15+ (더 빠른 cluster 전환 = 더 많은 bounce 기회)
  - 실험 전략: n_bins=7 독립 실험(atr_bounce_factor=0.0 유지) 결과와 비교
- **캐시/데이터 파이프라인**: DataFeed 안정성 확인, CSV 데이터 최신성 체크

#### B(리스크): 리스크 관리 개선
- **DrawdownMonitor tiered halt 회복 로직 테스트 추가** (Cycle302 코드 변경 검증)
  - `test_tiered_halt_recovery_faster_than_legacy`: tiered halt 후 tiered 조건 해소 → 빠른 재개 확인
  - `test_legacy_halt_recovery_unchanged`: legacy MDD halt는 기존 로직 유지 확인
- **price_cluster 거래 빈도 근본 원인 재분석**:
  - n_bins=7 역효과, n_bins=5 유지 확정
  - close_window=40 효과 측정 후 결정
  - 대안: bounce_pct 완화 (0.025→0.030) 단독 실험

#### F(리서치): 최신 연구 기반 개선
- **walk_forward DEFAULT_GRIDS price_cluster 활용**: 
  - close_window 40봉 실험 근거로 [40,50] 그리드에서 IS/OOS Sharpe 비교
  - n_bins [4,5,6] 탐색: 각각 독립 실험 (동시 실험 금지)
- **narrow_range trend_regime_filter**: ATR/ATR_MA > 1.4 시 억제 (Cycle301 F 제안)
  - A(품질) 사이클이 맞지만, 리서치 근거 강화: 2023-12 BTC 급등 구간 분석

### ⚠️ 주의 사항 (Cycle 303)
- **PAPER_SIM_STRATEGY_PARAMS 현재 설정** (Cycle 302 최종, 복원 확인):
  - `value_area: {"vol_filter_mult": 0.5}` ← Cycle 295 A
  - `wick_reversal: {"min_volatility": 0.001, "vol_mult": 0.6}` ← Cycle 295 A
  - `relative_volume: {"rvol_buy_sell": 1.2}` ← Cycle 297 B
  - `momentum_quality: {"quality_score_buy_threshold": 0.8, "consistency_buy_threshold": 0.3}` ← Cycle 295 C
  - `price_cluster: {"bounce_pct": 0.025, "vol_regime_filter": True, "vol_use_relative": True, "vol_atr_trend_min": 1.5}` ← Cycle 302 복원 (n_bins=7/atr_bounce_factor 역효과)
  - `order_flow_imbalance_v2: {"trend_span": 20}` ← Cycle 298 F
- **Engine adaptive_slippage=True**: paper_simulation에 활성화 (Cycle 299 E)
- **Engine consec_loss_scale_threshold=5**: paper_simulation에 활성화 (Cycle 298 B)
- **신규 전략 파일 생성 금지** — 파라미터 오버라이드로만 접근
- **Bundle OOS 실행 시 --csv-dir data/historical 필수**
- **단독 실험 원칙**: 두 파라미터를 동시에 변경하면 역효과 원인 특정 불가 (n_bins+atr_bounce 교훈)

### 핵심 메트릭 (Cycle 302)
- 테스트: **8392 passed, 23 skipped** (전체 스위트) ← 회귀 없음
- Paper Sim BTC 4h (8 windows, 실험 시):
  - n_bins=7 + atr_bounce_factor=1.5: price_cluster Sharpe 3.76→**-1.76** (대폭 역효과)
  - 복원 후: Cycle 301과 동일 예상 (rank1 price_cluster score=72.1)
- Bundle OOS BTC 4h (5-fold): **2/5 PASS** (cmf=2.508, supertrend_multi=3.674) ← 동일

### 주요 코드 변경 이력 (Cycle 302)
1. `src/risk/drawdown_monitor.py` — tiered halt 회복 로직 개선 (B(리스크))
   - `_tiered_halt: bool` 추가: halt 원인 추적 (일간/주간 tiered vs legacy MDD)
   - `_halt_drawdown: float` 추가: halt 시 낙폭 기록
   - 회복 조건: tiered halt → `halt_drawdown - recovery_pct` 달성 시 재개 (기존 legacy 임계값 대비 더 빠른 재개 가능)
   - `reset()` 메서드에 새 상태 변수 초기화 추가
2. `src/backtest/walk_forward.py` — price_cluster DEFAULT_GRIDS 추가 (D(ML))
   - bounce_pct: [0.020, 0.025, 0.030]
   - n_bins: [4, 5, 6] (7 제외 - 역효과 확인)
   - close_window: [40, 50]
   - vol_atr_trend_min: [1.3, 1.5, 2.0]
3. `scripts/paper_simulation.py` — n_bins=7+atr_bounce_factor=1.5 실험 후 복원 (주석 기록)

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: real CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows)
- ETH/SOL: synthetic CSV (data/historical/synthetic/)
- Bundle OOS: `--csv-dir data/historical` 필수 (5-fold 4h 구조, 2023~2024 실제 BTC)
- Paper simulation 4h: 22 전략 × 8 windows → 약 3-4분 소요 (BTC 단일)
