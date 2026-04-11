======================================================================
🔄 CYCLE 96 — 2026-04-11T18:48:38.703305Z
======================================================================

## 이번 사이클 배정 카테고리 (병렬 3개)

### [A] Quality Assurance
- **Agent**: backtest-agent
- **Focus**: 전략 품질 재검증, 테스트 커버리지, 기존 실패 테스트 수정

### [C] Data & Infrastructure
- **Agent**: data-agent
- **Focus**: WebSocket 안정성, DataFeed 캐시, OrderFlow 정확도, 온체인 데이터

### [SIM] Paper Simulation & Auto-improve
- **Agent**: backtest-agent
- **Focus**: scripts/paper_simulation.py 실행 → 결과 분석 → PASS 전략 하위 1-2개 개선 제안/적용

### [F] Research
- **Agent**: strategy-researcher-agent
- **Focus**: 트레이딩봇 실패/성공 케이스 리서치 (필수), 최신 논문 조사 (구현 없이)

## 이전 사이클 현황
**Cycle 95 COMPLETED — D + E + SIM + F** (2026-04-12 13:50 UTC)
  **[D] ML:** tests/test_adaptive_selector.py +1 저 Sharpe → 선택 빈도 감소 검증.
  **[E] Execution:** tests/test_kelly_twap.py +2 Kelly+TWAP 파이프라인 통합 시나리오.
  **[SIM] Auto-improve:** relative_volume RVOL 임계값 2.0 → 1.5 완화 + VWAP OR 조건. **+0.74% → +7.87%** (Sharpe 0.32 → 1.86). 테스트 1개 업데이트 (rvol 1.67 기존 HOLD → BUY 허용).
  **[F] Research:** Walk-forward 파라미터. IS/OOS 70-80/20-30 표준, 67/33 권장 (OOS Sharpe 1.89). 창 크기: 단기 2y/6m, 장기 5y/1y.

## ⛔ 금지 사항
- 새 전략 파일 생성 금지 (현재 ~355개로 충분)
- 한 카테고리에 2 사이클 연속 집중 금지
- 실패 사례 리서치 없이 코드만 작성 금지

## 📋 사이클 종료 시 필수 수행
1. .claude-state/WORKLOG.md 업데이트 (이번 사이클 작업 기록)
2. STATUS.md 업데이트 (전체 현황)
3. .claude-state/NEXT_STEPS.md 업데이트 (다음 작업 힌트)
4. git add -A && git commit -m '[Cycle N] 카테고리 요약' && git push
5. CYCLE_STATE.txt 다음 사이클 번호로 업데이트

## 🚀 실행 지침 (Claude Code 세션용)
이 브리핑을 읽은 Claude Code는 다음과 같이 진행:
1. 위 3개 카테고리를 Agent tool로 *병렬* 실행
2. 각 agent는 해당 카테고리 focus 항목 중 1~2개 실제 개선 작업 수행
3. 모든 agent 완료 후 WORKLOG/STATUS/NEXT_STEPS 업데이트
4. 커밋 + push
