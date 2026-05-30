======================================================================
🔄 CYCLE 246 — 2026-05-30
======================================================================

## 이번 사이클 배정 카테고리

**Cycle 246** (246 mod 5 = 1 → B(리스크) + D(ML) + F(리서치))

---

### [B] 리스크 — 완료
- **DrawdownMonitor `kelly_reduce_at_mdd` 파라미터 추가** (`src/risk/drawdown_monitor.py`)
  - `kelly_reduce_at_mdd: float = 0.08` — MDD > 8% 시 Kelly fraction 0.5x 축소 신호
  - `get_kelly_fraction_multiplier()` 메서드 추가
  - `DrawdownStatus.kelly_fraction_multiplier: float = 1.0` 필드 추가
  - `to_dict()` / `from_dict()` 직렬화 지원
  - 5개 신규 테스트 추가 (tests/test_drawdown_monitor.py)
  - 배경: lob_maker AvgMDD=20.0%, cmf AvgMDD=21.1% — 20% 경계 전 조기 축소 필요

### [D] ML — 완료
- **BacktestEngine `mc_min_trades` / `mc_block_size` 파라미터 노출** (`src/backtest/engine.py`)
  - `mc_min_trades: int = 0` — MC 검정 최소 거래 수 (0=MIN_TRADES=15 유지)
  - `mc_block_size: int = 1` — 블록 부호 셔플 크기 (>1이면 직렬 상관 보존)
  - run() 내부에서 self.mc_min_trades, self.mc_block_size 사용
  - 효과: 거래 수 15~19건 전략의 불안정 MC p-value를 mc_min_trades=20으로 제외 가능

### [F] 리서치 — 완료
- **mc_p_value 실패 패턴 분석**:
  - 합성 BlockBootstrap 데이터에서 모든 전략 p > 0.05 (0.124~0.494)
  - 신호-노이즈 비율 낮은 합성 데이터 특성 → 실거래소 데이터에서 p < 0.05 기대
  - mc_block_size=24 (일별 블록) 적용 시 시계열 보존 개선 가능

---

## 시뮬레이션 결과

### Bundle OOS (5-bundle, 4h봉 합성 데이터)
- **PASS: 0/5** (IS Sharpe 전부 음수: elder_impulse/wick_reversal/narrow_range)
- cmf 가장 우수 (Score=75.1): OOS Sharpe -2.373, SharpeStd 2.155
- value_area: fold 6만 PASS (OOS Sharpe 1.775), min_oos_trades=10 기준 전 fold 미달

### Paper Sim (Walk-Forward, 1h봉 BlockBootstrap)
- **PASS: 0/22** (consistency 기준 엄격)
- Top BTC: price_action_momentum(Sharpe 5.42, SharpeStd 1.37), momentum_quality(3.31), supertrend_multi(2.80)
- lob_maker: AvgMDD=20.0% (경계), cmf: AvgMDD=21.1% > 20%
- 주요 FAIL: mc_p_value > 0.05 (합성 데이터 한계), profit_factor < 1.5

---

## 테스트 결과
- **8332 passed, 23 skipped** (신규 5개 kelly_reduce_at_mdd 포함)
