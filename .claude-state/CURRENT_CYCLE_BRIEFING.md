# Current Cycle Briefing

_Cycle 343 | 2026-06-22 | C(데이터) + B(리스크) + F(리서치)_

## 완료된 사이클: 343
**카테고리**: C(데이터) + B(리스크) + F(리서치)

### C(데이터): BTC 1h.csv 데이터 품질 재확인

**발견 사항**:
- OHLCV 정합성: 완벽 (스파이크 0, 갭 0, OHLC 위반 0, ATR14 0값 0)
- **합성 데이터 확인**: 시작가 20,000.0 고정, 2024-05 종가 266,400 (실제 당시 ~60-65k와 불일치)
- **cumulative VWAP 버그**: `enrich_indicators()`의 `df["vwap"]`는 12000봉 누적 가중평균 → 데이터 끝에서 -59% 편차
  - 하지만 paper_sim 20개 전략 중 `df["vwap"]` 직접 사용 전략 없음 → 현재 성능에 무영향
  - `df["vwap20"]` (rolling-20)는 정상 (0.7% 편차)
- MACD, Donchian 계산 정확성 확인 → 정상

### B(리스크): loss_scale 창별 분포 vs Sharpe 상관관계

**핵심 발견**:
- `loss_scale_full_count` vs Sharpe: **Pearson r = -0.668** (강한 음의 상관)
- W5(vol=0.0139, RANGING)가 가장 나쁨: avg_sharpe=-2.994, avg_full=9.3
- W8(vol=0.0138, TREND_UP 진입)이 가장 좋음: avg_sharpe=+0.730, avg_full=3.5
- loss_scale_full이 많이 걸리는 창 = FAIL 예측 지표로 활용 가능

**코드 변경 1** — `src/risk/drawdown_monitor.py`:
```python
REGIME_COOLDOWN_MULTIPLIERS = {
    'RANGING': 1.2,  # 1.0 → 1.2 (RANGING 손실 빈도 높음)
}
_REGIME_KILL_MULTIPLIER_MAX = {
    'RANGING': 1.2,  # 1.5 → 1.2 (하락장 수준으로 빠른 kill)
}
```

**코드 변경 2** — `src/backtest/walk_forward.py`:
- `WindowResult`에 `oos_mdd: float = 0.0` 추가 (fold별 OOS 낙폭)
- `WalkForwardResult`에 `avg_oos_mdd: Optional[float]` 추가
- `summary()` 출력에 MDD 태그 (LOW/MED/HIGH)

### F(리서치): RANGING 시장 PF≥1.5 달성 전략 패턴

**발견**:
- W3~W5 Top3: price_cluster(W5 PF=1.63 유일 PASS), lob_maker(W5 PF=1.46), frama(W4 PF=1.47)
- 공통 특징: mean-reversion 기반, HIGH confidence 필터, 짧은 홀딩(~1.4일/포지션)
- PF≥1.5 달성 조건: 평균복귀 로직 + 동적 신뢰도 필터 + 빠른 이익실현

## 시뮬레이션 결과

### Paper Simulation (1h, 8-fold, BTC only)
- **PASS: 0/20** (23연속)
- Top: price_cluster (Sharpe=0.87, PF=1.20, 1/8), roc_ma_cross (0.34, 1.22, 2/8)
- 주요 FAIL: profit_factor < 1.5 (전체 FAIL의 40%+)

### Bundle OOS (4h, BTC/USDT)
- **PASS: 5/5** — cmf, order_flow_imbalance_v2, supertrend_multi, vwap_cross, value_area
- #1 order_flow_imbalance_v2 (Score=62.0, OOS Sharpe=4.345, PF=1.941)

## 테스트 결과

- 162 passed (drawdown_monitor + walk_forward 회귀 없음)
- drawdown_monitor 변경 후 기존 테스트 전체 통과
- walk_forward 변경 후 기존 테스트 전체 통과

## 다음 사이클 (344) 방향

344 mod 5 = 4 → **D(ML) + E(실행) + F**

1. D(ML): mean-reversion ML 신호 실험, `avg_oos_mdd` 필드 Bundle OOS 노출
2. E(실행): W5 저변동성 구간 슬리피지 레짐 분포 확인 (low/normal/high 비율)
3. F(리서치): 4h Bundle OOS 전략이 1h RANGING에서 실패하는 구조적 이유 분석
