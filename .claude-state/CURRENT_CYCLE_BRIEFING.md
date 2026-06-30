# Current Cycle Briefing

_Last updated: 2026-06-30 (Cycle 374 완료)_

## 현재 상태

- **완료된 사이클**: 374
- **다음 사이클**: 375 (375 mod 5 = 0 → A+C+F)
- **연속 PASS 실패**: 59연속 (0/19 1h paper_sim)
- **Bundle OOS**: 5/5 PASS 유지

## Cycle 374 주요 결과

### D(ML): dema_cross BB width squeeze 필터 추가
- `bb_width_min_filter=0.0` 파라미터 추가
- BTC 1h bb_width 분포: mean=0.0645, p25=0.041 → threshold=0.04(하위 23%) 실험
- 실험 결과: **Sharpe 0.80→0.85(+0.05), PF=1.38(유지), Trades 30→26** — mild positive
- 판단: dead param 아님 — paper_simulation.py에 유지

### E(실행): PaperConnector 데이터 흐름 확인
- PaperConnector는 주문 실행 전담 — 지표 계산 체인과 무관
- enrich_indicators()에서 bb_width/macd_hist 이미 정상 계산됨 (Cycle373 C)
- **결론**: 추가 조치 불필요

### F(리서치): SL 방향 발굴
- avg_win=186.5 USD, avg_loss=93.9 USD, win_loss_ratio=1.987
- max_hold=48 이미 최적
- **SL=1.2 ATR 발굴**: 전체 데이터 PF +5%, Sharpe +25%, W/L ratio +27%
- WF 컨텍스트 검증 필요 → Cycle375 F에서 paper_sim 실험

## 코드 변경 사항

| 파일 | 변경 |
|------|------|
| `src/strategy/dema_cross.py` | `bb_width_min_filter=0.0` 파라미터 + BB squeeze 차단 로직 (D) |
| `src/backtest/walk_forward.py` | DEFAULT_GRIDS + factory에 `bb_width_min_filter` 추가 (D) |
| `scripts/paper_simulation.py` | `bb_width_min_filter=0.04` 실험 — mild positive 유지 (D) |

## Cycle 375 예고 (375 mod 5 = 0 → A+C+F)

- **A(품질)**: bb_width_min_filter 단위 테스트 추가 (test_phase_d.py)
- **C(데이터)**: bb_width_min_filter=0.05 실험 (더 강한 squeeze 필터 탐색)
- **F(리서치)**: atr_multiplier_sl=1.2 paper_sim WF 검증
