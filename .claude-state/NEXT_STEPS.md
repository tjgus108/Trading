# Next Steps

_Last updated: 2026-05-30 (Cycle 246 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 241, 242, 243, 244, 245, 246

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 241 | A+C+SIM+F | check_distribution_drift(KS-test+2-signal), OFI edge cases, 15개 신규 테스트 |
| 242 | B+D+SIM+F | PerformanceMonitor drift 통합, ensemble stability penalty, WFE 분석 |
| 243 | C+B+SIM+F | min_oos_trades 3→10, regime_change_alert DrawdownMonitor 연동, rank 버그 수정 |
| 244 | D+E+SIM+F | WFE 역방향 fix, avg_slippage_per_trade, compute_ensemble_weight fold_direction |
| 245 | A+C+SIM+F | value_area EMA filter 수정(0→8 trades), MC annualization bug fix, regime-switching 합성 데이터 |
| 246 | B+D+SIM+F | kelly_reduce_at_mdd(0.15), MIN_MC_TRADES=20 분리, MC_N_PERMUTATIONS 500→1000 |

### 🎯 Cycle 247 작업 방향 (247 mod 5 = 2 → B(리스크) + D(ML) + F(리서치))

#### B(리스크): DrawdownMonitor 연동 실사용 검증
- Cycle 246 추가: `kelly_reduce_at_mdd=0.15`, `get_kelly_fraction_multiplier()`
- 다음 단계: src/risk/manager.py에서 kelly_fraction_multiplier 실제 연동 여부 점검
  - DrawdownStatus.kelly_fraction_multiplier → KellySizer.fraction에 실제 곱해지는지 확인
- MDD BLOCK_ENTRY(10%) 완전 차단(0.0) vs 단계적 축소 재평가:
  - 현재: 10%에서 mdd_size_multiplier=0.0 (완전 차단)
  - 제안: BLOCK_ENTRY를 0.25x로 완화 (더 점진적인 감소)

#### D(ML): MIN_MC_TRADES 효과 모니터링 + 앙상블 가중치
- Cycle 246: MIN_MC_TRADES=20, MC_N_PERMUTATIONS=1000 적용
- 다음 SIM 결과에서 mc_p_value FAIL 빈도 변화 확인
- momentum_quality(Sharpe 7.96, SharpeStd 1.38) 앙상블 최우선 후보 분석
- compute_ensemble_weight에서 momentum_quality 가중치 증가 검토

#### F(리서치): value_area min_oos_trades 완화 + Bundle 전략 개선
- Bundle OOS: value_area fold 6 PASS(Sharpe 1.775) 지속, 나머지 OOS trades 2-8 (min_oos_trades=10 병목)
- 제안 1: run_bundle_oos.py min_oos_trades 10→5 (4h 봉 신호 빈도 반영)
  - walk_forward.py DEFAULT_GRIDS와 충돌 없이 스크립트 파라미터로 조정 가능
- 제안 2: Bundle 전략 교체
  - 현재: cmf, elder_impulse, wick_reversal, narrow_range, value_area
  - 후보: price_action_momentum, momentum_quality (Paper SIM 1-2위)
  - IS Sharpe 음수 전략(elder_impulse 100%, wick_reversal 100%) 교체 우선

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- 합성 데이터 결과는 방향성 참고만

### 핵심 메트릭 (Cycle 246 이후)
- Paper SIM 상위 BTC: price_action_momentum(Sharpe 6.81, MDD 8.1%), momentum_quality(Sharpe 7.96, MDD 7.3%)
- Paper SIM 상위 SOL: momentum_quality(Sharpe 4.95), volatility_cluster(Sharpe 2.87)
- 테스트: **8332 passed** (7개 신규 kelly_reduce_at_mdd 포함)
- DrawdownMonitor: kelly_reduce_at_mdd=0.15 추가, get_kelly_fraction_multiplier()
- MC 개선: MIN_MC_TRADES=20(소표본 분리), MC_N_PERMUTATIONS=1000(정밀도 2배)
- value_area: Bundle OOS fold 6 PASS(Sharpe 1.775) 유지, min_oos_trades=10이 병목
