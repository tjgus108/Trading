======================================================================
🔄 CYCLE 244 — 2026-05-29
======================================================================

## 이번 사이클 배정 카테고리

**Cycle 244** (244 mod 5 = 4 → D(ML) + E(실행) + F(리서치))

---

### [D] ML — 완료
- **WFE 역방향 신호 수정** (`walk_forward.py` + `engine.py`)
  - IS < -1.0 + OOS > 0 케이스: WFE = 1.0 → **0.0** (fold FAIL 처리)
  - elder_impulse fold1(IS=-2.859, OOS=+3.794): 이전 PASS → **FAIL**
  - wick_reversal 역방향 fold들도 FAIL 처리됨
- **`compute_ensemble_weight_recency()` fold_direction 지원** (`trainer.py`)
  - `fold_sharpes: Optional[List[tuple]]` 파라미터 추가
  - `sign_reversal_penalty=0.3`: IS < -1.0 + OOS > 0 fold 가중치 30%로 감소

### [E] 실행 — 완료
- **`avg_slippage_per_trade` 필드 추가** (`engine.py`)
  - `BacktestResult.avg_slippage_per_trade = total_slippage_cost / total_trades`
  - `summary()` 출력에 포함

### [F] Research — 완료
- **IS→OOS 역전 케이스 결론**: GBM 합성 데이터 노이즈 (IS=-2.859는 해당 구간 불리)
- 9개 fold 중 유일한 OOS 양수 fold → 통계적으로 우연에 가까움
- 실거래소 데이터 없이는 판단 불가 (SSL 차단 환경 한계)

---

## 시뮬레이션 결과

### Paper Sim (Walk-Forward, 1h봉)
- **PASS: 0/22** (합성 데이터 한계)
- Top composite: volume_breakout(score 75.7, Sharpe 3.69), order_flow_imbalance_v2(74.7, Sharpe 3.85)
- 가장 안정적: volatility_cluster(SharpeStd=0.40), relative_volume(SharpeStd=0.51)

### Bundle OOS (5-bundle, 4h봉, min_oos_trades=10)
- **PASS: 0/5**
- WFE fix 효과: elder_impulse avg_wfe -1.185 → **-1.352** (역방향 fold 정리)
- wick_reversal avg_wfe 0.222 → **0.000** (모든 fold FAIL)
- value_area: 여전히 0 trades (4h봉 부적합 — 245에서 해결 예정)

---

## 테스트 결과
- **175 passed, 3 skipped** (기존 테스트 전부 통과, 신규 테스트 없음)
