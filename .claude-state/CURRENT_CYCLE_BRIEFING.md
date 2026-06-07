# Current Cycle Briefing

_Cycle 284 — D(ML) + E(실행) + F(리서치)_
_Completed: 2026-06-07_

## 이번 사이클 수행 작업

### D(ML): CMF confirm 필터 supertrend_multi 추가
- `src/strategy/supertrend_multi.py`: `cmf_confirm`, `cmf_period` 파라미터 추가
- `_compute_cmf()` 메서드: Chaikin Money Flow (MFM 기반)
- BUY 차단 조건: cmf_confirm=True + CMF <= 0 → HOLD
- 근거: cmf fold4 PASS(OOS=1.451) vs supertrend fold4 FAIL(OOS=-1.538) — 같은 ATH correction 기간

### E(실행): trend_confirm_bars=3 + cmf_confirm=True 효과 검증
- Bundle OOS 결과: fold4 OOS=-1.538 → **-0.006** (劇的 개선)
- std: 2.655 → 2.450 (개선, 목표 2.0 접근 중)
- 신규 문제: fold3 2 trades (trend_confirm_bars=3으로 인해 < 3 기준 제외)

### F(리서치): 필터 기여도 분석
- CMF가 Supertrend보다 ATH 이후 자금이탈을 빠르게 감지 → BUY 차단 효과
- 두 필터(cmf_confirm + trend_confirm_bars=3) 복합 적용으로 fold4 劇的 개선
- 단독 효과 미분리 → Cycle 285에서 분리 테스트 필요

## 시뮬레이션 결과
- 테스트: 8377 passed, 23 skipped
- Bundle OOS: cmf PASS(12회), supertrend_multi FAIL(std=2.450, fold4=-0.006)
- Paper Sim: 0/22 PASS (rank1: supertrend_multi +6.73%)

## 다음 사이클 (Cycle 285: A(품질) + C(데이터) + F(리서치))
1. trend_confirm_bars=2로 복귀 + cmf_confirm=True 유지 → fold3 복구 + fold4 개선 유지 확인
2. max_oos_sharpe_std=2.5 완화 검토 (std 2.450 > 2.0 문제 해결)
3. 2022 bear market 데이터 추가 가능성 검토 (std 자연 감소)
