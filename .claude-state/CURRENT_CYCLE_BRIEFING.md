# Current Cycle Briefing

_Last updated: 2026-07-01 (Cycle 375 완료)_

## 현재 상태

- **완료된 사이클**: 375
- **다음 사이클**: 376 (376 mod 5 = 1 → B+D+F)
- **연속 PASS 실패**: 60연속 (0/19 1h paper_sim)
- **Bundle OOS**: 5/5 PASS 유지

## Cycle 375 주요 결과

### A(품질): bb_width_min_filter 테스트 추가
- `tests/test_phase_d.py`에 `TestDemaCrossBbWidthFilter` 클래스 4개 테스트 추가
- bb_width < threshold → HOLD 확인, >= threshold → 정상 신호 확인
- bb_width_min_filter=0.0(기본) → 필터 비활성, bb_width 컬럼 없음 → 미작동
- 전체 테스트: **8457 passed** (+4 신규)

### C(데이터): bb_width_min_filter=0.05 실험
- 기존 0.04 → 0.05로 상향 실험
- 결과: Sharpe=0.86, Trades=23 — **0.04와 완전 동일 (dead param)**
- 원인: bb_width 분포 p25=0.041 → 0.04~0.05 구간에 추가 cross 없음
- **결론**: 0.04 복원. bb_width_min_filter 탐색 완전 종료

### F(리서치): atr_multiplier_sl=1.2 WF 검증
- BacktestEngine atr_multiplier_sl=1.2 적용
- 결과: dema_cross **Sharpe 0.86→0.84(-0.02), PF 1.51→1.34(-0.17), Rank 1→3**
- 전체 데이터셋(Cycle374 F) 긍정과 WF 컨텍스트 역효과 불일치
- **결론**: atr_multiplier_sl=1.2 역효과 확정. SL=1.5(기본값) 유지. SL 방향 탐색 종료

## 코드 변경 사항

| 파일 | 변경 |
|------|------|
| `tests/test_phase_d.py` | `TestDemaCrossBbWidthFilter` 4개 테스트 추가 (A) |
| `scripts/paper_simulation.py` | 0.05 실험 → 복원 + 결과 주석 (C) |
| `scripts/paper_simulation.py` | SL=1.2 실험 → 복원 + 결과 주석 (F) |

## Cycle 376 예고 (376 mod 5 = 1 → B+D+F)

- **B(리스크)**: DrawdownMonitor/KellySizer 코드 품질 점검
- **D(ML)**: rsi_dir_threshold=35 실험 (현재 40 → 더 완화 → Trades 증가 기대)
- **F(리서치)**: dema_cross PASS 윈도우 분석 (2/8 PASS 윈도우 특성 파악)
