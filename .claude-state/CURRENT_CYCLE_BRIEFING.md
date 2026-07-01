# Current Cycle Briefing

_Last updated: 2026-07-01 (Cycle 376 완료)_

## 현재 상태

- **완료된 사이클**: 376
- **다음 사이클**: 377 (377 mod 5 = 2 → E+A+F)
- **연속 PASS 실패**: 61연속 (0/19 1h paper_sim)
- **Bundle OOS**: 5/5 PASS 유지

## Cycle 376 주요 결과

### B(리스크): DrawdownMonitor + KellySizer 검토 + 버그 수정
- DrawdownMonitor cooldown(1h/4h) → dema_cross 평균 1.8일/거래 간격 대비 적절. 변경 불필요
- KellySizer Half-Kelly=6.9% < max_fraction=10% → Kelly binding, 현 설정 적절
- **버그 수정**: `src/risk/kelly_sizer.py` `MIN_TRADES_FOR_KELLY: int = 10` 중복 정의 제거 (line 609)
  - 152개 Kelly 테스트 통과 ✓

### D(ML): rsi_dir_threshold=35 실험
- 기존 thr=40 → thr=35 실험: Sharpe=0.41, Trades=28 (vs thr=40: Sh=0.85, Trades=26)
- **결과**: Sharpe -52%, Trades +2 → **dead param 확정**. thr=40 복원
- rsi_dir_threshold 탐색 완전 종료 (35/40/45/50 전부 검증됨)

### F(리서치): dema_cross WF 윈도우별 PASS/FAIL 분석
- W1/W5 PASS (Sh≈2.95): BTC 강세장 기간 (2023 여름, 2024 초)
- W6 근접 (Sh=1.82, PF=1.53): mc_p_value=0.194 실패 (Trades=23, 통계 유의성 부족)
- W7 근접 (Sh=0.93): 0.07 부족
- W3 최악 (Sh=-3.27): 2023 하락/횡보 레짐
- **핵심 결론**: PASS = BTC 강세 레짐. EMA200 BUY 필터가 다음 탐색 방향

## 코드 변경 사항

| 파일 | 변경 |
|------|------|
| `src/risk/kelly_sizer.py` | `MIN_TRADES_FOR_KELLY` 중복 제거 (B) |
| `scripts/paper_simulation.py` | rsi_thr=35 실험 → 복원 + 결과 주석 (D) |

## Cycle 377 예고 (377 mod 5 = 2 → E+A+F)

- **E(실행)**: BacktestEngine 실행 품질 점검 (W3 극단 손실 원인 분석)
- **A(품질)**: EMA200 BUY 필터 구현 실험 (feed.py + dema_cross.py + paper_sim)
- **F(리서치)**: dema_cross 장세 레짐별 성과 분석 심화
