# Current Cycle Briefing

_Last updated: 2026-06-30 (Cycle 372 완료)_

## 현재 상태

- **완료된 사이클**: 372
- **다음 사이클**: 373 (373 mod 5 = 3 → C+B+F)
- **연속 PASS 실패**: 57연속 (0/19 1h paper_sim)
- **Bundle OOS**: 5/5 PASS 유지

## Cycle 372 주요 결과

### B(리스크): risk 모듈 현황 점검 — 이상 없음
- DrawdownMonitor: to_dict/from_dict 정상, cooldown_active 주석 완비 (Cycle357~358)
- CircuitBreaker: rapid_decline BTC 1h 실데이터 기반 파라미터 주석 완비 (Cycle363)
- KellySizer: dead param debug 로그 추가됨 (Cycle362)
- **결론**: 3개 모듈 모두 현재 이슈 없음

### D(ML): dema_cross ema_slope_min_buy=0.0003 실험 → 역효과 확정
- 실험 결과: Sh=0.80→0.21 (대폭 하락), PF=1.38→1.30, Trades=30→26
- 역효과 이유: RANGING 47.3% 구간에서 BUY 과도 차단 → 유효 cross 이벤트 놓침
- **결론**: ema_slope_min_buy 방향 탐색 종료. 기본값(0.0) 유지. 코드는 보존 (다른 심볼용)

### F(리서치): EMA slope 실패 원인 분석
- cross 직후 EMA20 slope이 아직 0에 가까움 → 진입 직후 slope 측정은 타이밍 어긋남
- RANGING(47.3%)에서 cross가 많음 → slope 필터가 유리한 RANGING cross도 차단
- **다음 탐색 방향**: feed.py 추가 피처 파악 (atr 기반 변동성 조건 등)

## 코드 변경 사항

| 파일 | 변경 |
|------|------|
| `src/strategy/dema_cross.py` | `ema_slope_min_buy` 파라미터 추가 (Cycle372 D) |
| `src/backtest/walk_forward.py` | DEFAULT_GRIDS + optimize_dema_cross() ema_slope 추가 |
| `scripts/paper_simulation.py` | ema_slope_min_buy 실험 후 복원 |

## Cycle 373 예고

- **C(데이터)**: feed.py 추가 피처 파악 → dema_cross 새 필터 방향 탐색
- **B(리스크)**: DrawdownMonitor transition_cushion 직렬화 테스트 추가
- **F(리서치)**: RANGING 구간 dema_cross 성능 분석 → 다음 실험 방향 결정
