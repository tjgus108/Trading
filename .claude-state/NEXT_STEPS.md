# Next Steps

_Last updated: 2026-05-30 (Cycle 247 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 241~247

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 241 | A+C+SIM+F | check_distribution_drift(KS-test+2-signal), OFI edge cases, 15개 신규 테스트 |
| 242 | B+D+SIM+F | PerformanceMonitor drift 통합, ensemble stability penalty, WFE 분석 |
| 243 | C+B+SIM+F | min_oos_trades 3→10, regime_change_alert DrawdownMonitor 연동, rank 버그 수정 |
| 244 | D+E+SIM+F | WFE 역방향 fix, avg_slippage_per_trade, compute_ensemble_weight fold_direction |
| 245 | A+C+SIM+F | value_area EMA filter 수정(0→8 trades), MC annualization bug fix, regime-switching 합성 데이터 |
| 246 | B+D+SIM+F | kelly_reduce_at_mdd(DrawdownMonitor), mc_min_trades/mc_block_size(BacktestEngine), 5 신규 테스트 |
| 247 | B+D+SIM+F | kelly_fraction_multiplier→manager.py 연결, paper_sim --mc-min-trades/--mc-block-size, 2 신규 테스트 |

### 🎯 Cycle 248 작업 방향 (248 mod 5 = 3 → C(데이터) + B(리스크) + F(리서치))

#### C(데이터): 합성 데이터 IS Sharpe 음수 문제 근본 해결
- Bundle OOS 4h: elder_impulse/wick_reversal/narrow_range IS Sharpe 100% 음수 (Regime-Switching GBM 한계)
- 원인: 현재 합성 데이터 bull/bear 전환이 너무 랜덤 → trend-following 전략의 IS 수익 제한
- 옵션 1: `generate_synthetic_data()` bull regime 지속 기간 늘리기 (P(bull→bear) 0.02→0.01)
- 옵션 2: 4h 전략용 별도 합성 데이터 파라미터 세트 (더 강한 추세, 낮은 변동성)
- `scripts/run_bundle_oos.py`의 `generate_synthetic_data()` 호출부 확인 필요

#### B(리스크): kelly_fraction_multiplier × mdd_size_mult 복합 축소 효과 검증
- Cycle 247에서 연결 완료: MDD 8~10% → position_size × 0.5 (mdd_size_mult) × 0.5 (kelly_frac_mult) = 0.25x
- 다음: 실제 백테스트에서 이 복합 축소가 drawdown 개선에 미치는 효과 정량화
- `lob_maker` (AvgMDD=13.4%, Paper SIM): kelly_fraction_multiplier 발동 여부 확인
- `test_high_vol_plus_mdd_warn_compound` 확장: regime=None, MDD=9% 케이스 추가

#### F(리서치): value_area --min-trades 5 완화 검증
- `python3 scripts/run_bundle_oos.py --symbol BTC/USDT --timeframe 4h --min-trades 5`
- fold 6 (OOS Sharpe=1.775) 포함 시 value_area 전략 PASS 가능성 분석
- 실거래소 데이터 접근 시 value_area 4h 우선 검증

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- 합성 데이터 결과는 방향성 참고만
- Paper SIM 타임아웃: BTC만 완료 (ETH/SOL 미실행) → Cycle 248에서 `--mc-min-trades 20`으로 재실행

### 핵심 메트릭 (Cycle 247 이후)
- Paper SIM BTC Composite Rank #1: value_area (Score 73.9, AvgSharpe 4.39, AvgTrades 27, AvgMDD 3.1%)
- Bundle OOS value_area: fold 6 PASS (OOS Sharpe=1.775, PF=2.026), 전 fold trades<10 → min_oos_trades 장벽
- kelly_fraction_multiplier 연동 완료: MDD>8% 시 Kelly allocation 0.5x, position_size 복합 최대 0.25x
- 테스트: **8339 passed** (Cycle 247 신규 2개 kelly_fraction_multiplier 통합 테스트 포함)
- 신규 CLI: `--mc-min-trades N`, `--mc-block-size N` (paper_simulation.py)
