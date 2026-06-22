# Next Steps

_Last updated: 2026-06-22 (Cycle 344 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 344

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 342 | B+D+F | loss_scale 집계 paper_sim 연결, IS/OOS Pearson 추가, 0/20 22연속 |
| 343 | C+B+F | BTC CSV 품질확인, RANGING kill 1.5→1.2, avg_oos_mdd 추가, 0/20 23연속 |
| 344 | D+E+F | avg_oos_mdd Bundle OOS 노출, Slip_High% per-window 추가, 4h/1h 구조 분석, 0/20 24연속 |

### 🎯 Cycle 345 작업 방향 (345 mod 5 = 0 → A(품질) + C(데이터) + F)

#### A(품질): 테스트 커버리지 점검 + BundleOOSResult avg_oos_mdd 테스트 추가

- **배경**: Cycle 343-344에서 2개 테스트 버그 발견 (코드 변경 후 테스트 미업데이트)
  - RANGING cooldown/kill multiplier 변경 후 관련 테스트 자동 동기화 미흡
- **작업**:
  - `tests/test_walk_forward.py`에 `BundleOOSResult.avg_oos_mdd` 계산 검증 테스트 추가
  - `tests/test_risk.py`, `tests/test_risk_manager.py` RANGING 관련 테스트 전체 점검
  - avg_oos_mdd=None (fold 없음), avg_oos_mdd=0.05 (fold 있음) 두 케이스 커버

#### C(데이터): enrich_indicators VWAP 버그 수정 검토

- **배경**: Cycle 343에서 발견된 cumulative VWAP 버그 (vwap vs vwap20 편차 -59%)
  - `scripts/run_bundle_oos.py`의 `enrich_indicators()`에서 `df["vwap"]` = 기간 전체 누적
  - 현재: paper_sim 전략 중 `vwap`을 직접 사용하는 전략 없어 영향 미미
- **작업**:
  - `vwap` vs `vwap20`(rolling-20) 사용 전략 전수 확인 (grep)
  - cumulative VWAP를 rolling VWAP(20)로 교체 시 영향 평가
  - 교체가 합리적이면 `enrich_indicators()` 수정 (단독 실험 원칙)

#### F(리서치): cmf 1h 신호 노이즈 감소 — min_hold_bars 실험 검토

- **배경**: Cycle 344 F분석: cmf 4h Sharpe=2.508 vs 1h Sharpe=-1.23
  - 1h에서 68 trades (4h 17 trades의 4배) → 신호 과다 구조 확인
  - 신호 억제 방법: min_hold_bars 증가로 연속 신호 차단 가능성
- **작업**:
  - 현재 paper_sim의 `min_hold_bars` 설정 확인 (현재 0=비활성)
  - min_hold_bars=4 (4봉=4h 최소 대기) 실험 설계
    - 예상: cmf trades 68→~17, 4h와 유사한 신호 밀도 확보
    - 단독 실험 원칙: min_hold_bars만 변경
  - 실험 전 반드시 기존 전략들의 영향도 평가 (roc_ma_cross 등 영향 없어야 함)

### ⚠️ 주의 사항 (Cycle 345)

- **max_hold_candles_override=48 유지**: paper_simulation.py engine에 고정
- **BUNDLE_STRATEGY_OVERRIDES 임계값 변경 금지**: 1h 연간화 기준 캘리브레이션됨
- **atr_multiplier_tp=3.5 유지**: Cycle 338 실험으로 확정
- **2단계 손실 스케일링 유지**: threshold=5 기준 2→75%, 5→50%
- **슬리피지 임계값 변경 금지**: `atr_ratio < 0.03 * tf_scale`
- **PAPER_SIM_REGIME_FILTER**: `set()` (빈 집합) — 유지
- **새 전략 파일 생성 금지**: 355개 이상 추가 금지
- **합성 데이터 실험 금지**: 반드시 `--csv-dir data/historical` 사용

### 핵심 메트릭 (Cycle 344 확정)

| 지표 | Cycle 343 | Cycle 344 | 변화 |
|------|-----------|-----------|------|
| price_cluster Sharpe | 0.87 | **0.87** | 유지 |
| price_cluster Consistency | 1/8 | **1/8** | 유지 |
| roc_ma_cross Sharpe | 0.34 | **0.34** | 유지 |
| roc_ma_cross Consistency | 2/8 | **2/8** | 유지 |
| 1h PASS 수 | 0/20 (23연속) | **0/20 (24연속)** | — |
| Bundle OOS PASS | 5/5 | **5/5** | 유지 ✅ |
| Bundle OOS avg_oos_mdd 노출 | ✗ | **✅** | 신규 |

### Cycle 344 코드 변경 요약

| 파일 | 변경 내용 |
|------|----------|
| `src/backtest/walk_forward.py` | BundleOOSResult.avg_oos_mdd 추가, validate()에서 계산, summary()에 출력 |
| `scripts/run_bundle_oos.py` | format_summary_table()에 Avg OOS MDD 컬럼 추가 |
| `scripts/paper_simulation.py` | 창별 Slip_High% 컬럼 추가 (VERBOSE_WINDOWS 모드) |
| `tests/test_risk.py` | RANGING cooldown 테스트 기대값 3600.0→4320.0 수정 |
| `tests/test_risk_manager.py` | unknown regime 테스트를 SIDEWAYS로 수정, RANGING 1.2cap 테스트 2건 추가 |

### IS/OOS 레짐 진단 결과 (Cycle 340 신규)

| Window | IS end-state | OOS dominant | mkt | price_cluster | roc_ma_cross |
|--------|-------------|--------------|-----|---------------|--------------|
| W1 | TREND_UP | TREND_UP | bull | -1.43 FAIL | 4.04 PASS |
| W2 | TREND_UP | RANGING | bull | 0.11 FAIL | 3.84 PASS |
| W3 | RANGING | RANGING | bear | 0.00 FAIL | -0.04 FAIL |
| W4 | RANGING | RANGING | bear | -0.41 FAIL | -2.01 FAIL |
| W5 | RANGING | RANGING | sideways | 0.99 FAIL | -3.77 FAIL |
| W6 | RANGING | RANGING | sideways | **3.78 PASS** | -0.28 FAIL |
| W7 | RANGING | RANGING | bull | -0.08 FAIL | -1.12 FAIL |
| W8 | TREND_UP | RANGING | bull | 0.21 FAIL | -2.05 FAIL |

- price_cluster 최적 환경: RANGING+RANGING+sideways (W6)
- roc_ma_cross 최적 환경: IS=TREND_UP + bull market momentum (W1, W2)

### Cycle 344 F(리서치): 4h PASS vs 1h FAIL 구조 분석 결과

| 전략 | 4h Sharpe (Bundle OOS) | 1h Sharpe (paper_sim) | 1h Trades | 4h avg Trades |
|------|------------------------|----------------------|-----------|---------------|
| cmf | 2.508 | -1.23 | 68 | 17 |
| order_flow_imbalance_v2 | 4.345 | -0.77 | 67 | 14 |
| supertrend_multi | 3.892 | (미포함) | - | 7.6 |

**원인**:
1. 신호 밀도 4-5배 증가 (4h → 1h) → 노이즈 비율 급증
2. 1h 8개 윈도우 전부 RANGING → 추세추종 구조적 불리
3. 1h 거래비용 누적: 68×0.16% ≈ 11% vs 4h 14×0.16% ≈ 2.2%
4. 1h ATR 더 작음 → SL/TP 범위 좁음 → 노이즈로 SL 빈번

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: real CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows, 갭 없음)
- ETH/SOL: synthetic CSV (data/historical/synthetic/) — NaN 없음, OHLC 정상
- Bundle OOS: `--csv-dir data/historical` 필수 (합성 데이터 run은 리포트 덮어쓰기 방지됨)
- Paper simulation 1h: **20 전략** × 8 windows → 약 6분 소요 (BTC only)

