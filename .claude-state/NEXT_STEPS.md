# Next Steps

_Last updated: 2026-06-12 (Cycle 303 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 303

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 301 | B+D+F | bounce_pct 0.025 (Sharpe+10%/PF+11%), ATR 동적 bounce_pct 기능 추가 |
| 302 | B+D+F | n_bins=7+atr_bounce_factor=1.5 역효과 복원, DrawdownMonitor tiered halt 개선, price_cluster 그리드 추가 |
| 303 | C+B+F | close_window=40 역효과(Sharpe -61%) 확인→50 복원, tiered halt 회복 테스트 2개 추가 |

### 🎯 Cycle 304 작업 방향 (304 mod 5 = 4 → D(ML) + E(실행) + F(리서치))

#### D(ML): ML/신호 개선
- **bounce_pct=0.030 단독 실험**: n_bins=5, close_window=50 유지하면서 threshold만 완화
  - 현재: bounce_pct=0.025 → 0.030으로 확대 (threshold 10% 이완)
  - 기대: trades 12→15+ (진입 장벽 낮춤으로 더 많은 bounce 포착)
  - 주의: Cycle301에서 0.025가 오히려 Sharpe 향상. 0.030은 PF 저하 가능성 있음
  - 실험 전략: 단독 실험 (close_window, n_bins 변경 금지)
- **walk_forward 그리드 close_window 업데이트**:
  - 현재 그리드: [40, 50] → 결과: 40 역효과 확인
  - 업데이트: [50, 60] (50 유지, 60 추가 - 더 안정적인 cluster 탐색)

#### E(실행): 실행 모듈 개선
- **adaptive_slippage 파라미터 검토**: BacktestEngine에서 adaptive_slippage=True 효과 재측정
  - Cycle299 E에서 활성화됨 — 효과 지속 확인
- **Paper trading 모드**: 실시간 신호 생성 파이프라인 점검

#### F(리서치): 최신 연구 기반 개선
- **close_window 실험 근거 강화**: 
  - close_window=40 역효과 분석: BTC 4h는 cluster 안정성이 중요 (50봉 > 40봉)
  - close_window=60 탐색 근거: 더 긴 price memory가 support/resistance 품질 향상
- **narrow_range trend_regime_filter**: ATR/ATR_MA > 1.4 시 억제 (Cycle301 F 제안)
  - Bundle OOS fold2/3 고변동성 구간에서 narrow_range FAIL 분석

### ⚠️ 주의 사항 (Cycle 304)
- **PAPER_SIM_STRATEGY_PARAMS 현재 설정** (Cycle 303 최종, close_window 제거):
  - `value_area: {"vol_filter_mult": 0.5}` ← Cycle 295 A
  - `wick_reversal: {"min_volatility": 0.001, "vol_mult": 0.6}` ← Cycle 295 A
  - `relative_volume: {"rvol_buy_sell": 1.2}` ← Cycle 297 B
  - `momentum_quality: {"quality_score_buy_threshold": 0.8, "consistency_buy_threshold": 0.3}` ← Cycle 295 C
  - `price_cluster: {"bounce_pct": 0.025, "vol_regime_filter": True, "vol_use_relative": True, "vol_atr_trend_min": 1.5}` ← Cycle 303 복원 (close_window=40 역효과)
  - `order_flow_imbalance_v2: {"trend_span": 20}` ← Cycle 298 F
- **Engine adaptive_slippage=True**: paper_simulation에 활성화 (Cycle 299 E)
- **Engine consec_loss_scale_threshold=5**: paper_simulation에 활성화 (Cycle 298 B)
- **신규 전략 파일 생성 금지** — 파라미터 오버라이드로만 접근
- **Bundle OOS 실행 시 --csv-dir data/historical 필수**
- **단독 실험 원칙**: 두 파라미터를 동시에 변경하면 역효과 원인 특정 불가

### 핵심 메트릭 (Cycle 303)
- 테스트: **8394 passed, 23 skipped** (+2 새 테스트, 전체 스위트) ← 회귀 없음
- Paper Sim BTC 4h (8 windows):
  - close_window=40 실험: price_cluster Sharpe 3.76→**1.47** (-61% 역효과)
  - 복원 후: Cycle302와 동일 예상 (rank1 momentum_quality score=69.7)
- Bundle OOS BTC 4h (5-fold): **2/5 PASS** (cmf=2.508, supertrend_multi=3.674) ← 동일

### 주요 코드 변경 이력 (Cycle 303)
1. `tests/test_drawdown_monitor.py` — tiered halt 회복 테스트 2개 추가 (B(리스크))
   - `test_tiered_halt_recovery_faster_than_legacy`: tiered halt total_dd > max_dd 시나리오 검증
   - `test_legacy_halt_recovery_unchanged`: legacy MDD halt 기존 기준 유지 검증
2. `scripts/paper_simulation.py` — close_window=40 실험 후 역효과 확인 → 50 복원 (C(데이터))
   - 실험: close_window=40 (Sharpe 3.76→1.47, PF 2.28→1.54, trades 변화없음)
   - 결론: close_window=50 확정, 다음 실험 close_window=60 or bounce_pct=0.030

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: real CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows)
- ETH/SOL: synthetic CSV (data/historical/synthetic/)
- Bundle OOS: `--csv-dir data/historical` 필수 (5-fold 4h 구조, 2023~2024 실제 BTC)
- Paper simulation 4h: 22 전략 × 8 windows → 약 3-4분 소요 (BTC 단일)

### close_window 실험 역사 (price_cluster)
| 실험 | close_window | Sharpe | PF | Trades | 결론 |
|------|-------------|--------|-----|--------|------|
| 기본 | 50 | ~3.4 | ~2.0 | 12 | 기준선 |
| Cycle301 B | 50+bounce=0.025 | 3.76 | 2.28 | 12 | 최적 기준선 |
| Cycle303 C | 40 | 1.47 | 1.54 | 12 | 역효과 (Sharpe -61%) |
| 다음 실험 | 60 | - | - | - | 더 안정적 cluster 탐색 |
