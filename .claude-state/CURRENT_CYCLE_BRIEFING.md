# Current Cycle Briefing

_Cycle 293 — C(데이터) + B(리스크) + F(리서치)_
_Completed: 2026-06-09_

## 완료 항목

### C(데이터): paper_simulation.py --verbose-windows 플래그 추가
- `scripts/paper_simulation.py`: `--verbose-windows N` CLI 인자 추가
- 상위 N개 전략의 window별 Sharpe/PF/Trades/MDD/Pass/Fail-Reason 상세 테이블을 리포트에 포함
- NEXT_STEPS 요청 이행: "cmf Paper Sim window별 상세 출력 옵션 추가"
- 사용법: `--verbose-windows 5` (상위 5개 전략 window 상세 출력)

### B(리스크): CircuitBreaker reset_daily 4h 타임프레임 버그 수정
- `src/risk/circuit_breaker.py`: `reset_daily(daily_start_balance, preserve_price_history=False)` 추가
- 문제: 4h 타임프레임에서 rapid_decline_window=5봉(20h)이 일 경계(00:00 UTC)를 넘을 때, reset_daily()가 _price_history를 초기화하여 전날 하락 감지 불가
- 수정: `preserve_price_history=True` 옵션으로 history 보존 가능 (backward compatible)
- 테스트: 기존 40개 CB 테스트 모두 PASS

### F(리서치): Paper Sim 0/22 vs Bundle OOS 2/5 불일치 원인 완전 분석

**핵심 발견:**
1. **trades < 15가 Paper Sim FAIL의 지배적 원인** (전체 FAIL 사유 Top 9/10)
   - 4h 타임프레임 + 60일 테스트 창 = 360봉 → 전략들이 15회 거래 달성 어려움
2. **cmf FAIL 상세**: PF=1.24 < 1.5 (binding constraint), MC p-value > 0.05 (통계 비유의)
   - Bundle OOS avg_pf=1.387도 1.5 미달 → 두 환경 모두 PF가 병목
3. **supertrend_multi FAIL 상세**: no trades × 3창, trades < 15 × 2창
   - 3개 Supertrend 합의 조건이 4h에서 너무 엄격하여 신호 극히 희소
4. **불일치 구조**: Bundle OOS는 WFE/Sharpe decay 중심, PF 기준 없고 min_oos_trades=3
   - Paper Sim은 PF≥1.5 + Trades≥15 동시 요구 → 4h 전략들에 더 엄격

## 시뮬레이션 결과

| 항목 | 결과 |
|------|------|
| Tests | 8392 passed |
| Paper Sim (4h BTC, 8w) | 0/22 PASS |
| Bundle OOS (5-fold, real CSV) | **2/5 PASS** (cmf, supertrend_multi) |

## 다음 사이클: 294 (D+E+F)
- D(ML): cmf PF 개선 — avg_pf 1.24→1.5 목표 (손절 최적화)
- E(실행): 4h 타임프레임 Trades≥15 기준 재검토 (10으로 완화 검토)
- F(리서치): cmf avg_win/avg_loss 구조 분석
