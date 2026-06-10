# Current Cycle Briefing

_Cycle 296 완료 — 2026-06-10_
_카테고리: B(리스크) + D(ML) + F(리서치)_

## 이번 사이클 요약

### 완료한 작업

1. **B(리스크)**: MC 임계값 완화 — 15 trades 수준 통계 검증력 개선
   - `src/backtest/engine.py`: MC_P_THRESHOLD 0.05 → 0.10
   - `scripts/paper_simulation.py`: run_simulation/argparse default 0.05→0.10 동기화
   - **버그 수정**: paper_simulation의 run_simulation() 기본값이 engine.py 변경을 덮어쓰는 문제 발견·수정

2. **D(ML)**: relative_volume bull_only 레짐 필터
   - `src/strategy/relative_volume.py`: bull_only 파라미터 추가 (기본값=False)
   - **실험**: PAPER_SIM에 bull_only=True → trades 15→14 (역효과) → PAPER_SIM에서 제거
   - 코드 기능은 보존 (향후 실험 가능)

3. **F(리서치)**: price_cluster 파라미터화
   - `src/strategy/price_cluster.py`: close_window, n_bins 생성자 파라미터 추가
   - PAPER_SIM 오버라이드: close_window=35 테스트 → trades 여전히 11 (효과 없음)
   - 다음 사이클: n_bins=3 시도 검토

### 현재 성과 지표

- **테스트**: 8392 passed (회귀 없음)
- **Paper Sim**: 0/22 PASS (MC 임계값 버그로 구기준 적용됨 → Cycle 297에서 재확인)
  - 최고 전략: momentum_quality (Sharpe=1.82, trades=22, score=73.3)
  - relative_volume: trades=14 (bull_only 역효과)
- **Bundle OOS**: 2/5 PASS (cmf + supertrend_multi, Cycle 295 동일)

### 다음 사이클 우선순위

**Cycle 297 = B(리스크) + D(ML) + F(리서치)**

1. **B**: 수정된 MC_P_THRESHOLD=0.10 기준으로 Paper Sim 재실행 → order_flow_imbalance_v2 통과 확인
2. **D**: price_cluster n_bins=3 실험 (더 넓은 bin → trades 증가 가능성)
3. **F**: momentum_quality bear 레짐 FAIL 분석 → bull_only 파라미터 추가 검토
