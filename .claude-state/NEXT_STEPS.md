# Next Steps

_Last updated: 2026-05-31 (Cycle 250 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 241~250

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 245 | A+C+SIM+F | value_area EMA filter 수정(0→8 trades), MC annualization bug fix |
| 246 | B+D+SIM+F | kelly_reduce_at_mdd, mc_min_trades/mc_block_size, 5 신규 테스트 |
| 247 | B+D+SIM+F | kelly_fraction_multiplier→manager.py 연결, paper_sim 옵션 추가 |
| 248 | C+B+SIM+F | generate_synthetic_data() regime 파라미터 개선, --min-trades 5 검증 |
| 249 | D+E+SIM+F | elder_impulse _calculate_atr() 버그 수정, --use-quality-data 옵션, avg_slippage 테스트 3개 |
| 250 | A+C+SIM+F | IS neg fold 진단(walk_forward.py), GARCH 기본 fallback, elder IS neg 100%→44% 확인 |

### 🎯 Cycle 251 작업 방향 (251 mod 5 = 1 → B(리스크) + D(ML) + F(리서치))

#### B(리스크): DrawdownMonitor + GARCH 파라미터 검토
- Cycle 248에서 개선된 DrawdownMonitor (kelly_reduce_at_mdd=0.09) 실제 영향 검증
- GARCH 시뮬 결과: cmf IS neg 44%, narrow_range IS neg 44% → 리스크 파라미터 조정 가능성
- CircuitBreaker 룰: 합성 데이터 기반 trigger 빈도 점검 (IS neg fold가 많은 환경에서 과도 trigger?)
- VaR/CVaR: GARCH 레짐 데이터 기반 신뢰구간 재검증

#### D(ML): GARCH fold 별 성과 분석 + 앙상블 가중치 검토
- cmf GARCH: IS 양수 fold (fold 2, 3, 7, 8 기준 OOS Sharpe 2.4~5.4) 파라미터 분석
- narrow_range GARCH: fold 5~7 IS 양수 (7.7, 6.6, 3.3) 구간 특성 분석 (추세 강도?)
- 앙상블 가중치: GARCH IS 양수 fold에서 cmf/narrow_range 우위 확인 시 가중치 증가 검토
- Walk-Forward 통합: GARCH 기본 fallback 적용 후 WFO 결과 변화 추적

#### F(리서치): OOS Sharpe std > 1.5 근본 원인
- 현재: cmf std 3.7, narrow_range std 4.4 (합성 데이터 fold 간 레짐 불일치)
- 레짐 불일치: fold 0~4(초기 bull 구간)와 fold 5~8(레짐 전환 구간) 간 성과 차이
- 개선 방향: 레짐 인식 fold 구분 + fold 가중치 (HIGH_VOL fold 다운웨이팅)
- 관련 코드: `WalkForwardOptimizer.use_regime_weights=True` 효과 검토

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단 (GARCH fallback 사용 중)
- GARCH 데이터: IS neg 비율 개선(100%→44%) 하지만 OOS Sharpe std > 1.5 여전
- wick_reversal, value_area: GARCH에서도 0 OOS trades → 실거래소 데이터 없이 검증 불가
- Paper SIM: 0/22 PASS 지속 (mc_p_value > 0.05, MDD 과다)

### 핵심 메트릭 (Cycle 250 이후)
- Bundle OOS Rank #1: cmf (Score 88.7, OOS Sharpe 1.085, IS neg 44%, GARCH)
- Bundle OOS Rank #2: narrow_range (Score 85.6, OOS Sharpe 1.029)
- elder_impulse: IS neg 44% (Cycle 249 ATR 수정 + Cycle 250 GARCH fallback 효과)
- walk_forward.py: `avg_is_sharpe`, `is_negative_fold_pct` 진단 필드 추가 완료
- run_bundle_oos.py: GARCH 기본 fallback (실거래소 차단 시)
- 테스트: **8349 passed** (Cycle 250 신규 3개: IS neg fold 진단 테스트)
