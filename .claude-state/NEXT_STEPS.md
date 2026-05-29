# Next Steps

_Last updated: 2026-05-29 (Cycle 245 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 241, 242, 243, 244, 245

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 241 | A+C+SIM+F | check_distribution_drift(KS-test+2-signal), OFI edge cases, 15개 신규 테스트 |
| 242 | B+D+SIM+F | PerformanceMonitor drift 통합, ensemble stability penalty, WFE 분석 |
| 243 | C+B+SIM+F | min_oos_trades 3→10, regime_change_alert DrawdownMonitor 연동, rank 버그 수정 |
| 244 | D+E+SIM+F | WFE 역방향 fix, avg_slippage_per_trade, compute_ensemble_weight fold_direction |
| 245 | A+C+SIM+F | value_area EMA filter 수정(0→8 trades), MC annualization bug fix, regime-switching 합성 데이터 |

### 🎯 Cycle 246 작업 방향 (246 mod 5 = 1 → B(리스크) + D(ML) + F(리서치))

#### B(리스크): DrawdownMonitor + Kelly 연동 강화
- Cycle 245 Paper SIM에서 cmf MDD=19.6%, lob_maker MDD=17.8% → 20% 경계 위험
- DrawdownMonitor에서 MDD > 15% 시 Kelly fraction을 0.5x 자동 축소 검토
- `src/risk/drawdown_monitor.py`: `kelly_reduce_at_mdd` 파라미터 추가 고려
- 기존 테스트에서 kelly_quarter_cap + DrawdownMonitor 상호작용 검증

#### D(ML): MC p-value 통과 전략 특성 분석
- Cycle 245 MC fix 효과: p-value 0.156~0.430 (이전 0.248~0.568)
- 0.156(price_action_momentum), 0.222(momentum_quality) → 여전히 0.05 초과
- MC p-value 통과 조건 분석:
  - 어떤 특성의 전략이 p < 0.05 달성하는지 (trade 수, win rate, PF 분포)
  - min_mc_trades 임계값 조정 (현재 15, 높이면 더 엄격하지만 better precision)
- relative_volume (SharpeStd=0.51, 가장 안정적) → 실거래소 데이터 접근 시 검증 우선 대상

#### F(리서치): value_area 4h 추가 개선 방향
- Cycle 245 결과: 0→2-8 trades/fold (fold 6 PASS: Sharpe=1.775, PF=2.026)
- 여전히 min_oos_trades=10 미달 (최대 8 trades/fold)
- 다음 단계 옵션:
  1. min_oos_trades 완화: 10→5 (4h 봉의 신호 빈도 특성 반영)
  2. VA 밴드 추가 완화: `_VA_MULT 0.6→0.5` (더 잦은 이탈/재진입)
  3. 실거래소 1h 데이터로 별도 검증 (SSL 차단 해제 시 우선)
- 합성 데이터 Regime-Switching 효과: IS 음수 비율 cmf 100%→78% 개선

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단
- 합성 데이터 결과는 방향성 참고만

### 핵심 메트릭 (Cycle 245 이후)
- Paper SIM 상위 BTC: price_action_momentum(Sharpe 5.35), momentum_quality(6.04), supertrend_multi(4.54)
- Paper SIM 상위 ETH/SOL: order_flow_imbalance_v2 일관성 높음
- 테스트: **145 passed** (Cycle 245 신규 2개 포함)
- value_area: EMA filter 수정 → 4h 0→2-8 trades, fold 6 PASS(Sharpe 1.775)
- MC annualization fix: `_mc_permutation_test(ann_factor=실제값)` 적용
- Regime-Switching 합성 데이터: generate_synthetic_data() 개선 (bull/bear 레짐 포함)
