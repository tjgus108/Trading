# Current Cycle Briefing

_Cycle 313 | 2026-06-15 | C(데이터) + B(리스크) + F(리서치)_

## 완료된 작업

### C(데이터) — NR_SCAN_WINDOW 실험
- `src/strategy/narrow_range.py` NR_SCAN_WINDOW: 3→5 실험 후 **즉시 복원 (역효과 확정)**
  - BTC 1h: rank15, Sharpe=-1.42, PF=0.90, return=-6.87% (기존 대비 악화)
  - 4h OOS: std=5.447 (불안정 증가) — 오래된 NR 참조 → 오신호 증가
  - 결론: NR_SCAN_WINDOW=3 유지. 다음 실험 후보: VOL_SPIKE_MULT 1.0→0.5

### B(리스크) — should_kill_strategy 레짐별 테스트
- `tests/test_risk_manager.py` `TestShouldKillStrategyRegime` 클래스 추가 (9개 테스트)
  - BULL/BEAR/CRISIS/HIGH_VOL/RANGING/None 시나리오 완전 커버
  - 총 **8413 passed, 23 skipped** (회귀 없음)

### F(리서치) — 1h PF 구조적 FAIL 분석
- atr_multiplier_tp=3.5 (Cycle 256에서 이미 최적화됨, NEXT_STEPS의 3.0은 오류 수정)
- 1h PF<1.5 구조적 문제: TP/SL 비율 개선 아닌 신호 승률 문제 → 4h OOS 집중 전략 채택
- supertrend_multi 4h: 5/6 valid PASS (avg=4.880) — 실전 투입 후보 #1

## 시뮬레이션 결과

| 항목 | BTC 1h | ETH 1h | SOL 1h |
|------|--------|--------|--------|
| PASS | 0/22 | 0/22 | 0/22 |
| rank1 | price_cluster (0.59) | momentum_quality | elder_impulse |
| narrow_range | Sharpe=-1.42, PF=0.90 | rank3, Sharpe=-1.17 | - |
| 주 실패 원인 | PF<1.5 (압도적) | PF<1.5 | PF<1.5 |

Bundle OOS 4h (9-fold, --csv-dir 누락 주의):
- supertrend_multi: 5/6 PASS, avg=4.880 ← 유망 전략 #1
- narrow_range (NR=5): 3/8 PASS, std=5.447 ← 역효과 → 복원

## 다음 사이클 (314: D+E+F)

| 카테고리 | 작업 | 근거 |
|---------|------|------|
| D(ML) | VOL_SPIKE_MULT 1.0→0.5 실험 | narrow_range 거래 수 증가 마지막 후보 |
| E(실행) | supertrend_multi 4h 파라미터 검토 | 5/6 valid PASS 유망 전략 |
| F(리서치) | Bundle OOS --csv-dir 의존성 재확인 | Cycle 313 누락으로 9-fold 변경 |

**⚠️ 주의**: 다음 Bundle OOS 실행 시 반드시 `--csv-dir data/historical` 포함
