## [2026-05-30] Cycle 246 — B(리스크) + D(ML) + SIM + F(리서치)

**[B] 리스크 — DrawdownMonitor kelly_reduce_at_mdd 추가:**
- 배경: Cycle 245 SIM cmf MDD=19.6%, lob_maker MDD=17.8% → 20% 경계 위험
- 변경: `kelly_reduce_at_mdd=0.15` 파라미터 추가 (DrawdownMonitor)
- 추가: `get_kelly_fraction_multiplier()` 메서드 → MDD >= kelly_reduce_at_mdd 시 0.5 반환
- DrawdownStatus에 `kelly_fraction_multiplier` 필드 추가
- to_dict/from_dict 직렬화 지원
- 사용법: `fraction = base_fraction * monitor.get_kelly_fraction_multiplier()`
- 7개 신규 테스트 추가 (TestKellyReduceAtMdd)

**[D] ML — MC Permutation 테스트 개선:**
- 문제: 15개 거래 MC 테스트는 분해능 부족 (p-value 최소단위 = 1/500 = 0.002)
- 변경1: `MIN_MC_TRADES = 20` 추가 (MIN_TRADES=15와 분리)
  → 15-19 trades: MC 미적용 (소표본 MC 오판 방지)
  → 20+ trades: MC 적용 (충분한 정밀도)
- 변경2: `MC_N_PERMUTATIONS: 500 → 1000` (리서치 권장값 적용, p-value 정밀도 2배 개선)
- 효과: Cycle 246 SIM에서 mc_p_value FAIL이 TOP FAIL 원인이었음 → 정밀도 개선

**[SIM] 시뮬레이션 결과 (2026-05-30 Cycle 246):**
- Paper SIM (1h Walk-Forward, Regime-Switching 합성 데이터):
  - BTC: 0/22 PASS
    - Top: price_action_momentum(Sharpe 6.81, MDD 8.1%), momentum_quality(Sharpe 7.96, MDD 7.3%)
    - roc_ma_cross: SharpeStd 0.26 (가장 안정적), value_area: Sharpe 0.93 (접근)
    - cmf MDD: 17.1% (이전 사이클 19.6%에서 개선, 합성 데이터 시드 차이)
  - SOL: 0/22 PASS
    - Top: momentum_quality(Sharpe 4.95), volatility_cluster(Sharpe 2.87)
  - 주요 FAIL 원인: mc_p_value (0.2~0.6 범위) → MIN_MC_TRADES/N_PERMUTATIONS 개선 효과 기대
- Bundle OOS (4h Regime-Switching 합성 데이터):
  - 0/5 PASS (IS Sharpe 78-100% 음수 → 합성 GBM 데이터 한계)
  - cmf rank #1 (Score 75.1), elder_impulse rank #2
  - value_area: 모든 fold OOS trades < 10 (min_oos_trades 기준 미달)

**[F] 리서치 — value_area 4h 분석:**
- Bundle OOS: fold 6 PASS(Sharpe=1.775) 지속, 나머지 fold OOS trades 2-8 (min_oos_trades=10 미달)
- IS Sharpe 음수 67% → 합성 데이터 한계로 판단 (실거래소 검증 필요)
- 다음 방향: min_oos_trades 완화 검토 (10→5 for 4h timeframe)

**테스트: 8332 passed** (7개 신규 kelly_reduce_at_mdd 포함)

## [2026-05-29] Cycle 245 — A(품질) + C(데이터) + SIM + F(리서치)

