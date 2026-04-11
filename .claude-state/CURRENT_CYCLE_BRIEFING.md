======================================================================
🔄 CYCLE 36 — 2026-04-11T08:42:11.517927Z
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
**Cycle 35 COMPLETED — D + E + F** (2026-04-11 13:45 UTC)
  **[D] ML:** tests/test_multi_signal.py에 동점 처리 테스트 3개 추가. _aggregate() tie 로직이 이미 정확히 HOLD+LOW 반환함을 검증.
  **[E] Execution:** scripts/cycle_dispatcher.py에 read_worklog_summary() 추가. 브리핑에 이전 사이클 요약 + CRITICAL/FAIL/ERROR/pending 감지 자동 삽입. 다음 사이클부터 더 풍부한 컨텍스트.
  **[F] Research:** TradingView webhook 봇. Plus 필수, 포트 80/443 한정, 응답 3초 제한. Pine Script 바 마감 1회만 실행으로 고빈도 불가. 외부 Flask 서버 연동 필요, 지연/보안 리스크.
  **Tests:** 6008 passed (+3 from Cycle 34).

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
