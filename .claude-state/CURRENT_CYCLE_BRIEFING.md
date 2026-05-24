# Current Cycle Briefing

_Updated: 2026-05-24 — Cycle 206 완료 (B+D+F)_

## 현재 상태

| 항목 | 값 |
|------|-----|
| 완료 사이클 | Cycle 206 |
| 다음 사이클 | Cycle 207 |
| 카테고리 | B(리스크) + D(ML) + F(리서치) |
| 테스트 수 | 7803 passed, 23 skipped |
| PASS 전략 수 | 22개 (QUALITY_AUDIT.csv) |
| SIM 결과 | 0/5 Bundle OOS PASS, 0/22 Paper SIM PASS (합성 데이터) |

## Cycle 206 변경 요약

### B1 KellySizer kelly_cap 보수화
- `src/risk/kelly_sizer.py`: kelly_cap 기본값 0.25 → 0.20
- OOS Sharpe std 높은 전략군 대상 포지션 상한 강화
- `tests/test_kelly_quarter_cap.py` + `tests/test_kelly_twap.py` 테스트 업데이트

### B2 DrawdownMonitor 하이브리드 streak 회복
- `src/risk/drawdown_monitor.py`: `streak_recovery_grace_seconds` 파라미터 추가 (기본 0=비활성)
- 마지막 손실 이후 grace_seconds 경과 시 consecutive_losses 자동 초기화
- 하이브리드(실적 기반 + 시간 기반) 회복 방식 지원
- `_last_loss_at` 상태 + to_dict/from_dict/reset 완전 통합

### B3 DataFeed CircuitBreaker recovery_timeout 연장
- `src/data/feed.py`: recovery_timeout 60s → 300s (5분)
- API 장애 직후 OPEN→HALF_OPEN 전환 대기 시간 연장으로 재시도 폭주 방지

### D1 MLSignalGenerator feature pruning helper
- `src/ml/model.py`: `get_low_importance_features(threshold=0.01)` 추가
- 낮은 중요도 피처 이름 반환 → 재학습 시 피처 선택 지원

### F narrow_range 신호 조건 완화
- `src/strategy/narrow_range.py`: ATR_THRESHOLD 0.85→0.90, VOL_SPIKE_MULT 1.2→1.0
- 4h 봉 거래 수 증가 목적 (현재 모든 fold 0건 → 다음 SIM 확인)

## SIM 결과 주요 패턴 (Cycle 206)

- Paper SIM 1h (합성): 0/22 PASS (동일 패턴)
  - price_action_momentum: avg Sharpe=6.90, cmf: 5.99
  - elder_impulse: avg Sharpe=1.32, 28 trades
- Bundle OOS 4h (합성): 0/5 PASS
  - narrow_range: 모든 fold 거래 0건 (ATR_THRESHOLD 완화 적용됨, 다음 SIM 검증 필요)
  - elder_impulse fold 1 PASS (OOS=3.794) — 실데이터 검증 후보
  - value_area: OOS Sharpe std=6.589 (va_mult 범위 축소 효과는 실데이터에서 확인 필요)

## 다음 사이클 우선순위 (Cycle 207, 207 mod 5 = 2)

**B(리스크) + D(ML) + F(리서치)** (동일 패턴)

1. narrow_range ATR 완화 효과 Bundle OOS 재확인
2. VaR/CVaR 계산 정확도 검증 (`src/risk/portfolio_optimizer.py`)
3. CircuitBreaker vs DrawdownMonitor streak 임계값 정합성 검토 (3 vs 5)
4. HMM 레짐 감지 모델 활성화 여부 확인