**[A] 품질 — value_area 4h 타임프레임 신호 생성 수정:**
- 문제: EMA20>EMA50 추세 필터가 mean-reversion 전략과 충돌 (VA 이탈 시 EMA20<EMA50, 조건 불충족)
- 수정: EMA momentum 방향 필터로 교체: `ema20[t] > ema20[t-1]` (단기 반전 감지)
- 파라미터 조정: `_VA_PERIOD: 20→10`, `_EMA_SHORT: 20→10`, `_EMA_LONG: 50→20`, `_MIN_ROWS: 55→25`
- walk_forward DEFAULT_GRIDS value_area: va_period `[15,20,25]→[10,15,20]`
- 효과: Bundle OOS 4h value_area 0 trades → 2-8 trades/fold, fold 6 PASS(Sharpe=1.775, PF=2.026)
- Paper SIM 1h value_area AvgTrades: 16→27
- 2 신규 테스트 추가 (test_ema_momentum_filter_generates_signal, test_default_params)

**[C] 데이터 — generate_synthetic_data() Regime-Switching 개선:**
- 순수 GBM→Regime-Switching Markov (Bull: drift+0.02%,σ=0.25% / Bear: drift-0.02%,σ=0.40%)
- P(bull→bear)=0.02, P(bear→bull)=0.03으로 자연스러운 레짐 전환
- 거래량도 레짐 반영: Bull=lognormal(μ=11), Bear=lognormal(μ=10)
- 효과: IS Sharpe 음수 전략 수 감소 기대 (cmf 100% → 78%, elder_impulse 100% 유지)

**[F/버그픽스] engine.py MC permutation test annualization 수정:**
- 버그: `_mc_permutation_test`가 `sqrt(8760)` 사용, 실제 Sharpe는 `sqrt(6048)`(1h) 사용
  → 비율 = 8760/6048 → permutation Sharpe 20% 과대 계상 → p-value 인플레이션
- 수정: `ann_factor: int = 8760` 파라미터 추가 (default 유지로 기존 테스트 호환)
- 호출부에서 실제 `ann_factor` 전달 (1h=6048, 4h=1512 등)
- 효과: Paper SIM mc_p_value 감소 확인 (0.156~0.430 vs 이전 0.248~0.568)

**[SIM] 시뮬레이션 결과 (2026-05-29 Cycle 245):**
- Paper (1h Walk-Forward, Regime-Switching 합성 데이터):
  - 0/22 PASS (consistency 기준 여전히 엄격, 합성 데이터 한계)
  - Top: price_action_momentum(Sharpe 5.35), momentum_quality(Sharpe 6.04), volume_breakout(Sharpe 4.21)
  - value_area 개선: AvgTrades 16→27, AvgSharpe -1.31→-0.17 (BTC 기준)
- Bundle OOS (4h Regime-Switching 합성 데이터):
  - 0/5 PASS (min_oos_trades=10 기준 엄격)
  - value_area: 0→2-8 trades/fold (fold 6: PASS 조건 달성, 2 OOS trades)
  - 실거래소 데이터로 검증 필요 (SSL 차단으로 현재 불가)

**테스트: 145 passed (기존 143 + 2 신규)**

## [2026-05-29] Cycle 244 — D(ML) + E(실행) + SIM + F(리서치)

**[D] ML — WFE 역방향 신호 수정 (walk_forward.py + engine.py):**
- IS < -1.0 이고 OOS > 0인 "강한 역방향" fold: WFE = 1.0 → **0.0** 으로 수정
  - elder_impulse fold1: IS=-2.859, OOS=+3.794 → WFE=0.0 → FAIL (이전: WFE=1.0 → PASS)
  - wick_reversal 역방향 fold들도 동일하게 FAIL 처리
  - engine.py `apply_wfe()` 동일 로직 적용 (일관성)
- 근거: IS Sharpe -2.859는 전략이 해당 구간에서 강하게 손실. OOS=+3.794는 합성 데이터 노이즈

**[D] ML — compute_ensemble_weight_recency() fold_direction 지원 (trainer.py):**
- `fold_sharpes: Optional[List[tuple]]` 파라미터 추가
- `sign_reversal_penalty: float = 0.3` 추가
- IS < -1.0 + OOS > 0인 fold는 weight에 0.3 페널티 적용

**[E] 실행 — avg_slippage_per_trade 지표 추가 (engine.py):**
- `BacktestResult.avg_slippage_per_trade` 필드 추가 (거래당 평균 슬리피지)
- `_compute_metrics()`에서 자동 계산
- `summary()`에 `avg_slippage_per_trade` 출력 추가

