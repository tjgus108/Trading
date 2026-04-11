======================================================================
🔄 CYCLE 37 — 2026-04-11T08:45:30.356966Z
======================================================================

## 이번 사이클 배정 카테고리 (병렬 3개)

### [B] Risk Management
- **Agent**: risk-agent
- **Focus**: DrawdownMonitor, Kelly Sizer 튜닝, CircuitBreaker 개선, VaR/CVaR 검증

### [D] ML & Signals
- **Agent**: ml-agent
- **Focus**: LSTM 재학습, RF 피처 분석, 앙상블 가중치, Walk-Forward 통합

### [F] Research
- **Agent**: strategy-researcher-agent
- **Focus**: 트레이딩봇 실패/성공 케이스 리서치 (필수), 최신 논문 조사 (구현 없이)

## 이전 사이클 현황
**Cycle 36 COMPLETED — A + C + F** (2026-04-11 14:05 UTC)
  **[A] Quality:** tests/test_monte_carlo.py 신규 (+10 경계 조건). Monte Carlo 빈 데이터/단일 거래/NaN/음수/seed 재현성/0 변동성/annualization 검증. src/backtest/monte_carlo.py에 빈 배열 처리 버그 수정.
  **[C] Data:** src/data/feed.py 에러 분류 (transient vs fatal). NetworkError/Timeout/RateLimit → 재시도, BadSymbol/Auth → 즉시 raise. +2 tests.
  **[F] Research:** 선물 vs 현물 봇. 선물은 레버리지(5~10x) 수익 확대 가능하나 청산/펀딩비 리스크. 현물은 청산 없고 그리드 적합. 성과 차이는 봇 유형보다 전략/레짐 적합성에 의존.
  **Tests:** 6020 passed (+12 from Cycle 35).

**[!] 감지된 이슈:**
  - CRITICAL 항목 감지
  - FAIL 기록 존재
  - ERROR 기록 존재
  - pending 항목 존재

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
