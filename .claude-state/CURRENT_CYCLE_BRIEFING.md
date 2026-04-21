======================================================================
🔄 CYCLE 180 — 2026-04-22
======================================================================

## 이번 사이클 배정 카테고리 (병렬 3개)

### [A] Quality Assurance
- **Agent**: backtest-agent
- **Focus**: 실데이터 OOS 실행 (run_bundle_oos.py), 5-Bundle WFE 검증

### [C] Data & Infrastructure
- **Agent**: data-agent
- **Focus**: DataFeed 안정성 검증, WebSocket reconnect 로직, 레짐 피처 E2E

### [F] Research
- **Agent**: strategy-researcher-agent
- **Focus**: 트레이딩봇 실패/성공 케이스 리서치 (필수), 포지션 동기화 + 장애 복구 패턴

## 이전 사이클 현황
**Cycle 179 COMPLETED — D + E + F** (2026-04-22)
  **[D] ML:** RegimeDetector→paper_trader 통합 (23 tests). CRISIS 0.5x, 라우터 스킵.
  **[E] 실행:** 5-Bundle OOS 스크립트 + PerformanceMonitor→paper_trader 연결 (11 tests).
  **[F] 리서치:** Paper 4~8주+5%급락 필수, Go/No-Go 자동판정, systemd/Ofelia, API 3패턴.

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