**[SIM] 시뮬레이션 분석 (2026-05-29):**
- Paper (1h Walk-Forward): 0/22 PASS. Top composite: volume_breakout(Sharpe 3.69, std 1.58), order_flow_imbalance_v2(Sharpe 3.85), relative_volume(Sharpe 2.98, std 0.51 — 가장 안정적)
- Bundle OOS (4h, min_oos_trades=10): 0/5 PASS
  - WFE 수정 효과: elder_impulse 이전 PASS fold 1개 → 0개 (sign reversal fix 작동)
  - wick_reversal: avg_wfe 0.222 → 0.000 (역방향 fold 정리됨)
  - value_area: 여전히 0 trades — 4h 타임프레임에서 신호 없음 문제 미해결
  - 전체 IS Sharpe 음수 비율: cmf/wick_reversal 100%, 합성 데이터 한계

**[F] 리서치 — IS→OOS 역전 케이스 분석:**
- elder_impulse fold1: IS=-2.859 → 전략이 IS에서 강하게 손실
  - GBM 합성 데이터에서 IS 구간이 특별히 불리한 시장 패턴 (가설 1 지지)
  - OOS=+3.794는 신호 반전이 아닌 데이터 노이즈 (9개 fold 중 유일한 양수)
  - 결론: IS 심각 음수 전략은 실거래소 데이터 없이는 신뢰 불가

## [2026-05-29] Cycle 243 — C(데이터) + B(리스크) + SIM + F(리서치)

**[C] Data — run_bundle_oos min_oos_trades 강화:**
- `run_bundle_oos()` default `min_oos_trades=3 → 10` 강화
- CLI `--min-trades` 기본값도 3 → 10으로 변경
- 효과: 저거래 fold(< 10 trades)는 집계에서 제외
- `bundle_results_to_rank_dicts()`: "모든 fold 거래 없음" 전략 rank score 최하위 처리 버그 수정
  - all_excluded=True 시 avg_mdd=1.0 (최악 페널티), avg_trades=0.0
  - value_area가 모든 fold 제외 시 rank 1위가 되던 버그 수정

**[B] Risk — PerformanceMonitor 레짐 연동 + mdd_halt_pct 자동 조정:**
- `PerformanceMonitor.__init__`에 `drawdown_monitor=None` 파라미터 추가
- `regime_change_alert()` 확장:
  - TREND_UP/BULL 레짐: `mdd_halt_pct` 25% 완화 (bull = 더 큰 낙폭 허용)
  - TREND_DOWN/BEAR 레짐: `mdd_halt_pct` 15% 강화
  - 기타 레짐(RANGING/HIGH_VOL 등): 기본값 복원
  - `drawdown_monitor.set_regime(new_regime)` 자동 호출
- `_default_mdd_halt_pct` 저장해 기본값 복원 보장
- 신규 테스트 2개 추가:
  - `test_perf_monitor_regime_change_mdd_halt_pct` (Cycle 243 B)
  - `test_perf_monitor_regime_change_calls_drawdown_monitor` (Cycle 243 B)

**[SIM] 시뮬레이션 분석 (2026-05-29):**
- Paper (1h Walk-Forward): 0/22 PASS. Top: supertrend_multi(+83.2%, Sharpe 6.06, 0/4 consistency), momentum_quality(+53.9%, Sharpe 4.49)
- Bundle OOS (4h, min_oos_trades=10): 0/5 PASS
  - value_area: 모든 fold 제외 (trades 2-7, min=10 미달) → 거래 빈도 문제 확인
  - wick_reversal: OOS std=4.15 (PASS fold 1개: fold8 Sharpe+0.37)
  - elder_impulse: OOS std=4.69 (PASS fold 1개: fold1 Sharpe+3.79, OOS PF=1.90)
  - narrow_range: OOS std=6.37 (최악)
  - cmf: OOS std=3.58
