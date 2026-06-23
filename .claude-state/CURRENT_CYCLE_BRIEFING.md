# Current Cycle Briefing

_Last updated: 2026-06-23 (Cycle 346 완료)_

## 현재 상태 요약

- **현재 사이클**: 346 완료 (B(리스크) + D(ML) + F(리서치))
- **1h Paper Sim**: 0/20 PASS — 26연속 FAIL streak
- **4h Bundle OOS**: 5/5 PASS 안정 유지 (OFI Sharpe=4.345)
- **테스트**: 8430 passed, 23 skipped

## 이번 사이클 핵심 변경

| 변경 | 파일 | 내용 |
|------|------|------|
| B(리스크) | `src/risk/drawdown_monitor.py` | RANGING 매크로 방향성 중립 판별 추가 |
| D(ML) | `src/backtest/walk_forward.py` | narrow_range ema_slope 그리드 0.002→0.0005 |
| 테스트 | `tests/test_risk.py` | 매크로 중립 판별 테스트 4개 추가 |

## 핵심 인사이트

1. **RANGING 매크로 중립**: |ema50_slope| < 0.0005인 캔들이 RANGING에서 45.1%
   - 이 구간에서만 price_cluster 같은 mean-reversion이 PASS (W6 Sharpe=3.78)
   - DrawdownMonitor가 이제 RANGING을 neutral/directional로 세분화

2. **narrow_range ema_slope**: 0.001 임계값은 RANGING BUY 72.9% 차단 → 너무 엄격
   - 0.0005로 완화하면 61.8% 차단 → WFO가 최적값 탐색 가능

3. **1h PASS 구조적 한계 재확인**: PF < 1.5가 핵심 bottleneck
   - 수수료 0.11% round-trip의 1h 상대비중이 너무 높음
   - 4h Bundle OOS 5/5 PASS → 타임프레임 업그레이드가 근본 해결책

## 다음 사이클 (347, mod 5 = 2 → B+D+F 동일)

- B: DrawdownMonitor macro neutral 실전 연동 (manager.py 통합)
- D: narrow_range 0.0005 WFO 효과 검증
- F: 4h paper_sim 시험 가능성 탐색 (`--timeframe 4h`)
