# Next Steps

_Last updated: 2026-04-10_

## ⛔ 중요: 전략 추가 중단

**더 이상 새로운 전략을 추가하지 마세요.**
현재 387개 전략이 있으며, 이 중 실제로 유효한 전략을 검증하는 것이 우선입니다.

---

## 우선순위 작업 (순서대로 진행)

### 1️⃣ 전략 백테스트 품질 검증 (최우선)
- 387개 전략 중 상위 전략 선별 (Sharpe, win_rate, max_drawdown 기준)
- 수수료(0.1%) + 슬리피지(0.05%) 반영된 백테스트 결과로 평가
- **Sharpe < 0.5 or win_rate < 40% 전략은 비활성화 후보로 분류**
- 결과를 `.claude-state/BACKTEST_REPORT.md`에 기록

### 2️⃣ 전략 간 상관관계 분석
- `src/analysis/strategy_correlation.py` 활용
- 실제 신호 시계열 기반 Pearson 상관 계산
- 상관관계 0.8 이상인 중복 전략 쌍 식별 → 하나만 유지
- 결과를 `.claude-state/CORRELATION_REPORT.md`에 기록

### 3️⃣ Walk-Forward 토너먼트 통합
- `src/backtest/walk_forward.py`를 토너먼트 파이프라인에 연결
- IS/OOS 비율로 과최적화 필터링
- 과최적화된 전략 식별 및 제거

### 4️⃣ Paper Trading 준비
- 검증 통과한 상위 10~20개 전략만 활성화
- Paper trading 모드 설정 및 테스트
- Telegram 알림 활성화 (`config.yaml`에서 `enabled: true`)

---

## 완료된 작업 (건드리지 말 것)
- 전략 387개 구현 (충분함, 더 추가하지 말 것)
- 테스트 5,600개+ 통과
- BacktestEngine 수수료/슬리피지 반영
- Config limit 1000 확장
- Phase A~L 전체 완료
