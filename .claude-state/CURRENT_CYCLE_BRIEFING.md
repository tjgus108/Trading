# Current Cycle Briefing

_Cycle 337 | 2026-06-21 | B(리스크) + D(ML) + F(리서치)_

## 완료된 작업

### B(리스크): max_hold_candles_override=48 — 1h paper_sim 전용 MAX_HOLD 분리

- `BacktestEngine`에 `max_hold_candles_override: Optional[int] = None` 파라미터 추가
  - None이면 `MAX_HOLD_CANDLES=24` 사용 (4h Bundle OOS 기본값 유지)
  - `paper_simulation.py`에서만 `max_hold_candles_override=48` 전달 → 1h 전용 48봉
- `walk_forward.py` `RollingOOSValidator`에 `timeframe` 파라미터 추가 (저장용)
  - 중요 발견: Bundle OOS override 임계값은 1h 연간화 기준 캘리브레이션됨
  - `timeframe="4h"` engine 전달 시 Sharpe 50% 하락 → 5/5 PASS → 1/5 FAIL 확인
  - 결론: validate()의 BacktestEngine에는 timeframe 전달 않음 (engine 기본값 "1h" 유지)
- Paper Sim 효과:
  - price_cluster: Sharpe 0.34 → 0.90 (+0.56)
  - roc_ma_cross: Sharpe -0.41 → 0.25 (+0.66)

### D(ML): OFI v2 buy_thresh 0.30 → 0.25 복원

- PAPER_SIM_STRATEGY_PARAMS 변경:
  - `{"trend_span": 20, "buy_thresh": 0.30, "sell_thresh": -0.30}` → `{"trend_span": 20}`
  - 사유: ETH 악화(rank15, Sharpe=-2.40), Cycle300 역효과 전례 재확인
- OFI 결과: rank6(Sharpe=-0.70) ← 여전히 FAIL, buy_thresh=0.25가 안정적

### F(리서치): ATR 기반 SL/TP 구조 분석

- 현재: SL=ATR×1.5, TP=ATR×3.5 → R:R=2.33:1
- 수수료 포함 BEP WR ≈ 36%, 실측 WR ≈ 37-40% (여유 매우 얇음)
- MAX_HOLD=48(1h) 적용 후 tp% 증가 확인 (price_cluster Sharpe +0.56)
- 다음 실험 후보: atr_multiplier_tp=2.5 (R:R=1.67, BEP=38%) — Cycle 338에서 검증 권장

## 시뮬레이션 결과 (Cycle 337)

- **테스트**: 8425 passed, 23 skipped (회귀 없음)

- **Paper Sim BTC 1h (20전략, 8 windows, max_hold=48, buy_thresh=0.25)**: **0/20 PASS** (17사이클 연속)
  - rank1: price_cluster (Sharpe=0.90, Return=+5.60%, PF=1.21, 2/8) ← +0.56 개선
  - rank2: roc_ma_cross (Sharpe=0.25, Return=+2.54%, PF=1.20, 2/8) ← +0.66 개선
  - rank3: frama (Sharpe=0.33, Return=+2.20%, PF=1.15, 1/8)
  - rank6: order_flow_imbalance_v2 (Sharpe=-0.70, PF=0.96, 0/8)
  - 주요 FAIL 원인: profit_factor < 1.5 (전체 전략)

- **Bundle OOS BTC 4h**: **5/5 PASS** ← 유지
  - rank1: order_flow_imbalance_v2 (avg=4.345, std=0.907)
  - rank2: supertrend_multi (avg=3.892, std=1.239)
  - rank3: value_area (avg=3.069, std=0.085)
  - rank4: vwap_cross (avg=3.047, std=1.437)
  - rank5: cmf (avg=2.508, std=1.888)

## 다음 사이클 (338 mod 5 = 3): C(데이터) + B(리스크) + F(리서치)

- **C(데이터)**: ETH/SOL 합성 데이터 품질 재확인, 심볼별 전략 성능 분산 분석
- **B(리스크)**: atr_multiplier_tp 3.5→2.5 실험 (R:R 변화, PF 영향)
- **F(리서치)**: price_cluster, roc_ma_cross 8개 윈도우별 성능 분포 분석 (PASS 근접 윈도우 파악)
