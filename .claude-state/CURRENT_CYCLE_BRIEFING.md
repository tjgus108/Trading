======================================================================
🔄 CYCLE 246 — 2026-05-30
======================================================================

## 이번 사이클 배정 카테고리

**Cycle 246** (246 mod 5 = 1 → B(리스크) + D(ML) + F(리서치))

### [B] 리스크 — 완료
- DrawdownMonitor: `kelly_reduce_at_mdd=0.15`, `get_kelly_fraction_multiplier()` 추가
- DrawdownStatus: `kelly_fraction_multiplier` 필드 추가, 직렬화 지원
- 7개 신규 테스트 (TestKellyReduceAtMdd)

### [D] ML — 완료
- `MIN_MC_TRADES = 20` 신규 상수 (MIN_TRADES=15와 분리, 소표본 MC 오판 방지)
- `MC_N_PERMUTATIONS: 500 → 1000` (p-value 정밀도 2배)

### [SIM] 결과
- Paper BTC: 0/22 PASS, Top: momentum_quality(7.96), price_action_momentum(6.81)
- Bundle OOS 4h: 0/5 PASS, cmf rank#1, value_area fold6 PASS(1.775) 유지
- 테스트: 8332 passed (전체), 7개 신규

---

## [이전] CYCLE 245 — 2026-05-29

## 이번 사이클 배정 카테고리

**Cycle 245** (245 mod 5 = 0 → A(품질) + C(데이터) + F(리서치))

---

### [A] 품질 — 완료
- **value_area EMA 필터 수정** (`src/strategy/value_area.py`)
  - 문제: `ema20 > ema50` 추세 필터가 mean-reversion 신호와 충돌 → 4h 0 trades
  - 수정: EMA momentum 방향 필터 `ema20[t] > ema20[t-1]` (단기 반전 감지)
  - 파라미터 축소: `_VA_PERIOD: 20→10`, `_EMA_SHORT: 20→10`, `_EMA_LONG: 50→20`
  - `_MIN_ROWS: 55→25` (EMA50 warmup 불필요)
  - DEFAULT_GRIDS 업데이트: `va_period [15,20,25]→[10,15,20]` (`walk_forward.py`)
  - 신규 테스트 2개 추가

### [C] 데이터 — 완료
- **generate_synthetic_data() Regime-Switching 개선** (`scripts/run_bundle_oos.py`)
  - 순수 GBM → Markov Regime-Switching (Bull/Bear 자동 전환)
  - Bull: drift=+0.02%/bar, σ=0.25% | Bear: drift=-0.02%/bar, σ=0.40%
  - P(bull→bear)=0.02, P(bear→bull)=0.03
  - 거래량도 레짐 반영 (Bull 높음, Bear 낮음)

### [F/버그픽스] MC Permutation Test Annualization 수정 — 완료
- **버그**: `_mc_permutation_test` 고정 `sqrt(8760)` vs 실제 Sharpe `sqrt(6048)` (1h)
  - 비율 sqrt(8760/6048) ≈ 1.20 → permutation Sharpe 20% 과대 → p-value 인플레이션
- **수정**: `ann_factor: int = 8760` 파라미터 추가, 호출부에서 실제 값 전달
- 효과: mc_p_value 0.156~0.430 (이전 0.248~0.568)

---

## 시뮬레이션 결과

### Bundle OOS (5-bundle, 4h봉 Regime-Switching 합성 데이터)
- **PASS: 0/5** (min_oos_trades=10 기준 엄격)
- **value_area 개선**: 0→2-8 trades/fold, fold 6 PASS(Sharpe=1.775, PF=2.026, WFE=2.167)
- IS Sharpe 음수 비율 개선: cmf 100%→78% (Regime-Switching 효과)

### Paper Sim (Walk-Forward, 1h봉 BlockBootstrap)
- **PASS: 0/22** (consistency 기준 엄격)
- Top BTC: price_action_momentum(Sharpe 5.35), momentum_quality(6.04), supertrend_multi(4.54)
- value_area AvgTrades: 16→27 (+68%), AvgSharpe: -1.31→-0.17 개선
- mc_p_value 감소 확인: 0.156(price_action_momentum), 0.222(momentum_quality)

---

## 테스트 결과
- **145 passed** (신규 2개 포함: test_ema_momentum_filter, test_default_params)