### BUNDLE_STRATEGY_INIT_PARAMS 현재 설정 (Cycle 340 변경 없음)
- `vwap_cross: {}` ← 기본 파라미터
- `supertrend_multi: {atr_threshold=0.5, atr_threshold_max=1.5, ema_filter=True, confidence_filter=True, rsi_ob_filter=True, rsi_ob_threshold=80, trend_confirm_bars=2, cmf_confirm=False}` ← 고정
- `order_flow_imbalance_v2: {"trend_span": 20}` ← 최적 확정 (delta_window=10 기본값)

### BUNDLE_STRATEGY_OVERRIDES 현재 설정 (Cycle 330 변경 없음)
- `cmf: {"min_wfe": 0.4, "sharpe_decay_max": 0.40}`
- `supertrend_multi: {"min_oos_trades": 3, "max_oos_sharpe_std": 3.0, "regime_transition_is_min": 2.0}`
- `order_flow_imbalance_v2: {"regime_transition_is_min": 2.0, "min_oos_trades": 3}`
- `vwap_cross: {"min_oos_trades": 3, "is_negative_regime_max": -2.0, "bear_oos_max": 1.0}` ← 고정
- `value_area: {"regime_transition_is_min": 2.0, "min_oos_trades": 5, "is_negative_regime_max": -1.4}` ← 유지

### PAPER_SIM_STRATEGY_PARAMS 현재 설정 (Cycle 340 변경 없음)
- `value_area: {"vol_filter_mult": 0.5}` (1h paper_sim에서 제외됨)
- `wick_reversal: {"min_volatility": 0.001, "vol_mult": 0.6}`
- `relative_volume: {"rvol_buy_sell": 1.2}`
- `momentum_quality: {"quality_score_buy_threshold": 0.8, "consistency_buy_threshold": 0.3}`
- `order_flow_imbalance_v2: {"trend_span": 20}` ← Cycle 337 D(ML) 복원
- `cmf: {"buy_thresh": 0.10}`

### PAPER_SIM_REGIME_FILTER 현재 설정 (Cycle 339 롤백 유지)
- `set()` ← 빈 집합 (레짐 필터 비활성화)
- 이유: 개별 봉 수준 TREND_UP 필터 → roc_ma_cross trades 57→18, Sharpe +0.32→-0.43 역효과 확인

### 핵심 메트릭 (Cycle 338: MAX_HOLD 분리 아키텍처, 유지)

| 구분 | max_hold_candles | 설정 위치 |
|------|-----------------|---------|
| 1h paper_sim | 48봉 (48시간) | `paper_simulation.py`: `max_hold_candles_override=48` |
| 4h Bundle OOS | 24봉 (96시간=4일) | `BacktestEngine` 기본값 `MAX_HOLD_CANDLES=24` |
| 기타(테스트 등) | 24봉 | `BacktestEngine` 기본값 |
