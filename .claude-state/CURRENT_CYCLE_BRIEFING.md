# Current Cycle Briefing

_Cycle 336 | 2026-06-20 | B(리스크) + D(ML) + F(리서치)_

## 완료된 작업

### B(리스크): MAX_HOLD_CANDLES=24 vs 48 실험

- BTC 1h 실데이터로 close_reason 분포 측정 (engine.py 기존 필드 활용):
  - price_cluster: max_hold% 12%→3%, Sharpe +0.498, PF +0.100, MDD +0.5%p
  - roc_ma_cross: max_hold% 18%→5%, Sharpe +0.665, PF +0.120, MDD -6.4%p
  - positional_scaling: max_hold% 17%→4%, Sharpe +0.295, PF +0.051, MDD -4.5%p
  - tp% 전 전략 +7~8%p (TP 도달 기회 증가 — MAX_HOLD 억제 효과 확인)
  - 세 전략 모두 여전히 FAIL (PF<1.5, MDD>20% 일부)
- **결론**: MAX_HOLD=48 권장 → Cycle 337 B에서 engine.py 실제 변경 + Paper Sim 재실행 예정
- 코드 변경 없음 (실험만 수행)

### D(ML): OFI v2 buy_thresh=0.30 1h Paper Sim 실험

- `scripts/paper_simulation.py` PAPER_SIM_STRATEGY_PARAMS 변경:
  - `order_flow_imbalance_v2: {"trend_span": 20, "buy_thresh": 0.30, "sell_thresh": -0.30}`
- BTC 결과: rank10(Sharpe=-0.83, PF=0.95, 73trades) → rank5(Sharpe=-0.64, PF=1.04, 70trades) **개선**
- ETH 결과: rank15(Sharpe=-2.40, PF=0.74) **악화**
- SOL 결과: rank3(Sharpe=0.01, PF=1.04) 중립
- **결론**: BTC 개선/ETH 악화 복합 결과 → Cycle 337 D에서 ETH 악화 원인 분석 후 결정

### F(리서치): 구조적 FAIL 원인 분석

- 16사이클 연속 0/20 PASS:
  - 주요 원인: SL=5%, TP=2% → 손절 우세 구조 (2.5:1 역R:R)
  - 평균 WR 37~40%에서 PF>1.5 달성 어려움 (최소 WR ≈ 60% 필요)
  - MAX_HOLD 강제청산 추가 악화 (12-18% 거래)
- 다음 실험 후보: SL/TP 비율 재검토 (SL=2%, TP=4% = 1:2 리스크리워드)

## 시뮬레이션 결과 (Cycle 336)

- **테스트**: 8425 passed, 23 skipped (회귀 없음)

- **Paper Sim BTC 1h (20전략, 8 windows, buy_thresh=0.30 적용)**: **0/20 PASS** (16사이클 연속)
  - rank1: price_cluster (Sharpe=0.34, Return=+2.19%, PF=1.11, 1/8)
  - rank2: roc_ma_cross (Sharpe=-0.41, PF=1.10, 2/8)
  - rank3: positional_scaling (Sharpe=0.00, PF=1.18, 1/8)
  - rank5: order_flow_imbalance_v2 (Sharpe=-0.64, PF=1.04, 70trades, 1/8) ← 이전 rank10 대비 개선
  - 주요 FAIL 원인: profit_factor < 1.5 (전체)

- **Bundle OOS BTC 4h**: **5/5 PASS** ← 유지
  - rank1: order_flow_imbalance_v2 (avg=4.345, std=0.907)
  - rank2: supertrend_multi (avg=3.892, std=1.239)
  - rank3: value_area (avg=3.069, std=0.085)
  - rank4: vwap_cross (avg=3.047, std=1.437)
  - rank5: cmf (avg=2.508, std=1.888)

## 다음 사이클 (337 mod 5 = 2): B(리스크) + D(ML) + F(리서치)

- **B(리스크)**: engine.py `MAX_HOLD_CANDLES = 24` → `48` 실제 변경 + Paper Sim 전체 재실행
- **D(ML)**: OFI v2 ETH 악화 원인 분석 → buy_thresh=0.30 유지 or 복원 결정
- **F(리서치)**: SL/TP 비율 재검토 (SL=2%, TP=4% 실험 가능성 탐색)
