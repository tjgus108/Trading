======================================================================
🔄 CYCLE 97 — 2026-04-11T19:17:17.072845Z
======================================================================

## 이번 사이클 배정 카테고리 (병렬 3개)

### [B] Risk Management
- **Agent**: risk-agent
- **Focus**: DrawdownMonitor, Kelly Sizer 튜닝, CircuitBreaker 개선, VaR/CVaR 검증

### [D] ML & Signals
- **Agent**: ml-agent
- **Focus**: LSTM 재학습, RF 피처 분석, 앙상블 가중치, Walk-Forward 통합

### [SIM] Paper Simulation & Auto-improve
- **Agent**: backtest-agent
- **Focus**: scripts/paper_simulation.py 실행 → 결과 분석 → PASS 전략 하위 1-2개 개선 제안/적용

### [F] Research
- **Agent**: strategy-researcher-agent
- **Focus**: 트레이딩봇 실패/성공 케이스 리서치 (필수), 최신 논문 조사 (구현 없이)

## 이전 사이클 현황
**Cycle 96 COMPLETED — A + C + SIM + F** (2026-04-12 14:30 UTC)
  **[A] Quality:** 13 SIM 회귀 138/138 PASS 확인.
  **[C] Data:** src/data/news.py 중복 감지 공백/대소문자 정규화. +2 tests.
  **[SIM] No-op:** dema_cross 5가지 필터 시도 모두 실패 (PF 1.38 → 1.22/1.32 악화). 구조적 한계 확인, 원본 복원.
  **[F] Research:** Kelly 실전. 풀 켈리는 백테스트 전용, 실전은 Half/Quarter Kelly 또는 Fixed Fractional 1-2%. Kelly-Lite가 균형점.

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
