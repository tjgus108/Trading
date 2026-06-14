# Next Steps

_Last updated: 2026-06-14 (Cycle 310 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 310

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 308 | C+B+F | CMFStrategy warmup 버그 수정, DrawdownMonitor WARN 히스테리시스 추가 |
| 309 | D+E+F | cmf buy_thresh=0.10 실험(미미한 개선), 슬리피지 레짐 추적 추가 |
| 310 | A+C+F | cmf period=40 역효과 확정, NR ema_slope 필터 구현, slippage_regime 리포트 인프라 |

### 🎯 Cycle 311 작업 방향 (311 mod 5 = 1 → B(리스크) + D(ML) + F(리서치))

#### B(리스크): BUNDLE_STRATEGY_INIT_PARAMS narrow_range 업데이트
- **Cycle 310 C(데이터) 구현 완료**: ema_slope_min_buy/max_sell 파라미터 추가 완료
  - `run_bundle_oos.py enrich_indicators()`: ema20_slope 추가 완료 (다음 Bundle OOS부터 적용)
  - 다음 Bundle OOS에서 narrow_range ema_slope 필터 효과 검증 필요
  - 현재 BUNDLE_STRATEGY_INIT_PARAMS: `{"trend_regime_filter": True, "atr_trend_max": 1.1}` (비효율 확정)
  - **제안**: `{"trend_regime_filter": False, "ema_slope_min_buy": 0.0, "ema_slope_max_sell": 0.0}` 로 변경
  - 근거: atr_trend_max 비효율 확정 (Cycle307), ema_slope_min_buy=0.0 = 음수 slope에서 BUY 차단
  - ⚠️ 단독 실험 원칙: trend_regime_filter=False + ema_slope만 변경

#### D(ML): cmf 1h 개선 방향 전환
- **Cycle 310 A(품질) 결론**: period=40 역효과 (Sharpe -1.21→-2.33)
  - period 길이는 cmf 1h 문제의 핵심이 아님
  - **새 가설**: 1h cmf가 횡보 구간에서 과다 신호 → 볼륨 필터 추가
  - **실험 제안**: `cmf: {"period": 20, "buy_thresh": 0.10, "vol_percentile": 0.80}` (vol 기준 강화)
  - 또는 전혀 다른 접근: cmf는 4h에서만 사용하고 1h paper_sim에서 제외 검토
  - ⚠️ PAPER_SIM_STRATEGY_PARAMS 원복 필요: period=40→20 (역효과 확정)

#### F(리서치): slippage_regime_counts 분포 첫 실측 분석
- **Cycle 310 F 구현 완료**: paper_simulation 리포트에 슬리피지 레짐 섹션 추가
  - 다음 paper_sim 결과에 슬리피지 레짐 분포 (low/normal/high) 등장 예정
  - **분석 포인트**: price_cluster (MDD=12.2%) high regime 비율이 높으면 슬리피지 핵심 원인
  - supertrend_multi vs price_cluster 레짐 분포 비교
  - high% > 30%이면 adaptive_slippage 튜닝 또는 고변동성 필터 강화 검토

### ⚠️ 주의 사항 (Cycle 311)
- **PAPER_SIM_STRATEGY_PARAMS 현재 설정** (Cycle 310 변경):
  - `cmf: {"period": 40, "buy_thresh": 0.10}` ← **Cycle 310 A(품질) 역효과 확정 → 원복 필요**
    - 원복: `{"period": 20, "buy_thresh": 0.10}` (vol_percentile 실험 병행 가능)
  - 나머지: value_area, wick_reversal, relative_volume, momentum_quality, price_cluster, order_flow_imbalance_v2 동일
- **신규 구현 (Cycle 310 C)**:
  - NarrowRangeStrategy.ema_slope_min_buy/max_sell (기본값=0.0)
  - feed.py + paper_sim + bundle_oos enrich_indicators에 ema20_slope 추가
  - 다음 Bundle OOS에서 narrow_range ema_slope 효과 자동 적용
- **Bundle OOS 실행 옵션**:
  - `--csv-dir data/historical`: 5-fold (2023~2024, 이전 사이클과 비교 가능)
  - 옵션 없음: 9-fold (2022~2024 거래소 실데이터, 더 엄격한 검증)
  - Cycle 311부터는 두 방식을 명시적으로 구분하여 실행
- **단독 실험 원칙**: 두 파라미터를 동시에 변경하면 역효과 원인 특정 불가

### 핵심 메트릭 (Cycle 310)
- 테스트: **8400 passed, 23 skipped** (회귀 없음)
- Paper Sim BTC 1h (8 windows): **0/22 PASS**
  - price_cluster: rank1 score=75.7 (안정, 3/8 PASS)
  - supertrend_multi: rank2 score=68.3 (안정, 2/8 PASS)
  - narrow_range: rank7 score=56.5 Sharpe=-0.42 (ema_slope 필터 미적용 기준치)
  - cmf: rank19 Sharpe=-2.33 trades=59 (period=40 역효과 확정)
- Bundle OOS BTC 4h (9-fold, 2022~2024): **0/5 PASS**
  - supertrend_multi: score=89.4 rank1 (5/7 유효 fold PASS)
  - narrow_range: score=64.7 OOS Sharpe std=5.184 (ema_slope 필터 적용 시 개선 예상)
  - value_area: 0 trades in all folds (근본적 신호 부족 문제)

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단 (bybit→binance→okx fallback)
- BTC: real CSV (data/historical/binance/BTCUSDT/1h.csv, 2023-01~2024-05, 12000 rows)
- ETH/SOL: synthetic CSV (data/historical/synthetic/)
- Bundle OOS: `--csv-dir data/historical` = 5-fold / 옵션없음 = 9-fold 거래소 실데이터
- Paper simulation 1h: 22 전략 × 8 windows → 약 7-10분 소요
