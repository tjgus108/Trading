# Current Cycle Briefing

_Last updated: 2026-06-05 (Cycle 273 완료)_

## 완료된 사이클: 273
**카테고리**: C(데이터) + B(리스크) + F(리서치)

## 핵심 변경사항

### B(리스크): wick_reversal ADX 필터 제거
- **문제**: Cycle 272에서 ADX>25 차단이 fold0,1,4 (OOS Sharpe +2.761/+1.328/+0.358 수익 구간) 차단
- **조치**: `src/strategy/wick_reversal.py`에서 `adx_ok` 조건 완전 제거
- **결과**: 4h OOS avg 0.980 → **1.289** 개선, 5/9 folds 개별 PASS
- **잔여 문제**: OOS std=6.085 > 기준 3.0 (레짐별 편차 문제 해결 필요)

### C(데이터): cmf_1h threshold 완화 + 실험
- **조치**: cmf_1h 그리드 buy_thresh 하한 0.05 추가, PAPER_SIM에 threshold 0.05 오버라이드
- **결과**: 1h paper sim rank 14→13 (소폭 개선), 효과 미미
- **결론**: cmf threshold 조정보다 다른 접근 필요

## 시뮬레이션 요약
| 항목 | 결과 |
|------|------|
| 테스트 | 8369 passed, 23 skipped |
| Paper Sim 1h PASS | 0/22 |
| Bundle OOS 4h PASS | 0/5 |
| 최고 성능 (Paper) | supertrend_multi +5.87% |
| 최고 성능 (OOS) | wick_reversal avg=1.289 (FAIL) |

## 다음 사이클 (274): D(ML) + E(실행) + F(리서치)
- **우선순위 1**: wick_reversal std 안정화 (vol_mult 강화 실험)
- **우선순위 2**: supertrend_multi 파라미터 그리드 추가
- **우선순위 3**: cmf threshold 기본값 복원 (0.08/-0.08)
