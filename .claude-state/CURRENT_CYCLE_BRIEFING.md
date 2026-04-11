======================================================================
🔄 CYCLE 51 — 2026-04-11T09:34:53.912507Z
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
**Cycle 49 COMPLETED — C + B + F** (2026-04-11 18:35 UTC)
  **[C] Data:** src/data/news.py 중복 감지 추가. MD5 hash (정규화), 24h 윈도우, 만료 자동 제거. NewsEvent.title_hash 필드. +7 tests.
  **[B] Risk:** tests/test_risk_manager.py +2 multi-position 경계. 동일 방향 누적 30% 경계, 반대 방향 gross 35% BLOCKED (net 5% 아님).
  **[F] Research:** Bybit 2025 사건. Feb 21 Lazarus $1.5B 해킹 (역대 최대). 멀티시그 강화, API 보안 오버홀. Aug 2025 기관 rate limit 도입, 일반 perp 400 req/s 유지. **우리 봇: API 키 2FA 필수**.
  **Tests:** 6093 passed (+9 from Cycle 48).

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
