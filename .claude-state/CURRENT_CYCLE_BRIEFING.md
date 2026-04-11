======================================================================
🔄 CYCLE 36 — 2026-04-11T08:40:19.230583Z
======================================================================

## 이번 사이클 배정 카테고리 (병렬 3개)

### [A] Quality Assurance
- **Agent**: backtest-agent
- **Focus**: 전략 품질 재검증, 테스트 커버리지, 기존 실패 테스트 수정

### [C] Data & Infrastructure
- **Agent**: data-agent
- **Focus**: WebSocket 안정성, DataFeed 캐시, OrderFlow 정확도, 온체인 데이터

### [F] Research
- **Agent**: strategy-researcher-agent
- **Focus**: 트레이딩봇 실패/성공 케이스 리서치 (필수), 최신 논문 조사 (구현 없이)

## 이전 사이클 현황
**Cycle 34 COMPLETED — C + B + F** (2026-04-11 13:25 UTC)
  **[C] Data:** src/data/feed.py에 cache_stats() 메서드 추가. hit_count/miss_count 추적, hit_rate 계산. +4 tests.
  **[B] Risk:** src/risk/circuit_breaker.py 연속 손실 쿨다운 구현. record_trade_result() + tick_cooldown() + max_consecutive_losses 도달 시 cooldown_remaining 설정. +3 tests. 기존 로직 전무했음.
  **[F] Research:** Paper→Live 전환 기준. 4~8주 paper + 100+ 트레이드 + 상승/하락 레짐 각 1회. 전환 지표 Sharpe≥1.0, PF≥1.5, MDD≤20%. 자본 5~10%로 시작 후 증액.
  **Tests:** 6005 passed 🎉 (+7 from Cycle 33).

**[!] 감지된 이슈:**
  - CRITICAL 항목 감지
  - FAIL 기록 존재

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
