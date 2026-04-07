---
name: resume-work
description: 이전 세션 상태를 복원하고 오늘의 작업 계획을 확인하는 스킬
---

# 작업 재개 프로토콜

이 스킬을 실행하면 현재 프로젝트 상태를 빠르게 파악하고 다음 할 일을 확인합니다.

## Step 1: 상태 파일 읽기

다음 파일을 순서대로 읽으세요:

```
.claude-state/NEXT_STEPS.md   — 전체 Phase 완료 현황 + 남은 작업
.claude-state/TODAY_PLAN.md   — 오늘 에이전트별 할 일 목록 + 완료 체크
.claude-state/POSITIONS.md    — 현재 오픈 포지션 (있을 경우)
```

## Step 2: 현재 상태 요약 출력

읽은 내용을 바탕으로 아래 형식으로 출력하세요:

```
=== TRADING BOT 작업 재개 ===

[프로젝트 상태]
- Phase 완료: A/B/C/D 전체
- 전략 수: 6~8종 (STRATEGY_REGISTRY 확인)
- 테스트: XXX passed

[오늘 남은 작업]
- [ ] 미완료 태스크 1
- [ ] 미완료 태스크 2
- [x] 완료된 태스크

[다음 즉시 할 일]
1. 가장 우선순위 높은 미완료 태스크
2. 의존성 없는 병렬 가능 태스크

[유의사항]
- python3 = /usr/bin/python3 (3.9.6) 사용
- 테스트: /usr/bin/python3 -m pytest tests/ --ignore=tests/integration
- 새 전략: BaseStrategy 상속 + STRATEGY_REGISTRY 등록
```

## Step 3: 작업 시작

미완료 태스크가 있으면 즉시 작업을 시작하세요.
의존성 없는 태스크는 병렬 Agent로 실행하세요.

---

## 핵심 파일 위치 (빠른 참조)

| 파일 | 역할 |
|---|---|
| src/orchestrator.py | BotOrchestrator + STRATEGY_REGISTRY |
| src/pipeline/runner.py | TradingPipeline (data→context→alpha→risk→exec) |
| src/strategy/base.py | BaseStrategy ABC |
| src/alpha/context.py | MarketContext (B1~B3) |
| src/alpha/ensemble.py | MultiLLMEnsemble (D1) |
| src/data/websocket_feed.py | BinanceWebSocketFeed (D2) |
| src/backtest/walk_forward.py | WalkForwardOptimizer (D3) |
| src/ml/trainer.py | WalkForwardTrainer (RF) |
| src/ml/lstm_model.py | LSTMSignalGenerator |
| scripts/train_ml.py | ML 학습 스크립트 |

## 실행 명령어

```bash
# 데모 (API 키 없이)
/usr/bin/python3 main.py --demo --tournament --dashboard

# 전체 기능
/usr/bin/python3 main.py --websocket --ensemble --walk-forward --loop --dashboard

# 테스트
/usr/bin/python3 -m pytest tests/ --ignore=tests/integration -v

# ML 학습 (sklearn 필요)
/usr/bin/python3 scripts/train_ml.py --model rf --symbol BTC/USDT

# 새 전략 백테스트
/usr/bin/python3 main.py --backtest --demo
```

## 에이전트 팀 (14종)

| 에이전트 | 모델 | 역할 |
|---|---|---|
| orchestrator | Sonnet | 전체 파이프라인 조율 |
| strategy-researcher-agent | Sonnet | 새 전략 리서치/구현 |
| alpha-agent | Sonnet | 신호 생성 (Bull/Bear 토론) |
| risk-agent | Sonnet | 리스크 게이트키퍼 |
| ml-agent | Sonnet | ML 학습/추론 |
| data-agent | Haiku | 시세/지표 수집 |
| backtest-agent | Haiku | 전략 성과 검증 |
| sentiment-agent | Haiku | Fear&Greed + 펀딩비 |
| onchain-agent | Haiku | 온체인 신호 |
| news-agent | Haiku | 뉴스 리스크 감지 |
| execution-agent | Haiku | 주문 실행/슬리피지 |
| memory-agent | Haiku | 세션 상태 복원 |
| researcher | Haiku | 코드베이스 탐색 |
| reviewer | Haiku | 코드 검토 |
