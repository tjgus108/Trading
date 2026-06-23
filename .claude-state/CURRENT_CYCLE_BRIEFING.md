# Current Cycle Briefing

_Last updated: 2026-06-23 (Cycle 349 완료)_

## 현재 상태 요약

- **현재 사이클**: 349 완료 (D(ML) + E(실행) + F(리서치))
- **1h Paper Sim**: 0/20 PASS — 29연속 FAIL streak
- **4h Bundle OOS**: 5/5 PASS 안정 유지 (OFI Sharpe=4.345)
- **테스트**: 8434 passed, 23 skipped

## 이번 사이클 핵심 변경

| 변경 | 파일 | 내용 |
|------|------|------|
| E(실행) | `scripts/paper_simulation.py` | `--max-hold-override` CLI 인자 추가 |
| E(실행) | `scripts/paper_simulation.py` | 4h 기본 max_hold: ACTIVE_TIMEFRAME 기반 자동 설정 (4h→24봉, 1h→48봉) |

## 핵심 인사이트

1. **4h max_hold=24봉(4일)이 48봉(8일)보다 현저히 우수**:
   - price_cluster: 4h Sharpe 1.08(max48) → **2.26(max24)** (+109%)
   - cmf: 4h Sharpe 0.58 → 0.84 (+45%)
   - supertrend_multi: Sharpe 2.06 → 2.20 (+7%)
   - Bundle OOS와 max_hold 통일 완료 (24봉 = 4일)

2. **ETH dema_cross HIGH% 구조적 원인 확정**:
   - dist_pct >= 0.5% 필터 = EMA 상위 5th percentile 분기만 선택
   - 전체 780 crossover: HIGH% = 21% (전체 데이터와 동일)
   - 0.5% 필터 후 41 신호: HIGH% = 85.4% (4배 상승)
   - EMA crossover 본질적 특성 → 필터 완화 없이는 해결 불가
   - 결론: "80.8% HIGH"는 dema_cross 전략 특성상 수용 가능

3. **4h paper_sim의 유효성 확인**:
   - 수수료 드래그: 1h 0.11% round-trip → 4h 0.11% (동일) but 봉당 기회 1/4
   - 4h에서 Sharpe 2.26 달성 (price_cluster) — 다음 사이클 전략 전체 4h 테스트 필요

4. **29연속 0/20 1h FAIL 지속**:
   - 근본: 수수료 대비 alpha 부족 (PF 1.20 < 1.5 기준)
   - 4h 경로가 더 유망: max_hold=24 조정 후 2배 이상 Sharpe 개선

## 다음 사이클 (350, mod 5 = 0 → A(품질) + C(데이터) + F(리서치))

- A(품질): 4h paper_sim 전체 실행 (전략 전체, max_hold=24 기본값 활용)
- C(데이터): SOL vol_spike_prob 0.35→0.25 보정 검토 (HIGH% 54%→40% 목표)
- F(리서치): price_cluster 4h OOS 검증 가능성, Bundle OOS 추가 전략 검토
