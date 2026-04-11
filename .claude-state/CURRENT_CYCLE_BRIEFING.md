======================================================================
🔄 CYCLE 64 — 2026-04-11T10:26:38.306867Z
======================================================================

## 이번 사이클 배정 카테고리 (병렬 3개)

### [C] Data & Infrastructure
- **Agent**: data-agent
- **Focus**: WebSocket 안정성, DataFeed 캐시, OrderFlow 정확도, 온체인 데이터

### [B] Risk Management
- **Agent**: risk-agent
- **Focus**: DrawdownMonitor, Kelly Sizer 튜닝, CircuitBreaker 개선, VaR/CVaR 검증

### [F] Research
- **Agent**: strategy-researcher-agent
- **Focus**: 트레이딩봇 실패/성공 케이스 리서치 (필수), 최신 논문 조사 (구현 없이)

## 이전 사이클 현황
**Cycle 63 COMPLETED — E + A + F** (2026-04-12 00:20 UTC)
  **[E] Execution:** tests/test_paper_trader.py +2 multi-symbol. BTC/ETH/SOL 동시 매수 balance 보존, BTC 매도가 ETH 포지션 간섭하지 않음.
  **[A] Quality:** 중복 테스트 이름 410개 발견 (여러 전략 파일에서 동일 test_buy_signal 등 사용). 전체 작동 정상, 정리는 향후 숙제.
  **[F] Research:** 거래소 수수료 2026. Bybit 선물 maker 0.020%/taker 0.055%. Binance taker 0.05% 소폭 낮음. Bybit MM 리베이트 -0.015% (기관). 봇은 maker 우선 권장.
  **Tests:** 6160 passed (+2 from Cycle 62).

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
