# Next Steps

_Last updated: 2026-06-15 (Cycle 313 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 313

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 311 | B+D+F | 슬리피지 레짐 리포트 추가(paper_sim), NR ema_slope 버그수정, ema_slope 실험 복원 |
| 312 | B+D+F | kelly_fraction_multiplier 테스트 추가(4개), nr_lookback=4 실험→효과없음(복원), TRAIN_HOURS=84일 실험→역효과(210일 복원) |
| 313 | C+B+F | NR_SCAN_WINDOW=5 실험→역효과(PF=0.90, std=5.447) 확정 후 3 복원, should_kill_strategy 레짐별 테스트 추가(9개) |

### 🎯 Cycle 314 작업 방향 (314 mod 5 = 4 → D(ML) + E(실행) + F(리서치))

#### D(ML): narrow_range VOL_SPIKE_MULT 실험
- **Cycle 313 C 결론**: NR_SCAN_WINDOW=5 역효과 확정 (복원 완료)
  - NR_SCAN_WINDOW 확장은 오래된 NR 참조 → 오신호 → PF 하락
  - binding constraint 탐구: ATR_THRESHOLD(0.95)와 VOL_SPIKE_MULT(1.0)가 남은 후보
- **다음 실험 후보** (단독 실험 원칙):
  - `VOL_SPIKE_MULT` 완화: 1.0→0.5 — 거래량 스파이크 없어도 진입 허용
    - 기대: trades 대폭 증가, 하지만 신호 품질 저하 위험
  - `ATR_THRESHOLD` 완화: 0.95→1.05 — ATR 수축 조건 거의 폐기
    - 기대: ATR 필터 통과율 증가, 하지만 고변동성 구간에서 오신호 증가
  - 권고: **VOL_SPIKE_MULT 1.0→0.5 시도** (Cycle 314 D(ML) 실험)
- **주의**: BUNDLE_STRATEGY_INIT_PARAMS["narrow_range"] 업데이트 (실험 전용)
  - 단, NR_SCAN_WINDOW=3(클래스 상수)은 이미 복원됨 — init_params로 변경 불가

#### E(실행): supertrend_multi 4h 파라미터 검토
- **Bundle OOS 9-fold 결과**: supertrend_multi 5/6 valid PASS (avg=4.880, PF=2.321)
  - fold[0] FAIL (2022-01~2022-06 OOS, WFE=0.215 < 0.50) → 초기 bear market 구간
  - fold[4] trades<3 제외, fold[5,6] 레짐 전환 제외
  - **실전 투입 후보 #1**: supertrend_multi 4h가 가장 유망
- **E 작업**: supertrend_multi 현재 파라미터 확인 및 paper_trading mode 활성화 검토
  - `src/exchange/paper_trader.py` 또는 유사 파일 검토
  - paper_trading 4h 백테스트 설정 가능한지 확인

#### F(리서치): Bundle OOS --csv-dir 의존성 확인
- **Cycle 313 F 결론**: atr_multiplier_tp=3.5 (이미 Cycle 256에서 최적화됨)
  - PF<1.5 구조적 FAIL은 1h BTC 노이즈 문제 — TP/SL 조정으로 해결 불가
  - **결론 확정**: 4h Bundle OOS 결과 기반으로 실전 전략 선정
- **Cycle 313 Bundle OOS 주의사항**:
  - `--csv-dir data/historical` 누락 → 9-fold (2022-2023 데이터)
  - Cycle 312 5-fold (2023-2024)와 비교 불가
  - **필수**: 다음 Bundle OOS 실행 시 반드시 `--csv-dir data/historical` 포함
- **가설 검토**: supertrend_multi 4h PASS fold[0] 실패 원인
  - 2022-01~06 기간: 극심한 bear market (BTC $48K→$20K)
  - WFE=0.215 < 0.50 → IS 최적화된 파라미터가 OOS에서 divergence
  - IS=3.968 (고성능) → 과적합 가능성 → 더 보수적인 파라미터 검토

### ⚠️ 주의 사항 (Cycle 314)
- **NR_SCAN_WINDOW**: 현재 3 (복원됨) — 변경 금지
- **PAPER_SIM_STRATEGY_PARAMS 현재 설정** (Cycle 313 변경 없음):
  - `value_area: {"vol_filter_mult": 0.5}` ← Cycle 295 A
  - `wick_reversal: {"min_volatility": 0.001, "vol_mult": 0.6}` ← Cycle 295 A
  - `relative_volume: {"rvol_buy_sell": 1.2}` ← Cycle 297 B
  - `momentum_quality: {"quality_score_buy_threshold": 0.8, "consistency_buy_threshold": 0.3}` ← Cycle 295 C
  - `price_cluster: {"bounce_pct": 0.025, "close_window": 60, "vol_regime_filter": True, "vol_use_relative": True, "vol_atr_trend_min": 1.5}` ← Cycle 305 C
  - `order_flow_imbalance_v2: {"trend_span": 20}` ← Cycle 298 F
  - `cmf: {"buy_thresh": 0.10}` ← Cycle 309 D
- **BUNDLE_STRATEGY_INIT_PARAMS 현재 설정** (Cycle 313 변경 없음):
  - `narrow_range: {"trend_regime_filter": False, "ema_slope_min_buy": 0.0, "ema_slope_max_sell": 0.0}` ← Cycle311 D(ML) 복원
  - `supertrend_multi: {atr_threshold=0.5, ema_filter=True, cmf_confirm=True, ...}`
- **paper_simulation.py TRAIN_HOURS**: `24 * 210` (변경 없음)
- **Bundle OOS 실행 시 `--csv-dir data/historical` 필수** (Cycle 313에서 누락 → 9-fold로 변경됨)
- **단독 실험 원칙**: 두 파라미터를 동시에 변경하면 역효과 원인 특정 불가

### 핵심 메트릭 (Cycle 313)
- 테스트: **8413 passed, 23 skipped** (9개 신규 추가, 회귀 없음)
- Paper Sim BTC 1h (8 windows, TRAIN=210일): **0/22 PASS**
  - rank1: price_cluster (Sharpe=0.59, 3/8, PF=1.18)
  - rank2: supertrend_multi (Sharpe=0.32, 2/8, PF=1.14)
  - narrow_range (NR_SCAN_WINDOW=5 실험): rank15, Sharpe=-1.42, PF=0.90 → 역효과 → 복원
  - 주 실패 원인: PF < 1.5 (구조적 문제)
- Bundle OOS BTC 4h (9-fold, --csv-dir 누락): **0/5 PASS**
  - supertrend_multi: 5/6 valid PASS (avg=4.880) — 유망 전략 #1
  - narrow_range: 3/8 valid PASS, std=5.447 (불안정)
  - cmf: 4/9 PASS, std=3.854 (2022 데이터 포함으로 불안정)
  - ⚠️ 이전 Cycle 312 5-fold(--csv-dir 포함)와 직접 비교 불가

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: real CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows)
- ETH/SOL: synthetic CSV (data/historical/synthetic/)
- Bundle OOS: `--csv-dir data/historical` 필수 (5-fold 4h 구조, 2023~2024 실제 BTC)
- Paper simulation 1h: 22 전략 × 8 windows (210일 train) → 약 7-10분 소요 (BTC 기준)
