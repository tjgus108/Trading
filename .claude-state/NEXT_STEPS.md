# Next Steps

_Last updated: 2026-06-23 (Cycle 345 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 345

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 343 | C+B+F | BTC CSV 품질확인, RANGING kill 1.5→1.2, avg_oos_mdd 추가, 0/20 24연속 |
| 344 | D+E+F | BundleOOSResult.avg_oos_mdd 필드화, SlipH% window진단, 슬리피지 무관 확인, 0/20 24연속 |
| 345 | A+C+F | ema20_slope 동기화 버그 수정, price_cluster WFO 그리드 수정, 0/20 25연속 |

### 🎯 Cycle 346 작업 방향 (346 mod 5 = 1 → B(리스크) + D(ML) + F(리서치))

#### B(리스크): RANGING 매크로 방향성 필터 탐색

- **배경**: Cycle 345 F(리서치) 분석 결과 — price_cluster FAIL 원인 확정
  - RANGING micro + neutral macro(W6 mkt=sideways) → PASS (Sharpe=3.78)
  - RANGING micro + directional macro(W2-W5 bull/bear) → FAIL
  - 매크로 방향성 중립 여부가 mean-reversion PF≥1.5의 핵심 변수
- **작업**:
  - `src/risk/drawdown_monitor.py`의 RANGING 레짐 처리 검토
  - 매크로 방향성 중립 판별: ema50 slope magnitude 임계값 탐색
  - PAPER_SIM_STRATEGY_PARAMS에 price_cluster bounce_pct=0.010 명시적 등록 검토

#### D(ML): narrow_range ema_slope 필터 효과 검증

- **배경**: Cycle 345 C(데이터)에서 paper_sim에 ema20_slope 추가됨
  - narrow_range 전략이 이제 paper_sim에서도 EMA slope 필터 적용
  - WFO DEFAULT_GRIDS: ema_slope_min_buy=[0.0, 0.001, 0.002]
  - 기본값 0.0 → 필터 비활성 (paper_sim은 기본 params 사용)
- **작업**:
  - PAPER_SIM_STRATEGY_PARAMS에 narrow_range: {"ema_slope_min_buy": 0.001} 추가 실험 검토
  - 단, ema_slope=0.001 필터가 BTC 1h에서 RANGING 기간 BUY를 얼마나 차단하는지 먼저 확인
  - ML 신호 품질: `src/backtest/walk_forward.py` is_oos_pearson 값 분석 (plateau_score와 함께)

#### F(리서치): 1h PASS 전략 실존 여부 재탐색

- **배경**: 25연속 0/20 FAIL → 1h 시장 구조 자체가 PF≥1.5 달성을 막는지 확인 필요
  - 4h Bundle OOS 5/5 PASS → 동일 전략이 4h에선 작동
  - 1h timeframe 구조적 한계: 수수료 상대비중, RANGING 비율 75%
- **작업**:
  - 레짐별 수익 분해: bull 창(W1)에서 어떤 1h 전략이 Sharpe≥1.0 달성하는가?
  - W1(TREND_UP→TREND_UP, mkt=bull): roc_ma_cross PASS 4.04 → 이 창에서 다른 트렌드 추종 전략 탐색
  - Bundle OOS의 vwap_cross가 1h paper_sim rank로 진입 가능성 분석 (기본 파라미터 사용 중)

### ⚠️ 주의 사항 (Cycle 346)

- **max_hold_candles_override=48 유지**: paper_simulation.py engine에 고정
- **BUNDLE_STRATEGY_OVERRIDES 임계값 변경 금지**: 1h 연간화 기준 캘리브레이션됨
- **atr_multiplier_tp=3.5 유지**: Cycle 338 실험으로 확정
- **2단계 손실 스케일링 유지**: threshold=5 기준 2→75%, 5→50%
- **슬리피지 임계값 변경 금지**: Cycle 344 확인 → HIGH% < 1%, 동적 조정 불필요
- **PAPER_SIM_REGIME_FILTER**: `set()` (빈 집합) — 유지
- **새 전략 파일 생성 금지**: 355개 이상 추가 금지
- **합성 데이터 실험 금지**: 반드시 `--csv-dir data/historical` 사용

### 핵심 메트릭 (Cycle 345 확정)

| 지표 | Cycle 344 | Cycle 345 | 변화 |
|------|-----------|-----------|------|
| price_cluster Sharpe | 0.87 | **0.87** | 유지 |
| price_cluster Consistency | 1/8 | **1/8** | 유지 |
| roc_ma_cross Sharpe | 0.34 | **0.34** | 유지 |
| roc_ma_cross Consistency | 2/8 | **2/8** | 유지 |
| 1h PASS 수 | 0/20 (24연속) | **0/20 (25연속)** | — |
| Bundle OOS PASS | 5/5 | **5/5** | 유지 ✅ |
| Bundle OOS OFI Sharpe | 4.345 | **4.345** | 유지 |

### Cycle 345 코드 변경 요약

| 파일 | 변경 내용 |
|------|----------|
| `scripts/paper_simulation.py` | enrich_indicators()에 ema20_slope 추가 (feed.py 동기화) |
| `src/backtest/walk_forward.py` | price_cluster DEFAULT_GRIDS bounce_pct [0.020,0.025,0.030]→[0.010,0.020,0.025] |

### F(리서치) RANGING 패턴 진단 결과 (Cycle 345 확정)

| 창 | mkt | IS end | OOS dominant | price_cluster | 원인 분석 |
|----|-----|--------|--------------|--------------|---------|
| W1 | bull | TREND_UP | TREND_UP | -1.43 FAIL | 추세장, mean-reversion 역방향 |
| W2 | bull | TREND_UP | RANGING | 0.11 FAIL | 매크로 상승 중 RANGING → bounce 하한 선매수 약세 |
| W3 | bear | RANGING | RANGING | 0.00 FAIL | 하락 RANGING → 하단 bounce 실패 |
| W4 | bear | RANGING | RANGING | -0.41 FAIL | 하락 RANGING → 하단 bounce 실패 |
| W5 | sideways | RANGING | RANGING | 0.99 FAIL | sideways지만 변동성↑, PF 미달 |
| W6 | sideways | RANGING | RANGING | **3.78 PASS** | **neutral macro + RANGING = bounce 성공** |
| W7 | bull | RANGING | RANGING | -0.08 FAIL | 상승 재개 중 RANGING → bounce 하한 위험 |
| W8 | bull | TREND_UP | RANGING | 0.21 FAIL | TREND_UP 후 RANGING 전환, 방향 불명확 |

**핵심 결론**: W6만 sideways(중립) 매크로 + RANGING micro → mean-reversion 작동
W5도 sideways지만 변동성이 높아 PF 미달 (W5 vol=1.39% vs W6 추정 낮음)

### E(실행) 슬리피지 진단 결과 (Cycle 344 확정)

| 지표 | BTC 1h 전체 평균 |
|------|----------------|
| HIGH 레짐 비율 | 0~8% (최대 dema_cross 8.3%) |
| 동적 슬리피지 조정 필요성 | **없음** |

### Bundle OOS avg_oos_mdd (Cycle 344 확정)

| 전략 | avg_oos_mdd |
|------|-------------|
| cmf | 5.2% |
| order_flow_imbalance_v2 | 4.9% → Cycle 345: 4.85% |
| supertrend_multi | 3.1% → Cycle 345: 3.14% |
| vwap_cross | 2.4% → Cycle 345: 2.39% |
| value_area | 2.9% → Cycle 345: 2.92% |

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

### 핵심 메트릭 (Cycle 338: MAX_HOLD 분리 아키텍처, 유지)

| 구분 | max_hold_candles | 설정 위치 |
|------|-----------------|---------|
| 1h paper_sim | 48봉 (48시간) | `paper_simulation.py`: `max_hold_candles_override=48` |
| 4h Bundle OOS | 24봉 (96시간=4일) | `BacktestEngine` 기본값 `MAX_HOLD_CANDLES=24` |
| 기타(테스트 등) | 24봉 | `BacktestEngine` 기본값 |

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- BTC: real CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows, 갭 없음)
- ETH/SOL: synthetic CSV (data/historical/synthetic/) — NaN 없음, OHLC 정상
- Bundle OOS: `--csv-dir data/historical` 필수 (합성 데이터 run은 리포트 덮어쓰기 방지됨)
- Paper simulation 1h: **20 전략** × 8 windows → 약 6분 소요 (BTC only)
