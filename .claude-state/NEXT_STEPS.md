# Next Steps

_Last updated: 2026-05-30 (Cycle 249 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 241~249

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 243 | C+B+SIM+F | min_oos_trades 3→10, regime_change_alert DrawdownMonitor 연동, rank 버그 수정 |
| 244 | D+E+SIM+F | WFE 역방향 fix, avg_slippage_per_trade, compute_ensemble_weight fold_direction |
| 245 | A+C+SIM+F | value_area EMA filter 수정(0→8 trades), MC annualization bug fix, regime-switching 합성 데이터 |
| 246 | B+D+SIM+F | kelly_reduce_at_mdd(DrawdownMonitor), mc_min_trades/mc_block_size(BacktestEngine), 5 신규 테스트 |
| 247 | B+D+SIM+F | kelly_fraction_multiplier→manager.py 연결, paper_sim --mc-min-trades/--mc-block-size, 2 신규 테스트 |
| 248 | C+B+SIM+F | generate_synthetic_data() regime 파라미터 개선, regime=None MDD=9% 복합 테스트, --min-trades 5 검증 |
| 249 | D+E+SIM+F | elder_impulse _calculate_atr() 버그 수정, --use-quality-data 옵션, avg_slippage 테스트 3개 |

### 🎯 Cycle 250 작업 방향 (250 mod 5 = 0 → A(품질) + C(데이터) + F(리서치))

#### A(품질): elder_impulse ATR 수정 효과 검증
- Cycle 249에서 수정한 ATR 버그가 IS Sharpe 개선으로 이어지는지 확인
- `python3 scripts/run_bundle_oos.py --dry-run --use-quality-data` 실행: GARCH 데이터에서 IS Sharpe 비교
- 예상: elder_impulse IS 음수 비율 100%→70% 이하로 개선될 경우 OOS 재검증 우선순위
- wick_reversal도 89% 음수: 변동성 필터 로직 검토 (TR 기반 vs ATR 기반)

#### C(데이터): BlockBootstrap 합성 데이터 성능 비교
- `python3 scripts/run_bundle_oos.py --dry-run --use-quality-data` 결과와 GBM 결과 비교표 작성
- GARCH 데이터(trend 120-180봉, range 100-150봉)에서 5전략 IS Sharpe 개선 여부 확인
- BlockBootstrap이 GBM보다 trend-following에 유리한지 정량적 비교 (fold별 IS Sharpe)
- 만약 GARCH에서도 IS Sharpe 개선 없다면 → 전략 신호 로직 문제 확정

#### F(리서치): 실거래소 데이터 없는 환경에서 신뢰가능한 전략 검증 대안
- BlockBootstrap + real distribution 활용한 validation 방법론 검토
- 관련 논문: Lopez de Prado "Advances in Financial Machine Learning" - Data Snooping 방어
- 전략 신호 생성 로직 vs 합성 데이터 충돌: trend-following 전략에 적합한 합성 데이터 조건

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단 (합성 데이터 fallback 불가피)
- IS Sharpe 음수 근본 원인: 전략 신호와 GBM 데이터 충돌 (elder_impulse ATR 버그 수정 → 부분 해소 기대)
- Paper SIM: 타임아웃 지속 (8 fold × 전략 수, 합성 데이터 생성 + 백테스트 연산)

### 핵심 메트릭 (Cycle 249 이후)
- Bundle OOS Rank #1: cmf (Score 76.6, OOS Sharpe -1.270, Avg Trades 12.4, OOS MDD 7.64%)
- elder_impulse: _calculate_atr() 버그 수정 완료 (단일 TR → 14기간 ATR 평균)
- run_bundle_oos.py: --use-quality-data 옵션 추가 (GARCH+regime 합성 데이터)
- avg_slippage_per_trade: BacktestResult 필드 정상 동작 확인 (3개 테스트)
- 테스트: **8346 passed** (Cycle 249 신규 6개: ATR 3개 + avg_slippage 3개)
