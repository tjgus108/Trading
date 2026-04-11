======================================================================
🔄 CYCLE 75 — 2026-04-11T11:26:36.185861Z
======================================================================

## 이번 사이클 배정 카테고리 (병렬 3개)

### [D] ML & Signals
- **Agent**: ml-agent
- **Focus**: LSTM 재학습, RF 피처 분석, 앙상블 가중치, Walk-Forward 통합

### [E] Execution
- **Agent**: execution-agent
- **Focus**: Paper Trading, TWAP 검증, 슬리피지 모델, Telegram 알림

### [F] Research
- **Agent**: strategy-researcher-agent
- **Focus**: 트레이딩봇 실패/성공 케이스 리서치 (필수), 최신 논문 조사 (구현 없이)

## 이전 사이클 현황
**Cycle 74 COMPLETED — C + B + F** (2026-04-12 04:00 UTC)
  **[C] Data:** tests/test_onchain_consistency.py 신규 +3. mock 일관성, score 재계산, [-3,+3] 경계 검증.
  **[B] Risk:** tests/test_circuit_breaker.py +2 reset_all. 연속 손실+쿨다운 초기화, 플래시 크래시 트리거 후 재개 확인.
  **[F] Research:** ETF Option Bots. BITO(선물) + IBIT(현물) 옵션 체인 활성화. IV rank 기반 strangle 매도, GEX flip 결합 타이밍 정밀도 향상.
  **Tests:** 6212 passed (+5 from Cycle 73).

**[!] 감지된 이슈:**
  - CRITICAL 항목 감지

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
