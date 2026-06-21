# Next Steps

_Last updated: 2026-06-21 (Cycle 338 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 338

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 336 | B+D+F | MAX_HOLD=48 실험(Sharpe 전 전략 개선), OFI buy_thresh=0.30(BTC개선/ETH악화), 0/20 PASS 16연속 |
| 337 | B+D+F | max_hold_candles_override=48(1h전용), OFI buy_thresh복원, 5/5 Bundle PASS 유지, 0/20 17연속 |
| 338 | C+B+F | TP=2.5 역효과 확인(TP=3.5 확정), 2단계 손실스케일링 추가, 윈도우별 레짐 분석, 0/20 18연속 |

### 🎯 Cycle 339 작업 방향 (339 mod 5 = 4 → D(ML) + E(실행) + F(리서치))

#### D(ML): 레짐 기반 시그널 필터링 실험

- **배경**: Cycle 338 F(리서치) 핵심 발견 — 18사이클 0/20 PASS의 근본 원인은 시장 국면 불일치
  - roc_ma_cross: W1-W2(초기 bull) 완벽하지만 W3-W8(이후 모든 국면) 전부 FAIL
  - price_cluster: W6(sideways), W8(bull) PASS, 나머지 구간 FAIL
  - 두 전략의 PASS 구간이 달라 portfolio 효과도 제한적
- **작업**: MarketRegimeDetector 기반 1h 레짐 레이블 분석
  - `src/strategy/regime.py` `MarketRegimeDetector.detect()` 8개 윈도우에 적용
  - W1(bull/early): ADX는 얼마? W5(sideways): ADX < 22 확인?
  - 목표: PASS 윈도우에서 ADX 패턴 발견 → 필터 기준값 도출
- **제약**: 전략 파일 생성/수정 금지. 실험은 paper_simulation.py의 PAPER_SIM_STRATEGY_PARAMS로만

#### E(실행): 실행 품질 점검

- **배경**: 2단계 손실 스케일링(Cycle 338 B)이 MDD를 낮췄지만 일부 전략은 Sharpe도 낮아짐
- **작업**: 슬리피지 레짐 분포 재분석
  - adaptive_slippage=True 상태에서 high-slippage 비율이 높은 전략 식별
  - roc_ma_cross ETH: 62.7% High slippage — 이게 ETH 성능 열화의 얼마나 기여?
  - price_cluster BTC: 12.2% High, ETH: 11.5% High → 유사함에도 성능 차이 큼
  - ETH 성능 열화는 synthetic 데이터 특성(평균복귀 성향 강함)이 더 큰 원인

#### F(리서치): 레짐 전환 시점 예측 리서치

- **배경**: roc_ma_cross W3부터 급격한 성능 하락 — 2023년 5월 bull→bear 전환 시점
- **작업**: 레짐 전환 조기 감지 방법론 리서치
  - ADX 방향성 변화 (ADX 상승 vs 하락으로 추세 강화/약화 감지)
  - VIX 유사 지표 (암호화폐 implied volatility) 활용 가능성
  - 결과를 PAPER_SIM_STRATEGY_PARAMS에 반영 가능한 형태로 정리

### ⚠️ 주의 사항 (Cycle 339)

- **max_hold_candles_override=48 유지**: `paper_simulation.py` engine에 고정, 절대 제거 금지
  - Bundle OOS engine에는 전달 안 함 (RollingOOSValidator → BacktestEngine 기본값 24 유지)
- **BUNDLE_STRATEGY_OVERRIDES 임계값 변경 금지**: 1h 연간화 기준 캘리브레이션됨
  - `timeframe="4h"` engine 전달 금지 → Sharpe 50% 하락, 전체 임계값 무효화 확인됨
- **atr_multiplier_tp=3.5 유지**: Cycle 338 실험으로 확정. TP=2.5 역효과 확인.
- **2단계 손실 스케일링 유지**: threshold=5 기준 2→75%, 5→50%. Bundle OOS 영향 없음.
- **order_flow_imbalance_v2 현재 상태**: `{"trend_span": 20}` ← Cycle 337 D(ML) 복원
- **vwap_cross override 고정**: `{"min_oos_trades": 3, "is_negative_regime_max": -2.0, "bear_oos_max": 1.0}` 변경 금지
- **value_area override 고정**: `{"regime_transition_is_min": 2.0, "min_oos_trades": 5, "is_negative_regime_max": -1.4}` 변경 금지
- **STRATEGIES_TIMEFRAME_EXCLUDE 유지**: `"1h": {"value_area", "supertrend_multi"}` 변경 금지
- **새 전략 파일 생성 금지**: 355개 이상 추가 금지
- **합성 데이터 실험 금지**: 반드시 `--csv-dir data/historical` 사용

### 핵심 메트릭 (Cycle 338 결과)

| 지표 | Cycle 337 (1-tier 50%) | Cycle 338 (2-tier 75%/50%) | 변화 |
|------|------------------------|---------------------------|------|
| price_cluster Sharpe | 0.90 | 0.84 | -0.06 ↓ |
| price_cluster MDD | 10.8% | 9.8% | -1.0%p ↓ (better) |
| price_cluster Consistency | 2/8 | 1/8 | -1 ↓ |
| roc_ma_cross Sharpe | 0.25 | 0.32 | +0.07 ↑ |
| roc_ma_cross MDD | 9.4% | 8.2% | -1.2%p ↓ (better) |
| 1h PASS 수 | 0/20 | 0/20 | 변화 없음 (18연속) |
| Bundle OOS PASS | 5/5 | 5/5 | 유지 ✅ |

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
- Paper simulation 1h: **20 전략** × 8 windows → 약 13분 소요 (BTC only)

### BUNDLE_STRATEGY_INIT_PARAMS 현재 설정 (Cycle 338 변경 없음)
- `vwap_cross: {}` ← 기본 파라미터
- `supertrend_multi: {atr_threshold=0.5, atr_threshold_max=1.5, ema_filter=True, confidence_filter=True, rsi_ob_filter=True, rsi_ob_threshold=80, trend_confirm_bars=2, cmf_confirm=False}` ← 고정
- `order_flow_imbalance_v2: {"trend_span": 20}` ← 최적 확정 (delta_window=10 기본값)

### BUNDLE_STRATEGY_OVERRIDES 현재 설정 (Cycle 330 변경 없음)
- `cmf: {"min_wfe": 0.4, "sharpe_decay_max": 0.40}`
- `supertrend_multi: {"min_oos_trades": 3, "max_oos_sharpe_std": 3.0, "regime_transition_is_min": 2.0}`
- `order_flow_imbalance_v2: {"regime_transition_is_min": 2.0, "min_oos_trades": 3}`
- `vwap_cross: {"min_oos_trades": 3, "is_negative_regime_max": -2.0, "bear_oos_max": 1.0}` ← 고정
- `value_area: {"regime_transition_is_min": 2.0, "min_oos_trades": 5, "is_negative_regime_max": -1.4}` ← 유지

### PAPER_SIM_STRATEGY_PARAMS 현재 설정 (Cycle 338 변경 없음)
- `value_area: {"vol_filter_mult": 0.5}` (1h paper_sim에서 제외됨)
- `wick_reversal: {"min_volatility": 0.001, "vol_mult": 0.6}`
- `relative_volume: {"rvol_buy_sell": 1.2}`
- `momentum_quality: {"quality_score_buy_threshold": 0.8, "consistency_buy_threshold": 0.3}`
- `order_flow_imbalance_v2: {"trend_span": 20}` ← Cycle 337 D(ML) 복원 (0.30→0.25 기본값)
- `cmf: {"buy_thresh": 0.10}`

### 윈도우별 성능 분석 (Cycle 338 F(리서치) 결과, TP=3.5 기준)

| Window | Market | price_cluster | roc_ma_cross |
|--------|--------|---------------|--------------|
| W1 | bull | Sharpe=-0.55 ❌ | Sharpe=4.39 ✅ |
| W2 | bull | Sharpe=-0.05 ❌ | Sharpe=3.51 ✅ |
| W3 | bear | Sharpe=-0.12 ❌ | Sharpe=0.20 ❌ |
| W4 | bear | Sharpe=0.62 ❌ | Sharpe=-0.45 ❌ |
| W5 | sideways | Sharpe=0.98 ❌ | Sharpe=-3.91 ❌ |
| W6 | sideways | Sharpe=3.17 ✅ | Sharpe=0.28 ❌ |
| W7 | bull | Sharpe=0.94 ❌ | Sharpe=0.26 ❌ |
| W8 | bull | Sharpe=2.23 ✅ | Sharpe=-2.25 ❌ |

- 레짐 의존성: price_cluster ↔ late sideways/bull | roc_ma_cross ↔ early strong bull only
- roc_ma_cross W5 -3.91: 횡보장 whipsaw 재발 방지 → ADX 필터 탐색 필요 (Cycle 339 D(ML))