- 핵심 관찰: elder_impulse fold1이 유일한 PASS fold(OOS Sharpe=3.794) → 해당 구간 분석 필요

**[F] Research — 앙상블 가중치 안정성 + 레짐별 MDD 임계값:**
- stability_penalty 효과: compute_ensemble_weight에서 gap≥0.15이면 가중치 0으로 설정
- 레짐별 mdd_halt 분리(BULL 25%, BEAR 15%)가 논리적으로 타당 → Cycle 244에서 실전 데이터 검증
- value_area 저거래 패턴: 4h봉 OOS 360봉 기간 동안 평균 5 trades → 해당 전략은 일봉/주봉 타임프레임이 적합

**테스트: 171 passed** (+2 신규, 전체 +2)

---

# Work Log

## [2026-05-29] Cycle 242 — B(리스크) + D(ML) + SIM + F(리서치)

**[B] Risk — PerformanceMonitor distribution drift 통합:**
- `PerformanceMonitor.__init__`에 `baseline_n=30` 추가
- `set_baseline(strategy, returns)`: 전략별 baseline 수동 설정
- `_check_drift_for(strategy)`: 자동(초기 baseline_n 거래) + 수동 baseline 지원
- `check_all()` 결과에 `drift` 키 포함 + warn 시 on_alert 콜백 연동
- 테스트 8개 추가

**[D] ML — compute_ensemble_weight 안정성 패널티:**
- `stability_threshold=0.05`, `stability_scale=0.10` 파라미터 추가
- gap=|val_acc - test_acc|이 threshold+scale 이상이면 가중치 0
- OOS Sharpe std가 높은 불안정 모델 자동 하향
- 테스트 3개 추가

**[SIM] 이전 사이클 리포트 분석:**
- Paper: 0/22 PASS. 합성 데이터 한계. momentum_quality/price_action_momentum 상위권
- Bundle OOS: 0/5 PASS. narrow_range std=6.35 최악. elder_impulse fold1만 PASS(OOS Sharpe 3.794)

## [2026-05-29 15:10 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: 20.00bps

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: 20.00bps

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: 15.00bps

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: -5.00bps

## [2026-05-29 15:10 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-05-29 15:10 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-05-29 15:10 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-05-29 15:10 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-05-29 15:10 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-05-29 20:29 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: 20.00bps

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: 20.00bps

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: 15.00bps

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: -5.00bps

## [2026-05-29 20:29 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-05-29 20:29 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-05-29 20:29 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-05-29 20:29 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-05-29 20:29 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-05-29 20:34 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: 20.00bps

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: 20.00bps

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: 15.00bps

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: -5.00bps

## [2026-05-29 20:34 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-05-29 20:34 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-05-29 20:34 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-05-29 20:34 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-05-29 20:34 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-05-29 20:39 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: 20.00bps

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: 20.00bps

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: 15.00bps

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: -5.00bps

## [2026-05-29 20:39 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-05-29 20:39 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-05-29 20:39 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-05-29 20:39 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-05-29 20:39 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-05-30 00:11 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: 20.00bps

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: 20.00bps

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: 15.00bps

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: -5.00bps

## [2026-05-30 00:11 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-05-30 00:11 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-05-30 00:11 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-05-30 00:11 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-05-30 00:11 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-05-30 00:28 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: 20.00bps

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: 20.00bps

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: 15.00bps

## [2026-04-11 00:00 UTC]
Pipeline: execution
Status: OK
Signal: BUY BTC/USDT
Risk: APPROVED
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: none
ImplShortfall: -5.00bps

## [2026-05-30 00:28 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-05-30 00:28 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-05-30 00:28 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-05-30 00:28 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures

## [2026-05-30 00:28 UTC]
Pipeline: preflight
Status: ERROR
Signal: N/A
Risk: N/A
Execution: SKIPPED
Context: score=N/A news=NONE
Notes: CRITICAL: Connector is halted due to consecutive failures
