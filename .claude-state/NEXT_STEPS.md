# Next Steps

_Last updated: 2026-05-31 (Cycle 250 완료)_

> **정책**: 이 파일은 "다음에 뭘 할지" 포인터만 보관. 과거 사이클 히스토리는 `.claude-state/WORKLOG.md`로 이관.

## 다음 세션이 이어받을 지점

### 이번 세션 완료 사이클: 241~250

| Cycle | 카테고리 | 주요 성과 |
|-------|---------|----------|
| 245 | A+C+SIM+F | value_area EMA filter 수정(0→8 trades), MC annualization bug fix |
| 246 | B+D+SIM+F | kelly_reduce_at_mdd(DrawdownMonitor), mc_min_trades/mc_block_size |
| 247 | B+D+SIM+F | kelly_fraction_multiplier→manager.py 연결 |
| 248 | C+B+SIM+F | generate_synthetic_data() regime 파라미터 개선 |
| 249 | D+E+SIM+F | elder_impulse _calculate_atr() 버그 수정, --use-quality-data 옵션 |
| 250 | A+C+SIM+F | GARCH wick multiplier 수정(0.010→0.5), fold_pass_rate 필드 추가 |

### 🎯 Cycle 251 작업 방향 (251 mod 5 = 1 → B(리스크) + D(ML) + F(리서치))

#### B(리스크): OOS Sharpe std 기준 검토
- cmf GARCH에서 avg OOS Sharpe 1.075 (양수)이지만 OOS std 4.236 > 1.5로 FAIL
- `RollingOOSValidator.OOS_SHARPE_STD_MAX = 1.5` 기준 근거 재검토
- 대안: std 기준 완화(1.5→2.0) 또는 fold_pass_rate >= 60% 조건 추가
- `DrawdownMonitor` circuit_breaker 로직: 연속 손실 시 circuit_breaker가 작동하는지 테스트 추가

#### D(ML): GARCH 데이터 cmf/narrow_range PASS fold 분석
- Cycle 250 GARCH: cmf 4/9 PASS fold, narrow_range 1/9 PASS fold
- PASS fold 공통 조건 분석: fold 레짐 구조(trend_up/range/vol_spike 비율) 추출
- 만약 cmf가 "range 레짐 < 40%" 조건에서 일관적으로 PASS → 레짐 기반 조건부 신호 활성화 검토
- OOS std 개선 방향: 레짐별 파라미터 선택 (Walk-Forward 내에서 레짐 분기)

#### F(리서치): OOS 기간 wick_reversal 0 trades 원인 분석
- GARCH 고정 regime 패턴에서 wick 패턴 분포 확인
  - IS 구간(1080봉): trend_up/trend_down → wick 많음
  - OOS 구간(360봉): regime에 따라 wick 적음 가능
- 실거래소 4h 데이터가 있다면 wick_reversal OOS trades 몇 건인지 확인 필요
- 대안: `_generate_quality_synthetic_data`에서 OOS 기간 시드를 다르게 설정하여 regime 분포 균등화

### ⚠️ 환경 제약
- SSL 인터셉션으로 외부 거래소 API 차단 (합성 데이터 fallback 불가피)
- value_area: GARCH/GBM 모두 OOS 0 trades → 합성 데이터로 검증 불가
- wick_reversal: IS Sharpe 모두 양수(GARCH wick 수정 후) but OOS < 10 trades

### 핵심 메트릭 (Cycle 250 이후)
- Bundle OOS Rank #1 (GBM): cmf (Score 76.6, OOS Sharpe -1.270, Avg Trades 12.4, MDD 7.64%)
- Bundle OOS Rank #1 (GARCH 신규): cmf (Score 92.9, OOS Sharpe 1.075, Fold Pass% 44%)
- wick_reversal GARCH IS Sharpe: 0% 음수 (9/9 양수) ← wick multiplier 0.010→0.5 수정 효과
- fold_pass_rate: BundleOOSResult 필드 추가, BUNDLE_OOS_REPORT 테이블에 "Fold Pass%" 열 추가
- 테스트: **8350 passed** (Cycle 250 신규 4개: fold_pass_rate ×3 + wick_ratio 1개)
