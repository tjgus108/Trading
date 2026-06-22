# Current Cycle Briefing

_Cycle 342 | 2026-06-22 | B(리스크) + D(ML) + F(리서치)_

## 완료된 작업

### B(리스크): loss_scale 집계를 paper_simulation 보고서에 연결

Cycle 341에서 추가한 `loss_scale_half_count`/`loss_scale_full_count` (engine.py) 를
paper_simulation.py 보고서에 완전 연결:

**`scripts/paper_simulation.py` 변경**:
- `window_results` dict에 `loss_scale_half_count`, `loss_scale_full_count` 필드 추가
  ```python
  "loss_scale_half_count": getattr(bt, "loss_scale_half_count", 0),
  "loss_scale_full_count": getattr(bt, "loss_scale_full_count", 0),
  ```
- 전략별 전체 집계: `total_loss_scale_half_count`, `total_loss_scale_full_count`
- 보고서에 "2단계 손실 스케일 적용 현황" 테이블 추가:
  - Half(75%) = 연속손실≥2 시 적용 횟수
  - Full(50%) = 연속손실≥5 시 적용 횟수
  - 비율(full/half) = 손실 스케일 강도 지표

### D(ML): IS/OOS Pearson 상관계수 WalkForwardResult에 추가

**`src/backtest/walk_forward.py` 변경**:
- `WalkForwardResult` 데이터클래스에 `is_oos_pearson: Optional[float]` 필드 추가
  ```python
  # IS/OOS Pearson: fold별 IS Sharpe와 OOS Sharpe 간 Pearson 상관계수
  # 양수(특히 > 0.3)이면 IS 성능이 OOS를 예측 → 과최적화 낮음
  # 음수이면 IS 최적화가 OOS를 역방향 예측 → 심각한 과최적화 신호
  is_oos_pearson: Optional[float] = None
  ```
- `WalkForwardOptimizer.run()`에서 fold 수 ≥3 시 계산 (표준 Pearson)
- `summary()` 출력에 태그: PREDICTIVE(>0.3) / ANTI(<-0.1) / WEAK

### F(리서치): RANGING 시장 0 PASS 원인 분석

핵심 발견:
1. BTC 1h 8개 윈도우 중 75%(6/8)이 RANGING → trend-following 전략 구조적 불리
2. WFO 레짐 변화 지연: IS=TREND_UP 최적화 후 OOS=RANGING 전환 시 성능 역전
3. 저변동성(W5: vol=0.054) 구간에서 슬리피지가 PF를 0.5~1.0 침식
4. 현재 고정 슬리피지 모델은 변동성 조건을 미반영 → 개선 여지

## 시뮬레이션 결과

### Paper Simulation (1h, 8-fold, BTC only)
- **PASS: 0/20** (22연속)
- Top: price_cluster (Sharpe=0.87, PF=1.20, 1/8), roc_ma_cross (0.34, 1.22, 2/8)
- 주요 FAIL: profit_factor < 1.5 (전체 FAIL의 40%+)

### Bundle OOS (4h, BTC/USDT)
- **PASS: 5/5** — cmf, order_flow_imbalance_v2, supertrend_multi, vwap_cross, value_area
- #1 order_flow_imbalance_v2 (Score=62.0, OOS Sharpe=4.345)

## 테스트 결과

- 8425 passed, 23 skipped (전체 회귀 없음)
- walk_forward + engine 테스트 130개 통과 확인

## 다음 사이클 (343) 방향

343 mod 5 = 3 → **C(데이터) + B(리스크) + F**

1. C(데이터): BTC 1h CSV 품질 점검 (스파이크, 갭, ATR0 빈도)
2. B(리스크): loss_scale 창별 분포 vs Sharpe 상관관계 분석 (새로 추가된 데이터 활용)
3. F(리서치): RANGING 시장에서 PF≥1.5 달성 전략 케이스 스터디
