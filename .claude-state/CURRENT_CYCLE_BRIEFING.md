# Current Cycle Briefing

_Cycle 293 — C(데이터) + B(리스크) + F(리서치)_
_Completed: 2026-06-09_

## 완료 항목

### C(데이터): --verbose-windows 옵션 추가
- `scripts/paper_simulation.py`: `VERBOSE_WINDOWS` 모듈 플래그 + `--verbose-windows` CLI 옵션
- `generate_report()` 내 상위 5 전략 윈도우별 Sharpe/PF/Trades/MDD/FailReasons 테이블
- 효과: FAIL 원인 집계 → 윈도우별 정확한 진단 가능

### B(리스크): VolTargeting.for_timeframe() classmethod
- `src/risk/vol_targeting.py`: `_TF_CANDLES_PER_DAY` + `for_timeframe(timeframe)` 추가
- 4h 캔들에서 기본 1h annualization 사용 시 실현변동성 2배 과장 방지
- `VolTargeting.for_timeframe("4h")` → annualization=252×6=1512 자동 설정

### F(리서치): Paper Sim 0/22 FAIL 원인 완전 분석
- verbose-windows 출력으로 cmf/supertrend_multi 실패 원인 확정
- **cmf**: PF < 1.5 (7/8 windows) + MC p-value test (W2 차단)
- **supertrend_multi**: trades < 15 (W2-W3) + 0 trades (W5-W7 sideways 구간)
- Paper Sim vs Bundle OOS 불일치 결론:
  - Bundle OOS는 저거래 fold 제외 + Sharpe/WFE 기준 → 2/5 PASS
  - Paper Sim은 4개 동시 충족 필요 + MC 테스트 + 거래수 최소 15 → 0/22 PASS

## 시뮬레이션 결과
- Paper Sim BTC 4h: 0/22 PASS (rank1=cmf score=68.3, rank5=supertrend_multi score=54.6)
- Bundle OOS BTC 4h: 2/5 PASS (cmf avg_sharpe=2.508, supertrend_multi avg_sharpe=3.674)
- 테스트: 8392 passed (목표)

## 다음 사이클 (294): D(ML) + E(실행) + F(리서치)
- D(ML): cmf 레짐 조건부 앙상블 가중치 강화 (PF < 1.5 해결 시도)
- E(실행): supertrend_multi 신호 빈도 진단 (sideways 0 거래 해결)
- F(리서치): 레짐별 전략 포트폴리오 구성 방안 연구
